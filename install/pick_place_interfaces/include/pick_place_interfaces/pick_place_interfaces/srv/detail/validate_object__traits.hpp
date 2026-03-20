// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from pick_place_interfaces:srv/ValidateObject.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__TRAITS_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "pick_place_interfaces/srv/detail/validate_object__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace pick_place_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ValidateObject_Request & msg,
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
  const ValidateObject_Request & msg,
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

inline std::string to_yaml(const ValidateObject_Request & msg, bool use_flow_style = false)
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
  const pick_place_interfaces::srv::ValidateObject_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  pick_place_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use pick_place_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const pick_place_interfaces::srv::ValidateObject_Request & msg)
{
  return pick_place_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<pick_place_interfaces::srv::ValidateObject_Request>()
{
  return "pick_place_interfaces::srv::ValidateObject_Request";
}

template<>
inline const char * name<pick_place_interfaces::srv::ValidateObject_Request>()
{
  return "pick_place_interfaces/srv/ValidateObject_Request";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::ValidateObject_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<pick_place_interfaces::srv::ValidateObject_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<pick_place_interfaces::srv::ValidateObject_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace pick_place_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ValidateObject_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: is_valid
  {
    out << "is_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.is_valid, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ValidateObject_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: is_valid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.is_valid, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ValidateObject_Response & msg, bool use_flow_style = false)
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
  const pick_place_interfaces::srv::ValidateObject_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  pick_place_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use pick_place_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const pick_place_interfaces::srv::ValidateObject_Response & msg)
{
  return pick_place_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<pick_place_interfaces::srv::ValidateObject_Response>()
{
  return "pick_place_interfaces::srv::ValidateObject_Response";
}

template<>
inline const char * name<pick_place_interfaces::srv::ValidateObject_Response>()
{
  return "pick_place_interfaces/srv/ValidateObject_Response";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::ValidateObject_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<pick_place_interfaces::srv::ValidateObject_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<pick_place_interfaces::srv::ValidateObject_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<pick_place_interfaces::srv::ValidateObject>()
{
  return "pick_place_interfaces::srv::ValidateObject";
}

template<>
inline const char * name<pick_place_interfaces::srv::ValidateObject>()
{
  return "pick_place_interfaces/srv/ValidateObject";
}

template<>
struct has_fixed_size<pick_place_interfaces::srv::ValidateObject>
  : std::integral_constant<
    bool,
    has_fixed_size<pick_place_interfaces::srv::ValidateObject_Request>::value &&
    has_fixed_size<pick_place_interfaces::srv::ValidateObject_Response>::value
  >
{
};

template<>
struct has_bounded_size<pick_place_interfaces::srv::ValidateObject>
  : std::integral_constant<
    bool,
    has_bounded_size<pick_place_interfaces::srv::ValidateObject_Request>::value &&
    has_bounded_size<pick_place_interfaces::srv::ValidateObject_Response>::value
  >
{
};

template<>
struct is_service<pick_place_interfaces::srv::ValidateObject>
  : std::true_type
{
};

template<>
struct is_service_request<pick_place_interfaces::srv::ValidateObject_Request>
  : std::true_type
{
};

template<>
struct is_service_response<pick_place_interfaces::srv::ValidateObject_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__TRAITS_HPP_
