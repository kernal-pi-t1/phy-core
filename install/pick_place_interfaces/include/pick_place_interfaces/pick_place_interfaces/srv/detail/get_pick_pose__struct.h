// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from pick_place_interfaces:srv/GetPickPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__STRUCT_H_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'object_name'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetPickPose in the package pick_place_interfaces.
typedef struct pick_place_interfaces__srv__GetPickPose_Request
{
  rosidl_runtime_c__String object_name;
} pick_place_interfaces__srv__GetPickPose_Request;

// Struct for a sequence of pick_place_interfaces__srv__GetPickPose_Request.
typedef struct pick_place_interfaces__srv__GetPickPose_Request__Sequence
{
  pick_place_interfaces__srv__GetPickPose_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} pick_place_interfaces__srv__GetPickPose_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "pick_place_interfaces/msg/detail/object_pose__struct.h"
// Member 'error_message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/GetPickPose in the package pick_place_interfaces.
typedef struct pick_place_interfaces__srv__GetPickPose_Response
{
  bool success;
  pick_place_interfaces__msg__ObjectPose pose;
  rosidl_runtime_c__String error_message;
} pick_place_interfaces__srv__GetPickPose_Response;

// Struct for a sequence of pick_place_interfaces__srv__GetPickPose_Response.
typedef struct pick_place_interfaces__srv__GetPickPose_Response__Sequence
{
  pick_place_interfaces__srv__GetPickPose_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} pick_place_interfaces__srv__GetPickPose_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__GET_PICK_POSE__STRUCT_H_
