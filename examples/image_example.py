#!/usr/bin/env python3

# import struct
import sys
import time
# from io import BytesIO
# from random import random
# from typing import List

from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
from foxglove_schemas_protobuf.RawImage_pb2 import RawImage
from google.protobuf.timestamp_pb2 import Timestamp
from mcap_protobuf.writer import Writer

import cv2

bgr2gray = lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

imgs = []

def write_frame(writer: Writer, frame, now: int):

    ts = timestamp(now)
    height, width = frame.shape

    # /camera/image
    img = RawImage(
        timestamp=ts,
        frame_id="camera",
        width=width,
        height=height,
        # encoding="rgb8",
        # step=width * 3,
        encoding="mono8",
        step=width,
        data=frame.tobytes(),
    )
    writer.write_message(
        topic="/camera/image",
        log_time=now,
        message=img,
        publish_time=now,
    )

    # /camera/calibration
    focal_length_mm = 35.0
    sensor_width_mm = 10.0
    fx = (focal_length_mm / sensor_width_mm) * width
    fy = (focal_length_mm / sensor_width_mm) * height
    cx = width / 2
    cy = height / 2
    cal = CameraCalibration(
        timestamp=ts,
        frame_id="camera",
        width=width,
        height=height,
        distortion_model="plumb_bob",
        D=[0.0, 0.0, 0.0, 0.0, 0.0],
        K=[fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0],
        R=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        P=[fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0],
    )
    writer.write_message(
        topic="/camera/calibration",
        log_time=now,
        message=cal,
        publish_time=now,
    )

def timestamp(time_ns: int) -> Timestamp:
    return Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output.mcap>")
        sys.exit(1)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    ok, frame = camera.read()

    for _ in range(100):
        ok, frame = camera.read()
        if ok is False:
            time.sleep(0.01)
            continue

        frame = bgr2gray(frame)
        imgs.append((frame, time.time_ns(),))

    with open(sys.argv[1], "wb") as f, Writer(f) as writer:
        for img, ts in imgs:
            write_frame(writer, img, ts)

if __name__ == "__main__":
    main()