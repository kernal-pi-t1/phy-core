// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phy_interface:action/Move.idl
// generated code does not contain a copyright notice

#ifndef PHY_INTERFACE__ACTION__DETAIL__MOVE__BUILDER_HPP_
#define PHY_INTERFACE__ACTION__DETAIL__MOVE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phy_interface/action/detail/move__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_Goal_target_pose
{
public:
  Init_Move_Goal_target_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::action::Move_Goal target_pose(::phy_interface::action::Move_Goal::_target_pose_type arg)
  {
    msg_.target_pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_Goal>()
{
  return phy_interface::action::builder::Init_Move_Goal_target_pose();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_Result_success
{
public:
  Init_Move_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::action::Move_Result success(::phy_interface::action::Move_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_Result>()
{
  return phy_interface::action::builder::Init_Move_Result_success();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_Feedback_status
{
public:
  Init_Move_Feedback_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::action::Move_Feedback status(::phy_interface::action::Move_Feedback::_status_type arg)
  {
    msg_.status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_Feedback>()
{
  return phy_interface::action::builder::Init_Move_Feedback_status();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_SendGoal_Request_goal
{
public:
  explicit Init_Move_SendGoal_Request_goal(::phy_interface::action::Move_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::phy_interface::action::Move_SendGoal_Request goal(::phy_interface::action::Move_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_SendGoal_Request msg_;
};

class Init_Move_SendGoal_Request_goal_id
{
public:
  Init_Move_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Move_SendGoal_Request_goal goal_id(::phy_interface::action::Move_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_Move_SendGoal_Request_goal(msg_);
  }

private:
  ::phy_interface::action::Move_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_SendGoal_Request>()
{
  return phy_interface::action::builder::Init_Move_SendGoal_Request_goal_id();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_SendGoal_Response_stamp
{
public:
  explicit Init_Move_SendGoal_Response_stamp(::phy_interface::action::Move_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::phy_interface::action::Move_SendGoal_Response stamp(::phy_interface::action::Move_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_SendGoal_Response msg_;
};

class Init_Move_SendGoal_Response_accepted
{
public:
  Init_Move_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Move_SendGoal_Response_stamp accepted(::phy_interface::action::Move_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_Move_SendGoal_Response_stamp(msg_);
  }

private:
  ::phy_interface::action::Move_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_SendGoal_Response>()
{
  return phy_interface::action::builder::Init_Move_SendGoal_Response_accepted();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_GetResult_Request_goal_id
{
public:
  Init_Move_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::phy_interface::action::Move_GetResult_Request goal_id(::phy_interface::action::Move_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_GetResult_Request>()
{
  return phy_interface::action::builder::Init_Move_GetResult_Request_goal_id();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_GetResult_Response_result
{
public:
  explicit Init_Move_GetResult_Response_result(::phy_interface::action::Move_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::phy_interface::action::Move_GetResult_Response result(::phy_interface::action::Move_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_GetResult_Response msg_;
};

class Init_Move_GetResult_Response_status
{
public:
  Init_Move_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Move_GetResult_Response_result status(::phy_interface::action::Move_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_Move_GetResult_Response_result(msg_);
  }

private:
  ::phy_interface::action::Move_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_GetResult_Response>()
{
  return phy_interface::action::builder::Init_Move_GetResult_Response_status();
}

}  // namespace phy_interface


namespace phy_interface
{

namespace action
{

namespace builder
{

class Init_Move_FeedbackMessage_feedback
{
public:
  explicit Init_Move_FeedbackMessage_feedback(::phy_interface::action::Move_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::phy_interface::action::Move_FeedbackMessage feedback(::phy_interface::action::Move_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phy_interface::action::Move_FeedbackMessage msg_;
};

class Init_Move_FeedbackMessage_goal_id
{
public:
  Init_Move_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Move_FeedbackMessage_feedback goal_id(::phy_interface::action::Move_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_Move_FeedbackMessage_feedback(msg_);
  }

private:
  ::phy_interface::action::Move_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::phy_interface::action::Move_FeedbackMessage>()
{
  return phy_interface::action::builder::Init_Move_FeedbackMessage_goal_id();
}

}  // namespace phy_interface

#endif  // PHY_INTERFACE__ACTION__DETAIL__MOVE__BUILDER_HPP_
