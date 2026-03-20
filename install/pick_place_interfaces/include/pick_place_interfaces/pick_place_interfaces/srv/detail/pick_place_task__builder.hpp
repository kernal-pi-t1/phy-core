// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from pick_place_interfaces:srv/PickPlaceTask.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__BUILDER_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "pick_place_interfaces/srv/detail/pick_place_task__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_PickPlaceTask_Request_return_reason
{
public:
  explicit Init_PickPlaceTask_Request_return_reason(::pick_place_interfaces::srv::PickPlaceTask_Request & msg)
  : msg_(msg)
  {}
  ::pick_place_interfaces::srv::PickPlaceTask_Request return_reason(::pick_place_interfaces::srv::PickPlaceTask_Request::_return_reason_type arg)
  {
    msg_.return_reason = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::PickPlaceTask_Request msg_;
};

class Init_PickPlaceTask_Request_object_name
{
public:
  Init_PickPlaceTask_Request_object_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickPlaceTask_Request_return_reason object_name(::pick_place_interfaces::srv::PickPlaceTask_Request::_object_name_type arg)
  {
    msg_.object_name = std::move(arg);
    return Init_PickPlaceTask_Request_return_reason(msg_);
  }

private:
  ::pick_place_interfaces::srv::PickPlaceTask_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::PickPlaceTask_Request>()
{
  return pick_place_interfaces::srv::builder::Init_PickPlaceTask_Request_object_name();
}

}  // namespace pick_place_interfaces


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_PickPlaceTask_Response_error_message
{
public:
  explicit Init_PickPlaceTask_Response_error_message(::pick_place_interfaces::srv::PickPlaceTask_Response & msg)
  : msg_(msg)
  {}
  ::pick_place_interfaces::srv::PickPlaceTask_Response error_message(::pick_place_interfaces::srv::PickPlaceTask_Response::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::PickPlaceTask_Response msg_;
};

class Init_PickPlaceTask_Response_success
{
public:
  Init_PickPlaceTask_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickPlaceTask_Response_error_message success(::pick_place_interfaces::srv::PickPlaceTask_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_PickPlaceTask_Response_error_message(msg_);
  }

private:
  ::pick_place_interfaces::srv::PickPlaceTask_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::PickPlaceTask_Response>()
{
  return pick_place_interfaces::srv::builder::Init_PickPlaceTask_Response_success();
}

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__BUILDER_HPP_
