// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from phy_interface:srv/GetPose.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "phy_interface/srv/detail/get_pose__rosidl_typesupport_introspection_c.h"
#include "phy_interface/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "phy_interface/srv/detail/get_pose__functions.h"
#include "phy_interface/srv/detail/get_pose__struct.h"


// Include directives for member types
// Member `method`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  phy_interface__srv__GetPose_Request__init(message_memory);
}

void phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_fini_function(void * message_memory)
{
  phy_interface__srv__GetPose_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_member_array[1] = {
  {
    "method",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(phy_interface__srv__GetPose_Request, method),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_members = {
  "phy_interface__srv",  // message namespace
  "GetPose_Request",  // message name
  1,  // number of fields
  sizeof(phy_interface__srv__GetPose_Request),
  phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_member_array,  // message members
  phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_type_support_handle = {
  0,
  &phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_phy_interface
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Request)() {
  if (!phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_type_support_handle.typesupport_identifier) {
    phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &phy_interface__srv__GetPose_Request__rosidl_typesupport_introspection_c__GetPose_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "phy_interface/srv/detail/get_pose__rosidl_typesupport_introspection_c.h"
// already included above
// #include "phy_interface/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "phy_interface/srv/detail/get_pose__functions.h"
// already included above
// #include "phy_interface/srv/detail/get_pose__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  phy_interface__srv__GetPose_Response__init(message_memory);
}

void phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_fini_function(void * message_memory)
{
  phy_interface__srv__GetPose_Response__fini(message_memory);
}

size_t phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__size_function__GetPose_Response__pose(
  const void * untyped_member)
{
  (void)untyped_member;
  return 6;
}

const void * phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_const_function__GetPose_Response__pose(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_function__GetPose_Response__pose(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__fetch_function__GetPose_Response__pose(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_const_function__GetPose_Response__pose(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__assign_function__GetPose_Response__pose(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_function__GetPose_Response__pose(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_member_array[1] = {
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    6,  // array size
    false,  // is upper bound
    offsetof(phy_interface__srv__GetPose_Response, pose),  // bytes offset in struct
    NULL,  // default value
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__size_function__GetPose_Response__pose,  // size() function pointer
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_const_function__GetPose_Response__pose,  // get_const(index) function pointer
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__get_function__GetPose_Response__pose,  // get(index) function pointer
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__fetch_function__GetPose_Response__pose,  // fetch(index, &value) function pointer
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__assign_function__GetPose_Response__pose,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_members = {
  "phy_interface__srv",  // message namespace
  "GetPose_Response",  // message name
  1,  // number of fields
  sizeof(phy_interface__srv__GetPose_Response),
  phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_member_array,  // message members
  phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_type_support_handle = {
  0,
  &phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_phy_interface
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Response)() {
  if (!phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_type_support_handle.typesupport_identifier) {
    phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &phy_interface__srv__GetPose_Response__rosidl_typesupport_introspection_c__GetPose_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "phy_interface/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "phy_interface/srv/detail/get_pose__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_members = {
  "phy_interface__srv",  // service namespace
  "GetPose",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_Request_message_type_support_handle,
  NULL  // response message
  // phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_Response_message_type_support_handle
};

static rosidl_service_type_support_t phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_type_support_handle = {
  0,
  &phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_phy_interface
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose)() {
  if (!phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_type_support_handle.typesupport_identifier) {
    phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, phy_interface, srv, GetPose_Response)()->data;
  }

  return &phy_interface__srv__detail__get_pose__rosidl_typesupport_introspection_c__GetPose_service_type_support_handle;
}
