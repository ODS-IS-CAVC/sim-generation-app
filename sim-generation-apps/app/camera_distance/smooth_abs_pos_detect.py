import argparse
import copy
import json
import os
import sys

from commons.constants import ABS_COORD_JSON_FILE_NAME
from cvt_lat_long_cartesian import calc_org_lat_long
from tools.estimate_abs_pos import interpolate_abs_pos


def main():
    parser = argparse.ArgumentParser(
        description="他車の動きの平滑化"
    )
    parser.add_argument(
        "--car_abs_coord_file_path",
        type=str,
        required=True,
        help="車両座標のjsonファイルパス",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        required=False,
        default=1,
        help="平滑化の繰り返し数",
    )
    
    args = parser.parse_args()
    car_abs_coord_file_path = args.car_abs_coord_file_path
    repeat = args.repeat
    
    with open(car_abs_coord_file_path, "r", errors="ignore") as f:
        car_abs_coords = json.load(f)
    
    if "EPSG" not in car_abs_coords.keys():
        print("[EPSG]情報なし")
        sys.exit()
    
    phi0_deg, lambda0_deg, epsg_code = calc_org_lat_long(epsg_code=car_abs_coords["EPSG"])
    
    output_dict = copy.deepcopy(car_abs_coords)
    output_results = output_dict["results"]
    
    for i in range(repeat):
        prev_detections_idxes = {}
        for ii, result in enumerate(output_results):
            # First frame
            if ii == 0:
                for jj, detection in enumerate(result["detections"]):
                    prev_detections_idxes |= {
                        detection["obj_id"]: jj
                    }
                continue
            
            # Last frame
            if ii == len(output_results) - 1:
                continue
            
            # Get index of detections of next frame
            next_detections_idxes = {}
            for jj, detection in enumerate(output_results[ii+1]["detections"]):
                next_detections_idxes |= {
                    detection["obj_id"]: jj
                }
            
            # Smoothen abs pos
            curr_detections_idxes = {}
            for jj, detection in enumerate(result["detections"]):
                obj_id = detection["obj_id"]
                if obj_id in prev_detections_idxes.keys() and obj_id in next_detections_idxes.keys():
                    prev_idx = prev_detections_idxes[obj_id]
                    next_idx = next_detections_idxes[obj_id]
                    xy_est, lat_est, lon_est, velocity_est, yaw_est = interpolate_abs_pos(result["frame"],
                                                                                        output_results[ii-1]["frame"], 
                                                                                        output_results[ii+1]["frame"],
                                                                                        output_results[ii-1]["detections"][prev_idx]["world_coordinate"],
                                                                                        output_results[ii+1]["detections"][next_idx]["world_coordinate"],
                                                                                        output_results[ii-1]["detections"][prev_idx]["velocity"],
                                                                                        output_results[ii+1]["detections"][next_idx]["velocity"],
                                                                                        phi0_deg, lambda0_deg)
                    
                    # Update detection data
                    detection["world_coordinate"][0] = xy_est[0]
                    detection["world_coordinate"][1] = xy_est[1]
                    if len(detection["world_coordinate"]) > 2:
                        frame_ratio = (result["frame"] - output_results[ii-1]["frame"]) / (output_results[ii+1]["frame"] - output_results[ii-1]["frame"])
                        detection["world_coordinate"][2] = output_results[ii-1]["detections"][prev_idx]["world_coordinate"][2] + \
                            (output_results[ii+1]["detections"][next_idx]["world_coordinate"][2] - \
                            output_results[ii-1]["detections"][prev_idx]["world_coordinate"][2]) * frame_ratio
                    
                    detection["latitude"] = lat_est
                    detection["longitude"] = lon_est
                    detection["velocity"] = velocity_est
                    detection["yaw"] = yaw_est
                    
                    curr_detections_idxes |= {
                        detection["obj_id"]: jj
                    }
            
            prev_detections_idxes = curr_detections_idxes
            
    # output result to json
    output_abs_coord_file_path = os.path.join(os.path.dirname(car_abs_coord_file_path), ABS_COORD_JSON_FILE_NAME)

    with open(output_abs_coord_file_path, mode='w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()