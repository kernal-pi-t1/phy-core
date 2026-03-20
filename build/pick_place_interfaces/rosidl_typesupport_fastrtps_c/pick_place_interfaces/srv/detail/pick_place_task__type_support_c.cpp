// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from pick_place_interfaces:srv/PickPlaceTask.idl
// generated code does not contain a copyright notice
#include "pick_place_interfaces/srv/detail/pick_place_task__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "pick_place_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "pick_place_interfaces/srv/detail/pick_place_task__struct.h"
#include "pick_place_interfaces/srv/detail/pick_place_task__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/string.h"  // object_name, return_reason
#include "rosidl_runtime_c/string_functions.h"  // object_name, return_reason

// forward declare type support functions


using _PickPlaceTask_Request__ros_msg_type = pick_place_interfaces__srv__PickPlaceTask_Request;

static bool _PickPlaceTask_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _PickPlaceTask_Request__ros_msg_type * ros_message = static_cast<const _PickPlaceTask_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: object_name
  {
    const rosidl_runtime_c__String * str = &ros_message->object_name;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: return_reason
  {
    const rosidl_runtime_c__String * str = &ros_message->return_reason;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _PickPlaceTask_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _PickPlaceTask_Request__ros_msg_type * ros_message = static_cast<_PickPlaceTask_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: object_name
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->object_name.data) {
      rosidl_runtime_c__String__init(&ros_message->object_name);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->object_name,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'object_name'\n");
      return false;
    }
  }

  // Field name: return_reason
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->return_reason.data) {
      rosidl_runtime_c__String__init(&ros_message->return_reason);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->return_reason,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'return_reason'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_pick_place_interfaces
size_t get_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _PickPlaceTask_Request__ros_msg_type * ros_message = static_cast<const _PickPlaceTask_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name object_name
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->object_name.size + 1);
  // field.name return_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->return_reason.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _PickPlaceTask_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_pick_place_interfaces
size_t max_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Request(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: object_name
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: return_reason
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = pick_place_interfaces__srv__PickPlaceTask_Request;
    is_plain =
      (
      offsetof(DataType, return_reason) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _PickPlaceTask_Request__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Request(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_PickPlaceTask_Request = {
  "pick_place_interfaces::srv",
  "PickPlaceTask_Request",
  _PickPlaceTask_Request__cdr_serialize,
  _PickPlaceTask_Request__cdr_deserialize,
  _PickPlaceTask_Request__get_serialized_size,
  _PickPlaceTask_Request__max_serialized_size
};

static rosidl_message_type_support_t _PickPlaceTask_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_PickPlaceTask_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, PickPlaceTask_Request)() {
  return &_PickPlaceTask_Request__type_support;
}

#if defined(__cplusplus)
}
#endif

// already included above
// #include <cassert>
// already included above
// #include <limits>
// already included above
// #include <string>
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
// already included above
// #include "pick_place_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "pick_place_interfaces/srv/detail/pick_place_task__struct.h"
// already included above
// #include "pick_place_interfaces/srv/detail/pick_place_task__functions.h"
// already included above
// #include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

// already included above
// #include "rosidl_runtime_c/string.h"  // error_message
// already included above
// #include "rosidl_runtime_c/string_functions.h"  // error_message

// forward declare type support functions


using _PickPlaceTask_Response__ros_msg_type = pick_place_interfaces__srv__PickPlaceTask_Response;

static bool _PickPlaceTask_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _PickPlaceTask_Response__ros_msg_type * ros_message = static_cast<const _PickPlaceTask_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    cdr << (ros_message->success ? true : false);
  }

  // Field name: error_message
  {
    const rosidl_runtime_c__String * str = &ros_message->error_message;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _PickPlaceTask_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _PickPlaceTask_Response__ros_msg_type * ros_message = static_cast<_PickPlaceTask_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: success
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->success = tmp ? true : false;
  }

  // Field name: error_message
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->error_message.data) {
      rosidl_runtime_c__String__init(&ros_message->error_message);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->error_message,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'error_message'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_pick_place_interfaces
size_t get_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _PickPlaceTask_Response__ros_msg_type * ros_message = static_cast<const _PickPlaceTask_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name success
  {
    size_t item_size = sizeof(ros_message->success);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name error_message
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->error_message.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _PickPlaceTask_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_pick_place_interfaces
size_t max_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Response(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: success
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: error_message
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = pick_place_interfaces__srv__PickPlaceTask_Response;
    is_plain =
      (
      offsetof(DataType, error_message) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _PickPlaceTask_Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_pick_place_interfaces__srv__PickPlaceTask_Response(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_PickPlaceTask_Response = {
  "pick_place_interfaces::srv",
  "PickPlaceTask_Response",
  _PickPlaceTask_Response__cdr_serialize,
  _PickPlaceTask_Response__cdr_deserialize,
  _PickPlaceTask_Response__get_serialized_size,
  _PickPlaceTask_Response__max_serialized_size
};

static rosidl_message_type_support_t _PickPlaceTask_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_PickPlaceTask_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, PickPlaceTask_Response)() {
  return &_PickPlaceTask_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "pick_place_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "pick_place_interfaces/srv/pick_place_task.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t PickPlaceTask__callbacks = {
  "pick_place_interfaces::srv",
  "PickPlaceTask",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, PickPlaceTask_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, PickPlaceTask_Response)(),
};

static rosidl_service_type_support_t PickPlaceTask__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &PickPlaceTask__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, pick_place_interfaces, srv, PickPlaceTask)() {
  return &PickPlaceTask__handle;
}

#if defined(__cplusplus)
}
#endif
