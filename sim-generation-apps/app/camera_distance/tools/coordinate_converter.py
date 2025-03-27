import os
import sys
import argparse
import json
import math

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from commons.constants import *
from cvt_lat_long_cartesian import (
    convert_cartesian_to_lat_long,
    cvt_world_to_plane_cartesian,
    calc_org_lat_long,
)


def convert_coordinates(x, y, phi0_deg, lambda0_deg, map_offset):
    """元の座標系から基準座標系に座標を変換する

    Args:
        x, y (float, float): 位置座標
        phi0_deg, lambda0_deg (float, float): 平面直角座標系原点の緯度、平面直角座標系原点の経度
        map_offset (list): 座標系原点のオフセット
    """
    # Original coordinates
    x_origin = x + map_offset[0]
    y_origin = y + map_offset[1]
    
    # Convert to lat-lon
    xp, yp = cvt_world_to_plane_cartesian(x_origin, y_origin)
    lat, long = convert_cartesian_to_lat_long(xp, yp, phi0_deg, lambda0_deg)

    return lat, long

def get_converted_coordinates_lane_coord(input_json_path):
    """車線の座標を軽度・緯度に変換する

    Args:
        input_json_path (str): レーン座標のjsonファイルパス 
    """
    # Read data
    f = open(input_json_path, "r", encoding="utf-8", errors="ignore")
    data = json.load(f)
    f.close()

    epsg, map_offset = (
        data["EPSG"],
        data["map_offset"],
    )

    # calc original lat-lon
    phi0_deg, lambda0_deg, epsg_code = calc_org_lat_long(epsg_code=epsg)
    
    coords = []
    roads = data["roads"]
    for road in roads:
        lanes = road["lanes"]

        for lane in lanes:
            coordinate = lane["coordinate"]
            for i in range(len(coordinate)):
                lat, long = convert_coordinates(coordinate[i][0], coordinate[i][1], phi0_deg, lambda0_deg, map_offset)
                coordinate[i][0] = lat
                coordinate[i][1] = long
                coords.append([lat, long])

    return data
