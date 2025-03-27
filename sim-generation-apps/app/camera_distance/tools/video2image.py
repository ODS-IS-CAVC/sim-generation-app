import argparse
import os
import shutil
import av

import numpy as np
import pandas as pd


def video_to_images(input_path, output_path, frame_skip=0, start_time=0, end_time=-1, gps_coord_file=None):
    """動画から画像を抽出する関数

    Args:
        input_path (str): 動画ファイルパス(タイプ：string）
        output_path (str): 出力フォルダパス(タイプ：string）
        frame_skip (int): frame-skipは任意. Defaults to 0.
        start_time (float): 動画からの画像抽出開始時間. Defaults to 0.
        end_time (float): 動画からの画像抽出終了時間. Defaults to -1.
        gps_coord_file (str): GPSデータファイルパス. Defaults to None.
    """

    # 出力フォルダ作成
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    # 動画名を取得する
    file = os.path.basename(input_path)
    name = os.path.splitext(file)[0]
    # 動画をロードする
    container = av.open(input_path)

    video_stream = container.streams.video[0]
    #video_fps = video_stream.codec_context.framerate.numerator
    video_resolution = video_stream.codec_context.width, video_stream.codec_context.height
    video_duration = float(video_stream.duration * video_stream.time_base)
    video_fps = round(video_stream.frames / video_duration)
    print(f'Duration: {video_duration}\nFps: {video_fps}\nResolution: {video_resolution}')

    if (start_time < 0 or start_time >= video_duration):
        print('Warning: 指定した開始時間が不正です。')
        return
    if ((end_time != -1) and (end_time <= 0 or end_time > video_duration)):
        print('Warning: 指定した終了時間が不正です。')
        return

    gps_frames = None
    if gps_coord_file is not None:
        gps_data = pd.read_csv(gps_coord_file, delimiter=',', dtype=str)
        gps_data_time = gps_data['time'].values
        col_names = gps_data.columns.values
        if 'frame' not in col_names:
            data_num = len(gps_data_time)
            gps_data['frame'] = np.zeros(data_num, dtype=int)
            for ii in range(data_num):
                time_val = gps_data_time[ii]
                time, frame = time_val.split(':')[:2]
                frame = int(time) * video_fps + int(frame)
                gps_data.loc[ii, 'frame'] = frame
        else:
            gps_data['frame'] = gps_data['frame'].astype(int)
        gps_frames = gps_data['frame'].values

    start_idx = int(start_time * video_fps)
    end_idx = -1 if (end_time == -1) else int(end_time * video_fps)

    # フレームを保存するためのループ
    using_gps_frame = (gps_frames is not None)
    using_skip_frame = (frame_skip != 0)
    using_gps_skip_frame = (using_gps_frame and using_skip_frame)

    for ii, frame in enumerate(container.decode(video=0)):
        if (ii < start_idx):
            continue
        if (end_idx != -1 and ii > end_idx):
            break

        if (using_gps_skip_frame and ((ii in gps_frames) or ((ii-start_idx) % (frame_skip + 1) == 0))) \
            or (using_skip_frame and (not using_gps_skip_frame) and ((ii-start_idx) % (frame_skip + 1) == 0)) \
            or (using_gps_frame and (not using_gps_skip_frame) and (ii in gps_frames)) \
            or ((not using_skip_frame) and ( not using_gps_frame) and ((ii-start_idx) % (frame_skip + 1) == 0)):

            output_fn = name + "_%05d.jpg" % ii
            img_pil = frame.to_image()
            img_pil.save(output_path + "/" + output_fn)
            print(output_fn)


def main():
    # 引数をパースする
    parser = argparse.ArgumentParser(description="動画からの画像切り出し機能")
    parser.add_argument(
        "--input_path",
        type=str,
        required=True,
        help="動画ファイルパス（タイプ：string）",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="出力フォルダパス（タイプ：string）",
    )
    parser.add_argument(
        "--frame_skip",
        type=int,
        required=False,
        default=0,
        help="frame-skipは任意（タイプ：int; default=0）",
    )
    parser.add_argument(
        "--start_time",
        type=float,
        required=False,
        default=0.0,
        help="動画からの画像抽出開始時間（タイプ：float; default=0.0）",
    )
    parser.add_argument(
        "--end_time",
        type=float,
        required=False,
        default=-1.0,
        help="動画からの画像抽出終了時間（タイプ：float; default=-1）",
    )
    parser.add_argument(
        "--gps_coord_file",
        type=str,
        required=False,
        default=None,
        help="GPSデータファイルパス",
    )

    # 入力引数をパースする
    args = parser.parse_args()

    input_path = args.input_path
    assert isinstance(input_path, str)

    output_path = args.output_path
    assert isinstance(output_path, str)

    frame_skip = args.frame_skip
    assert isinstance(frame_skip, int)

    start_time = args.start_time
    assert isinstance(start_time, float)

    end_time = args.end_time
    assert isinstance(end_time, float)

    gps_coord_file = args.gps_coord_file

    video_to_images(
        input_path=input_path,
        output_path=output_path,
        frame_skip=frame_skip,
        start_time=start_time,
        end_time=end_time,
        gps_coord_file=gps_coord_file
    )


if __name__ == "__main__":
    main()
