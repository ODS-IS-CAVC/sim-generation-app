import datetime
import os
import shutil
import sys
import argparse
import json
import copy
import math
import time

import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString
from shapely import line_interpolate_point, line_locate_point, remove_repeated_points

from commons import image_util
from commons.constants import *
from tools.coordinate_converter import get_converted_coordinates_lane_coord
from tools.visualize_absolute_coord import gen_batch_abs_coord_img
from cvt_lat_long_cartesian import (
    convert_lat_long_to_cartesian,
    cvt_plane_cartesian_to_world,
    calc_org_lat_long
)


def correct_car_abs_coord(road_linestrings: list, car_coordinate: list):
    """車両座標と最も近いレーン座標を求める

    Args:
        road_linestrings (list): レーン座標
        car_coordinate (list): 車両座標
    """
    # find x, y
    car_point = Point(car_coordinate[0], car_coordinate[1])
    min_distance = float("inf")
    for road in road_linestrings:
        line = road["line"]
        distance = car_point.distance(line)
        if distance < min_distance:
            min_distance = distance
            dist_online = line_locate_point(line, car_point)
            point = line_interpolate_point(line, dist_online)
            corrected_car_coordinates = [point.x, point.y, point.z]
            road_id = road["road"]
            lane_id = road["lane"]

    return corrected_car_coordinates, road_id, lane_id


def filter_road_info(road_info, road_targets):
    filtered_roads = []
    for road in road_info:
        if road["id"] not in road_targets:
            continue
        new_road = {key: road[key] for key in road.keys() if key != "lanes"}
        new_road["lanes"] = []
        for lane in road["lanes"]:
            if lane["lane_id"] in road_targets[road["id"]]:
                new_road["lanes"].append(lane)
            
        filtered_roads.append(new_road)
    
    return filtered_roads

def cvt_road_data_to_linestring(road_coordinates):
    road_linestrings = []
    for road in road_coordinates:
        lane_coordinates = road["lanes"]
        for lane in lane_coordinates:
            line = remove_repeated_points(LineString(lane["coordinate"]))
            road_linestrings.append({
                "road": road["id"],
                "lane": lane["lane_id"],
                "line": line
            })
    return road_linestrings


