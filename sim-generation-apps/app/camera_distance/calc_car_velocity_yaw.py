import argparse
import copy
import json
import math
import os

from commons.constants import ABS_COORD_JSON_FILE_NAME, DETECTION_YAW_THD
from commons.math_util import get_angle_2d, get_distance_2d

def limit_yaw(self_yaw, detection_yaw):
    # calculate difference from 2 angles
    diff_angle = abs(((self_yaw - detection_yaw) + 180) % 360 - 180)
    
    # detection yaw within limit range
    if diff_angle <= DETECTION_YAW_THD:
        return detection_yaw
    
    # detection yaw out of limit range
    max_angle = ((self_yaw + DETECTION_YAW_THD) + 360) % 360
    min_angle = ((self_yaw - DETECTION_YAW_THD) + 360) % 360
    
    diff_max_angle = abs(((max_angle - detection_yaw) + 180) % 360 - 180)
    diff_min_angle = abs(((min_angle - detection_yaw) + 180) % 360 - 180)
    
    return max_angle if diff_max_angle <= diff_min_angle else min_angle

def cal_velocity_yaw(prev_abs_pos, curr_abs_pos, prev_frame, curr_frame, fps):
    # vehicle velocity
    movement_dist = get_distance_2d(prev_abs_pos, curr_abs_pos)
    movement_time = (curr_frame - prev_frame) / fps
    movement_velocity = movement_dist / movement_time
    # m/s => km/h
    velocity = 3.6 * movement_velocity

    # vehicle direction (z-axis rotation angle)
    movement_dx = curr_abs_pos[0] - prev_abs_pos[0]
    movement_dy = curr_abs_pos[1] - prev_abs_pos[1]
    yaw = get_angle_2d(movement_dx, movement_dy)
    yaw = math.degrees(yaw)
    
    return velocity, yaw

def main():
    parser = argparse.ArgumentParser(
        description="隣接フレーム間の座標から自車・他車の向き、速度を計算する"
    )
    parser.add_argument(
        "--car_abs_coord_file_path",
        type=str,
        required=True,
        help="車両座標のjsonファイルパス（タイプ：string）"
    )
    parser.add_argument(
        "--fps",
        type=int,
        required=False,
        default=30,
        help="FPS",
    )
    parser.add_argument(
        "--limit_detect_yaw_range",
        action="store_true",
        help="他車の向きの範囲を制限する",
    )
    
    args = parser.parse_args()
    car_abs_coord_file_path = args.car_abs_coord_file_path
    fps = args.fps
    limit_detect_yaw_range = args.limit_detect_yaw_range
    
    # read car absolute coords (.json file)
    with open(car_abs_coord_file_path, "r", errors="ignore") as f:
        car_abs_coords = json.load(f)
    
    # output result
    output_results = copy.deepcopy(car_abs_coords['results'])
    
    detections_prev_abs_pos = {}
    for ii, result in enumerate(output_results):
        prev_frame = output_results[ii-1]["frame"]
        curr_frame = result["frame"]
        
        if ii == 0:
            for jj, detection in enumerate(result["detections"]):
                detections_prev_abs_pos |= {
                    str(detection["obj_id"]): detection["world_coordinate"]
                }
        
        if ii > 0:
            # calculate for self car
            prev_abs_pos = output_results[ii-1]["self"]["world_coordinate"]
            curr_abs_pos = result["self"]["world_coordinate"]
            result["self"]["velocity"], result["self"]["yaw"] = cal_velocity_yaw(prev_abs_pos, curr_abs_pos, prev_frame, curr_frame, fps)
            
            # calculate for detections
            for jj, detection in enumerate(result["detections"]):
                if str(detection["obj_id"]) in detections_prev_abs_pos.keys():
                    prev_abs_pos = detections_prev_abs_pos[str(detection["obj_id"])]
                    curr_abs_pos = detection["world_coordinate"]

                    # 同座標に補正されていた場合の暫定対応
                    if(curr_abs_pos[0] != prev_abs_pos[0]):
                        detection["velocity"], detection["yaw"] = cal_velocity_yaw(prev_abs_pos, curr_abs_pos, prev_frame, curr_frame, fps)
                        if limit_detect_yaw_range:
                            detection["yaw"] = limit_yaw(result["self"]["yaw"], detection["yaw"])
                    
                    detections_prev_abs_pos[str(detection["obj_id"])] = curr_abs_pos
                
    # calculate for first frame
    output_results[0]["self"]["velocity"] = output_results[1]["self"]["velocity"]
    output_results[0]["self"]["yaw"] = output_results[1]["self"]["yaw"]
    for detection in output_results[0]["detections"]:
        detections_second_frame = [(det["velocity"], det["yaw"]) for det in output_results[1]["detections"] if det["obj_id"] == detection["obj_id"]]
        if len(detections_second_frame) > 0:
            (detection["velocity"], detection["yaw"]) = detections_second_frame[0]

    # output result to json
    output_dict = copy.deepcopy(car_abs_coords)
    output_dict['results'] = output_results
    
    output_abs_coord_file_path = os.path.join(os.path.dirname(car_abs_coord_file_path), ABS_COORD_JSON_FILE_NAME)

    with open(output_abs_coord_file_path, mode='w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    main()