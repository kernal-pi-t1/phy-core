// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from pick_place_interfaces:msg/ObjectPose.idl
// generated code does not contain a copyright notice

#ifndef PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__STRUCT_H_
#define PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ObjectPose in the package pick_place_interfaces.
typedef struct pick_place_interfaces__msg__ObjectPose
{
  /// meters
  double x;
  /// meters
  double y;
  /// meters
  double z;
  /// degrees
  double roll;
  /// degrees
  double pitch;
  /// degrees
  double yaw;
} pick_place_interfaces__msg__ObjectPose;

// Struct for a sequence of pick_place_interfaces__msg__ObjectPose.
typedef struct pick_place_interfaces__msg__ObjectPose__Sequence
{
  pick_place_interfaces__msg__ObjectPose * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} pick_place_interfaces__msg__ObjectPose__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PICK_PLACE_INTERFACES__MSG__DETAIL__OBJECT_POSE__STRUCT_H_
