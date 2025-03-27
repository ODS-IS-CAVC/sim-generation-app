import os
import json
import csv
import matplotlib.pyplot as plt
import math
import argparse
import pandas as pd
from shapely.geometry import LineString, Point
import numpy as np

BRAVS_CSV_HEADER = ["frame","timestamp","latitude","longitude","pos_z","roll_rad","pitch_rad","yaw_rad","vel_x","vel_y","vel_z","interpolation_type","road_id","lane_id"]
ABS_RESULT_CSV_HEADER = ["frame","timestamp","pos_x","pos_y","pos_z","yaw_rad","vel","interpolation_type","road_id","lane_id"]
SDMG_ROUTE_CSV_HEADER = ["timestamp","pos_x","pos_y","pos_z","roll_rad","pitch_rad","yaw_rad","vel_x","vel_y","vel_z"]
        
def frame_to_timecode(frame_number, fps=30):
    timecode = frame_number / fps
    return f"{timecode:.3f}"


def get_xodr_target_lane(roads_data, target_road_id, target_lane_id):
    for road in roads_data:
        if road["id"] != target_road_id:
            continue

        lanes = road["lanes"]
        for lane in lanes:
            if lane["lane_id"] != target_lane_id:
                continue

            coordinate = lane["coordinate"]
            return LineString(coordinate)
        
    return None


def recalc_beforein_position(df:pd.DataFrame, roads_data, map_offsets):
    before_in_df = df[df["interpolation_type"] == "beforeIn"]
    beforein_indices = df.index[df['interpolation_type'] == "beforeIn"].tolist()
    if len(before_in_df) <= 1:
        return df
    
    just_before_in_series = before_in_df.iloc[-1]
    target_road_id = just_before_in_series["road_id"]
    target_lane_id = just_before_in_series["lane_id"]

    line = get_xodr_target_lane(roads_data, target_road_id, target_lane_id)
    if line is None:
        return df
    
    correct_pt = Point(just_before_in_series["pos_x"] - map_offsets[0], just_before_in_series["pos_y"] - map_offsets[1])
    for idx in beforein_indices:
        if idx == beforein_indices[-1]:
            continue
        before_in_series = before_in_df.iloc[idx]

        movement_time = float(just_before_in_series["timestamp"]) - float(before_in_series["timestamp"])
        vel_mps = just_before_in_series["vel"] * (1000 / 3600) # 距離を計算 
        distance = vel_mps * movement_time

        correct_pt_on_line = line.project(correct_pt)
        target_point_dist = correct_pt_on_line - distance
        pt_on_line = line.interpolate(target_point_dist)

        # update data
        df.at[beforein_indices[idx], 'pos_x'] = pt_on_line.x + map_offsets[0]
        df.at[beforein_indices[idx], 'pos_y'] = pt_on_line.y + map_offsets[1]

    return df


