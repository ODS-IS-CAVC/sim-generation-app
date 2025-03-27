import os
import csv
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(description="map情報の登録")
    parser.add_argument(
        "--map_model_id",
        type=int,
        # required=True,
        default=60000,
        help="マップモデルのid",
    )
    parser.add_argument(
        "--divp_data_path",
        type=str,
        # required=True,
        default="efs/try/data/",
        help="map_dataファイルパス",
    )
    args = parser.parse_args()
    map_id = args.map_model_id
    divp_data_path = args.divp_data_path

    asset_path = divp_data_path + "Asset/"
    asset_csv_path = asset_path + "PathTrace_AssetDictionary.csv"
    map_csv_path = divp_data_path + "Setting/PathTrace_MapDictionary.csv"
    scene_path = divp_data_path + "Scene/"
    map_data_list = os.listdir(asset_path)
    map_model_list = [s for s in map_data_list if s.endswith('fbx') or s.endswith('amx')]
    add_map_model = []

    # map_modelがcsvに含まれているかを確認
    for map_model in map_model_list:
        flg = True
        # 各行を読み込む
        with open(asset_csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if map_model in row:
                    flg = False
                    break
            if flg:
                add_map_model.append([str(map_id),map_model,map_model])
                map_id = int(map_id) + 1

    # PathTrace_AssetDictionary.csvにidを追加
    if not len(add_map_model) == 0:
        with open(asset_csv_path, 'r') as file:
            file.readline()
            lines = file.readlines()
            flg = lines[-1][-1] == "\n"

        with open(asset_csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if not flg :
                writer.writerow('')
            for add_map in add_map_model:
                writer.writerow(add_map)

    # PathTrace_MapDictionary.csvにidを追加
    if not len(add_map_model) == 0:
        with open(map_csv_path, 'r') as file:
            file.readline()
            lines = file.readlines()
            flg = lines[-1][-1] == "\n"

        with open(map_csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if not flg :
                writer.writerow('')
            for add_map in add_map_model:
                # sceneファイルの作成
                camera_scene = add_map[1][:-4] +"_camera.scene"
                lidar_scene = add_map[1][:-4] +"_lidar.scene"
                radar_scene = add_map[1][:-4] +"_radar.scene"
                shutil.copy(scene_path + "etc_camera.scene", scene_path + camera_scene)
                shutil.copy(scene_path + "etc_radar.scene", scene_path + radar_scene)
                shutil.copy(scene_path + "etc_lidar.scene", scene_path + lidar_scene)
                # ファイル書き込み
                writer.writerow([add_map[1][:-4],add_map[0],camera_scene,lidar_scene,radar_scene,""])

if __name__ == "__main__":
    main()