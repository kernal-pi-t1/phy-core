// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phy_interface:srv/Json.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__JSON__BUILDER_HPP_
#define PHY_INTERFACE__SRV__DETAIL__JSON__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phy_interface/srv/detail/json__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phy_interface
{

namespace srv
{

namespace builder
{

class Init_Json_Request_payload
{
public:
  Init_Json_Request_payload()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::srv::Json_Request payload(::phy_interface::srv::Json_Request::_payload_type arg)
  {
    msg_.payload = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::srv::Json_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::srv::Json_Request>()
{
  return phy_interface::srv::builder::Init_Json_Request_payload();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace srv
{

namespace builder
{

class Init_Json_Response_success
{
public:
  Init_Json_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::srv::Json_Response success(::phy_interface::srv::Json_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::srv::Json_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::srv::Json_Response>()
{
  return phy_interface::srv::builder::Init_Json_Response_success();
}

}  // namespace phy_interface

#endif  // PHY_INTERFACE__SRV__DETAIL__JSON__BUILDER_HPP_
