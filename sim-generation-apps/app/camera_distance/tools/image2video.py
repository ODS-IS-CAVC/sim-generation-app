import os
import glob
from tqdm import tqdm
import cv2


input_dir = "input_dir"# 入力する画像が保存されたフォルダ名
output_path = input_dir + '_cv' + '.mp4'    # 作成する 動画ファイル
print(output_path)

# フォルダ内の画像のファイルリストを取得する
#files  = glob.glob(os.path.join(input_dir, '*.png'))
files = glob.glob(os.path.join(input_dir, '*overlay.jpg'))
files.sort()
frames=len(files)
assert frames != 0, 'not found image file'    # 画像ファイルが見つからない

# 最初の画像の情報を取得する
img = cv2.imread(files[0])
h, w, channels = img.shape[:3]

# 作成する動画
codec = cv2.VideoWriter_fourcc(*'mp4v')
#codec = cv2.VideoWriter_fourcc(*'avc1')
writer = cv2.VideoWriter(output_path, codec, 30, (w, h),1)

bar = tqdm(total=frames, dynamic_ncols=True)
for f in files:
    # 画像を1枚ずつ読み込んで 動画へ出力する
    img = cv2.imread(f)
    writer.write(img)   
    bar.update(1)
    
bar.close()
writer.release()