def main():
    parser = argparse.ArgumentParser(description="自車と検出者の絶対座標から経路出力")
    parser.add_argument(
        "--xodr_road_json",
        type=str,
        required=True,
        help="OpenDRIVEレーン情報ファイルパス",
    )
    parser.add_argument(
        "--abs_coord_file",
        type=str,
        required=True,
        help="自車と検出車の絶対座標のjsonファイルパス",
    )
    parser.add_argument(
        "--self_car_offset",
        type=float,
        required=False,
        default=-9.33,
        help="自車オフセット（y方向）",
    )
   
    args = parser.parse_args()
    xodr_road_json = args.xodr_road_json
    assert isinstance(xodr_road_json, str)
    abs_coord_file = args.abs_coord_file
    assert isinstance(abs_coord_file, str)
    self_car_offset = args.self_car_offset
    assert isinstance(self_car_offset, float)

    with open(xodr_road_json, mode='r', encoding='utf-8') as f:
        xodr_road_result = json.load(f)
        map_offset = xodr_road_result["map_offset"]
        roads_data = xodr_road_result["roads"]

    with open(abs_coord_file, mode='r', encoding='utf-8') as f:
        det_abs_coord_result = json.load(f)

    values = []
    other_values = {}
    for item in det_abs_coord_result['results']:
        frame = item['frame']
        self_item = item.get('self')
        if self_item is None:
            continue
        
        self_world_coordinate = self_item.get('world_coordinate')
        if self_world_coordinate is None:
            continue

        self_vel = self_item.get('velocity')
        self_lat = self_item.get('latitude')
        self_lon = self_item.get('longitude')
        self_yaw = math.radians(self_item.get('yaw'))
        
        time = frame_to_timecode(frame)
        values.append([frame, time, self_lat, self_lon, self_world_coordinate[0], self_world_coordinate[1], self_world_coordinate[2], self_vel, self_yaw])
        
        # other
        for detect in item['detections']:
            obj_id = detect['obj_id']
            world_coordinate = detect.get('world_coordinate')
            if world_coordinate is None:
                continue
            
            obj_vel = detect.get('velocity') if detect.get('velocity') is not None else self_vel
            obj_yaw = detect.get('yaw') if detect.get('yaw') is not None else self_yaw
            obj_yaw = math.radians(obj_yaw)
            obj_interpolation = detect.get('interpolation_type')
            obj_road_correction = detect.get('road_correction')
            obj_road_id = None
            obj_lane_id = None
            if obj_road_correction is not None:
                obj_road_id = obj_road_correction.get('road')
                obj_lane_id = obj_road_correction.get('lane')
            obj_id_str = str(obj_id)
            if obj_id_str not in other_values:
                other_values[obj_id_str] = []

            # other_values[obj_id_str].append([frame, time, obj_lat, obj_lon, world_coordinate[0], world_coordinate[1], obj_vel, obj_yaw])
            pos_z = 0
            if len(world_coordinate) > 2:
                pos_z = world_coordinate[2]
            other_values[obj_id_str].append(pd.DataFrame(dict(zip(
                ABS_RESULT_CSV_HEADER,
                [
                    [frame], [time], [world_coordinate[0]], [world_coordinate[1]], [pos_z],
                    [obj_yaw], [obj_vel],
                    [obj_interpolation], [obj_road_id], [obj_lane_id]
                ]
            ))))

    # concat dataframe        
    for k, v in other_values.items():
        df = pd.concat(v, ignore_index=True)
        recalc_df = recalc_beforein_position(df, roads_data, map_offset)

        # convert sdmg parameter
        recalc_df['pos_x'] = recalc_df['pos_x'] - map_offset[0]
        recalc_df['pos_y'] = recalc_df['pos_y'] - map_offset[1]
        temp_y = recalc_df['pos_y'].copy()
        recalc_df['pos_y'] = recalc_df['pos_x'] * -1
        recalc_df['pos_x'] = temp_y
        
        recalc_df['yaw_rad'] = recalc_df['yaw_rad'] - math.pi / 2
        recalc_df['vel_x'] = recalc_df['vel'] * np.cos(recalc_df['yaw_rad'])
        recalc_df['vel_y'] = recalc_df['vel'] * np.sin(recalc_df['yaw_rad'])

        # add remaining data
        recalc_df['roll_rad'] = 0
        recalc_df['pitch_rad'] = 0
        recalc_df['vel_z'] = 0
        
        sdmg_obj_csv_file = os.path.join(os.path.dirname(abs_coord_file), f"car_route_{k}.csv")
        recalc_df.to_csv(sdmg_obj_csv_file, columns=SDMG_ROUTE_CSV_HEADER, index=False)    


    # sdmg形式に変換
    sdmg_values = []
    for _, time, _, _, x, y, z, vel, yaw in values:
        map_pos_x = x - map_offset[0]
        map_pos_y = y - map_offset[1]
        # offset
        map_pos_x = map_pos_x + self_car_offset * math.cos(yaw)
        map_pos_y = map_pos_y + self_car_offset * math.sin(yaw)
        # SDMGの座標系←y↑xに合わせる。
        pos_x = map_pos_y
        pos_y = -map_pos_x
        pos_z = z
        yaw_rad = yaw - math.pi / 2
        vel_x = vel * math.cos(yaw_rad)
        vel_y = vel * math.sin(yaw_rad)
        # 算出できていないパラメータは暫定値
        roll_rad = 0
        pitch_rad = 0
        vel_z = 0
        sdmg_values.append(dict(zip(
            SDMG_ROUTE_CSV_HEADER,
            [
                time, pos_x, pos_y, pos_z,
                roll_rad, pitch_rad, yaw_rad,
                vel_x, vel_y, vel_z
            ]
        )))
    sdmg_csv_file = os.path.join(os.path.dirname(abs_coord_file), "car_route_self.csv")
    with open(sdmg_csv_file, mode='w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SDMG_ROUTE_CSV_HEADER)
        writer.writeheader()
        writer.writerows(sdmg_values)


if __name__ == "__main__":
    main()


def plot_route(self_val, obj_vals, map_offset = None, filename='figure_all.png'):
    x_values = []
    y_values = []
    names = []

    if map_offset is None:
        names.append("self")
        x_values.append([val[2] for val in self_val])
        y_values.append([val[3] for val in self_val])
        for key, obj in obj_vals.items():
            names.append(key)
            x_values.append([val[2] for val in obj])
            y_values.append([val[3] for val in obj])
    else:
        names.append("self_map")
        x_values.append([val[3] - map_offset[1] for val in self_val])
        y_values.append([val[2] - map_offset[0] for val in self_val])
        for key, obj in obj_vals.items():
            names.append(key+"_map")
            x_values.append([val[3] - map_offset[1] for val in obj])
            y_values.append([val[2] - map_offset[0] for val in obj])


    for idx in range(0, len(x_values)):
        plt.plot(x_values[idx], y_values[idx], label=names[idx])
        
    plt.title('Road Geometric Shape')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    return