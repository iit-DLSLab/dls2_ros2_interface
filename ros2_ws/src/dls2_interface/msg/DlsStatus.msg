dls2_interface/DlsHeader header
dls2_interface/ProcessStatus[] processes
dls2_interface/ReferenceLight reference  # followed by controller
dls2_interface/DlsRobotStateLight robot_state
dls2_interface/CSBasicCommand cs_command_feedback  # last command received from the control station (echo)
dls2_interface/CSBasicCommand cs_command_state  # modes actually applied by the orchestrator; enable = false only for a rover-side STOP
action_msgs/GoalStatusArray navigation_status  # status of the navigation action goals
