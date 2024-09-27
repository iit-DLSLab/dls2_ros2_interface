# dls2_ros2_bridge
This repository describes the steps to bridge dls2 with ros2.

The bridge is based on the [Integration-Service](https://integration-service.docs.eprosima.com/en/latest/index.html) tool. It allows different middlewares to communicate with each other.

Bridging dls2 with ros2 means letting dds (currently fastdds) communicate with ros2. To do so, you need:
- the integration service running with the dds (currently fastdds) and ros2 System Handles
- the ros2 messages you want to share with the corresponding dls2 messages (.idl files)
- a .yaml configuration file read by the integration service

You can find an example about bridging fastdds with ros2 [here](https://integration-service.docs.eprosima.com/en/latest/examples/different_protocols/pubsub/dds-ros2.html).

This repositories also contains the ros2 messages corresponding to off-the-shelf dls2 ones and the corresponding .yaml configuration files. Notice that these files uses a .xml file for configuring the domain participants as CLIENTS for SERVERS. So it is assumed that dls2 uses the [Discovery Server](https://fast-dds.docs.eprosima.com/en/latest/fastdds/discovery/discovery_server.html#discovery-server) mechanism, with servers having specific ip, port and GUID.


# [Procedure to launch the integration service DLS2-ROS2](#integration_service_procedure)
- pull the integration service image

    `docker pull server-harbor:80/dls2/dls2-integration_service-ros`
- open the image

    `dls-docker.py --api run -f -nv -fx -e DLS=2 -ex server-harbor:80/dls2/dls2-integration_service-ros --container_name integration_service`
- source the integration service and ROS2
    source /opt/integration_service/setup.bash
- if you have a **new custom message**
    - compile and source the package containing your ros2 message
    - create a .mix file used by the integration service to interpret your ros2 message

        `create_ros2_mix_files <name of the package where your message is>`
    - source the .mix files
        source /opt/integration_service/ros2_sh_ws/install/setup.bash
    - create an .idl file corresponding to the .msg file of your ros2 message (e.g. [blind_state](https://gitlab.advr.iit.it/dls-lab/dls_messages/-/blob/master/idls/blind_state.idl))
    - create a .yaml configuration file used by the integration service (e.g [blind_state](https://gitlab.advr.iit.it/dls-lab/dls2_ros2_bridge/-/blob/master/config/fastdds_ros2__blindState.yaml))
        - in the yaml file, the _paths_ field is the path to the folder containing your idl file
    - launch the integration service

        `integration-service <path_to_your_yaml_configuration_file>.yaml`
- if you need to use **off-the-shelf messages**
    - launch the integration_service using one of the available yaml file in /opt/integration_service/dls2_ros2_bridge/config
        
        `integration-service $DEFAULT_CONFIG/<file_name>.yaml`

Notice that you need to launch an integration-service per topic.

# Examples
The examples folder provides a set of example to interface a ROS2 node with DLS2.
