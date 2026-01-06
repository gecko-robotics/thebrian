
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.timestamp_pb2 import Timestamp
from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
from foxglove_schemas_protobuf.ModelPrimitive_pb2 import ModelPrimitive
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
from foxglove_websocket.server import FoxgloveServerListener
from foxglove_websocket.server import FoxgloveServer
from base64 import b64encode
# from colorama import Fore
import time
# from squaternion import Quaternion
from collections import namedtuple

Quat = namedtuple("Quat","w x y z")

def build_file_descriptor_set(message_class):
  """
  Build a FileDescriptorSet representing the message class and its dependencies.
  """
  file_descriptor_set = FileDescriptorSet()
  seen_dependencies: Set[str] = set()

  def append_file_descriptor(file_descriptor):
    for dep in file_descriptor.dependencies:
      if dep.name not in seen_dependencies:
        seen_dependencies.add(dep.name)
        append_file_descriptor(dep)
    file_descriptor.CopyToProto(file_descriptor_set.file.add())

  append_file_descriptor(message_class.DESCRIPTOR.file)
  return file_descriptor_set

def make_protobuf_channel(topic, class_type):
  info = {
    "topic": topic,
    "encoding": "protobuf",
    "schemaName": class_type.DESCRIPTOR.full_name,
    "schema": b64encode(
        build_file_descriptor_set(class_type).SerializeToString()
    ).decode("ascii"),
    "schemaEncoding": "protobuf",
  }
  return info

def read_stl(file_path):
  model_data = None
  try:
    with open(file_path, "rb") as fd:
      model_data = fd.read()
  except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
  except IOError as e:
    print(f"Error reading file: {e}")
  return model_data

class STLModel:
  parent_id = "root"
  frame_id = "model"
  id = "model"
  scale = 0.01

  def __init__(self):
    pass

  def get_scene(self, file_path, now=None):
    model_data = read_stl(file_path)

    if now is None:
      now = time.time_ns()

    scene_update = SceneUpdate()
    entity = scene_update.entities.add()
    entity.timestamp.FromNanoseconds(now)
    entity.id = self.id
    entity.frame_id = self.frame_id
    entity.frame_locked = True  # allow the entity to move when we update the "model" frame transforms
    model = entity.models.add()
    model.pose.position.x = -0.4
    model.pose.position.y = 0
    model.pose.position.z = -0.1
    model.pose.orientation.x = 0
    model.pose.orientation.y = 0
    model.pose.orientation.z = 0
    model.pose.orientation.w = 1
    model.color.r = 0.6
    model.color.g = 0.2
    model.color.b = 1
    model.color.a = 0.8
    model.override_color = True

    # Use scale.x/y/z = 1 to use the original scale factor embedded in the model
    # scale = 0.01
    model.scale.x = self.scale
    model.scale.y = self.scale
    model.scale.z = self.scale
    model.data = model_data
    model.media_type = "model/stl"

    return scene_update

  def get_tf(self, q=None, translation=None, now=None):
    if q is None:
      q = Quat(1,0,0,0)

    if now is None:
      now = time.time_ns()

    if translation is None:
      translation = (0,0,1,)

    x,y,z = translation

    T = FrameTransform()
    T.timestamp.FromNanoseconds(now)
    T.parent_frame_id = self.parent_id
    T.child_frame_id = self.frame_id
    T.translation.x = x
    T.translation.y = y
    T.translation.z = z
    T.rotation.x = q.x
    T.rotation.y = q.y
    T.rotation.z = q.z
    T.rotation.w = q.w
    return T

def make_oak_model(file_path, frame_id, parent_it, time_ns=None):
  model_data = read_stl(file_path)

  if time_ns is None:
    time_ns = time.time_ns()

  scene_update = SceneUpdate()
  entity = scene_update.entities.add()
  entity.timestamp.FromNanoseconds(time_ns)
  entity.id = "oak-camera"
  entity.frame_id = frame_id
  entity.frame_locked = True  # allow the entity to move when we update the "model" frame transforms
  model = entity.models.add()
  model.pose.position.x = -0.4
  model.pose.position.y = 0
  model.pose.position.z = -0.1
  model.pose.orientation.x = 0
  model.pose.orientation.y = 0
  model.pose.orientation.z = 0
  model.pose.orientation.w = 1
  model.color.r = 0.6
  model.color.g = 0.2
  model.color.b = 1
  model.color.a = 0.8
  model.override_color = True

  # Use scale.x/y/z = 1 to use the original scale factor embedded in the model
  scale = 0.01
  model.scale.x = scale
  model.scale.y = scale
  model.scale.z = scale
  model.data = model_data
  model.media_type = "model/stl"

  return scene_update