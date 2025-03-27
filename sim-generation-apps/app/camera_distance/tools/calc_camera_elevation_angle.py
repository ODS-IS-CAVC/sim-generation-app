import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import math
import cv2
import numpy as np

from commons.image_util import read_image
from commons.constants import *
from commons.math_util import calc_line_weight, find_two_line_intersect


class ImageSelection:
    DISPLAY_IMAGE_POS = (100, 0)
    DISPLAY_IMAGE_H = 960
    DISPLAY_IMAGE_W = None
    POINT_RADIUS = 6
    POINT_COLOR = [0, 0, 255]
    LINE_COLOR = [255, 0, 0]
    LINE_THICKNESS = 2
    TARGET_POINT_COLOR = [0, 255, 0]
    MAX_SELECTED_POINT = 4

    def __init__(self, image_path, selection_method) -> None:
        self.image_path = image_path
        self.image = read_image(self.image_path)
        self.selected_image = np.copy(self.image)
        self.org_size = (self.image.shape[1], self.image.shape[0])
        self.selected_pts = []
        self.org_selected_pts = []
        self.intersect_pt = []
        self.winname = "image"
        self.selection_method = selection_method

        # resize display image
        self.ratio = self.DISPLAY_IMAGE_H / self.org_size[1]
        self.DISPLAY_IMAGE_W = int(self.ratio * self.org_size[0])
        self.selected_image = cv2.resize(self.image, (self.DISPLAY_IMAGE_W, self.DISPLAY_IMAGE_H))

    def draw(self, is_add_point=True, is_redraw=False):
        if is_redraw:
            self.selected_image = cv2.resize(self.image, (self.DISPLAY_IMAGE_W, self.DISPLAY_IMAGE_H))

        # draw center point of image
        h, w = self.selected_image.shape[:-1]
        self.selected_image = cv2.circle(self.selected_image, (w//2,h//2), self.POINT_RADIUS, self.POINT_COLOR, -1)

        # select intersect point
        if self.selection_method == 0:
            self.selected_image = cv2.circle(self.selected_image, self.selected_pts[0], self.POINT_RADIUS, self.TARGET_POINT_COLOR, -1)
            return

        # points
        for ii in range(len(self.selected_pts)):
            if is_add_point and (ii < len(self.selected_pts)-1):
                continue
            x, y = self.selected_pts[ii]
            self.selected_image = cv2.circle(self.selected_image, (x,y), self.POINT_RADIUS, self.POINT_COLOR, -1)

        # line through points
        line_num = len(self.selected_pts) // 2
        for ii in range(line_num):
            p1 = self.selected_pts[2*ii]
            p2 = self.selected_pts[2*ii+1]
            m, b = calc_line_weight(p1, p2)
            start_pt = [0, int(m*0 + b)]
            end_pt = [self.DISPLAY_IMAGE_W, int(m*self.DISPLAY_IMAGE_W + b)]
            self.selected_image = cv2.line(self.selected_image, start_pt, end_pt, self.LINE_COLOR, self.LINE_THICKNESS)
            
        # intersect point
        if line_num == 2:
            intersect_x, intersect_y = find_two_line_intersect(self.selected_pts[0], self.selected_pts[1],
                                                            self.selected_pts[2], self.selected_pts[3])
            intersect_x, intersect_y = int(intersect_x), int(intersect_y)
            self.selected_image = cv2.circle(self.selected_image, (intersect_x, intersect_y), self.POINT_RADIUS, self.TARGET_POINT_COLOR, -1)

            org_intersect_x, org_intersect_y = int(intersect_x / self.ratio), int(intersect_y / self.ratio)
            self.intersect_pt = [org_intersect_x, org_intersect_y]

    def handle_click_event(self, event, x, y, flags, params):
        # checking for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"(x, y): {x}, {y}")
            if len(self.selected_pts) >= self.MAX_SELECTED_POINT:
                return
            
            org_x, org_y = int(x / self.ratio), int(y / self.ratio)
            is_redraw = False

            if self.selection_method == 0:
                if len(self.selected_pts) == 0:
                    self.selected_pts.append([x,y])
                else:
                    self.selected_pts[0] = [x,y]
                    is_redraw = True
                self.intersect_pt = [org_x, org_y]
            else:
                self.selected_pts.append([x,y])
                self.org_selected_pts.append([org_x, org_y])

            # draw selected point & line contains selected point
            self.draw(is_add_point=True, is_redraw=is_redraw)
            cv2.imshow(self.winname, self.selected_image)

        # checking for right mouse clicks, undo
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(self.selected_pts) > 0:
                self.selected_pts.pop()
                self.org_selected_pts.pop()

            # redraw & display
            self.draw(is_add_point=False, is_redraw=True)
            cv2.imshow(self.winname, self.selected_image)
    
    def display_for_select(self):
        cv2.imshow(self.winname, self.selected_image)
        cv2.moveWindow(self.winname, self.DISPLAY_IMAGE_POS[0], self.DISPLAY_IMAGE_POS[1])

        # setting mouse handler for the image and calling the callback
        cv2.setMouseCallback(self.winname, self.handle_click_event)

        key = cv2.waitKey(0)
        if (key == 27) or (key == 13): # Esc | Enter
            cv2.destroyWindow(self.winname)


def calc_cam_angle(theta, w, h, intersect_pt, proj_mode):
    """カメラの仰角を計算する

    Args:
        theta (float): 水平視野角θの値(degrees)
        w (int): 画像の幅
        h (int): 画像の高さ
        intersect_pt (list): カメラから地面と平行な方向への視線の画像上の点
        proj_mode (int): 射影方式 (0: 中心射影方式、1: 等距離射影方式)
    """
    camera_elevation_angle = 0
    theta_rad = math.radians(theta)
    camera_elevation = intersect_pt[1] - h//2
    camera_horizontal = w//2- intersect_pt[0]

    if proj_mode == 1:
        # 垂直視野角を計算する
        phi = theta_rad * (h / w)

        # カメラの仰角
        camera_elevation_angle = phi * camera_elevation/h
        
        # 進行方向とカメラの水平方向とのなす角度
        camera_horizontal_angle = theta_rad * camera_horizontal / w
    
    elif proj_mode == 0:
        # 垂直視野角を計算する
        tan_phi_half = (h / w) * math.tan(theta_rad / 2)
        phi = 2 * math.atan(tan_phi_half)

        # カメラの仰角
        cy = h / 2
        tan_lambda = (camera_elevation / cy) * math.tan(phi / 2)
        camera_elevation_angle = math.atan(tan_lambda)
        
        # 進行方向とカメラの水平方向とのなす角度
        cw = w / 2
        tan_psi_ch = (camera_horizontal / cw) * math.tan(theta_rad / 2)
        camera_horizontal_angle = math.atan(tan_psi_ch)

    return camera_elevation_angle, camera_horizontal_angle


def main():
    # 引数をパースする
    parser = argparse.ArgumentParser(description="カメラの仰角を計算する")
    parser.add_argument(
        "--input_image_path",
        type=str,
        required=True,
        help="入力画像ファイルパス",
    )
    parser.add_argument(
        "--theta",
        type=float,
        required=False,
        default=f"{HORIZONTAL_FOV}",
        help="水平視野角θの値（degrees）",
    )
    parser.add_argument(
        "--proj_mode",
        type=int,
        required=False,
        default=0,
        help="射影方式（0: 中心射影方式、1: 等距離射影方式）",
    )

    # parse input arguments
    args = parser.parse_args()

    input_image_path = args.input_image_path
    assert isinstance(input_image_path, str)

    theta = args.theta
    assert isinstance(theta, float)

    proj_mode = args.proj_mode
    assert isinstance(proj_mode, int)

    input_image = read_image(input_image_path)
    h, w = input_image.shape[:-1]

    # カメラから地面と平行な方向への視線の画像上の点
    # selection_method: 0(方法1:一般的な車高を基準に想定で決める), 1(方法2:消失点から求める)
    selection_method = 0
    selector = ImageSelection(input_image_path, selection_method)
    selector.display_for_select()
    intersect_pt = selector.intersect_pt
    print(f"カメラから地面と平行な方向への視線の画像上の点: {intersect_pt}")

    # カメラの仰角を求める
    camera_elevation_angle, camera_horizontal_angle = calc_cam_angle(theta, w, h, intersect_pt, proj_mode)
    print(f"カメラの仰角を求める: {math.degrees(camera_elevation_angle)}")
    print(f"進行方向とカメラの水平方向とのなす角度: {math.degrees(camera_horizontal_angle)}")


if __name__ == "__main__":
    main()
