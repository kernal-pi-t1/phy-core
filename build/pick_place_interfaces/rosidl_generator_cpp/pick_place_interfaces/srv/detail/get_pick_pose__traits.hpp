// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from pick_place_interfaces:srv/GetPickPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__TRAITS_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "pick_place_interfaces/srv/detail/get_pick_pose__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace pick_place_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetPickPose_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: object_name
  {
    out << "object_name: ";
    rosidl_generator_traits::value_to_yaml(msg.object_name, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetPickPose_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: object_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "object_name: ";
    rosidl_generator_traits::value_to_yaml(msg.object_name, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetPickPose_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace pick_place_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use pick_place_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const pick_place_interfaces::srv::GetPickPose_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  pick_place_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use pick_place_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const pick_place_interfaces::srv::GetPickPose_Request & msg)
{
  return pick_place_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<pick_place_interfaces::srv::GetPickPose_Request>()
{
  return "pick_place_interfaces::srv::GetPickPose_Request";
}

template<>
inline const char * name<pick_place_interfaces::srv::GetPickPose_Request>()
{
  return "pick_place_interfaces/srv/GetPickPose_Request";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::GetPickPose_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<pick_place_interfaces::srv::GetPickPose_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<pick_place_interfaces::srv::GetPickPose_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'pose'
#include "pick_place_interfaces/msg/detail/object_pose__traits.hpp"

namespace pick_place_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const GetPickPose_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

  // member: error_message
  {
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GetPickPose_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }

  // member: error_message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GetPickPose_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace pick_place_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use pick_place_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const pick_place_interfaces::srv::GetPickPose_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  pick_place_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use pick_place_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const pick_place_interfaces::srv::GetPickPose_Response & msg)
{
  return pick_place_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<pick_place_interfaces::srv::GetPickPose_Response>()
{
  return "pick_place_interfaces::srv::GetPickPose_Response";
}

template<>
inline const char * name<pick_place_interfaces::srv::GetPickPose_Response>()
{
  return "pick_place_interfaces/srv/GetPickPose_Response";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::GetPickPose_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<pick_place_interfaces::srv::GetPickPose_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<pick_place_interfaces::srv::GetPickPose_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<pick_place_interfaces::srv::GetPickPose>()
{
  return "pick_place_interfaces::srv::GetPickPose";
}

template<>
inline const char * name<pick_place_interfaces::srv::GetPickPose>()
{
  return "pick_place_interfaces/srv/GetPickPose";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::GetPickPose>
  : std::integral_constant<
    bool,
    has_fixed_size<pick_place_interfaces::srv::GetPickPose_Request>::value &&
    has_fixed_size<pick_place_interfaces::srv::GetPickPose_Response>::value
  >
{
};

template<>
struct has_bounded_size<pick_place_interfaces::srv::GetPickPose>
  : std::integral_constant<
    bool,
    has_bounded_size<pick_place_interfaces::srv::GetPickPose_Request>::value &&
    has_bounded_size<pick_place_interfaces::srv::GetPickPose_Response>::value
  >
{
};

template<>
struct is_service<pick_place_interfaces::srv::GetPickPose>
  : std::true_type
{
};

template<>
struct is_service_request<pick_place_interfaces::srv::GetPickPose_Request>
  : std::true_type
{
};

template<>
struct is_service_response<pick_place_interfaces::srv::GetPickPose_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__TRAITS_HPP_
