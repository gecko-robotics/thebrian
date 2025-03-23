#!/usr/bin/env python3
# https://github.com/foxglove/foxglove-sdk/tree/main/schemas/proto/foxglove
#
# pip install opencv-contrib-python websockets
# pip install websockets numpy opencv-python protobuf
# pip install foxglove-websocket[examples]
#
import asyncio
import sys
import time
from base64 import b64encode
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServerListener
from foxglove_websocket.server import FoxgloveServer
from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.RawImage_pb2 import RawImage
from foxglove_schemas_protobuf.LaserScan_pb2 import LaserScan
from foxglove_schemas_protobuf.FrameTransform_pb2 import FrameTransform
# from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FileDescriptor
from pyquaternion import Quaternion
import numpy as np
import cv2
from lidar_urg import URG04LX


bgr2gray = lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
deg2rad = np.pi / 180

lidar = URG04LX()

# def timestamp(time_ns: int):
#   return Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)

# Function to create a sample image
def create_sample_image():
  img = np.zeros((64, 64), dtype=np.uint8)
  for i in range(64):
    for j in range(64):
      img[i, j] = ((i // 8) + (j // 8)) % 2 * 255
  return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


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


async def main():
  class Listener(FoxgloveServerListener):
    async def on_subscribe(self, server, channel_id):
      print("First client subscribed to", channel_id)

    async def on_unsubscribe(self, server, channel_id):
      print("Last client unsubscribed from", channel_id)

  async with FoxgloveServer("0.0.0.0", 8765, "example server") as server:
    server.set_listener(Listener())
    chan_id = await server.add_channel(
      {
        "topic": "lidar_msg",
        "encoding": "protobuf",
        "schemaName": LaserScan.DESCRIPTOR.full_name,
        "schema": b64encode(
            build_file_descriptor_set(LaserScan).SerializeToString()
        ).decode("ascii"),
        "schemaEncoding": "protobuf",
      }
    )

    image_id = await server.add_channel(
      {
        "topic": "image_msg",
        "encoding": "protobuf",
        "schemaName": RawImage.DESCRIPTOR.full_name,
        "schema": b64encode(
            build_file_descriptor_set(RawImage).SerializeToString()
        ).decode("ascii"),
        "schemaEncoding": "protobuf",
      }
    )

    cal_id = await server.add_channel(
      {
        "topic": "cal_msg",
        "encoding": "protobuf",
        "schemaName": CameraCalibration.DESCRIPTOR.full_name,
        "schema": b64encode(
            build_file_descriptor_set(CameraCalibration).SerializeToString()
        ).decode("ascii"),
        "schemaEncoding": "protobuf",
      }
    )

    tf_id = await server.add_channel(
      {
        "topic": "tf_msg",
        "encoding": "protobuf",
        "schemaName": FrameTransform.DESCRIPTOR.full_name,
        "schema": b64encode(
            build_file_descriptor_set(FrameTransform).SerializeToString()
        ).decode("ascii"),
        "schemaEncoding": "protobuf",
      }
    )

    i = 0
    while True:
      i += 1
      await asyncio.sleep(0.05)
      now = time.time_ns()


      # scene_update = SceneUpdate()
      # entity = scene_update.entities.add()
      # entity.timestamp.FromNanoseconds(now)
      # entity.frame_id = "root"
      # cube = entity.cubes.add()
      # cube.size.x = 1
      # cube.size.y = 1
      # cube.size.z = 1
      # cube.pose.position.x = 2
      # cube.pose.position.y = 0
      # cube.pose.position.z = 0
      # q = Quaternion(axis=[0, 1, 1], angle=i * 0.1)
      # cube.pose.orientation.x = q.x
      # cube.pose.orientation.y = q.y
      # cube.pose.orientation.z = q.z
      # cube.pose.orientation.w = q.w
      # cube.color.r = 0.6
      # cube.color.g = 0.2
      # cube.color.b = 1
      # cube.color.a = 1

      # await server.send_message(chan_id, now, scene_update.SerializeToString())

      qr = Quaternion(axis=[0, 0, 1], angle=i*0.05)
      qfix = Quaternion(axis=[0,1,0], angle=np.pi/2)
      q = qr * qfix
      q = q.unit

      T = FrameTransform()
      T.timestamp.FromNanoseconds(now)
      T.parent_frame_id = "root"
      T.child_frame_id = "camera"
      T.translation.x = 0
      T.translation.y = 0
      T.translation.z = 0
      T.rotation.x = q.x
      T.rotation.y = q.y
      T.rotation.z = q.z
      T.rotation.w = q.w
      await server.send_message(tf_id, now, T.SerializeToString())

      # LIDAR ---------------------------------------------
      pts = lidar.capture()
      scan = LaserScan()
      scan.frame_id = "root"
      scan.timestamp.FromNanoseconds(now)
      scan.pose.orientation.x = 0.0
      scan.pose.orientation.y = 0.0
      scan.pose.orientation.z = 0.0
      scan.pose.orientation.w = 1.0
      scan.start_angle = lidar.angles.min*deg2rad
      scan.end_angle = lidar.angles.max*deg2rad
      # scan.ranges = pts.scan
      for pt in pts.scan:
        scan.ranges.append(pt)
        scan.intensities.append(pt)
      await server.send_message(chan_id, now, scan.SerializeToString())

      # Camera --------------------------------------------
      frame = create_sample_image()
      height, width, _ = frame.shape
      img = RawImage()
      img.frame_id = "camera"
      img.width = width
      img.height = height
      img.encoding = "rgb8"
      img.step = width*3
      img.timestamp.FromNanoseconds(now)
      img.data = frame.tobytes()
      await server.send_message(image_id, now, img.SerializeToString())

      # Calibration ---------------------------------------
      # /camera/calibration
      focal_length_mm = 35.0
      sensor_width_mm = 10.0
      fx = (focal_length_mm / sensor_width_mm) * width
      fy = (focal_length_mm / sensor_width_mm) * height
      cx = width / 2
      cy = height / 2
      cal = CameraCalibration(
          D=[0.0, 0.0, 0.0, 0.0, 0.0],
          K=[fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0],
          R=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
          P=[fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0],
      )
      cal.frame_id="camera"
      cal.width=width
      cal.height=height
      cal.distortion_model="plumb_bob"
      cal.timestamp.FromNanoseconds(now)
      await server.send_message(cal_id, now, cal.SerializeToString())


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("ERROR: No serial port given")
    print("Usage: {sys.argv[0]} <port>")
    sys.exit(1)

  port = sys.argv[1]
  ok = lidar.init(port, baudrate=19200)
  if not ok:
    print("*** Couldn't init lidar ***")
    sys.exit(1)

  print(lidar.pp_params)
  lidar.printInfo()

  run_cancellable(main())
