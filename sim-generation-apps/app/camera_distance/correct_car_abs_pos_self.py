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
from tools.estimate_abs_pos import interpolate_abs_pos
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
        "--no_overwrite",
        action="store_true",
        help="車両座標標のjsonファイルを上書きしない",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="修正後の自車座標の可視化画像を出力する",
    )

    args = parser.parse_args()

    lane_coord_file_path = args.lane_coord_file_path
    car_abs_coord_file_path = args.car_abs_coord_file_path
    road_correct_targets_file_path = args.road_correct_targets_file_path
    no_overwrite = args.no_overwrite
    visualize = args.visualize

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
            "self": {}
        }

        if "self" in road_correct_targets:
            for target_ in road_correct_targets["self"]["targets"]:
                road_id = target_["road"]
                lane_id = target_["lane"]
                if (road_id not in road_targets["self"]):
                    road_targets["self"][road_id] = set()
                road_targets["self"][road_id].add(lane_id)
    
    # read detected car absolute coords (.json file)
    with open(car_abs_coord_file_path, "r", errors="ignore") as f:
        detection_abs_coords = json.load(f)
    detection_results = detection_abs_coords["results"]
    
    if detection_abs_coords["EPSG"] != all_road_data["EPSG"]:
        print("「lane_coord_file_path」 と「detection_abs_coord_file_path」のEPSGコードが一致していない")
        sys.exit()
    
    # Correct self coord & detection coords
    phi0_deg, lambda0_deg, epsg_code = calc_org_lat_long(epsg_code=detection_abs_coords["EPSG"])

    output_dict = copy.deepcopy(detection_abs_coords)
    output_results = output_dict["results"]
    self_targets = []
    
    # correct self coord
    self_road_data = all_road_data["roads"]
    if using_road_correct_targets and road_targets["self"]:
        self_road_data = filter_road_info(all_road_data["roads"], road_targets["self"])
    self_road_linestrings = cvt_road_data_to_linestring(self_road_data)
        
    for ii, result in enumerate(detection_results):
        self_coord = [result["self"]["latitude"], result["self"]["longitude"], 0]
        corrected_self_coord, corrected_road_id, corrected_lane_id = correct_car_abs_coord(self_road_linestrings, self_coord)

        # update self coord
        output_results[ii]["self"]["latitude"] = corrected_self_coord[0]
        output_results[ii]["self"]["longitude"] = corrected_self_coord[1]
        self_cartesian_coord = convert_lat_long_to_cartesian(
            corrected_self_coord[0], corrected_self_coord[1], phi0_deg, lambda0_deg)
        self_abs_coord = cvt_plane_cartesian_to_world(self_cartesian_coord[0], self_cartesian_coord[1])
        self_abs_coord.append(corrected_self_coord[2])
        output_results[ii]["self"]["world_coordinate"] = self_abs_coord
        output_results[ii]["self"]["road_correction"] = {
            "road" : corrected_road_id,
            "lane" : corrected_lane_id
        }

        target_ = output_results[ii]["self"]["road_correction"]
        if target_ not in self_targets:
            self_targets.append(target_)

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
        
    road_correct_targets["self"] = {"targets": self_targets}
    with open(json_file_name, "w", encoding="utf-8") as f:
        json.dump(road_correct_targets, f, ensure_ascii=False, indent=2)
            
    # visualize corrected self coord
    if visualize:
        print("Visualize")
        self_car_coordinates = [(x["self"]["latitude"], x["self"]["longitude"]) for x in detection_results]
        self_car_frames = [x["frame"] for x in detection_results]
        corrected_coordinates = [(x["self"]["latitude"], x["self"]["longitude"]) for x in output_results]
        output_images = gen_batch_abs_coord_img(self_car_coordinates, corrected_coordinates, all_road_data)
        
        for idx in range(len(output_images)):
            output_img_path = os.path.join(output_path, f"visualized_frame_{self_car_frames[idx] : 06d}.jpg")
            image_util.save_image(output_img_path, output_images[idx])

if __name__ == "__main__":
    main()
