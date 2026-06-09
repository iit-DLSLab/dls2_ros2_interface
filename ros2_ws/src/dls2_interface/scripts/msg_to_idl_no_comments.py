#!/usr/bin/env python3
"""
Convert ROS 2 .msg files to IDL without carrying comments into @verbatim blocks.

This intentionally handles the ROS message subset used by this package:
- primitive fields
- custom message fields
- fixed arrays: T[N]
- dynamic arrays: T[]
- bounded arrays: T[<=N]
- constants: T NAME=value
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple


ROS_TO_IDL = {
    "bool": "boolean",
    "byte": "octet",
    "char": "char",
    "float32": "float",
    "float64": "double",
    "int8": "int8",
    "uint8": "octet",
    "int16": "short",
    "uint16": "unsigned short",
    "int32": "long",
    "uint32": "unsigned long",
    "int64": "long long",
    "uint64": "unsigned long long",
    "string": "string",
    "wstring": "wstring",
}

PRIMITIVE_TYPES = set(ROS_TO_IDL)
FIELD_RE = re.compile(
    r"^(?P<type>[A-Za-z][A-Za-z0-9_/]*)(?P<array>\[(?:<=)?\d*\])?\s+"
    r"(?P<name>[A-Za-z][A-Za-z0-9_]*)$"
)
CONST_RE = re.compile(
    r"^(?P<type>[A-Za-z][A-Za-z0-9_/]*)(?P<array>\[(?:<=)?\d*\])?\s+"
    r"(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*(?P<value>.+)$"
)


@dataclass(frozen=True)
class MsgType:
    ros_type: str
    array: Optional[str] = None


@dataclass(frozen=True)
class Field:
    type_info: MsgType
    name: str


@dataclass(frozen=True)
class Constant:
    type_info: MsgType
    name: str
    value: str


@dataclass
class MsgDefinition:
    constants: List[Constant]
    fields: List[Field]


def strip_comment(line: str) -> str:
    in_string = False
    quote = ""
    escaped = False

    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch in ("'", '"'):
            if in_string and ch == quote:
                in_string = False
                quote = ""
            elif not in_string:
                in_string = True
                quote = ch
            continue
        if ch == "#" and not in_string:
            return line[:i]

    return line


def parse_msg_type(raw_type: str, array: Optional[str]) -> MsgType:
    if array and raw_type in ("string", "wstring") and array.startswith("[<="):
        bound = array[3:-1]
        return MsgType(f"{raw_type}<={bound}")
    return MsgType(raw_type, array)


def parse_msg(path: Path) -> MsgDefinition:
    constants: List[Constant] = []
    fields: List[Field] = []

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_comment(raw_line).strip()
        if not line:
            continue

        const_match = CONST_RE.match(line)
        if const_match:
            if const_match.group("array"):
                raise ValueError(f"{path}:{line_no}: constants cannot be arrays")
            constants.append(
                Constant(
                    type_info=parse_msg_type(const_match.group("type"), None),
                    name=const_match.group("name"),
                    value=const_match.group("value").strip(),
                )
            )
            continue

        field_match = FIELD_RE.match(line)
        if field_match:
            fields.append(
                Field(
                    type_info=parse_msg_type(field_match.group("type"), field_match.group("array")),
                    name=field_match.group("name"),
                )
            )
            continue

        raise ValueError(f"{path}:{line_no}: unsupported .msg line: {raw_line!r}")

    return MsgDefinition(constants=constants, fields=fields)


def find_package_xml(start: Path) -> Optional[Path]:
    for path in [start, *start.parents]:
        package_xml = path / "package.xml"
        if package_xml.is_file():
            return package_xml
    return None


def infer_package_name(input_path: Path) -> Optional[str]:
    start = input_path if input_path.is_dir() else input_path.parent
    package_xml = find_package_xml(start)
    if not package_xml:
        return None

    match = re.search(r"<name>\s*([^<\s]+)\s*</name>", package_xml.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def normalize_ros_type(ros_type: str) -> Tuple[Optional[str], str]:
    parts = ros_type.split("/")
    if len(parts) == 1:
        return None, parts[0]
    if len(parts) == 2:
        return parts[0], parts[1]
    if len(parts) == 3 and parts[1] == "msg":
        return parts[0], parts[2]
    raise ValueError(f"unsupported ROS type name: {ros_type}")


def idl_base_type(type_info: MsgType, current_package: str) -> str:
    ros_type = type_info.ros_type

    bounded_string = re.match(r"^(w?string)<=([0-9]+)$", ros_type)
    if bounded_string:
        return f"{bounded_string.group(1)}<{bounded_string.group(2)}>"

    if ros_type in ROS_TO_IDL:
        return ROS_TO_IDL[ros_type]

    package, type_name = normalize_ros_type(ros_type)
    package = package or current_package
    return f"{package}::msg::{type_name}"


def idl_field_type(type_info: MsgType, current_package: str) -> str:
    base_type = idl_base_type(type_info, current_package)
    array = type_info.array
    if not array:
        return base_type
    if array == "[]":
        return f"sequence<{base_type}>"
    if array.startswith("[<="):
        return f"sequence<{base_type}, {array[3:-1]}>"
    return base_type


def idl_field_suffix(type_info: MsgType) -> str:
    array = type_info.array
    if array and array.startswith("[") and array.endswith("]") and array[1:-1].isdigit():
        return array
    return ""


def idl_constant_value(type_info: MsgType, value: str) -> str:
    if type_info.ros_type in ("string", "wstring") and not value.startswith(("'", '"')):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def include_for_type(type_info: MsgType, current_package: str) -> Optional[str]:
    ros_type = type_info.ros_type
    if ros_type in PRIMITIVE_TYPES or re.match(r"^(w?string)<=[0-9]+$", ros_type):
        return None

    package, type_name = normalize_ros_type(ros_type)
    package = package or current_package
    return f'{package}/msg/{type_name}.idl'


def collect_includes(definition: MsgDefinition, current_package: str, current_msg_name: str) -> List[str]:
    includes: Set[str] = set()
    for item in [*definition.constants, *definition.fields]:
        include = include_for_type(item.type_info, current_package)
        if include and include != f"{current_package}/msg/{current_msg_name}.idl":
            includes.add(include)
    return sorted(includes)


def msg_to_idl_text(definition: MsgDefinition, package_name: str, msg_name: str) -> str:
    lines: List[str] = []

    for include in collect_includes(definition, package_name, msg_name):
        lines.append(f'#include "{include}"')
    if lines:
        lines.append("")

    lines.extend(
        [
            f"module {package_name} {{",
            "  module msg {",
        ]
    )

    for const in definition.constants:
        idl_type = idl_base_type(const.type_info, package_name)
        value = idl_constant_value(const.type_info, const.value)
        lines.append(f"    const {idl_type} {const.name} = {value};")
    if definition.constants:
        lines.append("")

    lines.append(f"    struct {msg_name} {{")
    for field in definition.fields:
        idl_type = idl_field_type(field.type_info, package_name)
        suffix = idl_field_suffix(field.type_info)
        lines.append(f"      {idl_type} {field.name}{suffix};")
    lines.extend(
        [
            "    };",
            "  };",
            "};",
            "",
        ]
    )
    return "\n".join(lines)


def msg_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if input_path.suffix != ".msg":
            raise ValueError(f"input file must end with .msg: {input_path}")
        yield input_path
        return

    if input_path.is_dir():
        yield from sorted(path for path in input_path.rglob("*.msg") if path.is_file())
        return

    raise ValueError(f"input path does not exist: {input_path}")


def convert_file(msg_path: Path, output_dir: Path, package_name: str) -> Path:
    definition = parse_msg(msg_path)
    idl_text = msg_to_idl_text(definition, package_name, msg_path.stem)
    output_path = output_dir / f"{msg_path.stem}.idl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(idl_text, encoding="utf-8")
    return output_path


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert ROS 2 .msg files to IDL without comments or @verbatim annotations.",
    )
    parser.add_argument("input", help="A .msg file or a directory containing .msg files.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="idl_out",
        help="Directory where generated .idl files are written (default: ./idl_out).",
    )
    parser.add_argument(
        "-p",
        "--package-name",
        help="ROS package name. Defaults to the nearest package.xml name.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print generated files.")
    return parser


def main(argv: List[str]) -> int:
    parser = build_argparser()
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    package_name = args.package_name or infer_package_name(input_path)
    if not package_name:
        print("Error: could not infer package name; pass --package-name.", file=sys.stderr)
        return 2

    try:
        written = [convert_file(path, output_dir, package_name) for path in msg_files(input_path)]
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if not written:
        print(f"No .msg files found under: {input_path}", file=sys.stderr)
        return 2

    if args.verbose:
        for path in written:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
