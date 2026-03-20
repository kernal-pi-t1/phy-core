// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from pick_place_interfaces:msg/ObjectPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__BUILDER_HPP_
#define PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "pick_place_interfaces/msg/detail/object_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace pick_place_interfaces
{

namespace msg
{

namespace builder
{

class Init_ObjectPose_yaw
{
public:
  explicit Init_ObjectPose_yaw(::pick_place_interfaces::msg::ObjectPose & msg)
  : msg_(msg)
  {}
  ::pick_place_interfaces::msg::ObjectPose yaw(::pick_place_interfaces::msg::ObjectPose::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return std::move(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

class Init_ObjectPose_pitch
{
public:
  explicit Init_ObjectPose_pitch(::pick_place_interfaces::msg::ObjectPose & msg)
  : msg_(msg)
  {}
  Init_ObjectPose_yaw pitch(::pick_place_interfaces::msg::ObjectPose::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_ObjectPose_yaw(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

class Init_ObjectPose_roll
{
public:
  explicit Init_ObjectPose_roll(::pick_place_interfaces::msg::ObjectPose & msg)
  : msg_(msg)
  {}
  Init_ObjectPose_pitch roll(::pick_place_interfaces::msg::ObjectPose::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_ObjectPose_pitch(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

class Init_ObjectPose_z
{
public:
  explicit Init_ObjectPose_z(::pick_place_interfaces::msg::ObjectPose & msg)
  : msg_(msg)
  {}
  Init_ObjectPose_roll z(::pick_place_interfaces::msg::ObjectPose::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_ObjectPose_roll(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

class Init_ObjectPose_y
{
public:
  explicit Init_ObjectPose_y(::pick_place_interfaces::msg::ObjectPose & msg)
  : msg_(msg)
  {}
  Init_ObjectPose_z y(::pick_place_interfaces::msg::ObjectPose::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_ObjectPose_z(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

class Init_ObjectPose_x
{
public:
  Init_ObjectPose_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ObjectPose_y x(::pick_place_interfaces::msg::ObjectPose::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_ObjectPose_y(msg_);
  }

private:
  ::pick_place_interfaces::msg::ObjectPose msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::pick_place_interfaces::msg::ObjectPose>()
{
  return pick_place_interfaces::msg::builder::Init_ObjectPose_x();
}

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__BUILDER_HPP_
