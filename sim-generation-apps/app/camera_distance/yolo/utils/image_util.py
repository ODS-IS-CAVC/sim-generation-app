import os
import numpy as np
import cv2

def read_image_unicode_path(img_path):
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    return img

def write_image_unicode_path(img_path, img):
    file_name, file_ext = os.path.splitext(img_path)
    rtn_code, img_buffer = cv2.imencode(file_ext, img)
    img_buffer.tofile(img_path)
