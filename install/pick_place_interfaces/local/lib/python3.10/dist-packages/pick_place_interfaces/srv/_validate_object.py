# generated from rosidl_generator_py/resource/_idl.py.em
# with input from pick_place_interfaces:srv/ValidateObject.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ValidateObject_Request(type):
    """Metaclass of message 'ValidateObject_Request'."""

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
                'pick_place_interfaces.srv.ValidateObject_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__validate_object__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__validate_object__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__validate_object__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__validate_object__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__validate_object__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ValidateObject_Request(metaclass=Metaclass_ValidateObject_Request):
    """Message class 'ValidateObject_Request'."""

    __slots__ = [
        '_object_name',
    ]

    _fields_and_field_types = {
        'object_name': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.object_name = kwargs.get('object_name', str())

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


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ValidateObject_Response(type):
    """Metaclass of message 'ValidateObject_Response'."""

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
                'pick_place_interfaces.srv.ValidateObject_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__validate_object__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__validate_object__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__validate_object__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__validate_object__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__validate_object__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ValidateObject_Response(metaclass=Metaclass_ValidateObject_Response):
    """Message class 'ValidateObject_Response'."""

    __slots__ = [
        '_is_valid',
    ]

    _fields_and_field_types = {
        'is_valid': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.is_valid = kwargs.get('is_valid', bool())

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
        if self.is_valid != other.is_valid:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def is_valid(self):
        """Message field 'is_valid'."""
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'is_valid' field must be of type 'bool'"
        self._is_valid = value


class Metaclass_ValidateObject(type):
    """Metaclass of service 'ValidateObject'."""

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
                'pick_place_interfaces.srv.ValidateObject')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__validate_object

            from pick_place_interfaces.srv import _validate_object
            if _validate_object.Metaclass_ValidateObject_Request._TYPE_SUPPORT is None:
                _validate_object.Metaclass_ValidateObject_Request.__import_type_support__()
            if _validate_object.Metaclass_ValidateObject_Response._TYPE_SUPPORT is None:
                _validate_object.Metaclass_ValidateObject_Response.__import_type_support__()


class ValidateObject(metaclass=Metaclass_ValidateObject):
    from pick_place_interfaces.srv._validate_object import ValidateObject_Request as Request
    from pick_place_interfaces.srv._validate_object import ValidateObject_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
