# dls2_ros2_bridge
This repository describes the steps to bridge dls2 with ros2.

The bridge is based on the [Integration-Service](https://integration-service.docs.eprosima.com/en/latest/index.html) tool. It allows different middlewares to communicate with each other.

Bridging dls2 with ros2 means letting dds (currently fastdds) communicate with ros2. To do so, you need:
- the integration service running with the dds (currently fastdds) and ros2 System Handles
- the ros2 messages you want to share with the corresponding dls2 messages (.idl files)
- a .yaml configuration file read by the integration service

You can find an example about bridging fastdds with ros2 [here](https://integration-service.docs.eprosima.com/en/latest/examples/different_protocols/pubsub/dds-ros2.html).

This repositories also contains the ros2 messages corresponding to off-the-shelf dls2 ones and the corresponding .yaml configuration files. Notice that these files uses a .xml file for configuring the domain participants as CLIENTS for SERVERS. So it is assumed that dls2 uses the [Discovery Server](https://fast-dds.docs.eprosima.com/en/latest/fastdds/discovery/discovery_server.html#discovery-server) mechanism, with servers having specific ip, port and GUID.
