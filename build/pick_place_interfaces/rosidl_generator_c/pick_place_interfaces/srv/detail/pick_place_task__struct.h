// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from pick_place_interfaces:srv/PickPlaceTask.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_H_
#define PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_H_

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
// Member 'return_reason'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/PickPlaceTask in the package pick_place_interfaces.
typedef struct pick_place_interfaces__srv__PickPlaceTask_Request
{
  rosidl_runtime_c__String object_name;
  rosidl_runtime_c__String return_reason;
} pick_place_interfaces__srv__PickPlaceTask_Request;

// Struct for a sequence of pick_place_interfaces__srv__PickPlaceTask_Request.
typedef struct pick_place_interfaces__srv__PickPlaceTask_Request__Sequence
{
  pick_place_interfaces__srv__PickPlaceTask_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} pick_place_interfaces__srv__PickPlaceTask_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'error_message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/PickPlaceTask in the package pick_place_interfaces.
typedef struct pick_place_interfaces__srv__PickPlaceTask_Response
{
  bool success;
  rosidl_runtime_c__String error_message;
} pick_place_interfaces__srv__PickPlaceTask_Response;

// Struct for a sequence of pick_place_interfaces__srv__PickPlaceTask_Response.
typedef struct pick_place_interfaces__srv__PickPlaceTask_Response__Sequence
{
  pick_place_interfaces__srv__PickPlaceTask_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} pick_place_interfaces__srv__PickPlaceTask_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PICK_PLACE_INTERFACES__SRV__DETAIL__PICK_PLACE_TASK__STRUCT_H_
