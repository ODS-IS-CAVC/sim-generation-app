#!/usr/bin/env python
import os
import sys
import argparse
from pyproj import CRS

import carla


def get_proj_string(epsg_code):
    """ 座標投影文字列を作成する

    Args:
        epsg_code (int): EPSG コード

    Returns:
        (string): Osm2OdrSettings.proj_string で使用する座標投影文字列
    """
    crs = CRS.from_epsg(epsg_code)
    proj_string = crs.to_proj4()
    # proj_string = proj_string.replace("+ellps=GRS80", "+datum=WGS84")
    # '+type=crs' があるとcarla.Osm2Odr.convert()でエラーが発生する
    proj_string = proj_string.replace(" +type=crs", "")
    # '+proj=tmerc +lat_0=36 +lon_0=139.833333333333 +k=0.9999 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

    # print(proj_string)
    return proj_string


def convert(args):
    # Read the .osm data
    with open(args.input_path, 'r', encoding='utf-8') as f:
        osm_data = f.read()

    # print(osm_data)

    # Define the desired settings. In this case, default values.
    settings = carla.Osm2OdrSettings()
    # Set OSM road types to export to OpenDRIVE
    settings.set_osm_way_types([
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
        "primary",
        "primary_link",
        "secondary",
        "secondary_link",
        "tertiary",
        "tertiary_link",
        "unclassified",
        "residential"
        ])

    settings.default_lane_width = float(args.lane_width)
    settings.generate_traffic_lights = args.traffic_lights
    settings.all_junctions_with_traffic_lights = args.all_junctions_lights
    settings.center_map = args.center_map
    # 投影:default='+proj=tmerc'
    # +proj=tmerc  : 投影法として横メルカトルを使用
    # +lat_0=36    : 原点の緯度が0度
    # +lon_0=136.0 : 原点の経度が140.25
    # +k=0.9999    : 尺度係数
    # +x_0=0       : X座標の原点
    # +y_0=0       : Y座標の原点
    # +datum=WGS84 : 測地系が WGS84 緯度経度
    # +units=m     : 単位がメートル
    # +no_defs     : 他のデフォルトの定義を使用しない
    # 投影文字列
    proj_string = get_proj_string(args.epsg_code)

    settings.proj_string = proj_string
    # epsg = 6677
    # settings.proj_string = f"+proj=tmerc +init=epsg:{epsg}"
    # print(f"{settings.proj_string}")

    # Convert to .xodr
    try:
        xodr_data = carla.Osm2Odr.convert(osm_data, settings)
    except Exception as e:
        print(f"carlaOsm2Odr.convert failed: {e}")

    # save opendrive file
    with open(args.output_path, "w", encoding="utf-8") as xodrFile:
        xodrFile.write(xodr_data)


def main():
    src_path = "osm/two_ways_sample.osm"
    dst_path = "osm/two_ways_sample.xodr"

    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-i', '--input-path',
        # required=True,
        default=src_path,
        metavar='OSM_FILE_PATH',
        help='set the input OSM file path')
    argparser.add_argument(
        '-o', '--output-path',
        # required=True,
        default=dst_path,
        metavar='XODR_FILE_PATH',
        help='set the output XODR file path')
    argparser.add_argument(
        '--lane-width',
        default=3.0,
        help='width of each road lane in meters')
    argparser.add_argument(
        '--traffic-lights',
        default=False,
        action='store_true',
        help='enable traffic light generation from OSM data')
    argparser.add_argument(
        '--all-junctions-lights',
        action='store_true',
        default=False,
        help='set traffic lights for all junctions')
    argparser.add_argument(
        '--center-map',
        action='store_true',
        help='set center of map to the origin coordinates')
    argparser.add_argument(
        '--epsg-code',
        default=6677,
        help='transform to'
    )

    args = argparser.parse_args()

    if args.input_path is None or not os.path.exists(args.input_path):
        print('input file not found.')
    if args.output_path is None:
        print('output file path not found.')

    print(__doc__)

    try:
        convert(args)
    except:
        print('\nAn error has occurred in conversion.')


if __name__ == "__main__":
    main()

