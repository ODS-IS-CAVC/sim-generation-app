import os
import json
import argparse
import numpy as np
import cv2

def get_aabb(points, tolerance):
    points_2d = np.array([[x, y] for x, y, z in points], dtype=np.float32)

    # 外接矩形を求める
    rect = cv2.boundingRect(points_2d)

    # 外接矩形を描画
    x, y, w, h = rect
    a = [x-tolerance,y-tolerance]
    b = [x+w+tolerance,y-tolerance]
    c = [x-tolerance,y+h+tolerance]
    d = [x+w+tolerance,y+h+tolerance]
    aabb = [a, b, c, d]

    return aabb

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--map_data_path",
        type=str,
        # required=True,
        default="try_bravs/map_data/",
        help="map_dataファイルパス",
    )
    args = parser.parse_args()
    map_data_path = args.map_data_path

    map_data_list = os.listdir(map_data_path)
    if "V-DriveROOT" in map_data_list: map_data_list.remove("V-DriveROOT")

    rev_map_names = []
    for map_data_name in map_data_list:
        if map_data_name[:2] == "E1" or map_data_name[:5] == "MEXC1":
            rev_map_names.append(map_data_name)

    # 各マップの修正
    for rev_map_name in rev_map_names:
        map_info_path = map_data_path + rev_map_name + "/map_info.json"
        with open(map_info_path, "r", encoding="utf-8") as f:
            map_info = json.load(f)
        road_coordinates_path = map_info["road_coordinates_path"]
        with open(road_coordinates_path, "r", encoding="utf-8") as f:
            road_coordinates = json.load(f)
        map_offset = road_coordinates["map_offset"]
        if "rev_check" in road_coordinates:
            continue
        # xodr_road_coordinatesを更新する。
        for i in range(len(road_coordinates["roads"])):
            lanes = road_coordinates["roads"][i]["lanes"]
            for j in range(len(lanes)):
                coordinate = lanes[j]["coordinate"]
                for k in range(len(coordinate)):
                    coordinate[k] = [coordinate[k][0] + map_offset[0], coordinate[k][1] + map_offset[1], coordinate[k][2]]
                lanes[j]["coordinate"] = coordinate
            road_coordinates["roads"][i]["lanes"] = lanes

        map_offset = [road_coordinates["map_offset"][0]*-1,road_coordinates["map_offset"][1]*-1]
        road_coordinates["map_offset"] = map_offset
        map_info["map_offset"] = map_offset

        rev_check_dict = {"rev_check":True}
        rev_check_dict.update(road_coordinates)

        with open(road_coordinates_path, mode="wt", encoding="utf-8") as f:
            json.dump(rev_check_dict, f, ensure_ascii=False, indent=2)

        with open(map_info_path, mode="wt", encoding="utf-8") as f:
            json.dump(map_info, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()