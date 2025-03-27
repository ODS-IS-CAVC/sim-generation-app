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
from tools.estimate_abs_pos import interpolate_abs_pos


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
        "--car_abs_coord_file_path",
        type=str,
        required=True,
        help="車両座標のjsonファイルパス",
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

    car_abs_coord_file_path = args.car_abs_coord_file_path
    assert isinstance(car_abs_coord_file_path, str)

    epsg_code = args.epsg_code
    assert isinstance(epsg_code, str)

    fps = args.fps
    assert isinstance(fps, int)

    # read data files
    det_rel_coord_result = {}
    with open(car_abs_coord_file_path, mode='r', encoding='utf-8') as f:
        det_rel_coord_result = json.load(f)

    if epsg_code == 'auto':
        if 'EPSG' in det_rel_coord_result.keys():
            epsg_code = det_rel_coord_result["EPSG"]
        else:
            print("Error:「epsg_code」を指定ください。")
            sys.exit()
    elif (epsg_code != 'auto') and (epsg_code not in LAT_LONG_ORG.keys()):
        print("Warning: 「6669~6687」にある 「epsg_code」を指定ください。")
        return
    
    # calculate original lat-lon
    global phi0_deg
    global lambda0_deg
    phi0_deg = 0        # 平面直角座標系原点の緯度[度]
    lambda0_deg = 0     # 平面直角座標系原点の経度[度]
    phi0_deg, lambda0_deg, epsg_code = calc_org_lat_long(epsg_code=epsg_code)

    print(f'EPSGコード: {epsg_code}. Name: {LAT_LONG_ORG[epsg_code]["name"]}')
    print(f'平面直角座標系原点の緯度[度]: {LAT_LONG_ORG[epsg_code]["lat"]}')
    print(f'平面直角座標系原点の経度[度]: {LAT_LONG_ORG[epsg_code]["lon"]}')

    # execute
    # get same frame index of gps data and detected result
    detected_frame_idxes = [item['frame'] for item in det_rel_coord_result['results']]

    owned_prev_abs_pos = []
    owned_curr_abs_pos = []
    first_owned_prev_abs_pos = []
    first_owned_curr_abs_pos = []
    first_result = []

    # output result
    output_results = copy.deepcopy(det_rel_coord_result['results'])

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
                detection['interpolation_type'] = None
            
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
        detection['interpolation_type'] = None
    
    # CHECK ABNORMAL ABS POS
    # save all indexes of detections
    detection_idxes = {} # {obj_id: [[idx of frame in results, idx of detection in frame], ...], ...}
    for ii, result in enumerate(output_results):
        for jj, detection in enumerate(result['detections']):
            obj_id = detection['obj_id']
            if obj_id not in detection_idxes:
                detection_idxes |= {obj_id: [[ii, jj]]}
            else:
                detection_idxes[obj_id].append([ii, jj])

    for obj_id in detection_idxes.keys():
        if len(detection_idxes[obj_id]) == 1:
            continue
        valid_idxes = []
        detection0 = output_results[detection_idxes[obj_id][0][0]]["detections"][detection_idxes[obj_id][0][1]]
        detection30 = None
        # find frame >=30
        for jj in range(1, len(detection_idxes[obj_id])):
            if output_results[detection_idxes[obj_id][jj][0]]["frame"] >= output_results[detection_idxes[obj_id][0][0]]["frame"] + 30:
                detection30 = output_results[detection_idxes[obj_id][jj][0]]["detections"][detection_idxes[obj_id][jj][1]]
                break
        
        for ii, idxes in enumerate(detection_idxes[obj_id]):
            if not valid_idxes: # frame 0
                valid_idxes.append(idxes)
                continue
            elif output_results[idxes[0]]["frame"] - output_results[detection_idxes[obj_id][ii-1][0]]["frame"] > 15:
                    valid_idxes.append(idxes)
            else:
                if len(valid_idxes) == 1: # frame 1
                    if not detection30:
                        valid_idxes.append(idxes)
                    else:
                        detection1 = output_results[detection_idxes[obj_id][ii][0]]["detections"][detection_idxes[obj_id][ii][1]]
                        p1 = p3 = [detection0["latitude"], detection0["longitude"]]
                        p2 = [detection1["latitude"], detection1["longitude"]]
                        p4 = [detection30["latitude"], detection30["longitude"]]
                        vector1 = [p2[0] - p1[0], p2[1] - p1[1]]
                        vector2 = [p4[0] - p3[0], p4[1] - p3[1]]
                        
                        angle_rad, angle_deg = angle_between_vectors(vector1, vector2)
                        if angle_deg <= VECTORS_ANGLE_THD:
                            valid_idxes.append(idxes)
                        else:
                            continue
                else:
                    detection = output_results[detection_idxes[obj_id][ii][0]]["detections"][detection_idxes[obj_id][ii][1]]
                    detection_1 = output_results[valid_idxes[-1][0]]["detections"][valid_idxes[-1][1]]
                    detection_2 = output_results[valid_idxes[-2][0]]["detections"][valid_idxes[-2][1]]
                    p1 = [detection_2["latitude"], detection_2["longitude"]]
                    p2 = p3 = [detection_1["latitude"], detection_1["longitude"]]
                    p4 = [detection["latitude"], detection["longitude"]]
                    vector1 = [p2[0] - p1[0], p2[1] - p1[1]]
                    vector2 = [p4[0] - p3[0], p4[1] - p3[1]]
                    
                    angle_rad, angle_deg = angle_between_vectors(vector1, vector2)
                    if angle_deg <= VECTORS_ANGLE_THD:
                        valid_idxes.append(idxes)
                    else:
                        continue
        detection_idxes[obj_id] = valid_idxes
    
    detection_frame_idxes = {k: [idx[0] for idx in v] for k,v in detection_idxes.items()}
    for ii, result in enumerate(output_results):
        result["detections"] = [detection for detection in result["detections"] if ii in detection_frame_idxes[detection["obj_id"]]]

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
                    
                    xy_est, lat_est, lon_est, velocity_est, yaw_est = interpolate_abs_pos(est_detected_frame_idx, 
                                                                           prev_detected_frame_idx, 
                                                                           result["frame"],
                                                                           detection_prev_abs_pos_tmp,
                                                                           detection_curr_abs_pos,
                                                                           0,
                                                                           detection["velocity"],
                                                                           phi0_deg, lambda0_deg)
                
                    est_detection = {
                        "obj_id": int(obj_id),
                        "world_coordinate": xy_est,
                        "latitude": lat_est,
                        "longitude": lon_est,
                        "velocity": velocity_est,
                        "yaw": yaw_est,
                        "interpolation_type": "onScreen"
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
                xy_est, lat_est, lon_est, velocity_est, yaw_est = interpolate_abs_pos(result["frame"], 
                                                                           saved_detections[obj_id]["frames"][0], 
                                                                           saved_detections[obj_id]["frames"][1],
                                                                           saved_detections[obj_id]["first"]["world_coordinate"],
                                                                           saved_detections[obj_id]["second"]["world_coordinate"],
                                                                           saved_detections[obj_id]["first"]["velocity"],
                                                                           saved_detections[obj_id]["second"]["velocity"],
                                                                           phi0_deg, lambda0_deg)
                
                est_detection = {
                    "obj_id": int(obj_id),
                    "world_coordinate": xy_est,
                    "latitude": lat_est,
                    "longitude": lon_est,
                    "velocity": velocity_est,
                    "yaw": yaw_est,
                    "interpolation_type": "beforeIn"
                }
                result["detections"].append(est_detection)
            elif result["frame"] > saved_detections[obj_id]["frames"][3]:
                xy_est, lat_est, lon_est, velocity_est, yaw_est = interpolate_abs_pos(result["frame"], 
                                                                           saved_detections[obj_id]["frames"][2], 
                                                                           saved_detections[obj_id]["frames"][3],
                                                                           saved_detections[obj_id]["second_to_last"]["world_coordinate"],
                                                                           saved_detections[obj_id]["last"]["world_coordinate"],
                                                                           saved_detections[obj_id]["second_to_last"]["velocity"],
                                                                           saved_detections[obj_id]["last"]["velocity"],
                                                                           phi0_deg, lambda0_deg)
                
                est_detection = {
                    "obj_id": int(obj_id),
                    "world_coordinate": xy_est,
                    "latitude": lat_est,
                    "longitude": lon_est,
                    "velocity": velocity_est,
                    "yaw": yaw_est,
                    "interpolation_type": "afterOut"
                }
                result["detections"].append(est_detection)
            
    # output result to json
    output_dict = copy.deepcopy(det_rel_coord_result)
    output_dict['EPSG'] = epsg_code
    output_dict['results'] = output_results

    output_abs_coord_file_path = os.path.join(os.path.dirname(car_abs_coord_file_path), ABS_COORD_JSON_FILE_NAME)

    with open(output_abs_coord_file_path, mode='w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
