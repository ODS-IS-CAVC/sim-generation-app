import argparse
import csv
import json
import math
import os
import shutil

import cv2
import numpy as np
from tqdm import tqdm

from commons import image_util
from commons.constants import *
from yolo.detector import DetectorYOLOv8

ROUNDED_DIGIT_NUM = 6


def calc_dist_ctr_proj(
    img_path,
    theta,
    y,
    camera_elevation_angle,
    camera_height,
    return_extra=False,
):
    """画像から検出した車両情報から車両までの距離を推定する機能です。(中心射影)

    Args:
        img_path (str): 入力画像のパス
        theta (float): 水平視野角θの値(degrees)
        y (float): 車を検出したときの下側の高さ方向のピクセル
        camera_elevation_angle (float): カメラの仰角(degrees)
        camera_height (float): カメラの高さ
        return_extra (float): 計算した距離の他は返すかどうか

    Returns:
        float: 車までの距離
    """
    if not os.path.exists(img_path):
        print(f"File [{img_path}] is not found.")
        return

    # 画像の解像度を(w, h)とする。
    img = image_util.read_image(img_path)
    h, w, _ = img.shape

    # 垂直視野角Φ(phi)を計算する
    theta_rad = math.radians(theta)
    tan_phi_half = (h / w) * math.tan(theta_rad / 2)
    phi = 2 * math.atan(tan_phi_half)

    # 車を検出したときの下向きの視点の角度をψ(psi_y)と呼びます。
    cy = h / 2
    if y == cy and camera_elevation_angle == 0:
        return

    y = y - cy
    tan_psi_y = (y / cy) * math.tan(phi / 2)
    psi_y = math.atan(tan_psi_y)

    # 車までの奥行き方向の距離
    camera_elevation_angle_rad = math.radians(camera_elevation_angle)
    dy = camera_height / math.tan(psi_y - camera_elevation_angle_rad)

    if not return_extra:
        return dy
    return dy, w, h, phi, psi_y


# 対象の相対座標の計算(中心射影方式)
def calc_relative_coord_ctr_proj(
    img_path,
    theta,
    y,
    x,
    camera_elevation_angle,
    camera_height,
    return_extra=False,
):
    """対象の相対座標の計算(中心射影方式)

    Args:
        img_path (str): 入力画像のパス
        theta (float): 水平視野角θの値(degrees)
        y (float): 車を検出したときの下側の高さ方向のピクセル
        x (float): 検出車矩形の中央下部の座標
        camera_elevation_angle (float): カメラの仰角(degrees)
        camera_height (float): カメラの高さ
        return_extra (float): 計算した相対座標の他は返すかどうか

    Returns:
        Tuple[float, float, float]: 対象の相対座標
    """

    # 画像の中心座標
    c_x, c_y = image_util.get_center_coordinates(img_path)

    if return_extra:
        dy, w, h, phi, psi_y = calc_dist_ctr_proj(
            img_path,
            theta,
            y,
            camera_elevation_angle,
            camera_height,
            return_extra=return_extra,
        )
    else:
        dy = calc_dist_ctr_proj(
            img_path,
            theta,
            y,
            camera_elevation_angle,
            camera_height,
            return_extra=return_extra,
        )

    # x方向の距離
    x = x - c_x
    theta_rad = math.radians(theta)
    tan_psi_x = (x / c_x) * math.tan(theta_rad / 2)
    psi_x = math.atan(tan_psi_x)
    dx = dy * tan_psi_x

    # 対象車の空間座標
    # (dx, dy, -1.6)となる(単位m)
    relative_coordinates = (dx, dy, -camera_height)

    # 車までの直線距離
    d = math.sqrt(dx * dx + dy * dy)

    if not return_extra:
        return relative_coordinates

    return (relative_coordinates, w, h, phi, psi_y, psi_x, d)


