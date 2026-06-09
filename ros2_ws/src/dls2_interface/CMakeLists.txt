cmake_minimum_required(VERSION 3.8)
project(dls2_interface)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
"msg/ArmState.msg"
"msg/ArmTrajectoryGenerator.msg"
"msg/Attitude.msg"
"msg/BaseReference.msg"
"msg/BaseState.msg"
"msg/BaseStateLight.msg"
"msg/BatteryStatus.msg"
"msg/BatteryStatusLight.msg"
"msg/BlindState.msg"
"msg/BlindStateLight.msg"
"msg/Bool.msg"
"msg/ButtonEvent.msg"
"msg/CommandCall.msg"
"msg/ControllerCommand.msg"
"msg/ControlSignal.msg"
"msg/CSBasicCommand.msg"
"msg/CSEmergency.msg"
"msg/DesiredArmTorques.msg"
"msg/DesiredTorques.msg"
"msg/DlsEvents.msg"
"msg/DlsHeader.msg"
"msg/DlsRobotStateLight.msg"
"msg/DlsStatus.msg"
"msg/Double.msg"
"msg/EventLog.msg"
"msg/FeetReference.msg"
"msg/FrictionConeList.msg"
"msg/Imu.msg"
"msg/InputTopicInfo.msg"
"msg/JointStates.msg"
"msg/JointStatesLight.msg"
"msg/LegsPose.msg"
"msg/NavigationReference.msg"
"msg/ParamServer.msg"
"msg/Pose.msg"
"msg/Position2D.msg"
"msg/ProcessStatus.msg"
"msg/ProcessStatusLight.msg"
"msg/ReferenceLight.msg"
"msg/ReferencePath.msg"
"msg/Screw.msg"
"msg/SensorFusion.msg"
"msg/StanceStatus.msg"
"msg/StateMachineMonitor.msg"
"msg/StayOutZones.msg"
"msg/String.msg"
"msg/TargetPosition.msg"
"msg/TrajectoryGenerator.msg"
"msg/Vec3.msg"
"msg/Vicon.msg"
"msg/WrenchLight.msg"
"msg/Zone.msg"
)

ament_export_dependencies(rosidl_default_runtime)

install(DIRECTORY scripts
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
