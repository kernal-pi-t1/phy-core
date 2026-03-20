// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from pick_place_interfaces:srv/PickPlaceTask.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Request __attribute__((deprecated))
#else
# define DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Request __declspec(deprecated)
#endif

namespace pick_place_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct PickPlaceTask_Request_
{
  using Type = PickPlaceTask_Request_<ContainerAllocator>;

  explicit PickPlaceTask_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->object_name = "";
      this->return_reason = "";
    }
  }

  explicit PickPlaceTask_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : object_name(_alloc),
    return_reason(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->object_name = "";
      this->return_reason = "";
    }
  }

  // field types and members
  using _object_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _object_name_type object_name;
  using _return_reason_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _return_reason_type return_reason;

  // setters for named parameter idiom
  Type & set__object_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->object_name = _arg;
    return *this;
  }
  Type & set__return_reason(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->return_reason = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Request
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Request
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PickPlaceTask_Request_ & other) const
  {
    if (this->object_name != other.object_name) {
      return false;
    }
    if (this->return_reason != other.return_reason) {
      return false;
    }
    return true;
  }
  bool operator!=(const PickPlaceTask_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PickPlaceTask_Request_

// alias to use template instance with default allocator
using PickPlaceTask_Request =
  pick_place_interfaces::srv::PickPlaceTask_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace pick_place_interfaces


#ifndef _WIN32
# define DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Response __attribute__((deprecated))
#else
# define DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Response __declspec(deprecated)
#endif

namespace pick_place_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct PickPlaceTask_Response_
{
  using Type = PickPlaceTask_Response_<ContainerAllocator>;

  explicit PickPlaceTask_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->error_message = "";
    }
  }

  explicit PickPlaceTask_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : error_message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->error_message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _error_message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _error_message_type error_message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__error_message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->error_message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Response
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__pick_place_interfaces__srv__PickPlaceTask_Response
    std::shared_ptr<pick_place_interfaces::srv::PickPlaceTask_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PickPlaceTask_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->error_message != other.error_message) {
      return false;
    }
    return true;
  }
  bool operator!=(const PickPlaceTask_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PickPlaceTask_Response_

// alias to use template instance with default allocator
using PickPlaceTask_Response =
  pick_place_interfaces::srv::PickPlaceTask_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace pick_place_interfaces

namespace pick_place_interfaces
{

namespace srv
{

struct PickPlaceTask
{
  using Request = pick_place_interfaces::srv::PickPlaceTask_Request;
  using Response = pick_place_interfaces::srv::PickPlaceTask_Response;
};

}  // namespace srv

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_HPP_
