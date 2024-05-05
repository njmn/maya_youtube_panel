import os
import re
import shutil
import tempfile
import cv2
from pytube import YouTube
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
from maya import cmds
from PySide2 import QtWidgets


def get_maya_main_window() -> QtWidgets.QWidget:
    '''
    mayaのメインウィンドウを取得する

    Returns:
        QtWidgets.QWidget: メインウィンドウ
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def create_tmp_path() -> str:
    '''
    mp4やjpgファイルを保存するための一時ディレクトリのパスを取得する

    Returns:
        str: 一時ディレクトリのパス
    '''
    return os.path.join(tempfile.gettempdir(), 'youtube_panel')


def convert_video_to_images(video_path):
    '''
    video_pathで指定されたmp4をフレームごとに画像に変換し保存する

    Args:
        video_path (str): mp4ファイルのパス
    '''
    video_dir = os.path.dirname(video_path)
    # ビデオファイルを読み込む
    video = cv2.VideoCapture(video_path)

    # フレームを抽出して画像に変換し保存する
    current_frame = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        current_frame_str = str(current_frame).zfill(7)
        image_path = os.path.join(video_dir, f"frame_{current_frame_str}.jpg")
        cv2.imwrite(image_path, frame)

        current_frame += 1

    # リソースを解放する
    video.release()


def download(url):
    '''
    urlで指定されたYouTubeの動画をダウンロードし、フレームごとに画像に変換して保存する

    Args:
        url (str): YouTubeのURL
    '''

    try:
        yt = YouTube(url)
        stream = (
            yt.streams.filter(progressive=True, file_extension='mp4')
            .order_by('resolution')
            .desc()
            .first()
        )
        tmp_path = create_tmp_path()
        shutil.rmtree(tmp_path)
        file_path = stream.download(output_path=tmp_path, filename="tmp.mp4")
        convert_video_to_images(file_path)
    except Exception as e:
        print(e)


def set_aspect_ratio(transform, target_path):
    '''
    画像からaspect比を取得し、imagePlaneのScaleをその比に合わせて設定する

    Args:
        transform (str): imagePlaneのトランスフォームノード名
        target_path (str): 画像ファイルが格納されているディレクトリのパス
    '''

    img = cv2.imread(os.path.join(target_path, "frame_0000000.jpg"))
    height, width, _ = img.shape
    aspect_ratio = width / height
    scale_y = cmds.getAttr(f"{transform}.scaleY")
    scale_x = scale_y * aspect_ratio
    cmds.setAttr(f"{transform}.scaleX", scale_x)


def set_playbackOptions(target_path):
    '''
    target_path内の画像ファイルの最後のフレーム番号を取得し、再生範囲を設定する

    Args:
        target_path (str): 画像ファイルが格納されているディレクトリのパス
    '''
    # target_path内で、 frame_{number}.jpg の最後のファイルを取得
    files = os.listdir(target_path)
    files.sort()
    last_frame = None
    print(files)
    count = 0
    # 10回の試行で見つからなかったら終了
    while files or count < 10:
        last_file = files.pop()
        PATTERN = r"frame_(\d{7}).jpg"
        match = re.match(PATTERN, last_file)
        if match:
            last_frame = match.group(1)
            break
        count += 1
    if not last_frame:
        print("No image files found")
        return
    int_frame = int(last_frame)
    cmds.playbackOptions(
        minTime=0, maxTime=int_frame, animationStartTime=0, animationEndTime=int_frame
    )


def create_image_plane():
    '''
    画像プレーンを作成する
    '''
    image_plane = cmds.imagePlane(name="YoutubeImagePlane")
    transform = image_plane[0]
    shape = image_plane[1]
    tmp_path = create_tmp_path()
    seq_file_path = os.path.join(tmp_path, "frame_0000000.jpg")
    if not os.path.exists(seq_file_path):
        return
    set_aspect_ratio(transform, tmp_path)
    set_playbackOptions(tmp_path)

    cmds.setAttr(f"{transform}.imageName", seq_file_path, type="string")
    cmds.setAttr(f"{shape}.useFrameExtension", 1)


def delete_folder():
    '''
    一時ディレクトリを削除する
    '''
    tmp_path = create_tmp_path()
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
