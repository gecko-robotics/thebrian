import depthai as dai
import numpy as np
from pprint import pprint
from collections import namedtuple
from enum import Enum

class CameraName(Enum):
  rgb = 0
  left = 1
  right = 2

class CameraInfo:
  def __init__(self):
    self.rect = None
    self.distortionCoeff = None
    self.width = None
    self.height = None

class OakInfo:
  def __init__(self):
    self.name = None
    self.version = None
    self.batchtime = None
    self.boardname = None
    self.boardrev = None
    self.hardwareconf = None
    self.rgb = None
    self.left = None
    self.right = None
    self.imu = None

  def __str__(self):
    return "camera"

  def __repr__(self):
    return str(self)

  def set(self, json):
    pass

  def set_camera_info(self, json):
    cam = CameraInfo()
    cam.height = int(json["height"])
    cam.width =  int(json["width"])
    # ["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"]
    cam.distortionCoeff = np.array(json["distortionCoeff"])
    cam.HfovDeg = float(json["specHfovDeg"])
    return cam 

  def get(self, device=None):
    if device is None:
      device = dai.Device()

    calibData = device.readCalibration()
    json = calibData.eepromToJson()


  for data in json["cameraData"]:
    # pprint(data)
    if data[0] == CameraName.left:
      self.left = self.set_camera_info(data[1])
    elif data[0] == CameraName.right:
      self.right = self.set_camera_info(data[1])
    elif data[0] == CameraName.rgb:
      self.rgb = self.set_camera_info(data[1])



Extrinsics = namedtuple("Extrinsics","rotation translation relto spectranslation")


def imu_info(device=None, stereo_res=None, rgb_res=None):
  if device is None:
    device = dai.Device()

  imuType = device.getConnectedIMU()
  imuFirmwareVersion = device.getIMUFirmwareVersion()
  # print(f"IMU type: {imuType}, firmware version: {imuFirmwareVersion}")
  return {"type": imuType, "firmware": str(imuFirmwareVersion)}


def format_json(json):
  ret = {}
  ret["height"] = json["height"]
  ret["width"] =  json["width"]
  # ["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"]
  ret["distortionCoeff"] = np.array(json["distortionCoeff"])
  ret["HfovDeg"] = json["specHfovDeg"] 
  ext = json["extrinsics"]

  relto = None
  if json["extrinsics"]["toCameraSocket"] == 0: relto = CameraName.rgb
  elif json["extrinsics"]["toCameraSocket"] == 1: relto = CameraName.left
  elif json["extrinsics"]["toCameraSocket"] == 2: relto = CameraName.right

  ext = Extrinsics(
    np.array(ext["rotationMatrix"]),
    np.array([
      ext["translation"]["x"],
      ext["translation"]["y"],
      ext["translation"]["z"],
    ]),
    relto,
    np.array([
      ext["specTranslation"]["x"],
      ext["specTranslation"]["y"],
      ext["specTranslation"]["z"],
    ]),
  )
  ret["extrinsics"] = ext
  return ret

