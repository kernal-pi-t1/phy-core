// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from pick_place_interfaces:msg/ObjectPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__TRAITS_HPP_
#define PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "pick_place_interfaces/msg/detail/object_pose__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace pick_place_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const ObjectPose & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: roll
  {
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << ", ";
  }

  // member: pitch
  {
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << ", ";
  }

  // member: yaw
  {
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ObjectPose & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: roll
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << "\n";
  }

  // member: pitch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << "\n";
  }

  // member: yaw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ObjectPose & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace pick_place_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use pick_place_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const pick_place_interfaces::msg::ObjectPose & msg,
  std::ostream & out, size_t indentation = 0)
{
  pick_place_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use pick_place_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const pick_place_interfaces::msg::ObjectPose & msg)
{
  return pick_place_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<pick_place_interfaces::msg::ObjectPose>()
{
  return "pick_place_interfaces::msg::ObjectPose";
}

template<>
inline const char * name<pick_place_interfaces::msg::ObjectPose>()
{
  return "pick_place_interfaces/msg/ObjectPose";
}

template<>
struct has_fixed_size<pick_place_interfaces::msg::ObjectPose>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<pick_place_interfaces::msg::ObjectPose>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<pick_place_interfaces::msg::ObjectPose>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__TRAITS_HPP_
