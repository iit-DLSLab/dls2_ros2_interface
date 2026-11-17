
# header
string frame_id
uint32 sequence_id
float64 timestamp

# data
float64[] linear_velocity
float64[] angular_velocity
dls2_interface/Vec3[] feet_position  # one per leg, base frame
float64[3] base_velocity
bool[] stance_status
