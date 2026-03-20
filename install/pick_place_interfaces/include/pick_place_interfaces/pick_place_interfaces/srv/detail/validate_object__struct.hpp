// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from pick_place_interfaces:srv/ValidateObject.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__STRUCT_HPP_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__pick_place_interfaces__srv__ValidateObject_Request __attribute__((deprecated))
#else
# define DEPRECATED__pick_place_interfaces__srv__ValidateObject_Request __declspec(deprecated)
#endif

namespace pick_place_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ValidateObject_Request_
{
  using Type = ValidateObject_Request_<ContainerAllocator>;

  explicit ValidateObject_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->object_name = "";
    }
  }

  explicit ValidateObject_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : object_name(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->object_name = "";
    }
  }

  // field types and members
  using _object_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _object_name_type object_name;

  // setters for named parameter idiom
  Type & set__object_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->object_name = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__pick_place_interfaces__srv__ValidateObject_Request
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__pick_place_interfaces__srv__ValidateObject_Request
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ValidateObject_Request_ & other) const
  {
    if (this->object_name != other.object_name) {
      return false;
    }
    return true;
  }
  bool operator!=(const ValidateObject_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ValidateObject_Request_

// alias to use template instance with default allocator
using ValidateObject_Request =
  pick_place_interfaces::srv::ValidateObject_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace pick_place_interfaces


#ifndef _WIN32
# define DEPRECATED__pick_place_interfaces__srv__ValidateObject_Response __attribute__((deprecated))
#else
# define DEPRECATED__pick_place_interfaces__srv__ValidateObject_Response __declspec(deprecated)
#endif

namespace pick_place_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ValidateObject_Response_
{
  using Type = ValidateObject_Response_<ContainerAllocator>;

  explicit ValidateObject_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_valid = false;
    }
  }

  explicit ValidateObject_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_valid = false;
    }
  }

  // field types and members
  using _is_valid_type =
    bool;
  _is_valid_type is_valid;

  // setters for named parameter idiom
  Type & set__is_valid(
    const bool & _arg)
  {
    this->is_valid = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__pick_place_interfaces__srv__ValidateObject_Response
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__pick_place_interfaces__srv__ValidateObject_Response
    std::shared_ptr<pick_place_interfaces::srv::ValidateObject_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ValidateObject_Response_ & other) const
  {
    if (this->is_valid != other.is_valid) {
      return false;
    }
    return true;
  }
  bool operator!=(const ValidateObject_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ValidateObject_Response_

// alias to use template instance with default allocator
using ValidateObject_Response =
  pick_place_interfaces::srv::ValidateObject_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace pick_place_interfaces

namespace pick_place_interfaces
{

namespace srv
{

struct ValidateObject
{
  using Request = pick_place_interfaces::srv::ValidateObject_Request;
  using Response = pick_place_interfaces::srv::ValidateObject_Response;
};

}  // namespace srv

}  // namespace pick_place_interfaces

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__VALIDATE_OBJECT__STRUCT_HPP_
