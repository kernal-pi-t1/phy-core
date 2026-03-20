# generated from rosidl_generator_py/resource/_idl.py.em
# with input from pick_place_interfaces:srv/PickPlaceTask.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_PickPlaceTask_Request(type):
    """Metaclass of message 'PickPlaceTask_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('pick_place_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'pick_place_interfaces.srv.PickPlaceTask_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__pick_place_task__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__pick_place_task__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__pick_place_task__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__pick_place_task__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__pick_place_task__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class PickPlaceTask_Request(metaclass=Metaclass_PickPlaceTask_Request):
    """Message class 'PickPlaceTask_Request'."""

    __slots__ = [
        '_object_name',
        '_return_reason',
    ]

    _fields_and_field_types = {
        'object_name': 'string',
        'return_reason': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.object_name = kwargs.get('object_name', str())
        self.return_reason = kwargs.get('return_reason', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.object_name != other.object_name:
            return False
        if self.return_reason != other.return_reason:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def object_name(self):
        """Message field 'object_name'."""
        return self._object_name

    @object_name.setter
    def object_name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'object_name' field must be of type 'str'"
        self._object_name = value

    @builtins.property
    def return_reason(self):
        """Message field 'return_reason'."""
        return self._return_reason

    @return_reason.setter
    def return_reason(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'return_reason' field must be of type 'str'"
        self._return_reason = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_PickPlaceTask_Response(type):
    """Metaclass of message 'PickPlaceTask_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('pick_place_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'pick_place_interfaces.srv.PickPlaceTask_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__pick_place_task__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__pick_place_task__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__pick_place_task__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__pick_place_task__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__pick_place_task__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class PickPlaceTask_Response(metaclass=Metaclass_PickPlaceTask_Response):
    """Message class 'PickPlaceTask_Response'."""

    __slots__ = [
        '_success',
        '_error_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'error_message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.error_message = kwargs.get('error_message', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.success != other.success:
            return False
        if self.error_message != other.error_message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def error_message(self):
        """Message field 'error_message'."""
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'error_message' field must be of type 'str'"
        self._error_message = value


class Metaclass_PickPlaceTask(type):
    """Metaclass of service 'PickPlaceTask'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('pick_place_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'pick_place_interfaces.srv.PickPlaceTask')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__pick_place_task

            from pick_place_interfaces.srv import _pick_place_task
            if _pick_place_task.Metaclass_PickPlaceTask_Request._TYPE_SUPPORT is None:
                _pick_place_task.Metaclass_PickPlaceTask_Request.__import_type_support__()
            if _pick_place_task.Metaclass_PickPlaceTask_Response._TYPE_SUPPORT is None:
                _pick_place_task.Metaclass_PickPlaceTask_Response.__import_type_support__()


class PickPlaceTask(metaclass=Metaclass_PickPlaceTask):
    from pick_place_interfaces.srv._pick_place_task import PickPlaceTask_Request as Request
    from pick_place_interfaces.srv._pick_place_task import PickPlaceTask_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
