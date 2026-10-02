dls2_interface/DlsHeader header
uint8 safety_state  # RobotSafety::SafetyState
bool[] joint_pos_limit_violation_predicted
int32[] virtual_joint_limit_side  # +1 braking toward position_max, -1 toward position_min, 0 inactive
float64[] virtual_joint_limit_anchor  # [rad], NaN when inactive
float64[] virtual_joint_limit_k  # [Nm/rad]
float64[] virtual_joint_limit_d  # [Nm*s/rad]
bool[] virtual_joint_limit_damping_only  # latched damping only (damping_after_stop)
