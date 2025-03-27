import os
import argparse
import json
import copy
import math
import sys

import pandas as pd
import numpy as np

from cvt_lat_long_cartesian import (
    convert_lat_long_to_cartesian,
    cvt_plane_cartesian_to_world,
    cvt_world_to_plane_cartesian,
    convert_cartesian_to_lat_long,
    calc_org_lat_long,
)
from commons.constants import *
from commons.math_util import unit_v, get_perp_vec, get_distance_2d, get_angle_2d

def estimate_abs_pos(frame, frame1, frame2, coord1, coord2, velocity1 = 0, velocity2 = 0):
    """内挿法・外挿法で絶対座標と速度を計算する。
 
    Args:
        frame (int): 計算するフレーム
        frame1 (int): 参照する第一フレーム
        frame2 (int):  参照する第二フレーム
        coord1 (list): 参照する第一絶対座標
        coord2 (list): 参照する第二絶対座標
        velocity1 (float): 参照する第一速度
        velocity2 (float): 参照する第二速度
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


def calc_detect_car_pos(owned_prev_abs_pos: list, owned_curr_abs_pos: list, dx: float, dy: float):
    """検出車の絶対座標を求める

    Args:
        owned_prev_abs_pos (list): 過去フレームのそれぞれ自車の平面座標 (世界座標系)
        owned_curr_abs_pos (list): 現フレームのそれぞれ自車の平面座標 (世界座標系)
        dx (float): 相対距離 (X-axis)
        dy (float): 相対距離 (Y-axis)

    Returns:
        list: 検出車の絶対座標
    """
    # 移動方向ベクトル
    curr_dir = (owned_curr_abs_pos[0] - owned_prev_abs_pos[0],
                owned_curr_abs_pos[1] - owned_prev_abs_pos[1])
    curr_dir = unit_v(curr_dir)

    # 自車の現在方向にdx dyの方向を計算
    dy_dir = curr_dir
    is_right_side = dx > 0
    dx_dir = get_perp_vec(dy_dir, is_right_side)

    # 検出車の絶対座標
    dy_world = [dy_dir[0] * dy, dy_dir[1] * dy]
    dx_world = [dx_dir[0] * abs(dx), dx_dir[1] * abs(dx)]
    xd_world = owned_curr_abs_pos[0] + dy_world[0] + dx_world[0]
    yd_world = owned_curr_abs_pos[1] + dy_world[1] + dx_world[1]

    return [xd_world, yd_world]


def str2second(time_s: str, fps: int, delimiter: str):
    tokens = time_s.split(delimiter)
    frames = int(tokens[-1])
    seconds = int(tokens[-2])
    time = seconds + frames / fps
    if len(tokens) >= 3:
        minutes = int(tokens[-3])
        time = (minutes * 60) + seconds
    if len(tokens) == 4:
        hours = tokens[-4]
        time += (hours * 3600)
    return time

def angle_between_vectors(vector1, vector2):
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    norm_vector1 = math.sqrt(sum(i**2 for i in vector1))
    norm_vector2 = math.sqrt(sum(i**2 for i in vector2))
    cos_theta = dot_product / (norm_vector1 * norm_vector2)
    cos_theta = max(-1, min(1, cos_theta))
    angle_rad = math.acos(cos_theta)
    angle_deg = round(math.degrees(angle_rad), 2)
    return angle_rad, angle_deg

def main():
    # 引数をパースする
    parser = argparse.ArgumentParser(description="対象の相対座標の計算")
    parser.add_argument(
        "--rel_coord_file",
        type=str,
        required=True,
        help="相対距離推定結果jsonファイルパス",
    )
    parser.add_argument(
        "--gps_coord_file",
        type=str,
        required=True,
        help="GPSデータファイルパス",
    )
    parser.add_argument(
        "--acc_data_file",
        type=str,
        required=False,
        help="加速度データcsvファイルパス",
    )
    parser.add_argument(
        "--output_gps_csv",
        action='store_true',
        help="補正後GPS座標のCSVファイルを作成",
    )
    parser.add_argument(
        "--epsg_code",
        type=str,
        required=False,
        default="auto",
        help="EPSGコード（6669~6687）",
    )
    parser.add_argument(
        "--fps",
        type=int,
        required=False,
        default=30,
        help="FPS",
    )

    # parse input arguments
    args = parser.parse_args()

    rel_coord_file = args.rel_coord_file
    assert isinstance(rel_coord_file, str)

    gps_coord_file = args.gps_coord_file
    assert isinstance(gps_coord_file, str)

    epsg_code = args.epsg_code
    assert isinstance(epsg_code, str)

    output_gps_csv = args.output_gps_csv
    assert isinstance(output_gps_csv, bool)

    fps = args.fps
    assert isinstance(fps, int)

    acc_data = None
    if args.acc_data_file:
        acc_data_file = args.acc_data_file
        col_names = ['frame', 'acc_x', 'acc_y', 'acc_z', 'velocity']
        acc_data = pd.read_csv(acc_data_file, header=None, names=col_names)
        acc_data['frame'] = acc_data['frame'].astype(np.int32)

    if (epsg_code != 'auto') and (epsg_code not in LAT_LONG_ORG.keys()):
        print("Warning: 「6669~6687」にある 「epsg_code」を指定ください。")
        return

    # read data files
    det_rel_coord_result = {}
    with open(rel_coord_file, mode='r', encoding='utf-8') as f:
        det_rel_coord_result = json.load(f)

    gps_data = pd.read_csv(gps_coord_file)
    gps_data_lat = gps_data['lat'].values
    gps_data_lon = gps_data['lon'].values
    gps_data_time = gps_data['time'].values
    gps_data_frame_idxes = gps_data['frame'].values
    
    # check abnormal gps data
    prev_idx = None
    prev_vector = None
    gps_data_valid = [] # OK, NG, -
    gps_data_valid.append("OK")
    for ii, frame in enumerate(gps_data_frame_idxes):
        if ii == 0:
            continue
        if prev_idx == None:
            p1 = [gps_data_lat[ii - 1], gps_data_lon[ii - 1]]
            p2 = p3 = [gps_data_lat[ii], gps_data_lon[ii]]
            p4 = [gps_data_lat[ii + 1], gps_data_lon[ii + 1]]
            vector1 = [p2[0] - p1[0], p2[1] - p1[1]]
            vector2 = [p4[0] - p3[0], p4[1] - p3[1]]
            angle_rad, angle_deg = angle_between_vectors(vector1, vector2)
            if angle_deg <= VECTORS_ANGLE_THD:
                gps_data_valid.append("OK")
                prev_idx = ii
                prev_vector = vector1
            else:
                gps_data_valid[-1] = "-"
                gps_data_valid.append("OK")
        else:
            p3 = [gps_data_lat[prev_idx], gps_data_lon[prev_idx]]
            p4 = [gps_data_lat[ii], gps_data_lon[ii]]
            vector1 = prev_vector
            vector2 = [p4[0] - p3[0], p4[1] - p3[1]]
            angle_rad, angle_deg = angle_between_vectors(vector1, vector2)
            if angle_deg <= VECTORS_ANGLE_THD:
                gps_data_valid.append("OK")
                prev_idx = ii
                prev_vector = vector2
            else:
                gps_data_valid.append("NG")
                
    # update gps data
    idx_rm = [i for i in range(len(gps_data_valid)) if gps_data_valid[i] == "NG"]
    gps_data_lat = np.delete(gps_data_lat, idx_rm)
    gps_data_lon= np.delete(gps_data_lon, idx_rm)
    gps_data_time = np.delete(gps_data_time, idx_rm)
    gps_data_frame_idxes = np.delete(gps_data_frame_idxes, idx_rm)
    
    # save to csv
    if output_gps_csv:
        updated_gps_data = pd.DataFrame({"time": gps_data_time,
                                        "lat": gps_data_lat,
                                        "lon": gps_data_lon,
                                        "frame": gps_data_frame_idxes})
        
        gps_coord_file_name = os.path.basename(gps_coord_file)
        file_name, file_ext = os.path.splitext(gps_coord_file_name)
        output_csv_fn = f"{file_name}{GPS_CSV_SUFFIX}{file_ext}"
        output_csv_file_path = os.path.join(os.path.dirname(rel_coord_file), output_csv_fn)
        updated_gps_data.to_csv(output_csv_file_path, sep=',', encoding='utf-8', index=False, header=True)

    # calculate original lat-lon
    global phi0_deg
    global lambda0_deg
    phi0_deg = 0        # 平面直角座標系原点の緯度[度]
    lambda0_deg = 0     # 平面直角座標系原点の経度[度]
    gps_data_tmp = np.hstack((gps_data_lat.reshape((-1, 1)), gps_data_lon.reshape((-1, 1))))
    phi0_deg, lambda0_deg, epsg_code = calc_org_lat_long(epsg_code=epsg_code, gps_data=gps_data_tmp)

    print(f'EPSGコード: {epsg_code}. Name: {LAT_LONG_ORG[epsg_code]["name"]}')
    print(f'平面直角座標系原点の緯度[度]: {LAT_LONG_ORG[epsg_code]["lat"]}')
    print(f'平面直角座標系原点の経度[度]: {LAT_LONG_ORG[epsg_code]["lon"]}')

    # execute
    # get same frame index of gps data and detected result
    detected_frame_idxes = [item['frame'] for item in det_rel_coord_result['results']]
    target_frame_idxes = list(set(gps_data_frame_idxes).intersection(detected_frame_idxes))
    target_frame_idxes = sorted(target_frame_idxes)
    target_idxes = [(detected_idx, detected_frame_idx) for detected_idx, detected_frame_idx in enumerate(
        detected_frame_idxes) if detected_frame_idx in target_frame_idxes]
    detected_idxes = [x[0] for x in target_idxes]
    if len(target_idxes) < 2:
        print("「gps_coord_file」と「rel_coord_file」の一致するフレーム数が計算するのに不十分である。")
        sys.exit()
    if args.acc_data_file:
        acc_frame_idxs = acc_data['frame']

    owned_prev_abs_pos = []
    owned_curr_abs_pos = []
    first_owned_prev_abs_pos = []
    first_owned_curr_abs_pos = []
    first_result = []

    # output result
    output_results = copy.deepcopy(det_rel_coord_result['results'])

    # CALCULATE OWN CAR ABS POS
    for ii, (detected_idx, detected_frame_idx) in enumerate(target_idxes):
        result = output_results[detected_idx]

        # convert lat, lon to cartesian coord
        gps_row_idx = np.where(gps_data_frame_idxes == detected_frame_idx)[0][0]
        lat, lon = gps_data_lat[gps_row_idx], gps_data_lon[gps_row_idx]
        owned_cartesian_coord = convert_lat_long_to_cartesian(lat, lon, phi0_deg, lambda0_deg)
        owned_abs_coord = cvt_plane_cartesian_to_world(owned_cartesian_coord[0], owned_cartesian_coord[1])
        result['self']['world_coordinate'] = owned_abs_coord
        result['self']['latitude'] = lat
        result['self']['longitude'] = lon
        result['self']['acc_x'] = None
        result['self']['acc_y'] = None
        result['self']['acc_z'] = None

        # first frame
        if ii == 0:
            owned_prev_abs_pos = result['self']['world_coordinate']
            first_result = result

        # current frame
        if ii >= 1:
            owned_curr_abs_pos = result['self']['world_coordinate']
            prev_detected_idx, prev_detected_frame_idx = target_idxes[ii-1]
            owned_prev_abs_pos_tmp = output_results[prev_detected_idx]['self']['world_coordinate']
            prev_gps_row_idx = np.where(gps_data_frame_idxes == prev_detected_frame_idx)[0][0]

            # owned vehicle velocity
            movement_dist = get_distance_2d(owned_prev_abs_pos_tmp, owned_curr_abs_pos)
            time_s = str2second(gps_data_time[prev_gps_row_idx], fps=fps, delimiter=':')
            time_e = str2second(gps_data_time[gps_row_idx], fps=fps, delimiter=':')
            movement_time = time_e - time_s
            movement_velocity = movement_dist / movement_time
            # m/s => km/h
            result['self']['velocity'] = 3.6 * movement_velocity

            # owned vehicle direction (z-axis rotation angle)
            movement_dx = owned_curr_abs_pos[0] - owned_prev_abs_pos_tmp[0]
            movement_dy = owned_curr_abs_pos[1] - owned_prev_abs_pos_tmp[1]
            yaw = get_angle_2d(movement_dx, movement_dy)
            result['self']['yaw'] = math.degrees(yaw)

        # assign current to previous
        if ii > 1:
            owned_prev_abs_pos = owned_curr_abs_pos

        # acceleration information
        if acc_data is None:
            continue

        # nearest previous frame that contains acceleration data
        pre_idxs = np.where(acc_frame_idxs <= detected_frame_idx)
        nearest_pre_idx = pre_idxs[0][-1] if len(pre_idxs[0]) > 0 else None
        
        if nearest_pre_idx:
            nearest_pre_frame_idx = acc_frame_idxs[nearest_pre_idx]
            frame_diff_num = detected_frame_idx - nearest_pre_frame_idx

            if frame_diff_num/fps >= MAX_ACC_TIME_THD:
                continue

            result['self']['acc_x'] = acc_data['acc_x'][nearest_pre_idx]
            result['self']['acc_y'] = acc_data['acc_y'][nearest_pre_idx]
            result['self']['acc_z'] = acc_data['acc_z'][nearest_pre_idx]

    # save velocity/yaw at second frame to first frame
    second_detected_idx, second_detected_frame_idx = target_idxes[1]
    second_result = output_results[second_detected_idx]
    first_result['self']['velocity'] = second_result['self']['velocity']
    first_result['self']['yaw'] = second_result['self']['yaw']
    
    # INTERPOLATE/EXTRAPOLATE OWN CAR ABS POS
    for ii, result in enumerate(output_results):
        if ii not in detected_idxes:
            if ii < detected_idxes[0]:
                idx1 = detected_idxes[0]
                idx2 = detected_idxes[1]
            elif ii > detected_idxes[-1]:
                idx1 = detected_idxes[-2]
                idx2 = detected_idxes[-1]
            else:
                idx1 = sorted([x for x in detected_idxes if x < ii], reverse=True)[0]
                idx2 = sorted([x for x in detected_idxes if x > ii])[0]
                
            xy_est, lat_est, lon_est, velocity_est, yaw_est = estimate_abs_pos(result["frame"],
                                                                        output_results[idx1]["frame"], 
                                                                        output_results[idx2]["frame"],
                                                                        output_results[idx1]["self"]["world_coordinate"],
                                                                        output_results[idx2]["self"]["world_coordinate"],
                                                                        output_results[idx1]["self"]["velocity"],
                                                                        output_results[idx2]["self"]["velocity"])
            est_own_car = {
                "world_coordinate": xy_est,
                "latitude": lat_est,
                "longitude": lon_est,
                "velocity": velocity_est,
                "yaw": yaw_est
            }
            result["self"] |= est_own_car

    # CALCULATE DETECTIONS ABS POS
    owned_prev_abs_pos = []
    owned_curr_abs_pos = []
    
    for ii, result in enumerate(output_results):
        owned_curr_abs_pos = result['self']['world_coordinate']
        if ii == 0:
            first_owned_prev_abs_pos = result['self']['world_coordinate']
            first_result = result
        if ii == 1:
            first_owned_curr_abs_pos = owned_curr_abs_pos
        if ii > 0:
            for detection in result['detections']:
                obj_id = detection['obj_id']
                dx, dy, d = detection['distance']
                detect_abs_pos = calc_detect_car_pos(owned_prev_abs_pos, owned_curr_abs_pos, dx, dy)
                detection['world_coordinate'] = detect_abs_pos

                xw, yw = detect_abs_pos[0], detect_abs_pos[1]
                xp, yp = cvt_world_to_plane_cartesian(xw, yw)
                detected_lat, detected_lon = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)
                detection['latitude'] = detected_lat
                detection['longitude'] = detected_lon
            
        # set prev abs pos
        owned_prev_abs_pos = result['self']['world_coordinate']
    
    # calculate detections abs pos in first frame
    for ii, detection in enumerate(first_result['detections']):
        obj_id = detection['obj_id']
        dx, dy, d = detection['distance']
        detect_abs_pos = calc_detect_car_pos(first_owned_prev_abs_pos, first_owned_curr_abs_pos, dx, dy)
        detection['world_coordinate'] = detect_abs_pos

        xw, yw = detect_abs_pos[0], detect_abs_pos[1]
        xp, yp = cvt_world_to_plane_cartesian(xw, yw)
        detected_lat, detected_lon = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)
        detection['latitude'] = detected_lat
        detection['longitude'] = detected_lon
    
    # CALCULATE DETECTIONS' VELOCITY AND YAW
    # INTERPOLATE DETECTIONS' ABS POS
    prev_detection_info = {}
    saved_detections = {}
    
    for ii, result in enumerate(output_results):
        for jj, detection in enumerate(result['detections']):
            obj_id = str(detection['obj_id'])
            
            # save detection's data for extrapolate
            if obj_id in saved_detections.keys():
                if saved_detections[obj_id]["second"] == None: # second frame data
                    saved_detections[obj_id]["second"] = detection
                    saved_detections[obj_id]["second_to_last"] = saved_detections[obj_id]["first"]
                    saved_detections[obj_id]["last"] = detection
                    saved_detections[obj_id]["frames"].extend([result["frame"], saved_detections[obj_id]["frames"][0], result["frame"]])
                else:
                    saved_detections[obj_id]["second_to_last"] = saved_detections[obj_id]["last"]
                    saved_detections[obj_id]["last"] = detection
                    saved_detections[obj_id]["frames"][2] = saved_detections[obj_id]["frames"][3]
                    saved_detections[obj_id]["frames"][3] = result["frame"]

            # detection's first frame
            if (obj_id not in prev_detection_info.keys()):
                prev_detection_info[obj_id] = {"index" : ii}
                prev_detection_info[obj_id].update({"world_coordinate" : detection['world_coordinate']})
                prev_detection_info[obj_id].update({"velocity" : 0})
                prev_detection_info[obj_id].update({"yaw" : 0})
                prev_detection_info[obj_id].update({"first": detection})
                
                # save detection's first frame for extrapolate
                saved_detections[obj_id] = {
                    "first": detection,
                    "second": None,
                    "second_to_last": None,
                    "last": None,
                    "frames": [result["frame"]]
                }
                
            else:
                detection_curr_abs_pos = detection['world_coordinate']
                prev_detected_idx = prev_detection_info[obj_id]["index"]
                prev_detected_frame_idx = detected_frame_idxes[prev_detected_idx]
                detection_prev_abs_pos_tmp = prev_detection_info[obj_id]["world_coordinate"]

                # vehicle velocity
                movement_dist = get_distance_2d(detection_prev_abs_pos_tmp, detection_curr_abs_pos)
                movement_time = (result["frame"] - prev_detected_frame_idx) / fps
                movement_velocity = movement_dist / movement_time
                # m/s => km/h
                detection['velocity'] = 3.6 * movement_velocity

                # vehicle direction (z-axis rotation angle)
                movement_dx = detection_curr_abs_pos[0] - detection_prev_abs_pos_tmp[0]
                movement_dy = detection_curr_abs_pos[1] - detection_prev_abs_pos_tmp[1]
                yaw = get_angle_2d(movement_dx, movement_dy)
                detection['yaw'] = math.degrees(yaw)
                
                # copy data to detection's first frame
                if prev_detection_info[obj_id]["first"] != None:
                    first_detection = prev_detection_info[obj_id]["first"]
                    first_detection['velocity'] = detection['velocity']
                    first_detection['yaw'] = detection['yaw']
                    prev_detection_info[obj_id]["first"] = None
                    
                # interpolate detections' abs pos 
                for i in range(prev_detected_idx + 1, ii):
                    detections = output_results[i]["detections"]
                    est_detected_frame_idx = detected_frame_idxes[i]
                    
                    xy_est, lat_est, lon_est, velocity_est, yaw_est = estimate_abs_pos(est_detected_frame_idx, 
                                                                           prev_detected_frame_idx, 
                                                                           result["frame"],
                                                                           detection_prev_abs_pos_tmp,
                                                                           detection_curr_abs_pos,
                                                                           velocity2=detection["velocity"])
                
                    est_detection = {
                        "obj_id": int(obj_id),
                        "world_coordinate": xy_est,
                        "latitude": lat_est,
                        "longitude": lon_est,
                        "velocity": velocity_est,
                        "yaw": yaw_est
                    }
                    detections.append(est_detection)
                
                # update to prev detection
                prev_detection_info[obj_id]["index"] = ii
                prev_detection_info[obj_id]["world_coordinate"] = detection_curr_abs_pos
                prev_detection_info[obj_id]["velocity"] = detection['velocity']
                prev_detection_info[obj_id]["yaw"] = detection['yaw']
    
    # EXTRAPOLATE DETECTIONS' ABS POS
    saved_detections = {k: v for k, v in saved_detections.items() if v["second"] != None}
    for ii, result in enumerate(output_results):
        for obj_id in saved_detections.keys():
            if result["frame"] < saved_detections[obj_id]["frames"][0]:
                xy_est, lat_est, lon_est, velocity_est, yaw_est = estimate_abs_pos(result["frame"], 
                                                                           saved_detections[obj_id]["frames"][0], 
                                                                           saved_detections[obj_id]["frames"][1],
                                                                           saved_detections[obj_id]["first"]["world_coordinate"],
                                                                           saved_detections[obj_id]["second"]["world_coordinate"],
                                                                           saved_detections[obj_id]["first"]["velocity"],
                                                                           saved_detections[obj_id]["second"]["velocity"])
                
                est_detection = {
                    "obj_id": int(obj_id),
                    "world_coordinate": xy_est,
                    "latitude": lat_est,
                    "longitude": lon_est,
                    "velocity": velocity_est,
                    "yaw": yaw_est
                }
                result["detections"].append(est_detection)
            elif result["frame"] > saved_detections[obj_id]["frames"][3]:
                xy_est, lat_est, lon_est, velocity_est, yaw_est = estimate_abs_pos(result["frame"], 
                                                                           saved_detections[obj_id]["frames"][2], 
                                                                           saved_detections[obj_id]["frames"][3],
                                                                           saved_detections[obj_id]["second_to_last"]["world_coordinate"],
                                                                           saved_detections[obj_id]["last"]["world_coordinate"],
                                                                           saved_detections[obj_id]["second_to_last"]["velocity"],
                                                                           saved_detections[obj_id]["last"]["velocity"])
                
                est_detection = {
                    "obj_id": int(obj_id),
                    "world_coordinate": xy_est,
                    "latitude": lat_est,
                    "longitude": lon_est,
                    "velocity": velocity_est,
                    "yaw": yaw_est
                }
                result["detections"].append(est_detection)
            
    # output result to json
    output_dict = copy.deepcopy(det_rel_coord_result)
    output_dict['EPSG'] = epsg_code
    output_dict['results'] = output_results

    output_abs_coord_file_path = os.path.join(os.path.dirname(rel_coord_file), ABS_COORD_JSON_FILE_NAME)

    with open(output_abs_coord_file_path, mode='w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
