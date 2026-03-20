// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from phy_interface:srv/Json.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_H_
#define PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'payload'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Json in the package phy_interface.
typedef struct phy_interface__srv__Json_Request
{
  rosidl_runtime_c__String payload;
} phy_interface__srv__Json_Request;

// Struct for a sequence of phy_interface__srv__Json_Request.
typedef struct phy_interface__srv__Json_Request__Sequence
{
  phy_interface__srv__Json_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} phy_interface__srv__Json_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/Json in the package phy_interface.
typedef struct phy_interface__srv__Json_Response
{
  bool success;
} phy_interface__srv__Json_Response;

// Struct for a sequence of phy_interface__srv__Json_Response.
typedef struct phy_interface__srv__Json_Response__Sequence
{
  phy_interface__srv__Json_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} phy_interface__srv__Json_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PHY_INTERFACE__SRV__DETAIL__JSON__STRUCT_H_
