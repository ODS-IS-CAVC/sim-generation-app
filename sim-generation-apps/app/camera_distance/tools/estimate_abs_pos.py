import math
from commons.math_util import get_angle_2d
from cvt_lat_long_cartesian import convert_cartesian_to_lat_long, cvt_world_to_plane_cartesian


def interpolate_abs_pos(frame: int, frame1: int, frame2: int, coord1: list, coord2: list, 
                        velocity1: float, velocity2: float, phi0_deg: float, lambda0_deg: float):
    """内挿法・外挿法で絶対座標と速度を計算する。
 
    Args:
        frame (int): 計算するフレーム
        frame1 (int): 参照する第一フレーム
        frame2 (int):  参照する第二フレーム
        coord1 (list): 参照する第一絶対座標
        coord2 (list): 参照する第二絶対座標
        velocity1 (float): 参照する第一速度
        velocity2 (float): 参照する第二速度
        phi0_deg (float): 平面直角座標系原点の緯度[度]
        lambda0_deg (float): 平面直角座標系原点の経度[度]
    """
    if frame1 < frame < frame2: # interpolate
        frame_ratio = (frame - frame1) / (frame2 - frame1)
        xw_est = coord1[0] + (coord2[0] - coord1[0]) * frame_ratio
        yw_est = coord1[1] + (coord2[1] - coord1[1]) * frame_ratio
        
        xp, yp = cvt_world_to_plane_cartesian(xw_est, yw_est)
        lat_est, lon_est = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)
        
        # vehicle velocity
        velocity_est = velocity2

        # vehicle direction (z-axis rotation angle)
        movement_dx = xw_est - coord1[0]
        movement_dy = yw_est - coord1[1]
        yaw = get_angle_2d(movement_dx, movement_dy)
        yaw_est = math.degrees(yaw)
        
    elif frame < frame1: # extrapolate before first frame
        frame_ratio = (frame1 - frame) / (frame2 - frame1)
        xw_est = coord1[0] - (coord2[0] - coord1[0]) * frame_ratio
        yw_est = coord1[1] - (coord2[1] - coord1[1]) * frame_ratio
        
        xp, yp = cvt_world_to_plane_cartesian(xw_est, yw_est)
        lat_est, lon_est = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)
        
        # vehicle velocity
        velocity_est = velocity1

        # vehicle direction (z-axis rotation angle)
        movement_dx = coord1[0] - xw_est
        movement_dy = coord1[1] - yw_est
        yaw = get_angle_2d(movement_dx, movement_dy)
        yaw_est = math.degrees(yaw)
        
    else: # extrapolate after last frame
        frame_ratio = (frame - frame2) / (frame2 - frame1)
        xw_est = coord2[0] + (coord2[0] - coord1[0]) * frame_ratio
        yw_est = coord2[1] + (coord2[1] - coord1[1]) * frame_ratio
        
        xp, yp = cvt_world_to_plane_cartesian(xw_est, yw_est)
        lat_est, lon_est = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)
        
        # vehicle velocity
        velocity_est = velocity2

        # vehicle direction (z-axis rotation angle)
        movement_dx = xw_est - coord2[0]
        movement_dy = yw_est - coord2[1]
        yaw = get_angle_2d(movement_dx, movement_dy)
        yaw_est = math.degrees(yaw)
        
    return [xw_est, yw_est], lat_est, lon_est, velocity_est, yaw_est