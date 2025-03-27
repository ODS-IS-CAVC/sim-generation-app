import os
import json
import numpy as np
import cv2
import argparse
from pyproj import CRS, Transformer

def transform_coordinates(epsg_from, epsg_to, points):
    srcCRS = CRS(f'EPSG:{epsg_from}')
    dstCRS = CRS(f'EPSG:{epsg_to}')
    transformer = Transformer.from_crs(srcCRS, dstCRS, always_xy=True)
    results = []
    for pt in transformer.itransform(points):
        results.append(pt)
    return results

def check_road_rect(road_points,map_data_path):
    '''
    データ確認用
    点群、点群の外接矩形（aabb）、最少外接矩形（obb）を描画
    '''
    # 点群の中心を計算
    center = road_points.mean(axis=0)

    # 点群の範囲を計算
    min_x, min_y = road_points.min(axis=0)
    max_x, max_y = road_points.max(axis=0)

    # 画像サイズを設定（余裕を持たせるために少し大きめにする）
    margin = 1000
    width = int(max_x - min_x + 2 * margin)
    height = int(max_y - min_y + 2 * margin)

    # 画像を作成
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # 点群を画像の中心に合わせて配置
    adjusted_points = []
    for point in road_points:
        adjusted_point = point - center + [width // 2, height // 2]
        adjusted_points.append(adjusted_point)
        cv2.circle(img, (int(adjusted_point[0]), int(adjusted_point[1])), 3, (255, 255, 255), -1)

    # 調整された点群をNumPy配列に変換
    adjusted_points = np.array(adjusted_points, dtype=np.float32)

    # 外接矩形を求める
    rect = cv2.boundingRect(adjusted_points)

    # 外接矩形を描画
    x, y, w, h = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    rect = cv2.minAreaRect(adjusted_points)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,0,255),2)

    # 画像を保存
    cv2.imwrite(map_data_path+'bounding_rectangle.png', img)

def get_map_data(map_data_path,map_data_name, divp_path):
    map_data_path = map_data_path + map_data_name + "/"
    map_data = os.listdir(map_data_path)

    # ファイル存在チェック
    if not [s for s in map_data if 'xodr_road_coordinates.json' in s]:
        print(map_data_path + "にxodr_road_coordinates.jsonが含まれていません")
        return False

    # xodr_road_jsonを取得
    xodr_road_json = [s for s in map_data if 'xodr_road_coordinates.json' in s]
    xodr_road_json = map_data_path + ''.join(xodr_road_json)

    assert isinstance(xodr_road_json, str)

    # load xodr json file
    xodr_data = {}
    with open(xodr_road_json, "r", encoding="utf-8") as f:
        xodr_data = json.load(f)

    epsg = xodr_data["EPSG"]
    map_offset = xodr_data["map_offset"]

    # レーン情報の座標データ取得
    roads_points = []
    for road in xodr_data["roads"]:
        lanes = road["lanes"]
        for lane in lanes:
            coordinate = np.array(lane["coordinate"])
            roads_points.append(coordinate)
    roads_points = np.concatenate(roads_points)

    # リストを2次元に変換
    points_2d = np.array([[x, y] for x, y, z in roads_points], dtype=np.float32)

    # debug データ確認用
    check_road_rect(points_2d,map_data_path)

    # 外接矩形を求める
    rect = cv2.boundingRect(points_2d)

    # 外接矩形を描画
    x, y, w, h = rect
    aabb = [[x, y], [x+w, y], [x, y+h], [x+w, y+h]]

    rect = cv2.minAreaRect(points_2d)
    xy, wh, hdg = rect
    # 最少外接矩形の頂点取得
    obb = cv2.boxPoints(rect)
    obb = np.int0(obb)

    # jsonファイルを作成する。
    map_info_path = map_data_path + "map_info.json"
    xodr_path = divp_path + "XODR/"
    xodr_data_list = os.listdir(xodr_path)
    xodr_name = [s for s in xodr_data_list if s.startswith(map_data_name[:-3])]
    if len(map_data_name) == 0:
        print(map_data_name + ".xodrが存在しません")
        return False
    map_model_path = divp_path + "Asset/"
    map_model_data_list = os.listdir(map_model_path)
    map_model_name = [s for s in map_model_data_list if s.startswith(map_data_name) and (s.endswith(".amx") or s.endswith(".fbx"))]
    if len(map_model_name) == 0:
        print(map_data_name+"の3dMapModelが存在しません")
        return False
    map_coordinates_name = [s for s in map_data if s.endswith("coordinates.json")]

    # 座標を緯度経度に変換する
    for i in range(len(aabb)):
        aabb[i] = (aabb[i][0] + map_offset[0], aabb[i][1] + map_offset[1])

    epsg_to = 4326 # WGS84
    aabb = transform_coordinates(epsg, epsg_to, aabb)

    json_data =  {
        "name": map_data_name,
        "aabb": aabb,
        "obb": obb.tolist(),
        "obb_center-angle": [(xy[0], xy[1]), hdg],
        "center": map_offset,
        "epsg": epsg,
        "opendrive_path": xodr_path + xodr_name[0],
        "3dmapModel_path": map_model_path + map_model_name[0],
        "road_coordinates_path": map_data_path + map_coordinates_name[0]
    }

    with open(map_info_path,"w") as file :
        json.dump(json_data, file, indent = 2)

    return True
    '''
    cv2.minAreaRect が返すobbの傾きが[-90, 0)の範囲のため、正しい角度が欲しい場合は以下を参考にしてください。
    https://teratail.com/questions/228544
    https://stackoverflow.com/questions/15956124/minarearect-angles-unsure-about-the-angle-returned
    '''

def main():
    parser = argparse.ArgumentParser(description="地図情報を集約")
    parser.add_argument(
        "--map_data_path",
        type=str,
        # required=True,
        default="map_tools/map_data/",
        help="map_dataファイルパス",
    )
    parser.add_argument(
        "--divp_data_path",
        type=str,
        # required=True,
        default="efs/try/data/",
        help="map_dataファイルパス",
    )
    args = parser.parse_args()

    map_data_path = args.map_data_path
    divp_data_path = args.divp_data_path
    map_data_list = os.listdir(map_data_path)
    if "V-DriveROOT" in map_data_list: map_data_list.remove("V-DriveROOT")
    for map_data_name in map_data_list:
        if not get_map_data(map_data_path,map_data_name,divp_data_path):
            print(map_data_name + "のファイルが足りません")

if __name__ == "__main__":
    main()