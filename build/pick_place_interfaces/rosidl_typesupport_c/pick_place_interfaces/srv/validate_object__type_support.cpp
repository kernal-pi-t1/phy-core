// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from pick_place_interfaces:srv/ValidateObject.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "pick_place_interfaces/srv/detail/validate_object__struct.h"
#include "pick_place_interfaces/srv/detail/validate_object__type_support.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace pick_place_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _ValidateObject_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ValidateObject_Request_type_support_ids_t;

static const _ValidateObject_Request_type_support_ids_t _ValidateObject_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _ValidateObject_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ValidateObject_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ValidateObject_Request_type_support_symbol_names_t _ValidateObject_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, ValidateObject_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, pick_place_interfaces, srv, ValidateObject_Request)),
  }
};

typedef struct _ValidateObject_Request_type_support_data_t
{
  void * data[2];
} _ValidateObject_Request_type_support_data_t;

static _ValidateObject_Request_type_support_data_t _ValidateObject_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ValidateObject_Request_message_typesupport_map = {
  2,
  "pick_place_interfaces",
  &_ValidateObject_Request_message_typesupport_ids.typesupport_identifier[0],
  &_ValidateObject_Request_message_typesupport_symbol_names.symbol_name[0],
  &_ValidateObject_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ValidateObject_Request_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ValidateObject_Request_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace pick_place_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, pick_place_interfaces, srv, ValidateObject_Request)() {
  return &::pick_place_interfaces::srv::rosidl_typesupport_c::ValidateObject_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "pick_place_interfaces/srv/detail/validate_object__struct.h"
// already included above
// #include "pick_place_interfaces/srv/detail/validate_object__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
// already included above
// #include "rosidl_typesupport_c/message_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_c/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace pick_place_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _ValidateObject_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ValidateObject_Response_type_support_ids_t;

static const _ValidateObject_Response_type_support_ids_t _ValidateObject_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _ValidateObject_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ValidateObject_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ValidateObject_Response_type_support_symbol_names_t _ValidateObject_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, ValidateObject_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, pick_place_interfaces, srv, ValidateObject_Response)),
  }
};

typedef struct _ValidateObject_Response_type_support_data_t
{
  void * data[2];
} _ValidateObject_Response_type_support_data_t;

static _ValidateObject_Response_type_support_data_t _ValidateObject_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ValidateObject_Response_message_typesupport_map = {
  2,
  "pick_place_interfaces",
  &_ValidateObject_Response_message_typesupport_ids.typesupport_identifier[0],
  &_ValidateObject_Response_message_typesupport_symbol_names.symbol_name[0],
  &_ValidateObject_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ValidateObject_Response_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ValidateObject_Response_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace pick_place_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, pick_place_interfaces, srv, ValidateObject_Response)() {
  return &::pick_place_interfaces::srv::rosidl_typesupport_c::ValidateObject_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "pick_place_interfaces/srv/detail/validate_object__type_support.h"
// already included above
// #include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/service_type_support_dispatch.h"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace pick_place_interfaces
{

namespace srv
{

namespace rosidl_typesupport_c
{

typedef struct _ValidateObject_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ValidateObject_type_support_ids_t;

static const _ValidateObject_type_support_ids_t _ValidateObject_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _ValidateObject_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ValidateObject_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ValidateObject_type_support_symbol_names_t _ValidateObject_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, ValidateObject)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, pick_place_interfaces, srv, ValidateObject)),
  }
};

typedef struct _ValidateObject_type_support_data_t
{
  void * data[2];
} _ValidateObject_type_support_data_t;

static _ValidateObject_type_support_data_t _ValidateObject_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ValidateObject_service_typesupport_map = {
  2,
  "pick_place_interfaces",
  &_ValidateObject_service_typesupport_ids.typesupport_identifier[0],
  &_ValidateObject_service_typesupport_symbol_names.symbol_name[0],
  &_ValidateObject_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t ValidateObject_service_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ValidateObject_service_typesupport_map),
  rosidl_typesupport_c__get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace srv

}  // namespace pick_place_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_c, pick_place_interfaces, srv, ValidateObject)() {
  return &::pick_place_interfaces::srv::rosidl_typesupport_c::ValidateObject_service_type_support_handle;
}

#ifdef __cplusplus
}
#endif
