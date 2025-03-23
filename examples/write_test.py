#!/usr/bin/env python3

# write_message(
#     topic: str,
#     message: Any,
#     log_time: int | None = None,
#     publish_time: int | None = None,
#     sequence: int = 0)[source]
# Writes a message to an MCAP file.
#
# Parameters:
#     topic: the topic that this message was originally published on.
#     message: a Protobuf object to write into the MCAP.
#     log_time: unix nanosecond timestamp of when this message was written to the MCAP.
#     publish_time: unix nanosecond timestamp of when this message was originally published.
#     sequence: an optional sequence count for messages on this topic.

# RawImage Schema
# https://docs.foxglove.dev/docs/visualization/message-schemas/raw-image/
# timestamp time    Timestamp of image
# frame_id  string  Frame of reference for the image. The origin of the frame is the optical center of the camera. +x points to the right in the image, +y points down, and +z points into the plane of the image.
# width     uint32  Image width
# height    uint32  Image height
# encoding  string  Encoding of the raw image data
# step      uint32  Byte length of a single row
# data      bytes   Raw image data

# CompressedImage Schema
# https://docs.foxglove.dev/docs/visualization/message-schemas/compressed-image/
# timestamp time   Timestamp of image
# frame_id  string Frame of reference for the image. The origin of the frame is the optical center of the camera. +x points to the right in the image, +y points down, and +z points into the plane of the image.
# data      bytes  Compressed image data
# format    string Image format

import sys
import cv2
import numpy as np
from time import sleep, time_ns
from thebrian import *

from msgs.python.msgs_pb2 import RawFullImu, Vector


def main():
    # just grab any image to simulate one from a camera
    img = cv2.imread('robin.png', cv2.IMREAD_GRAYSCALE)
    height, width = img.shape[:2]
    ok, jpg = cv2.imencode(".jpg", img)
    jpg = jpg.tobytes()

    # number of data points
    size = 10

    data = defaultdict(deque)
    an = np.random.normal(0.0,0.01,(size,3))
    gn = np.random.normal(0.0,0.01,(size,3)) + np.array([0.1,-0.05,0.025])
    for i in range(size):
        ts = time_ns()

        msg=RawFullImu(
                accels=Vector(x=an[i,0],y=an[i,1],z=an[i,2]),
                gyros=Vector(x=gn[i,0],y=gn[i,1],z=gn[i,2]),
                mags=Vector(x=1,y=2,z=3),
                imu_temp = 25,
                temperature=26,
                pressure=1011,
                # timestamp=ts,
                timestamp=make_timestamp(ts),
            )

        data["/simple_msgs"].append(msg)

        data["/images"].append(
            # Image(
            #     data = jpg,
            #     width = width,
            #     height = height,
            #     channels = 1,
            #     timestamp = ts
            # )
            # RawImage(
            #     timestamp=make_timestamp(ts),
            #     # timestamp=ts,
            #     frame_id="camera",
            #     width=width,
            #     height=height,
            #     encoding="mono8",
            #     step=width,
            #     data=img.tobytes()
            # )
            CompressedImage(
                timestamp=make_timestamp(ts),
                frame_id="camera",
                # width=width,
                # height=height,
                # encoding="mono8",
                # step=width,
                data=jpg, #img.tobytes()
                format="jpeg"
            )
        )

        sleep(0.01)

    write_mcap(sys.argv[1], data)

    rdata, meta = read_mcap(sys.argv[1])
    print(meta)

if __name__ == "__main__":
    main()