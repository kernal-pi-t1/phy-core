// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from pick_place_interfaces:srv/ValidateObject.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__BUILDER_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "pick_place_interfaces/srv/detail/validate_object__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_ValidateObject_Request_object_name
{
public:
  Init_ValidateObject_Request_object_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::pick_place_interfaces::srv::ValidateObject_Request object_name(::pick_place_interfaces::srv::ValidateObject_Request::_object_name_type arg)
  {
    msg_.object_name = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::ValidateObject_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::ValidateObject_Request>()
{
  return pick_place_interfaces::srv::builder::Init_ValidateObject_Request_object_name();
}

}  // namespace pick_place_interfaces


namespace pick_place_interfaces
{

namespace srv
{

namespace builder
{

class Init_ValidateObject_Response_is_valid
{
public:
  Init_ValidateObject_Response_is_valid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::pick_place_interfaces::srv::ValidateObject_Response is_valid(::pick_place_interfaces::srv::ValidateObject_Response::_is_valid_type arg)
  {
    msg_.is_valid = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::srv::ValidateObject_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::srv::ValidateObject_Response>()
{
  return pick_place_interfaces::srv::builder::Init_ValidateObject_Response_is_valid();
}

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__BUILDER_HPP_
