// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from phy_interface:srv/Json.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__JSON__TRAITS_HPP_
#define PHY_INTERFACE__SRV__DETAIL__JSON__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "phy_interface/srv/detail/json__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace phy_interface
{

namespace srv
{

inline void to_flow_style_yaml(
  const Json_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: payload
  {
    out << "payload: ";
    rosidl_generator_traits::value_to_yaml(msg.payload, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Json_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: payload
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "payload: ";
    rosidl_generator_traits::value_to_yaml(msg.payload, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Json_Request & msg, bool use_flow_style = false)
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

}  // namespace phy_interface

namespace rosidl_generator_traits
{

[[deprecated("use phy_interface::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const phy_interface::srv::Json_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  phy_interface::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use phy_interface::srv::to_yaml() instead")]]
inline std::string to_yaml(const phy_interface::srv::Json_Request & msg)
{
  return phy_interface::srv::to_yaml(msg);
}

template<>
inline const char * data_type<phy_interface::srv::Json_Request>()
{
  return "phy_interface::srv::Json_Request";
}

template<>
inline const char * name<phy_interface::srv::Json_Request>()
{
  return "phy_interface/srv/Json_Request";
}

template<>
struct has_fixed_size<phy_interface::srv::Json_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<phy_interface::srv::Json_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<phy_interface::srv::Json_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace phy_interface
{

namespace srv
{

inline void to_flow_style_yaml(
  const Json_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Json_Response & msg,
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Json_Response & msg, bool use_flow_style = false)
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

}  // namespace phy_interface

namespace rosidl_generator_traits
{

[[deprecated("use phy_interface::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const phy_interface::srv::Json_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  phy_interface::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use phy_interface::srv::to_yaml() instead")]]
inline std::string to_yaml(const phy_interface::srv::Json_Response & msg)
{
  return phy_interface::srv::to_yaml(msg);
}

template<>
inline const char * data_type<phy_interface::srv::Json_Response>()
{
  return "phy_interface::srv::Json_Response";
}

template<>
inline const char * name<phy_interface::srv::Json_Response>()
{
  return "phy_interface/srv/Json_Response";
}

template<>
struct has_fixed_size<phy_interface::srv::Json_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<phy_interface::srv::Json_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<phy_interface::srv::Json_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<phy_interface::srv::Json>()
{
  return "phy_interface::srv::Json";
}

template<>
inline const char * name<phy_interface::srv::Json>()
{
  return "phy_interface/srv/Json";
}

template<>
struct has_fixed_size<phy_interface::srv::Json>
  : std::integral_constant<
    bool,
    has_fixed_size<phy_interface::srv::Json_Request>::value &&
    has_fixed_size<phy_interface::srv::Json_Response>::value
  >
{
};

template<>
struct has_bounded_size<phy_interface::srv::Json>
  : std::integral_constant<
    bool,
    has_bounded_size<phy_interface::srv::Json_Request>::value &&
    has_bounded_size<phy_interface::srv::Json_Response>::value
  >
{
};

template<>
struct is_service<phy_interface::srv::Json>
  : std::true_type
{
};

template<>
struct is_service_request<phy_interface::srv::Json_Request>
  : std::true_type
{
};

template<>
struct is_service_response<phy_interface::srv::Json_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // PHY_INTERFACE__SRV__DETAIL__JSON__TRAITS_HPP_
