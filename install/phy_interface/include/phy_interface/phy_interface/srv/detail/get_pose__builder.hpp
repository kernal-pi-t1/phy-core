// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phy_interface:srv/GetPose.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__GET_POSE__BUILDER_HPP_
#define PHY_INTERFACE__SRV__DETAIL__GET_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phy_interface/srv/detail/get_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phy_interface
{

namespace srv
{

namespace builder
{

class Init_GetPose_Request_method
{
public:
  Init_GetPose_Request_method()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::srv::GetPose_Request method(::phy_interface::srv::GetPose_Request::_method_type arg)
  {
    msg_.method = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::srv::GetPose_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::srv::GetPose_Request>()
{
  return phy_interface::srv::builder::Init_GetPose_Request_method();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace srv
{

namespace builder
{

class Init_GetPose_Response_pose
{
public:
  Init_GetPose_Response_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::srv::GetPose_Response pose(::phy_interface::srv::GetPose_Response::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::srv::GetPose_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::srv::GetPose_Response>()
{
  return phy_interface::srv::builder::Init_GetPose_Response_pose();
}

}  // namespace phy_interface

#endif  // PHY_INTERFACE__SRV__DETAIL__GET_POSE__BUILDER_HPP_
