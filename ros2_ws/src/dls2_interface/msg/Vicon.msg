
# header
string frame_id
uint32 sequence_id
float64 timestamp

# robot pose
float64[3] robot_position
float64[4] robot_orientation

# marker positions

# EDIT#2/7 use it when PlotJuggler plugin for FastDDS supports the inclusion of custom messages

# sequence<Position> markers_positions;

# sequence<double> markers_positions;
float64[21] markers_positions  # 7 markers * 3 (x,y,z)
