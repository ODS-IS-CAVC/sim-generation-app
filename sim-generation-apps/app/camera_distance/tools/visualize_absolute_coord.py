import argparse
import json
import math
import os
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from commons import image_util
from commons.constants import *


def get_coord_car_from_json(abs_coord_file, mperp):
    """jsonファイルから絶対座標の値を所得する関数

    Args:
        abs_coord_file (str): 自車と検出車の絶対座標のjsonファイルパス
        mperp (float): 1ピクセルあたりの距離 (meter per pixel)

    Returns:
        self_coords_info (list): 自車の座標情報
        detected_coords_info (list): 検出車の座標情報
    """
    # Opening JSON file
    file = open(abs_coord_file, "r", encoding="utf-8")
    data = json.load(file)
    file.close()
    results_data = data["results"]

    # coordinates on the image plane of the owned car
    self_coords_info = []
    # coordinates of detected car on the image plane
    detected_coords_info = []
    # the car coordinates in the first frame
    coord_origin = results_data[0]["self"]["world_coordinate"]

    for item in results_data:
        if "self" not in item:
            continue

        file = item["file"]
        self_coord_x = item["self"]["world_coordinate"][0]
        self_coord_y = item["self"]["world_coordinate"][1]
        self_coord = [
            (self_coord_x - coord_origin[0]) / mperp,
            (self_coord_y - coord_origin[1]) / mperp,
        ]
        self_coords_info.append(self_coord)

        detection_infos = []
        for detection in item["detections"]:
            obj_id = detection["obj_id"]
            detect_coord_x, detect_coord_y = (
                detection["world_coordinate"][0],
                detection["world_coordinate"][1],
            )
            detect_coord = [
                (detect_coord_x - coord_origin[0]) / mperp,
                (detect_coord_y - coord_origin[1]) / mperp,
            ]
            detection_infos.append({"obj_id": obj_id, "coord": detect_coord})

        detected_coords_info.append({"file": file, "detection_infos": detection_infos})

    return self_coords_info, detected_coords_info


