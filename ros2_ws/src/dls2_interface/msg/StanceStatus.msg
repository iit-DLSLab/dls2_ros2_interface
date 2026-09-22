
# header
string frame_id
uint32 sequence_id
float64 timestamp

# data
bool[] stance_status

# Estimated GRFs in base frame, flattened as [Fx, Fy, Fz] per limb id.
float64[] estimated_grfs
