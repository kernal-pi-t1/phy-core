// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from phy_interface:srv/GetPose.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__GET_POSE__STRUCT_HPP_
#define PHY_INTERFACE__SRV__DETAIL__GET_POSE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__phy_interface__srv__GetPose_Request __attribute__((deprecated))
#else
# define DEPRECATED__phy_interface__srv__GetPose_Request __declspec(deprecated)
#endif

namespace phy_interface
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetPose_Request_
{
  using Type = GetPose_Request_<ContainerAllocator>;

  explicit GetPose_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->method = "";
    }
  }

  explicit GetPose_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : method(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->method = "";
    }
  }

  // field types and members
  using _method_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _method_type method;

  // setters for named parameter idiom
  Type & set__method(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->method = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    phy_interface::srv::GetPose_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const phy_interface::srv::GetPose_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::GetPose_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::GetPose_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__phy_interface__srv__GetPose_Request
    std::shared_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__phy_interface__srv__GetPose_Request
    std::shared_ptr<phy_interface::srv::GetPose_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetPose_Request_ & other) const
  {
    if (this->method != other.method) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetPose_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetPose_Request_

// alias to use template instance with default allocator
using GetPose_Request =
  phy_interface::srv::GetPose_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace phy_interface


#ifndef _WIN32
# define DEPRECATED__phy_interface__srv__GetPose_Response __attribute__((deprecated))
#else
# define DEPRECATED__phy_interface__srv__GetPose_Response __declspec(deprecated)
#endif

namespace phy_interface
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct GetPose_Response_
{
  using Type = GetPose_Response_<ContainerAllocator>;

  explicit GetPose_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 6>::iterator, double>(this->pose.begin(), this->pose.end(), 0.0);
    }
  }

  explicit GetPose_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 6>::iterator, double>(this->pose.begin(), this->pose.end(), 0.0);
    }
  }

  // field types and members
  using _pose_type =
    std::array<double, 6>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__pose(
    const std::array<double, 6> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    phy_interface::srv::GetPose_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const phy_interface::srv::GetPose_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::GetPose_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      phy_interface::srv::GetPose_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__phy_interface__srv__GetPose_Response
    std::shared_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__phy_interface__srv__GetPose_Response
    std::shared_ptr<phy_interface::srv::GetPose_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GetPose_Response_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const GetPose_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GetPose_Response_

// alias to use template instance with default allocator
using GetPose_Response =
  phy_interface::srv::GetPose_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace phy_interface

namespace phy_interface
{

namespace srv
{

struct GetPose
{
  using Request = phy_interface::srv::GetPose_Request;
  using Response = phy_interface::srv::GetPose_Response;
};

}  // namespace srv

}  // namespace phy_interface

#endif  // PHY_INTERFACE__SRV__DETAIL__GET_POSE__STRUCT_HPP_