# 対象の相対座標の計算(等距離射影方式)
def calc_relative_coord_equidistant_proj(
    img_path,
    theta,
    y,
    x,
    camera_elevation_angle,
    camera_height,
    return_extra=False,
):
    """対象の相対座標の計算(等距離射影方式)

    Args:
        img_path (str): 入力画像のパス
        theta (float): 水平視野角θの値(degrees)
        y (float): 車を検出したときの下側の高さ方向のピクセル
        x (float): 検出車矩形の中央下部の座標
        camera_elevation_angle (float): カメラの仰角(degrees)
        camera_height (float): カメラの高さ
        return_extra (float): 計算した相対座標の他は返すかどうか

    Returns:
        Tuple[float, float, float]: 対象の相対座標
    """
    if not os.path.exists(img_path):
        print(f"File [{img_path}] is not found.")
        return

    # 画像の解像度を(w, h)とする。
    img = image_util.read_image(img_path)
    h, w, _ = img.shape

    # 画像中心の座標
    cx, cy = w / 2, h / 2

    theta_rad = math.radians(theta)

    # 垂直方向の視野角Φ
    phi = theta_rad * (h / w)

    # 対象点と画像中心の距離
    dist_to_center = math.sqrt((x - cx)**2 + (y - cy)**2)

    # 対象点への対角方向角
    psi_xy = dist_to_center / w * theta_rad

    # 奥行きピクセル距離
    ptemp = dist_to_center * (1 / math.tan(psi_xy))

    # 対象点への水平方向角
    psi_x = math.atan((x - cx) / ptemp)

    # 対象点への垂直方向角
    psi_y = math.atan((y - cy) / ptemp)

    camera_elevation_angle_rad = math.radians(camera_elevation_angle)
    dy = camera_height / math.tan(psi_y - camera_elevation_angle_rad)
    dx = dy * math.tan(psi_x)

    # 車までの直線距離
    d = math.sqrt(dx**2 + dy**2)

    # 対象車の空間座標
    relative_coordinates = (dx, dy, -camera_height)

    if not return_extra:
        return relative_coordinates

    return (relative_coordinates, w, h, phi, psi_y, psi_x, d)


