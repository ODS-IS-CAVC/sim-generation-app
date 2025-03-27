from pathlib import Path
import glob
import csv

#前と後ろそれぞれFRAME_RANGEだけ見て外れ値を補正
FRAME_RANGE = 30
#平均と比べて外れ値とみなす基準
DEV_FROM_MEAN = 0.8



input_dir = "input_dir"

#input_dir内のcsvファイルを集計
paths = glob.glob(input_dir+"\*lane_info.csv")
lane_infos = []
for path in paths:
    with open(path) as f:
        reader  = csv.reader(f)
        li = []
        for row in reader:
            li.append(row)
        lane_infos.append(li)

#各フレームで検出された車線数
lane_count = []
for lane_info in lane_infos:
    if len(lane_info) <= 1:#レーンが検出されていない場合
        lane_count.append(0)
    else:
        lane_count.append((int)(lane_info[len(lane_info) - 1][0]))


lane_count_corrected =[]
for i in range(0,len(lane_count)):
    sum = 0
    num = 0
    for j in range(i+1,min(i + FRAME_RANGE,len(lane_count))):
        sum += lane_count[j]
        num += 1
    for j in range(max(0,i - FRAME_RANGE),i):
        sum += lane_count[j]
        num += 1
    if abs(sum/num - lane_count[i]) > DEV_FROM_MEAN :
        lane_count_corrected.append(round(sum/num))
    else:
        lane_count_corrected.append(lane_count[i])

for i in range(0,len(lane_count)):
    print(i,lane_count[i],lane_count_corrected[i],"correct!" if lane_count[i] != lane_count_corrected[i] else "        ")
