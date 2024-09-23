#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "dls2_msgs/msg/blind_state_msg.hpp"
#include "dls2_msgs/msg/trajectory_generator_msg.hpp"
#include "dls2_msgs/msg/control_signal_msg.hpp"

using namespace std::chrono_literals;

using std::placeholders::_1;

class Pid : public rclcpp::Node
{
  public:
    Pid()
    : Node("pid")
    {
        // publisher
        publisher = this->create_publisher<dls2_msgs::msg::ControlSignalMsg>("dls2/pid", 10);
        timer_ = this->create_wall_timer(4ms, std::bind(&Pid::run, this));

        // subscribers
        subscriber_blind_state = this->create_subscription<dls2_msgs::msg::BlindStateMsg>(
        "/dls2/blind_state", 10, std::bind(&Pid::blind_state_callback, this, _1));
        subscriber_traj_gen = this->create_subscription<dls2_msgs::msg::TrajectoryGeneratorMsg>(
        "/dls2/trajectory_generator", 10, std::bind(&Pid::trajectory_generator_callback, this, _1));
    }

  private:
    void run()
    {
        for (long unsigned int i = 0; i < blind_state.joints_position.size(); i++)
        {
            //PD controller (with P=15 and D=3 there are shaking movements. Since this does not happen when using the same gains in DLS2, the problem could reside in the delays introduced by the integration service)
            des_tau_msg.torques[i] = 8*(traj_gen.joints_position[i]-blind_state.joints_position[i]) 
                                + 1*(traj_gen.joints_velocity[i]-blind_state.joints_velocity[i]);
        }

        publisher->publish(des_tau_msg);
    }

    void blind_state_callback(const dls2_msgs::msg::BlindStateMsg::SharedPtr msg)
    {
        blind_state = *msg;
    }

    void trajectory_generator_callback(const dls2_msgs::msg::TrajectoryGeneratorMsg::SharedPtr msg)
    {
        traj_gen = *msg;
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<dls2_msgs::msg::ControlSignalMsg>::SharedPtr publisher;
    rclcpp::Subscription<dls2_msgs::msg::BlindStateMsg>::SharedPtr subscriber_blind_state;
    rclcpp::Subscription<dls2_msgs::msg::TrajectoryGeneratorMsg>::SharedPtr subscriber_traj_gen;

    dls2_msgs::msg::ControlSignalMsg des_tau_msg;

    dls2_msgs::msg::BlindStateMsg blind_state;
    dls2_msgs::msg::TrajectoryGeneratorMsg traj_gen;    
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Pid>());
  rclcpp::shutdown();
  return 0;
}