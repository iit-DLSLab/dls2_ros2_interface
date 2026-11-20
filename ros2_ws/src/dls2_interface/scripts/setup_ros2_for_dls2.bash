#!/usr/bin/env bash

# This script is meant to be sourced: never call a bare `exit`, it would close
# the caller's shell. `return` works when sourced, `exit` when executed.
#
# Usage: source setup_ros2_for_dls2.bash [RMW_IMPLEMENTATION]
#   RMW_IMPLEMENTATION  ROS 2 middleware to use (default: rmw_fastrtps_cpp)
#
# Note: when sourced without arguments bash passes the caller's positional
# parameters, so callers that have their own arguments should pass the RMW
# explicitly.

echo "Setup ROS2 environment for DLS2"

rmw_implementation="${1:-rmw_fastrtps_cpp}"
case "${rmw_implementation}" in
	rmw_*) ;;
	*)
		echo "Invalid RMW implementation: '${rmw_implementation}' (expected rmw_*, e.g. rmw_fastrtps_cpp)" >&2
		echo "Usage: source setup_ros2_for_dls2.bash [RMW_IMPLEMENTATION]" >&2
		return 1 2>/dev/null || exit 1
		;;
esac

if [ -n "${CONDA_PREFIX:-}" ]; then
	echo "Warning: conda environment '${CONDA_DEFAULT_ENV:-${CONDA_PREFIX}}' is active." >&2
	echo "ROS 2 tools may use conda's python instead of the system one; run 'conda deactivate' if ros2 fails." >&2
fi

ros_distro="${DLS_ROS_DISTRO:-jazzy}"
ros_prefix="/opt/ros/${ros_distro}"

echo "Sourcing ROS 2 setup file from: ${ros_prefix}"
if [ -r "${ros_prefix}/setup.bash" ]; then
	source "${ros_prefix}/setup.bash"
elif [ -r "${ros_prefix}/setup.sh" ]; then
	source "${ros_prefix}/setup.sh"
else
	echo "Cannot read ROS 2 setup file in: ${ros_prefix}" >&2
	return 1 2>/dev/null || exit 1
fi

if ! command -v ros2 >/dev/null 2>&1; then
	echo "ros2 command not found after sourcing ${ros_prefix}/setup.*" >&2
	echo "Check that ROS 2 ${ros_distro} is installed and provides ${ros_prefix}/bin/ros2." >&2
	return 1 2>/dev/null || exit 1
fi

if [ ! -e "${ros_prefix}/lib/lib${rmw_implementation}.so" ]; then
	echo "Warning: ${rmw_implementation} not found in ${ros_prefix}/lib; is it installed?" >&2
fi
echo "Setting Middleware to ${rmw_implementation}"
export RMW_IMPLEMENTATION="${rmw_implementation}"

# Zenoh has no DDS discovery: drop the Fast DDS discovery variables (also any
# left over from a previous run in this shell) and skip the servers file.
if [ "${rmw_implementation}" = rmw_zenoh_cpp ]; then
	echo "rmw_zenoh_cpp: not setting ROS_DISCOVERY_SERVER and ROS_SUPER_CLIENT"
	unset ROS_DISCOVERY_SERVER ROS_SUPER_CLIENT

	echo "Restarting ROS 2 daemon..."
	ros2 daemon stop
	ros2 daemon start
	return 0 2>/dev/null || exit 0
fi

if [ "${rmw_implementation}" != rmw_fastrtps_cpp ]; then
	echo "Warning: ROS_DISCOVERY_SERVER and ROS_SUPER_CLIENT only apply to Fast DDS (rmw_fastrtps_cpp)." >&2
fi

ros_discovery_server=""
servers_path="${DLS_SERVERS_PATH:-/opt/dls2/include/dls2/util/messaging/servers.yaml}"

echo "Reading DLS servers from: ${servers_path}"

if [ ! -r "${servers_path}" ]; then
	echo "Cannot read DLS servers file: ${servers_path}" >&2
	echo "Please set DLS_SERVERS_PATH to a readable YAML file containing the discovery servers, or ensure the default path is correct." >&2 
	# set variable to false to avoid further processing
	ros_discovery_server=false
fi

if [ "${ros_discovery_server}" = false ]; then
	echo "Using default Discovery Servers"
	ros_discovery_server="127.0.0.1:11812;127.0.0.1:11813;127.0.0.1:11814;127.0.0.1:11818"
else
	ros_discovery_server="$(
		awk '
			{
				line = $0
				sub(/[[:space:]]*#.*/, "", line)
				if (line ~ /^[[:space:]]*ip:[[:space:]]*/) {
					ip = line
					sub(/^[[:space:]]*ip:[[:space:]]*/, "", ip)
					gsub(/["'\''[:space:]]/, "", ip)
				}
				if (line ~ /^[[:space:]]*port:[[:space:]]*/ && ip != "") {
					port = line
					sub(/^[[:space:]]*port:[[:space:]]*/, "", port)
					gsub(/["'\''[:space:]]/, "", port)
					if (server != "") {
						server = server ";"
					}
					server = server ip ":" port
					ip = ""
				}
			}
			END {
				print server
			}
		' "${servers_path}"
	)"
fi

if [ -n "${ros_discovery_server}" ]; then
	echo "exporting ROS_DISCOVERY_SERVER=${ros_discovery_server}"
	export ROS_DISCOVERY_SERVER="${ros_discovery_server}"

	echo "exporting ROS_SUPER_CLIENT=TRUE"
	export ROS_SUPER_CLIENT=FALSE

	echo "Restarting ROS 2 daemon..."
	ros2 daemon stop
	ros2 daemon start
else
	echo "No active discovery servers found in: ${servers_path}" >&2
fi

