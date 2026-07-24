# dls2_ros2_interface

ROS 2 interface package for DLS2 messages.

This repository contains a ROS 2 workspace with the `dls2_interface` package. The package generates ROS 2 message types from the DLS2 message definitions under:

```text
ros2_ws/src/dls2_interface/msg
```
The `dls2_interface` package also provides scripts for:

- network configuration for DLS2-ROS2 communication: `setup_ros2_for_dls2.bash`
- idl to msg conversion: `idl_to_msg.py`
- msg to idl conversion without comments: `msg_to_idl_no_comments.py`

## Requirements

- ROS 2, default distro: `jazzy` (humble is not recently tested but it should work too)
- FastDDS ROS middleware: `rmw_fastrtps_cpp`
- DLS2 installed, or a readable DLS discovery-server YAML file (otherwise fallback to default setting is happening)

## Build

From this directory:

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

To inspect the generated interfaces:

```bash
ros2 interface list | grep dls2_interface
ros2 interface show dls2_interface/msg/BaseState
```

## Configure ROS 2 for DLS2
Supported ROS2 middleware: **FastDDS**.

## Network 
To interface ROS2 with DLS2 and viceversa you have two ways:

### Fast way

    source install/dls2_interface/share/dls2_interface/scripts/setup_ros2_for_dls2.bash

By default the script:

- sources `/opt/ros/jazzy/setup.bash`
- sets `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`
- reads DLS discovery servers from `/usr/include/dls2/util/messaging/servers.yaml`
- exports `ROS_DISCOVERY_SERVER`
- exports `ROS_SUPER_CLIENT=TRUE`
- restarts the ROS 2 daemon

Override the ROS distro or server file if needed:

```bash
export DLS_ROS_DISTRO=humble
export DLS_SERVERS_PATH=/path/to/servers.yaml
source src/dls2_interface/scripts/setup_ros2_for_dls2.bash
```

If the server file is not available, the script falls back to:

```text
127.0.0.1:11812;127.0.0.1:11813;127.0.0.1:11814;127.0.0.1:11818
```

### Hands-on way
If you want to do things manually, do the following:
```bash	
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DISCOVERY_SERVER="127.0.0.1:11812;127.0.0.1:11813;127.0.0.1:11814;127.0.0.1:11818"
export ROS_SUPER_CLIENT=TRUE
ros2 daemon stop
ros2 daemon start
```
These commands:
- set FastDDS as ROS2 middleware
- set Discovery Server as discovery mechanism for ROS2, setting the ips and ports used by DLS2. Be aware that the order **MATTERS** and it has to follow the one you set in the servers.yaml configuration file (see [here](https://github.com/iit-DLSLab/dls2/blob/main/modules/ddscom/include/dls2/util/messaging/servers.yaml)).
- set the ROS client to SUPER_CLIENT. This is only needed for the ros2 CLI. You can set it to FALSE if you don't want to use the ros2 CLI.
- restart the ros2 daemon, which manages the cache of nodes, topics, and services. It makes ros2 CLI commands faster, but you need to stop and restart it to update it (for example, if you change the network, the discovery server, or the ROS_SUPER_CLIENT). Instead of stop and restart, you can use the ros2 CLI with the '--no-daemon' option.


## Topic Names

DLS2 and ROS 2 topic names must match at the DDS level to establish communication. ROS 2 topics using FastDDS are normally exposed with the `rt/` prefix in DDS. For example, the ROS 2 topic `chatter` maps to the DDS topic `rt/chatter`.

DLS2 usually prepends `rt/` automatically, so use matching topic names on both sides and check the DLS2 participant configuration if discovery works but messages do not flow.


## Use ROS2 message in DLS2 (.msg to .idl)
Off-the-shelf ROS2 messages are supported by default in DLS2.

To use custom ROS2 messages, do so you need to generate idl from .msg file by executing the command

```bash
python3 src/dls2_interface/scripts/msg_to_idl_no_comments.py src/dls2_interface/msg/message_name.msg -o ./idls
```

This generates IDL directly from the .msg file without comments and without \@verbatim annotations, avoiding FastDDSGen compilation issues seen with `rosidl translate`.

To convert all messages in the package

```bash
python3 src/dls2_interface/scripts/msg_to_idl_no_comments.py <path_to_msg_folder> -o ./idls
```

If the package name cannot be inferred from `package.xml`, pass it explicitly:

```bash
python3 src/dls2_interface/scripts/msg_to_idl_no_comments.py <path_to_msg_folder> -o ./idls --package-name package_name
```


## Use DLS2 message in ROS2 (.idl to .msg)
Off-the-shelf DLS2 messages are already supported in the dls2_inteface ROS2 package.

For custom DLS2 idl, please make sure that the idl file has namespace dls2_interface and msg like

```bash
module dls2_interface
{
  module msg
  {
    struct ExampleMsg
    {
      unsigned long sequence_id;
      double timestamp;
    };
  };
};
```

Then use the `idl_to_msg.py` tool to convert an idl to a msg. E.g.

    python3 src/dls2_interface/scripts/idl_to_msg.py <path_to_idl> -o ./ 

Then copy the .msg inside the dls2_interface/msg, add the message in the rosidl_generate_interfaces of the CMakeLists.txt and build the dls2_interface. Finally `source install/setup.bash`.