def camera_info(device=None):
  if device is None:
    device = dai.Device()

  calibData = device.readCalibration()
  json = calibData.eepromToJson()

  info = {
    "camera": {
      "boardname": json["boardName"],
      "batchtime": json["batchTime"],
      "boardrev": json["boardRev"],
      "hardwareconf": json["hardwareConf"],
      "productname": json["productName"],
      "version": json["version"],
      "left_rect": np.array(json["stereoRectificationData"]["rectifiedRotationLeft"]),
      "right_rect": np.array(json["stereoRectificationData"]["rectifiedRotationRight"]),
    },
    "stereo": {
      "left": None,
      "right": None
    },
    "rgb": None
  }

  for data in json["cameraData"]:
    # pprint(data)
    if data[0] == 1:
      info["stereo"]["left"] = format_json(data[1])
    elif data[0] == 2:
      info["stereo"]["right"] = format_json(data[1])
    elif data[0] == 0:
      info["rgb"] = format_json(data[1])

  return info

  # info = {
  #   "boardname": calibData.getEepromData().boardName,
  #   "stereo": {
  #     "A": None,
  #     "B": None
  #   },
  #   "rgb": None
  # }

  # for cam in [dai.CameraBoardSocket.CAM_A,dai.CameraBoardSocket.CAM_B,dai.CameraBoardSocket.CAM_C]:
  #   M, width, height = calibData.getDefaultIntrinsics(cam)
  #   # M = calibData.getCameraIntrinsics(cam, width, height)
  #   fov = M, width, height = calibData.getDefaultIntrinsics(cam)
  #   distortions = np.array(calibData.getDistortionCoefficients(cam))
  

  # device = dai.Device()
  # calibData = device.readCalibration()
  # print(f"{calibData.getEepromData().boardName}")
  # # print(calibData)
  # print(dir(calibData))

  # print("-----------------")
  # pprint(calibData.eepromToJson())

  # print("-----------------")
  # getDefaultIntrinsics(calibData, dai.CameraBoardSocket.CAM_A)
  # # getIntrinsics(calibData, dai.CameraBoardSocket.CAM_A, 3840, 2160)
  # # getIntrinsics(calibData, dai.CameraBoardSocket.CAM_A, 4056, 3040)
  # getDistortion(calibData, dai.CameraBoardSocket.CAM_A)

  # print("-----------------")
  # getDefaultIntrinsics(calibData, dai.CameraBoardSocket.CAM_B)
  # # getIntrinsics(calibData, dai.CameraBoardSocket.CAM_B, 640, 400)
  # getDistortion(calibData, dai.CameraBoardSocket.CAM_B)

  # print("-----------------")
  # getDefaultIntrinsics(calibData, dai.CameraBoardSocket.CAM_C)
  # # getIntrinsics(calibData, dai.CameraBoardSocket.CAM_C, 640, 400)
  # getDistortion(calibData, dai.CameraBoardSocket.CAM_C)

  # # M_right = np.array(calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_C, 1280, 720))
  # # print("RIGHT Camera resized intrinsics... 1280 x 720")
  # # print(M_right)

  # # D_left = np.array(calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_B))
  # # print("LEFT Distortion Coefficients...")
  # # [print(name+": "+value) for (name, value) in zip(["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"],[str(data) for data in D_left])]

  # # D_right = np.array(calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_C))
  # # print("RIGHT Distortion Coefficients...")
  # # [print(name+": "+value) for (name, value) in zip(["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"],[str(data) for data in D_right])]

  # # print(f"RGB FOV {calibData.getFov(dai.CameraBoardSocket.CAM_A)}, Mono FOV {calibData.getFov(dai.CameraBoardSocket.CAM_B)}")

  # R1 = np.array(calibData.getStereoLeftRectificationRotation())
  # R2 = np.array(calibData.getStereoRightRectificationRotation())
  # M_right = np.array(calibData.getCameraIntrinsics(calibData.getStereoRightCameraId(), 1280, 720))

  # H_left = np.matmul(np.matmul(M_right, R1), np.linalg.inv(M_left))
  # print("LEFT Camera stereo rectification matrix...")
  # print(H_left)

  # H_right = np.matmul(np.matmul(M_right, R1), np.linalg.inv(M_right))
  # print("RIGHT Camera stereo rectification matrix...")
  # print(H_right)

  # lr_extrinsics = np.array(calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_C))
  # print("Transformation matrix of where left Camera is W.R.T right Camera's optical center")
  # print(lr_extrinsics)

  # l_rgb_extrinsics = np.array(calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_A))
  # print("Transformation matrix of where left Camera is W.R.T RGB Camera's optical center")
  # print(l_rgb_extrinsics)

  # # print(calibData.getCameraExtrinsics(dai.CameraBoardSocket.CAM_B))
  # # print(calibData.getCameraToImuExtrinsics(dai.CameraBoardSocket.CAM_B))
  # # print(calibData.getEepromData(dai.CameraBoardSocket.CAM_B))
  # # print(calibData.getFov(dai.CameraBoardSocket.CAM_B))

  # # D_left = np.array(calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_B))
  # # print("LEFT Distortion Coefficients...")
  # # [print(name+": "+value) for (name, value) in zip(["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"],[str(data) for data in D_left])]

  # # D_right = np.array(calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_C))
  # # print("RIGHT Distortion Coefficients...")
  # # [print(name+": "+value) for (name, value) in zip(["k1","k2","p1","p2","k3","k4","k5","k6","s1","s2","s3","s4","τx","τy"],[str(data) for data in D_right])]

  # # print("-----------------")
  # # intri = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_B, 640, 400)
  # # # fx = intri[0][0]
  # # # cx = intri[0][2]
  # # # fy = intri[1][1]
  # # # cy = intri[1][2]
  # # # print("left cam", fx ,fy, cx, cy)
  # # print(np.array(intri))

  # # intri = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_C, 640, 400)
  # # print(np.array(intri))
  # # # fx = intri[0][0]
  # # # cx = intri[0][2]
  # # # fy = intri[1][1]
  # # # cy = intri[1][2]
  # # # print("right cam", fx ,fy, cx, cy)

  # # # print(intri)
  # # # print(dir(intri))
  