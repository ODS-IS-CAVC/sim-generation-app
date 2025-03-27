import os
from pathlib import Path
from typing import Tuple, List
from numpy import random
import torch
import sys

from ultralytics import YOLO
sys.path.append(os.path.dirname(__file__))
from commons.constants import YOLO_V8_MODEL_FILE, YOLOCLASSES, DEPRICATE_IOU_THD
from commons.math_util import calc_IoU
from utils.datasets import LoadBGRImages
from utils.general import set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized
from utils.image_util import write_image_unicode_path

class DetectorBase:
    # CONF_THD = 0.8
    # IOU_THD = 0.45
    CONF_THD = 0.25
    IOU_THD = 0.45
    OFFSET_THD = 0.05

    def __init__(self, device='cpu'):
        self.augment = False
        self.agnostic_nms = False
        self.save_img = False
        self.save_txt = True
        self.save_conf = True
        self.classify = False

        set_logging()
        self.device = select_device(device)

        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

class DetectorYOLOv8(DetectorBase):
    def load_model(self, weights=YOLO_V8_MODEL_FILE, image_size=640):
        self.model = YOLO(weights)
        self.image_size = image_size
    
    def detect_ultralytics(self, input_path, output_path, target_class=["car"]) -> Tuple[List, List, List, List]:
        # Directories
        save_dir = Path(output_path)
        (save_dir / 'labels' if self.save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir     
        txt_path = str(save_dir / 'labels' / 'labels.txt')
        if self.save_txt:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f'image_name, class_id, class_name, x, y, w, h')
                f.write(', conf\n') if self.save_conf else f.write('\n')
                
        # Set Dataloader
        dataset = LoadBGRImages(input_path, img_size=self.image_size)

        # Convert classes
        target_class = [YOLOCLASSES[t] for t in target_class]

        # Get names and colors
        random.seed(0)
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
        
        detected_objects: list = []
        detected_object_names: list = []
        relative_detected_objects: list = []
        # List of tracking ids detected in each image
        tracking_ids: list = []
        idx = 0

        for path, img, img0 in dataset:
            image_fn = os.path.basename(path)
            print(idx, image_fn)

            plotted = False
            detected_objects.append([])
            detected_object_names.append([])
            relative_detected_objects.append([])
            
            # Run inference
            t1 = time_synchronized()
            results = self.model.track(img0, classes=target_class, conf=self.CONF_THD, iou=self.IOU_THD, imgsz=self.image_size, 
                                         augment=self.augment, half=self.half, device=self.device, agnostic_nms=self.agnostic_nms,
                                         persist=True)
            t2 = time_synchronized()
            
            boxes = results[0].boxes
            if boxes.id is None:
                boxes_xyxy, boxes_xywh, boxes_conf, boxes_cls, boxes_ids = ([], [], [], [], [])
            else:
                boxes_xyxy = boxes.xyxy.cpu()
                boxes_xywh = boxes.xywh.cpu()
                boxes_conf = boxes.conf.cpu()
                boxes_cls = boxes.cls.cpu()
                boxes_ids = boxes.id.int().cpu().tolist()
            
            gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]
            s = ""
            if len(boxes_xyxy):
                # Print results
                for c in boxes_cls.unique():
                    n = (boxes_cls == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # remove deplicate detected objects based on IoU
                img_width = img0.shape[1]
                offset = int(self.OFFSET_THD * img_width)

                del_idxes = []
                for i, xyxyi in enumerate(boxes_xyxy):
                    if i in del_idxes:
                        continue
                    # check detected objects that are entirely in image
                    if xyxyi[0] < offset or xyxyi[2] > (img_width - offset):
                        del_idxes.append(i)
                        continue

                    for j in range(0, i):
                        xyxyj = boxes_xyxy[j]
                        if j in del_idxes:
                            continue
                        if calc_IoU(xyxyi, xyxyj) > DEPRICATE_IOU_THD:
                            del_idxes.append(j)

                if len(boxes_xyxy) > len(del_idxes):
                    boxes_xyxy, boxes_xywh, boxes_conf, boxes_cls, boxes_ids = zip(
                        *[(boxes_xyxy[i], boxes_xywh[i], boxes_conf[i], boxes_cls[i], boxes_ids[i]) for i in range(len(boxes_xyxy)) if i not in del_idxes])
                else:
                    boxes_xyxy, boxes_xywh, boxes_conf, boxes_cls, boxes_ids = ([], [], [], [], [])
                    
                # Write results
                tracking_ids.append(list(boxes_ids)[::-1])
                for i, xyxy in enumerate(reversed(boxes_xyxy)):
                    conf = boxes_conf[i]
                    cls = boxes_cls[i]
                    class_id = int(cls)
                    class_name = names[class_id]
                    label = f'{class_name} {conf:.2f}'

                    # absolute coordinate of bounding-box (xmin, ymin, xmax, ymax)
                    xmin, ymin, xmax, ymax = [x.numpy().tolist() for x in xyxy]
                    detected_objects[idx].append([xmin, ymin, xmax, ymax])
                    detected_object_names[idx].append(class_name)
                    
                    # relative coordinate of bounding-box (x/W, y/H, w/W, h/H)
                    xywh = (boxes_xywh[i] / gn).tolist()
                    relative_detected_objects[idx].append(xywh)
                    
                    if self.save_txt:  # Write to file
                        
                        line = (*xywh, conf) if self.save_conf else xywh  # label format
                        with open(txt_path, 'a', encoding='utf-8') as f:
                            text = f'{image_fn}, {class_id}, {class_name}, '
                            text += ('%g, ' * (len(line)-1) + '%g').rstrip() % line + '\n'
                            f.write(text)

                    plot_one_box(xyxy, img0, label=None, color=colors[int(cls)], line_thickness=1)
                    plotted = True
            else:
                tracking_ids.append([])

            # Print time (inference + NMS)
            print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Prediction')

            if self.save_img and plotted:
                output_fn = os.path.basename(path)
                output_fpath = os.path.join(save_dir, output_fn)
                write_image_unicode_path(output_fpath, img0)

            idx += 1

        return dataset.images, detected_objects, relative_detected_objects, detected_object_names, tracking_ids