#!/usr/bin/env python3
import depthai as dai
from thebrian.oak import imu_info, camera_info
from pprint import pprint

device = dai.Device()

info = imu_info(device)
pprint(info)

info = camera_info(device)
pprint(info)
