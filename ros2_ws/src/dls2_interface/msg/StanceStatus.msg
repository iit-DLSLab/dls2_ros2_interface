
# header
string frame_id
uint32 sequence_id
float64 timestamp

# data
bool[] stance_status

# Estimated GRFs in base frame, flattened as [Fx, Fy, Fz] per limb id.
float64[] estimated_grfs

# Filtered joint accelerations used by the GRF estimator [rad/s^2].
float64[] joints_acceleration

# Joint-space dynamics contributions [Nm], indexed by joint id.
float64[] gravity_torques
float64[] coriolis_torques
float64[] joint_inertia_torques
float64[] base_inertia_torques
float64[] friction_torques

# Raw measured joint torques from blind_state [Nm].
float64[] measured_joint_torques

# Dynamics contributions mapped to base-frame GRFs [Fx, Fy, Fz] per limb.
float64[] gravity_grfs

# Coriolis and centrifugal contribution: nonlinear effects minus gravity.
float64[] coriolis_grfs

# Joint-acceleration contribution M_jj*qdd.
float64[] joint_inertia_grfs

# Floating-base acceleration contribution M_jb*a_base.
float64[] base_inertia_grfs

# Friction contribution added to the dynamics residual.
float64[] friction_grfs

# Raw measured joint torques mapped through J^T, without model terms.
float64[] joint_torque_grfs
