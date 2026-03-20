// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from pick_place_interfaces:srv/GetPickPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__BUILDER_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "pick_place_interfaces/srv/detail/get_pick_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_GetPickPose_Request_object_name
{
public:
  Init_GetPickPose_Request_object_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::pick_place_interfaces::srv::GetPickPose_Request object_name(::pick_place_interfaces::srv::GetPickPose_Request::_object_name_type arg)
  {
    msg_.object_name = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::GetPickPose_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::GetPickPose_Request>()
{
  return pick_place_interfaces::srv::builder::Init_GetPickPose_Request_object_name();
}

}  // namespace pick_place_interfaces


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_GetPickPose_Response_error_message
{
public:
  explicit Init_GetPickPose_Response_error_message(::pick_place_interfaces::srv::GetPickPose_Response & msg)
  : msg_(msg)
  {}
  ::pick_place_interfaces::srv::GetPickPose_Response error_message(::pick_place_interfaces::srv::GetPickPose_Response::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::GetPickPose_Response msg_;
};

class Init_GetPickPose_Response_pose
{
public:
  explicit Init_GetPickPose_Response_pose(::pick_place_interfaces::srv::GetPickPose_Response & msg)
  : msg_(msg)
  {}
  Init_GetPickPose_Response_error_message pose(::pick_place_interfaces::srv::GetPickPose_Response::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_GetPickPose_Response_error_message(msg_);
  }

private:
  ::pick_place_interfaces::srv::GetPickPose_Response msg_;
};

class Init_GetPickPose_Response_success
{
public:
  Init_GetPickPose_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GetPickPose_Response_pose success(::pick_place_interfaces::srv::GetPickPose_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_GetPickPose_Response_pose(msg_);
  }

private:
  ::pick_place_interfaces::srv::GetPickPose_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::GetPickPose_Response>()
{
  return pick_place_interfaces::srv::builder::Init_GetPickPose_Response_success();
}

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__BUILDER_HPP_
