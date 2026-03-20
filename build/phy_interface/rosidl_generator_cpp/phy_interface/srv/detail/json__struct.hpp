// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from phy_interface:srv/Json.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_HPP_
#define PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__phy_interface__srv__Json_Request __attribute__((deprecated))
#else
# define DEPRECATED__phy_interface__srv__Json_Request __declspec(deprecated)
#endif

namespace phy_interface
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Json_Request_
{
  using Type = Json_Request_<ContainerAllocator>;

  explicit Json_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->payload = "";
    }
  }

  explicit Json_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : payload(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->payload = "";
    }
  }

  // field types and members
  using _payload_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _payload_type payload;

  // setters for named parameter idiom
  Type & set__payload(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->payload = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    phy_interface::srv::Json_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const phy_interface::srv::Json_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<phy_interface::srv::Json_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<phy_interface::srv::Json_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::Json_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::Json_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::Json_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::Json_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<phy_interface::srv::Json_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<phy_interface::srv::Json_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__phy_interface__srv__Json_Request
    std::shared_ptr<phy_interface::srv::Json_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__phy_interface__srv__Json_Request
    std::shared_ptr<phy_interface::srv::Json_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Json_Request_ & other) const
  {
    if (this->payload != other.payload) {
      return false;
    }
    return true;
  }
  bool operator!=(const Json_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Json_Request_

// alias to use template instance with default allocator
using Json_Request =
  phy_interface::srv::Json_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace phy_interface


#ifndef _WIN32
# define DEPRECATED__phy_interface__srv__Json_Response __attribute__((deprecated))
#else
# define DEPRECATED__phy_interface__srv__Json_Response __declspec(deprecated)
#endif

namespace phy_interface
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Json_Response_
{
  using Type = Json_Response_<ContainerAllocator>;

  explicit Json_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  explicit Json_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    phy_interface::srv::Json_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const phy_interface::srv::Json_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<phy_interface::srv::Json_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<phy_interface::srv::Json_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::Json_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::Json_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::Json_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::Json_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<phy_interface::srv::Json_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<phy_interface::srv::Json_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__phy_interface__srv__Json_Response
    std::shared_ptr<phy_interface::srv::Json_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__phy_interface__srv__Json_Response
    std::shared_ptr<phy_interface::srv::Json_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Json_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const Json_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Json_Response_

// alias to use template instance with default allocator
using Json_Response =
  phy_interface::srv::Json_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace phy_interface

namespace phy_interface
{

namespace srv
{

struct Json
{
  using Request = phy_interface::srv::Json_Request;
  using Response = phy_interface::srv::Json_Response;
};

}  // namespace srv

}  // namespace phy_interface

#endif  // PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_HPP_