# 車検出結果及び車の相対座標を可視化する
def visualize_result(image, bbox, obj_name, coord, id):
    """車検出結果及び車の相対座標を可視化する

    Args:
        image (np.ndarray): 画像
        bbox (np.ndarray): 矩形
        obj_name (str): 検出対象（車）
        coord (list): 車の相対座標
        id (int): トラッキングされてい検出車のid

    Returns:
        np.ndarray: 可視化画像
    """
    BBOX_COLOR = (0, 255, 0)
    TEXT_COLOR = (0, 0, 255)
    TEXT_COLOR_BORDER = (255, 255, 255)
    TEXT_FONT = cv2.FONT_HERSHEY_PLAIN
    TEXT_FONT_SCALE = 1.2
    TEXT_THICKNESS = 1
    CENTER_PT_COLOR = (0, 0, 255)
    CENTER_PT_RADIUS = 5
    CENTER_PT_THICKNESS = -1

    new_bbox = [int(x) for x in bbox]
    new_coord = [round(x, 2) for x in coord]
    output_text = (
        f"ID:{id}, {obj_name}: ({new_coord[0]}, {new_coord[1]}, {new_coord[2]})"
    )
    text_pos = (new_bbox[0], new_bbox[1] - 5)

    # draw bbox & relative coord of object
    output_image = np.copy(image)
    output_image = cv2.rectangle(
        output_image,
        (new_bbox[0], new_bbox[1]),
        (new_bbox[2], new_bbox[3]),
        BBOX_COLOR,
        1,
    )
    output_image = cv2.putText(
        output_image,
        output_text,
        text_pos,
        TEXT_FONT,
        TEXT_FONT_SCALE,
        TEXT_COLOR_BORDER,
        TEXT_THICKNESS+1,
    )
    output_image = cv2.putText(
        output_image,
        output_text,
        text_pos,
        TEXT_FONT,
        TEXT_FONT_SCALE,
        TEXT_COLOR,
        TEXT_THICKNESS,
    )

    # draw center image
    w, h = image.shape[1], image.shape[0]
    center_pt = (w // 2, h // 2)
    output_image = cv2.circle(
        output_image, center_pt, CENTER_PT_RADIUS, CENTER_PT_COLOR, CENTER_PT_THICKNESS
    )

    return output_image

# 車の相対座標を検出・推定する
def detect_and_calc(
    input_dir,
    output_dir,
    theta,
    camera_height,
    camera_elevation_angle,
    camera_horizontal_angle,
    proj_mode,
    max_distance_tracker,
    max_dissappear_num_tracker,
):
    """車の相対座標を検出・推定する

    Args:
        input_dir (str): 入力画像フォルダパス
        output_dir (str): 出力結果フォルダパス
        theta (float): 水平視野角θの値(degrees)
        camera_height (float): カメラ高さ
        camera_elevation_angle (float): カメラの仰角(degrees)
        camera_horizontal_angle (float): 進行方向とカメラの水平方向とのなす角度(degrees)
        proj_mode (int): 射影方式 (0: 中心射影方式、1: 等距離射影方式)
        max_distance (double):
            フレーム間で同一オブジェクトと見なす距離(ピクセル距離)
        max_dissappear_frame_num (int):
            検知が途切れた場合に保持し続けるフレーム数。
            一時的に検知が途切れても、このフレーム数以内に復活する場合はトラッキングが途切れない。（同一IDが振られる）

    """

    # load model & detect
    detector = DetectorYOLOv8()
    detector.CONF_THD = DETECTION_CONF_THD
    detector.IOU_THD = DETECTION_IOU_THD
    detector.MAX_DISTANCE_TRACKER = max_distance_tracker
    detector.MAX_DISSAPPEAR_FRAME_NUM_TRACKER = max_dissappear_num_tracker
    
    detector.load_model()
    (
        image_path_list,
        abs_detect_bbox_list,
        rel_detect_bbox_list,
        detect_name_list,
        tracking_id_list,
    ) = detector.detect_ultralytics(
        input_dir, output_dir, target_class=TARGET_DETECTION_CLASS
    )

    data_results = []

    # calculate relative coordinate of objects
    print("Calculate relative coordinate of objects")
    image_num = len(image_path_list)
    warning_detect_imgs = []

    for ii, image_path, detect_bboxes, detect_names, tracking_ids in tqdm(
        zip(
            list(range(image_num)),
            image_path_list,
            abs_detect_bbox_list,
            detect_name_list,
            tracking_id_list,
        ),
        total = image_num,
        desc = "Processing"
    ):
        image_fn = os.path.basename(image_path)
        frame = os.path.splitext(image_fn)[0].split("_")[-1]
        frame = int(frame)
        detections = []

        if len(detect_names) == 0:
            warning_detect_imgs.append(image_fn)
            continue

        input_image = image_util.read_image(image_path)
        output_image = np.copy(input_image)
        relative_dxs = []
        relative_coordinates_list = []

        for jj, detect_name in enumerate(detect_names):
            y = detect_bboxes[jj][3]
            x = (detect_bboxes[jj][0] + detect_bboxes[jj][2]) / 2

            # calculate relative coordinate
            if proj_mode == 0:
                results = calc_relative_coord_ctr_proj(
                    image_path, theta, y, x, camera_elevation_angle, camera_height, True
                )
            elif proj_mode == 1:
                results = calc_relative_coord_equidistant_proj(
                    image_path, theta, y, x, camera_elevation_angle, camera_height, True
                )

            relative_coordinates = results[0]
            w, h = results[1], results[2]
            phi_deg = round(math.degrees(results[3]), ROUNDED_DIGIT_NUM)
            psi_y_deg = round(math.degrees(results[4]), ROUNDED_DIGIT_NUM)
            psi_x_deg = round(math.degrees(results[5]), ROUNDED_DIGIT_NUM)
            dx_camera = round(relative_coordinates[0], ROUNDED_DIGIT_NUM)
            dy_camera = round(relative_coordinates[1], ROUNDED_DIGIT_NUM)
            d_camera = round(results[6], ROUNDED_DIGIT_NUM)
            
            # 進行方向に対してdx、dyの距離を計算する
            camera_horizontal_angle_rad = math.radians(camera_horizontal_angle)
            dx_direction = round(d_camera * math.sin(results[5] + camera_horizontal_angle_rad), ROUNDED_DIGIT_NUM)
            dy_direction = round(d_camera * math.cos(results[5] + camera_horizontal_angle_rad), ROUNDED_DIGIT_NUM)
            
            relative_dxs.append(dx_direction)
            relative_coordinates_list.append([dx_direction, dy_direction, -camera_height])

            obj_id = tracking_ids[jj] + 1

            # [カメラの中心から検出車下部までの幅に対応する角度 (β)]と
            # [カメラの仰角(γ)]との間の差(β-γ)を求めて
            camera_elevation_angle_rad = math.radians(camera_elevation_angle)
            diff_angle = results[4] - camera_elevation_angle_rad

            # if (diff_angle < 0) or (abs(diff_angle) < CAMERA_ELEVATION_ANGLE_DIFF_THD):
            #     print(f"Warning: Object {obj_id} is higher than camera.")
                #continue

            detection_result_elem = {
                "obj_id": obj_id,
                "detection_point": [int(x), int(y)],
                "distance": [dx_direction, dy_direction, d_camera],
                "angle": [psi_x_deg, psi_y_deg]
            }
            detections.append(detection_result_elem)   
        
        # visualize detected object & relative coordinate
        for jj, detect_name in enumerate(detect_names):
            obj_id = tracking_ids[jj] + 1

            output_image = visualize_result(
                output_image,
                detect_bboxes[jj],
                detect_name,
                relative_coordinates_list[jj],
                obj_id,
            )

        # save visualization image
        image_fn_prefix, ext = os.path.splitext(image_fn)
        output_fn = f"{image_fn_prefix}{REL_COORD_IMG_SUFFIX}{ext}"
        output_fpath = os.path.join(output_dir, output_fn)
        image_util.save_image(output_fpath, output_image, image_type=ext)

        data_result = {
            "file": output_fpath,
            "frame": frame,
            "self": {
            },
            "detections": detections
        }
        data_results.append(data_result)

    # print warnings
    for img in warning_detect_imgs:
        print(f"Warning: Cannot detect car in image [{img}]")

    data = {
        "camera_parameter": {
            "aov_horizontal": theta,
            "aov_vertical": phi_deg,
            "image_size": [w, h],    
            "camera_height" : camera_height,
            "camera_elevation_angle" : camera_elevation_angle,
            "camera_horizontal_angle" : camera_horizontal_angle,
            "proj_mode" : proj_mode
        },
        "results": data_results,
    }

    # write to json file
    json_file_name = output_dir + "/" + REL_COORD_JSON_FILE_NAME
    with open(json_file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # 引数をパースする
    parser = argparse.ArgumentParser(description="対象の相対座標を計算し、レーン推定を実施する")
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        default="input",
        help="入力画像フォルダパス",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        default="output",
        help="出力結果フォルダパス",
    )
    parser.add_argument(
        "--pos_est_setting_file",
        type=str,
        required=False,
        default="input/position_estimation_setting.json",
        help="距離推定の設定ファイル",
    )

    # parse input arguments
    args = parser.parse_args()

    input_dir = args.input_dir
    assert isinstance(input_dir, str)

    output_dir = args.output_dir
    assert isinstance(output_dir, str)

    pos_est_setting_file = args.pos_est_setting_file
    assert isinstance(pos_est_setting_file, str)

    # read setting file
    position_estimation_settings = None
    with open(pos_est_setting_file, "r", encoding="utf-8") as f:
        position_estimation_settings = json.load(f)

    # if output directory is existed, remove and recreate
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # detect cars、calculate relative coordinate
    detect_and_calc(
        input_dir,
        output_dir,
        position_estimation_settings["theta"],
        position_estimation_settings["camera_height"],
        position_estimation_settings["camera_elevation_angle"],
        position_estimation_settings["camera_horizontal_angle"],
        position_estimation_settings["proj_mode"],
        position_estimation_settings["max_distance"],
        position_estimation_settings["max_dissappear_frame_num"],
    )


if __name__ == "__main__":
    main()
