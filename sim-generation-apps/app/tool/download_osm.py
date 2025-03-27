#!/usr/bin/env python
import os
import argparse
import pandas as pd
import requests
import json
import overpy


def find_min_max(csv_path, column_names):
    """CSVファイルから緯度経度の最大、最小値を取得する

    Args:
        csv_path (string): CSV ファイルパス
        column_names (dic): 緯度経度のヘッダー文字列

    Returns:
        dic: 緯度経度 (min, max)
    """
    df = pd.read_csv(csv_path)
    results = {}

    for column in column_names:
        if column in df.columns:
            min_value = df[column].min()
            max_value = df[column].max()
            results[column] = (min_value, max_value)

    return results


def download_from_overpass_api(min_lat, min_lon, max_lat, max_lon, osm_path, file_format='xml', save_osm=True):
    """_summary_

    Args:
        min_lat (float): 緯度最小値
        min_lon (float): 経度最小値
        max_lat (float): 緯度最大値
        max_lon (float): 経度最大値
        osm_path (string): 保存ファイルパス
        file_format (str, optional): ファイルフォーマット. Defaults to 'xml'.
        save_osm (bool, optional): OSM ファイルを保存するか. Defaults to True.
    Returns:
        string : response.text
    """
    
    url = "http://overpass-api.de/api/interpreter"
    query = f"""[out:{file_format}];
(
  node({min_lat},{min_lon},{max_lat},{max_lon});
  way({min_lat},{min_lon},{max_lat},{max_lon});
  relation({min_lat},{min_lon},{max_lat},{max_lon});
);
out body;
"""

    response = requests.post(url, data=query)
    osm_data = {}
    if response.status_code == 200:
        if file_format == 'json':
            osm_data = response.json()
            if save_osm:
                with open(osm_path, 'w') as f:
                    json.dump(osm_data, f, indent=2, ensure_ascii=False)
        else:
            osm_data = response.text
            if save_osm:
                with open(osm_path, 'w', encoding='utf-8') as f:
                    f.write(osm_data)
    else:
        print(f"Error: Unable to download data. HTTP Status Code: {response.status_code}")

    print(f"query = {query}")
    return osm_data, query


def exec_overpass_api(query):
    """Overpass API 実行

    Args:
        query (stgring): クエリ

    Returns:
        Bool: True:成功, False:失敗
        overpy.Result: 結果
    """
    try:
        api = overpy.Overpass()
        result = api.query(query)
    except overpy.exception.OverpassGatewayTimeout:
        print("Error: Overpass API Gateway Timeout. Please try again later.")
        return False, None
    except overpy.exception.OverpassTooManyRequests:
        print("Error: Too many requests to the Overpass API. Please slow down and try again later.")
        return False, None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        print(f"query: {query}")
        return False, None

    return True, result


def post_overpass_api(query):
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data=query)
    osm_data = {}
    if response.status_code == 200:
        osm_data = response.text
    else:
        print(f"Error: Unable to download data. HTTP Status Code: {response.status_code}")
        return False, osm_data

    return True, osm_data


def get_osm_data(min_lat, min_lon, max_lat, max_lon, way_types, osm_path, save_osm=True):
    way_type_filters = "".join([f'way["highway"="{way_type}"]({min_lat},{min_lon},{max_lat},{max_lon});' for way_type in way_types])
    initial_query = f"""
[out:xml];
(
  {way_type_filters}
);
(._;>;);
out body;
"""

    # 道路情報取得
    success, result = exec_overpass_api(initial_query)
    if success is False:
        return None, ""

    way_ids = [way.id for way in result.ways]
    if not way_ids:
        print("No ways found for the given types and area")
        return None, ""

    way_id_filsters = "".join([f'way({way_id});' for way_id in way_ids])
    detailed_query = f"""
[out:xml];
(
  {way_id_filsters}
);
(._;>;);
out body;
"""
    success, detailed_result = post_overpass_api(detailed_query)
    if success is False:
        return None, ""

    if save_osm:
        with open(osm_path, "w") as file:
            file.write(detailed_result)

    return detailed_result, detailed_query


def convert(args):
    # 入力ファイルの場所に出力フォルダを作成
    osm_path = args.output_path
    output_dir = os.path.dirname(osm_path)
    os.makedirs(output_dir, exist_ok=True)

    # csv から min, max の lat, lon 抽出
    column_names = [ args.col_lat, args.col_lon ]
    min_max_values = find_min_max(args.input_path, column_names)

    lat_val = min_max_values[column_names[0]]
    lon_val = min_max_values[column_names[1]]
    expand = 0.002
    lat_min = lat_val[0] - expand
    lon_min = lon_val[0] - expand
    lat_max = lat_val[1] + expand
    lon_max = lon_val[1] + expand
    lat_cen = lat_min + (lat_max - lat_min) / 2
    lon_cen = lon_min + (lon_max - lon_min) / 2

    print(f"Latitude  : {lat_min}, {lat_max}")
    print(f"Longitude : {lon_min}, {lon_max}")
    print(f"Center    : {lat_cen}, {lon_cen}")

    # download OpenStreetMap
    way_types = []
    if args.motorway:
        way_types = ["motorway", "motorway_link"]
    else:
        way_types = [
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
            ]


    if True:
        osm_data, query = get_osm_data(
            lat_min,
            lon_min,
            lat_max,
            lon_max,
            way_types,
            osm_path,
            save_osm=True
        )
    else:
        osm_data, query = download_from_overpass_api(
            lat_min,
            lon_min,
            lat_max,
            lon_max,
            osm_path,
            file_format = "xml",
            save_osm=True)


def main():
    src_path = "data/gps_sample_1708.csv"
    dst_path = "output.osm"

    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--input-path',
        required=True,
        metavar='INPUT_PATH',
        help='set the input CSV file path')
    argparser.add_argument(
        '-o', '--output-path',
        # required=True,
        default=dst_path,
        metavar='OSM_FILE_PATH',
        help='set the output OSM file path')
    argparser.add_argument(
        '--col-lat',
        default='Latitude (deg)',
        metavar='LATITUDE',
        help='set the latitude column')
    argparser.add_argument(
        '--col-lon',
        default='Longitude (deg)',
        metavar='LONGITUDE',
        help='set the longitude column')
    argparser.add_argument(
        '-m', '--motorway',
        action='store_true',
        default=False,
        help='set way types to motorway'
    )

    args = argparser.parse_args()
    if args.input_path is None or not os.path.exists(args.input_path):
        print('input file not found.')

    # print(__doc__)
    try:
        convert(args)
    except Exception as e:
        print(f"\nAn error has occurred : {e}")


if __name__ == "__main__":
    main()