def gen_abs_coord_img(self_coords_info, detected_coords_info, colors, mperp):
    """座標を描画する関数

    Args:
        self_coords_info (list): 自車の座標情報
        detected_coords_info (list): 検出車の座標情報
        colors (list): 検出車の色
    """

    DPI = 100
    figsize = (VISUALIZE_IMG_SIZE[0] / DPI, VISUALIZE_IMG_SIZE[1] / DPI)
    fig = plt.figure(figsize=figsize, dpi=DPI)
    ax = fig.add_axes((0, 0, 1, 1))

    # Move left y-axis and bottom x-axis to centre, passing through (0,0)
    ax.spines["left"].set_position("center")
    ax.spines["bottom"].set_position("center")

    # Eliminate upper and right axes
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    # Show ticks in the left and lower axes only
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    plt.xlim([-VISUALIZE_IMG_SIZE[0] // 2, VISUALIZE_IMG_SIZE[0] // 2])
    plt.ylim([-VISUALIZE_IMG_SIZE[1] // 2, VISUALIZE_IMG_SIZE[1] // 2])

    # Plot self car coords
    x1 = [item[0] for item in self_coords_info]
    y1 = [item[1] for item in self_coords_info]
    plt.plot(x1, y1, "ro", c=SELF_COORD_COLOR, ms=COORD_RADIUS, label="自車")

    # Plot detected car coords
    obj_ids = list(set([item["obj_id"] for item in detected_coords_info]))
    number_of_cars = len(obj_ids)

    for ii in range(number_of_cars):
        obj_id = obj_ids[ii]
        detected_coords_tmp = []
        for item in detected_coords_info:
            if item["obj_id"] == obj_id:
                detected_coords_tmp.append(item["coord"])

        x2 = [ii[0] for ii in detected_coords_tmp]
        y2 = [ii[1] for ii in detected_coords_tmp]
        plt.plot(
            x2, y2, "ro", color=colors[obj_id], ms=COORD_RADIUS, label=f"車{obj_id}"
        )

    plt.legend(loc="upper right", framealpha=1, fontsize="large")
    ax.set_facecolor("#E0E0E0")
    visualized_coord_img = image_util.fig2image()

    # get zoom part near current position
    ax.get_legend().remove()
    plt.xlim(
        self_coords_info[-1][0] - math.ceil(ZOOM_RANGE / mperp),
        self_coords_info[-1][0] + math.ceil(ZOOM_RANGE / mperp),
    )
    plt.ylim(
        self_coords_info[-1][1] - math.ceil(ZOOM_RANGE / mperp),
        self_coords_info[-1][1] + math.ceil(ZOOM_RANGE / mperp),
    )
    plt.axis("off")
    zoom_img = image_util.fig2image()
    plt.close()

    output_img = cv2.vconcat([zoom_img, visualized_coord_img])

    return output_img


def gen_batch_abs_coord_img(current_coords_info, corrected_coords_info, roads_info):
    """座標を描画する関数

    Args:
        current_coords_info (list): 現在車両座標情報
        corrected_coords_info (list): 補正後の車両座標情報
        roads_info (dict): レーン座標情報
    """
    LANE_MARK_COLORS = [# RGB color
        (255,165,0),     #orange
        (0,255,0),      #green
        (0,255,255),    #aqua
        (255,255,0),    #yellow
        (0,0,255),      #blue
        (255,192,203),  #pink
        (210,105,30),   #chocolate
    ]
    output_images = []
    for i in tqdm(range(len(current_coords_info)), desc="Processing"):
        DPI = 100
        figsize = (VISUALIZE_IMG_SIZE[0] / DPI, VISUALIZE_IMG_SIZE[1] / DPI)
        fig = plt.figure(figsize=figsize, dpi=DPI)
        ax = fig.add_axes((0, 0, 1, 1))

        # Get self car coords
        x1 = current_coords_info[i][1]
        y1 = current_coords_info[i][0]
        
        # Set x limit and y limit
        ax.set_xlim(x1 - 0.00015, x1 + 0.00015)
        ax.set_ylim(y1 - 0.00015, y1 + 0.00015)
        
        # Plot lane coords
        # show_legend = True
        show_legends = []
        for road in roads_info["roads"]:
            for lane in road["lanes"]:
                x2 = [ii[1] for ii in lane["coordinate"]]
                y2 = [ii[0] for ii in lane["coordinate"]]
                if lane["lane_id"] not in show_legends:
                    plt.plot(
                        x2, y2, "o", color=tuple(c/255 for c in LANE_MARK_COLORS[int(lane['lane_id'])-1]), ms=COORD_RADIUS, label=f"Lane {lane['lane_id']}"
                    )
                    show_legends.append(lane["lane_id"])
                else:
                    plt.plot(
                        x2, y2, "o", color=tuple(c/255 for c in LANE_MARK_COLORS[int(lane['lane_id'])-1]), ms=COORD_RADIUS
                    )
                    
        # Plot current car coords
        plt.plot(x1, y1, "s", c=SELF_COORD_COLOR, ms=COORD_RADIUS, label="Current car")

        plt.legend(loc="upper left", framealpha=1, fontsize="large")
        ax.set_facecolor("#E0E0E0")
        plt.axis("off")
        
        visualized_coord_img = image_util.fig2image()
        
        # Plot corrected car coords
        x1_corrected = corrected_coords_info[i][1]
        y1_corrected = corrected_coords_info[i][0]
        plt.plot(x1_corrected, y1_corrected, "s", c="purple", ms=COORD_RADIUS, label="Corrected car")
        
        # Plot arrow
        plt.arrow(x1, y1, (x1_corrected - x1) * 0.5, (y1_corrected - y1) * 0.5, width=0.000001)
        
        plt.legend(loc="upper left", framealpha=1, fontsize="large")
        plt.axis("off")
        
        visualized_coord_img_2 = image_util.fig2image()
        plt.close()
        
        # Create border between images
        height, width = visualized_coord_img.shape[:2]
        border_height = 5
        border = np.zeros((border_height, width, 3), dtype=np.uint8)
        
        output_img = cv2.vconcat([visualized_coord_img, border, visualized_coord_img_2])
        output_images.append(output_img)
    
    return output_images

def merg_result_image(detect_img, visualized_coord_img):
    detect_img_size = (detect_img.shape[1], detect_img.shape[0])
    visualized_img_size = (visualized_coord_img.shape[1], visualized_coord_img.shape[0])

    output_size_h = visualized_img_size[1]
    detect_img_resized_w = int((output_size_h / detect_img_size[1]) * detect_img_size[0])

    # resize detected image
    detect_img = cv2.resize(detect_img, (detect_img_resized_w, output_size_h))

    # merge images
    merged_image = cv2.hconcat([detect_img, visualized_coord_img])

    return merged_image


def visualize_abs_coords(self_coords_info, detected_coords_info, output_path, mperp):
    """画像上の推定座標を表す関数

    Args:
        self_coords_info (list): 自車の座標情報
        detected_coords_info (list): 検出車の座標情報
        output_path (str): 出力フォルダパス
    """
    os.makedirs(f"{output_path}", exist_ok=True)

    # Number of detected cars
    obj_ids = set()
    for detected_info in detected_coords_info:
        for item in detected_info["detection_infos"]:
            obj_ids.add(item["obj_id"])
    obj_ids = list(obj_ids)

    # Detected cars color list
    colors = {}
    color_idx = 0
    while len(colors) < len(obj_ids):
        r = np.random.choice(RANDOM_COLOR_VALUES)
        g = np.random.choice(RANDOM_COLOR_VALUES)
        b = np.random.choice(RANDOM_COLOR_VALUES)
        color = (r, g, b)
        if (color == SELF_COORD_COLOR) or (color in colors.values()):
            continue
        colors[obj_ids[color_idx]] = color
        color_idx += 1

    # Loop over all frames
    detected_car_coords_info = []
    self_car_coords_info = []

    for ii, item in enumerate(tqdm(detected_coords_info, desc="Processing")):
        detected_img_file = item["file"]
        detection_infos = item["detection_infos"]

        image_fn = os.path.basename(detected_img_file)
        file_name, file_ext = os.path.splitext(image_fn)
        file_name = file_name.split(REL_COORD_IMG_SUFFIX)[0]

        # coords from start to current
        detected_car_coords_info.extend(detection_infos)
        self_car_coords_info.append(self_coords_info[ii])

        # visualized & merge
        visualized_coord_img = gen_abs_coord_img(
            self_car_coords_info, detected_car_coords_info, colors, mperp
        )
        detected_img = image_util.read_image(detected_img_file)

        # save image
        output_img = merg_result_image(detected_img, visualized_coord_img)
        output_img_path = os.path.join(
            output_path, f"{file_name}{ABS_COORD_IMG_SUFFIX}{file_ext}"
        )
        image_util.save_image(output_img_path, output_img)


def main():
    # 引数をパースする
    parser = argparse.ArgumentParser(
        description="推定によって計算した、自車の座標と検出車の座標を簡単に可視化する"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="出力フォルダパス（タイプ：string）",
    )
    parser.add_argument(
        "--abs_coord_file",
        type=str,
        required=True,
        help="自車と検出車の絶対座標のjsonファイルパス（タイプ：string）",
    )
    parser.add_argument(
        "--mperp",
        type=float,
        required=False,
        default=METER_PER_PIXEL,
        help="1ピクセルあたりの距離（meter）（タイプ：float）",
    )

    # 入力引数をパースする
    args = parser.parse_args()

    output_path = args.output_path
    assert isinstance(output_path, str)

    abs_coord_file = args.abs_coord_file
    assert isinstance(abs_coord_file, str)

    mperp = args.mperp
    assert isinstance(mperp, float)

    # execute
    self_coords_info, detected_coords_info = get_coord_car_from_json(
        abs_coord_file, mperp
    )
    visualize_abs_coords(self_coords_info, detected_coords_info, output_path, mperp)


if __name__ == "__main__":
    main()
