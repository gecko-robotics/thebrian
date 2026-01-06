
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
from gecko_messages import Timestamp
# from gecko_messages import TransformStamped
from gecko_messages import quaternion_t, vector_t
import time

def make_timestamp(time_ns: int):
  return Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)

def make_timestamp_now():
  time_ns = time.time_ns()
  return make_timestamp(time_ns)

def to_int(timestamp) -> int:
  return timestamp.seconds*1_000_000_000 + timestamp.nanos

def make_tf(frame_id, parent_id, orientation=None, translation=None, time_ns=None):
  if orientation is None:
    orientation = quaternion_t(1,0,0,0)

  if time_ns is None:
    time_ns = time.time_ns()

  if translation is None:
    translation = vector_t(0,0,0)

  # T.timestamp.FromNanoseconds(time_ns)
  # T.parent_frame_id = parent_id
  # T.child_frame_id = frame_id

  # T = TransformStamped()
  # T.header.timestamp.FromNanoseconds(time_ns)
  # T.header.frame_id = parent_id
  # T.child_frame_id = frame_id
  # T.header.frame_id = frame_id
  # T.child_frame_id = parent_id
  
  T = FrameTransform()
  T.timestamp.FromNanoseconds(time_ns)
  T.parent_frame_id = parent_id
  T.child_frame_id = frame_id

  T.translation.x = translation.x
  T.translation.y = translation.y
  T.translation.z = translation.z

  T.rotation.x = orientation.x
  T.rotation.y = orientation.y
  T.rotation.z = orientation.z
  T.rotation.w = orientation.w
  return T