def main():
    parser = argparse.ArgumentParser(
        description="レーンのGPS座標から車の位置を求める, \
            GPS座標と最も近いレーン上の点を補正後の車両座標とする"
    )
    parser.add_argument(
        "--lane_coord_file_path",
        type=str,
        required=True,
        help="レーン座標のjsonファイルパス （タイプ：string）",
    )
    parser.add_argument(
        "--car_abs_coord_file_path",
        type=str,
        required=True,
        help="車両座標のjsonファイルパス（タイプ：string）",
    )
    parser.add_argument(
        "--road_correct_targets_file_path",
        type=str,
        required=False,
        help="補正先道路のjsonファイルパス（タイプ：string）",
    )
    parser.add_argument(
        "--target_option",
        type=str,
        choices=["beforeIn", "onScreen", "afterOut"],
        required=False,
        help='interpolation_typeの他車を選択することで、["beforeIn", "onScreen", "afterOut"]を修正する。または指定しないことで全てを修正する。',
    )
    parser.add_argument(
        "--no_overwrite",
        action="store_true",
        help="車両座標標のjsonファイルを上書きしない",
    )

    args = parser.parse_args()

    lane_coord_file_path = args.lane_coord_file_path
    car_abs_coord_file_path = args.car_abs_coord_file_path
    road_correct_targets_file_path = args.road_correct_targets_file_path
    target_option = args.target_option
    no_overwrite = args.no_overwrite

    using_road_correct_targets = (road_correct_targets_file_path is not None)
    
    # Read input files
    all_road_data = get_converted_coordinates_lane_coord(lane_coord_file_path)

    if using_road_correct_targets:
        road_correct_targets = {}
        # read specified road correct target (.json file)
        with open(road_correct_targets_file_path, "r", errors="ignore") as f:
            road_correct_targets = json.load(f)

        # convert road correct targets
        road_targets = {
            "detections": {}
        }
                    
        if "detections" in road_correct_targets:
            for detection_target in road_correct_targets["detections"]:
                obj_id = detection_target["id"]
                targets = detection_target["targets"]
                road_targets["detections"][obj_id] = {}

                for target_ in targets:
                    road_id = target_["road"]
                    lane_id = target_["lane"]
                    if (road_id not in road_targets["detections"][obj_id]):
                        road_targets["detections"][obj_id][road_id] = set()
                    road_targets["detections"][obj_id][road_id].add(lane_id)
    
    # read detected car absolute coords (.json file)
    with open(car_abs_coord_file_path, "r", errors="ignore") as f:
        detection_abs_coords = json.load(f)
    detection_results = detection_abs_coords["results"]
    
    if detection_abs_coords["EPSG"] != all_road_data["EPSG"]:
        print("「lane_coord_file_path」 と「detection_abs_coord_file_path」のEPSGコードが一致していない")
        sys.exit()
    
    # Correct self coord & detection coords
    lat0_deg, lon0_deg, epsg_code = calc_org_lat_long(epsg_code=detection_abs_coords["EPSG"])

    output_dict = copy.deepcopy(detection_abs_coords)
    output_results = output_dict["results"]
    detections_targets = {}
    
    if target_option == "beforeIn":
        if not using_road_correct_targets:
            road_targets = {
                "detections": {}
            }
        
        beforeIn_obj = {}
        for ii, result in enumerate(detection_results):
            for jj, detection in enumerate(result["detections"]):
                if detection["interpolation_type"] == "beforeIn" and detection["obj_id"] not in beforeIn_obj.keys():
                    beforeIn_obj |= {
                        detection["obj_id"]: None
                    }
                elif detection["interpolation_type"] != "beforeIn" \
                    and detection["obj_id"] in beforeIn_obj.keys() \
                    and beforeIn_obj[detection["obj_id"]] == None:
                    # correct frame in
                    detection_road_data = all_road_data["roads"]
                    obj_id = detection["obj_id"]
                    if using_road_correct_targets and road_targets["detections"]:
                        detection_road_data = filter_road_info(all_road_data["roads"], road_targets["detections"][obj_id])
                    detection_road_linestrings = cvt_road_data_to_linestring(detection_road_data)

                    detection_coord = [detection["latitude"], detection["longitude"], 0]
                    corrected_detection_coord, corrected_road_id, corrected_lane_id = correct_car_abs_coord(
                        detection_road_linestrings, detection_coord)
                    
                    beforeIn_obj[detection["obj_id"]] = {
                        corrected_road_id: {corrected_lane_id}
                    }
                    
        road_targets["detections"] = beforeIn_obj
    
    detection_road_linestrings = {}
    for ii, result in enumerate(detection_results):
        for jj, detection in enumerate(result["detections"]):
            # correct all detection coords
            detection_road_data = all_road_data["roads"]
            obj_id = detection["obj_id"]

            if obj_id not in detection_road_linestrings:
                if (using_road_correct_targets or (target_option == "beforeIn" and detection["interpolation_type"] == "beforeIn")) \
                    and road_targets["detections"] and obj_id in road_targets["detections"]:
                    detection_road_data = filter_road_info(all_road_data["roads"], road_targets["detections"][obj_id])
                road_linestrings = cvt_road_data_to_linestring(detection_road_data)
                detection_road_linestrings |= {
                    obj_id: road_linestrings
                }
            
            detection_coord = [detection["latitude"], detection["longitude"], 0]
            corrected_detection_coord, corrected_road_id, corrected_lane_id = correct_car_abs_coord(
                detection_road_linestrings[obj_id], detection_coord)
            
            # update x,y,z of target detections
            if target_option == None or target_option == detection["interpolation_type"]:
                output_results[ii]["detections"][jj]["latitude"] = corrected_detection_coord[0]
                output_results[ii]["detections"][jj]["longitude"] = corrected_detection_coord[1]
                detection_cartesian_coord = convert_lat_long_to_cartesian(
                    corrected_detection_coord[0], corrected_detection_coord[1], lat0_deg, lon0_deg)
                detection_abs_coord = cvt_plane_cartesian_to_world(detection_cartesian_coord[0], detection_cartesian_coord[1])
                detection_abs_coord.append(corrected_detection_coord[2])
                output_results[ii]["detections"][jj]["world_coordinate"] = detection_abs_coord
                output_results[ii]["detections"][jj]["road_correction"] = {
                    "road" : corrected_road_id,
                    "lane" : corrected_lane_id
                }

                target_ = output_results[ii]["detections"][jj]["road_correction"]
                
                if obj_id not in detections_targets.keys():
                    detections_targets[obj_id] = [target_]
                elif target_ not in detections_targets[obj_id]:
                    detections_targets[obj_id].append(target_)
            else: # only update z if not target detections
                detection_abs_coord = output_results[ii]["detections"][jj]["world_coordinate"]
                if len(detection_abs_coord) < 3:
                    detection_abs_coord.append(corrected_detection_coord[2])
                else:
                    detection_abs_coord[2] = corrected_detection_coord[2]

    # save corrected abs coord (.json file)
    abs_coord_file_name = os.path.basename(car_abs_coord_file_path)
    file_name, file_ext = os.path.splitext(abs_coord_file_name)
    if no_overwrite:
        output_fn = f"{file_name}{ABS_COORD_CORRECTED_JSON_SUFFIX}{file_ext}"
    else:
        output_fn = f"{file_name}{file_ext}"
    
    output_path = os.path.dirname(car_abs_coord_file_path)
    output_abs_coord_file_path = os.path.join(output_path, output_fn)

    with open(output_abs_coord_file_path, mode='w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)

    # save road correct target (.json file)
    json_file_name = os.path.join(output_path, ROAD_CORRECT_TARGETS_FILE_NAME)
    if os.path.exists(json_file_name):
        with open(json_file_name, "r", errors="ignore") as f:
            road_correct_targets = json.load(f)
    else:
        road_correct_targets = {}
        
    road_correct_targets["detections"] = []
    for obj_id, detections_target in detections_targets.items():
        road_correct_targets["detections"].append({
            "id": obj_id,
            "targets": detections_target
        })
    with open(json_file_name, "w", encoding="utf-8") as f:
        json.dump(road_correct_targets, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
