// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from phy_interface:srv/GetPose.idl
// generated code does not contain a copyright notice
#include "phy_interface/srv/detail/get_pose__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `method`
#include "rosidl_runtime_c/string_functions.h"

bool
phy_interface__srv__GetPose_Request__init(phy_interface__srv__GetPose_Request * msg)
{
  if (!msg) {
    return false;
  }
  // method
  if (!rosidl_runtime_c__String__init(&msg->method)) {
    phy_interface__srv__GetPose_Request__fini(msg);
    return false;
  }
  return true;
}

void
phy_interface__srv__GetPose_Request__fini(phy_interface__srv__GetPose_Request * msg)
{
  if (!msg) {
    return;
  }
  // method
  rosidl_runtime_c__String__fini(&msg->method);
}

bool
phy_interface__srv__GetPose_Request__are_equal(const phy_interface__srv__GetPose_Request * lhs, const phy_interface__srv__GetPose_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // method
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->method), &(rhs->method)))
  {
    return false;
  }
  return true;
}

bool
phy_interface__srv__GetPose_Request__copy(
  const phy_interface__srv__GetPose_Request * input,
  phy_interface__srv__GetPose_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // method
  if (!rosidl_runtime_c__String__copy(
      &(input->method), &(output->method)))
  {
    return false;
  }
  return true;
}

phy_interface__srv__GetPose_Request *
phy_interface__srv__GetPose_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Request * msg = (phy_interface__srv__GetPose_Request *)allocator.allocate(sizeof(phy_interface__srv__GetPose_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(phy_interface__srv__GetPose_Request));
  bool success = phy_interface__srv__GetPose_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
phy_interface__srv__GetPose_Request__destroy(phy_interface__srv__GetPose_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    phy_interface__srv__GetPose_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
phy_interface__srv__GetPose_Request__Sequence__init(phy_interface__srv__GetPose_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Request * data = NULL;

  if (size) {
    data = (phy_interface__srv__GetPose_Request *)allocator.zero_allocate(size, sizeof(phy_interface__srv__GetPose_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = phy_interface__srv__GetPose_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        phy_interface__srv__GetPose_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
phy_interface__srv__GetPose_Request__Sequence__fini(phy_interface__srv__GetPose_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      phy_interface__srv__GetPose_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

phy_interface__srv__GetPose_Request__Sequence *
phy_interface__srv__GetPose_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Request__Sequence * array = (phy_interface__srv__GetPose_Request__Sequence *)allocator.allocate(sizeof(phy_interface__srv__GetPose_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = phy_interface__srv__GetPose_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
phy_interface__srv__GetPose_Request__Sequence__destroy(phy_interface__srv__GetPose_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    phy_interface__srv__GetPose_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
phy_interface__srv__GetPose_Request__Sequence__are_equal(const phy_interface__srv__GetPose_Request__Sequence * lhs, const phy_interface__srv__GetPose_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!phy_interface__srv__GetPose_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
phy_interface__srv__GetPose_Request__Sequence__copy(
  const phy_interface__srv__GetPose_Request__Sequence * input,
  phy_interface__srv__GetPose_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(phy_interface__srv__GetPose_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    phy_interface__srv__GetPose_Request * data =
      (phy_interface__srv__GetPose_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!phy_interface__srv__GetPose_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          phy_interface__srv__GetPose_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!phy_interface__srv__GetPose_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
phy_interface__srv__GetPose_Response__init(phy_interface__srv__GetPose_Response * msg)
{
  if (!msg) {
    return false;
  }
  // pose
  return true;
}

void
phy_interface__srv__GetPose_Response__fini(phy_interface__srv__GetPose_Response * msg)
{
  if (!msg) {
    return;
  }
  // pose
}

bool
phy_interface__srv__GetPose_Response__are_equal(const phy_interface__srv__GetPose_Response * lhs, const phy_interface__srv__GetPose_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // pose
  for (size_t i = 0; i < 6; ++i) {
    if (lhs->pose[i] != rhs->pose[i]) {
      return false;
    }
  }
  return true;
}

bool
phy_interface__srv__GetPose_Response__copy(
  const phy_interface__srv__GetPose_Response * input,
  phy_interface__srv__GetPose_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // pose
  for (size_t i = 0; i < 6; ++i) {
    output->pose[i] = input->pose[i];
  }
  return true;
}

phy_interface__srv__GetPose_Response *
phy_interface__srv__GetPose_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Response * msg = (phy_interface__srv__GetPose_Response *)allocator.allocate(sizeof(phy_interface__srv__GetPose_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(phy_interface__srv__GetPose_Response));
  bool success = phy_interface__srv__GetPose_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
phy_interface__srv__GetPose_Response__destroy(phy_interface__srv__GetPose_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    phy_interface__srv__GetPose_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
phy_interface__srv__GetPose_Response__Sequence__init(phy_interface__srv__GetPose_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Response * data = NULL;

  if (size) {
    data = (phy_interface__srv__GetPose_Response *)allocator.zero_allocate(size, sizeof(phy_interface__srv__GetPose_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = phy_interface__srv__GetPose_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        phy_interface__srv__GetPose_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
phy_interface__srv__GetPose_Response__Sequence__fini(phy_interface__srv__GetPose_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      phy_interface__srv__GetPose_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

phy_interface__srv__GetPose_Response__Sequence *
phy_interface__srv__GetPose_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  phy_interface__srv__GetPose_Response__Sequence * array = (phy_interface__srv__GetPose_Response__Sequence *)allocator.allocate(sizeof(phy_interface__srv__GetPose_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = phy_interface__srv__GetPose_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
phy_interface__srv__GetPose_Response__Sequence__destroy(phy_interface__srv__GetPose_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    phy_interface__srv__GetPose_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
phy_interface__srv__GetPose_Response__Sequence__are_equal(const phy_interface__srv__GetPose_Response__Sequence * lhs, const phy_interface__srv__GetPose_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!phy_interface__srv__GetPose_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
phy_interface__srv__GetPose_Response__Sequence__copy(
  const phy_interface__srv__GetPose_Response__Sequence * input,
  phy_interface__srv__GetPose_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(phy_interface__srv__GetPose_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    phy_interface__srv__GetPose_Response * data =
      (phy_interface__srv__GetPose_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!phy_interface__srv__GetPose_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          phy_interface__srv__GetPose_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!phy_interface__srv__GetPose_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
