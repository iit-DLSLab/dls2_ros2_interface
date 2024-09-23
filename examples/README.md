# pid_ws
This is an example showing how to implemente a pid (actually pd) controller in ros2 interfacing with DLS2.

# Compilation
```
cd dls2_ros2_bridge/examples/pid_ws
colcon build
```

# Usage
In order to use the pid ros2 node, you need to use the server-harbor:80/dls2/dls2-framework (or dls2-devel) image, the server-harbor:80/dls2/dls2-integration_service-ros image and the image used to compile this package.

## Running DLS2 image
In the dls2 image open two terminals. In one terminal launch the simulation

    dls --startup

In another terminal attached to the dls2 image launch the dls2 console

    dls -lconsole

Depending on the default startup procedure, the dls2 pid and trunk controllers can already run. In the dls2 console they can be therefore unloaded

    unloadController pid
    unloadController trunk_controller

The pid controller needs a desired joint trajectory, so let's load the periodic_generator (if not already loaded) and let's activate it

    loadGenerator periodic_generator
    periodic_generator::activate

The final step is to plug the external ros2 pid controller to DLS2. To do so run this command in the dls2 console

    loadExternalController pid

Here, the name of the controller needs to be equal to the dds topic used in the mapping specified in fastdds_ros2__pid.yaml.

DLS2 is now ready to receive (and apply) the desired torques coming from the pid topic.

## Running the integration service
Now we can launch the integration service. We need to bridge the _blind_state_ and _trajectory_generator_ topics from DLS2 to ROS2 and _/dls2/pid_ ROS2 topic to DLS2. Open 3 terminals attached to the the integration service image (see [here](../README.md#integration_service_procedure) for how to open such image). Then execute this command

        source /opt/integration_service/setup.bash

in each of them.

Now, each of the terminal will launch an integration service for a specific topic. The commands are the following

- blind_state topic

    integration-service $DEFAULT_CONFIG/fastdds_ros2__blindState.yaml

- trajectory_generator topic

    integration-service $DEFAULT_CONFIG/fastdds_ros2__trajectoryGenerator.yaml

- /dls2/pid topic

    integration-service dls2_ros2_bridge/examples/pid_ws/fastdds_ros2__pid.yaml

## Runing the ROS2 pid controller
We can now finally launch the ros2 pid. Open the image you have used to compile the ros2 package. Then

    source dls2_ros2_bridge/examples/pid_ws/install/setup.bash
    ros2 run pid pid

ROS2 and DLS2 start communicating. To see a periodic motion, come back to the DLS2 console, then execute the following commands

    freezeBase
    periodicGenerator::startMotion
