# -*- coding: utf-8 -*-
import sys
import csv
import cv2
import time
import math
import os.path
import boto3
import argparse
import numpy as np
import tobii_research as tr
from sys import platform
##from datetime import datetime
import datetime#from datetime import datetimeだとgetFileName()がうまくいかなかったので、代わりに挿入。
from pynput import mouse, keyboard
from threading import (Event, Thread)
from PIL import ImageGrab, Image, ImageTk#advertising用に後ろ二つを追加
import tkinter
import glob
import random


######### 定数定義
# Cameraのpreviewを使用する場合はture
# tureにした場合、keyboardのログと併用はできない
useShowImage = False
#useShowImage = True
# ログの取得時間をUnixTimeにするか否かのフラグ
useUnixTime = False


##ここから広告表示プログラムとして追加
#広告表示位置を変更するフラグ
ad_start = 0
flag = 0
im_sikaku_list = []#四角画像のpathを格納
im_yoko_list = []#横長画像
sikaku_dir = "image\\small_image\\sikaku\\"
yoko_dir = "image\\small_image\\yokonaga\\"
back = "white"

######### 定数定義終了
flag_pose = False#openposeキャプチャ取得しているかどうかのフラグ
flag_cap = False#Amazon
#flag_eye = False#tobii
flag_start = False#広告開始時間のフラグ
##ここまで広告表示プログラムとして追加


## 引数の確認と保存先の名称確認
RESULT_DIR = 'result\\'
if len(sys.argv) == 1:
    print("実行時の引数が異常です")
    sys.exit(1)
SAVE_DIR = RESULT_DIR + sys.argv[1]
CAMERA_DIR = SAVE_DIR+"\\cameraCapture"
SCREENSHOT_DIR = SAVE_DIR+"\\screenShot"
## 引数の確認と保存先の名称確認 終了

#def getNowTime():
#   if useUnixTime == True:
#      getTime = time.time()
#   else :
#      getTime = datetime.now().strftime("%H:%M:%S.%f")
#   return getTime

##def getFileName():
##   if useUnixTime == True:
##      getTime = time.time()
##   else :
##      getTime = datetime.now().strftime("%H_%M_%S_%f")
##   return getTime

def getNowTime():
   #global now
   if useUnixTime == True:
      getTime = time.perf_counter()
   else :
      getTime = (time.perf_counter() - start)
   return format(getTime,'.6f')

def getFileName():
   if useUnixTime == True:
      getTime = time.perf_counter()
   else :
      now = time.perf_counter() - start
      td = datetime.timedelta(seconds=now) #floatからtimedelta(秒数)に変換
      getTime = format(td.seconds,'.0f')+'_'+'{:06}'.format(td.microseconds,'.0f') 
   return getTime    


##ここから広告表示プログラムとして追加
#画像のpathを四角画像と横長画像にわけてlistに格納
def getImage(image_dir):
   image_path = image_dir+'*'
   image_path_list = glob.glob(image_path)
   return image_path_list #'20201020_fft-hist_csv\\takakura_pose_rwristY.csv'

im_sikaku_list = getImage(sikaku_dir)
im_yoko_list = getImage(yoko_dir)

def show_image():
##    print("showImage")
    #外から触れるようにグローバル変数で定義
    #global item,item2, root_canvas,frame2_canvas,root,frame2,img
    global item,root_canvas,root,img
 
    #画面作成(初期設定)
    root = tkinter.Tk()#ウィンドウ作成
    root.title('test')#ウィンドウタイトル
    root.withdraw()#ウィンドウを非表示にする
    root.overrideredirect(1) #ウィンドウ上部のバー(閉じる・最小化ボタンなど)を削除
    root.attributes("-topmost", True)#常に最前面に配置する
    root.geometry("300x300+100+400")#サイズ300x300のウィンドウを（100，400）に配置
    img = Image.open(im_sikaku_list[0])
    img = ImageTk.PhotoImage(img,master=root)
    root_canvas = tkinter.Canvas(bg = back, width=300, height=280,master=root)#canvasサイズ指定
    root_canvas.place(x=0, y=0)#canvas位置
    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
    #ボタンを作成
    root.loadimage = tkinter.PhotoImage(file="small_close_button.png")#ボタンにする画像を読み込み#＠＠
    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
    root.roundedbutton.place(x=270,y=0)#＠＠
##    root.deiconify()#ウィンドウを再表示する
    
##    #2つめのウィンドウを準備
##    frame2 = tkinter.Toplevel()
##    frame2.title('test2')  
##    frame2.withdraw()#ウィンドウを非表示にする
##    frame2.overrideredirect(1) #ウィンドウ上部のバー(閉じる・最小化ボタンなど)を削除
##    frame2.attributes("-topmost", True)#常に最前面に配置する
##    frame2.geometry("300x300+1500+400")
##    img2 = Image.open(im_sikaku_list[1])
##    img2 = ImageTk.PhotoImage(img2,master=frame2)    
##    frame2_canvas = tkinter.Canvas(bg = "black", width=300, height=280,master=frame2)#canvasサイズ指定
##    frame2_canvas.place(x=0, y=0)#canvas位置
##    item2 = frame2_canvas.create_image(0, 0, image=img2, anchor=tkinter.NW)#canvas内の画像位置
####    frame2.deiconify()#ウィンドウを再表示する

    root.mainloop()#表示
    
def change_fig(mas,canvas,item,img_path,img):
    global new_img
    new_img = img
    mas.withdraw()#ウィンドウを非表示にする   
    new_img = Image.open(img_path)
    new_img = ImageTk.PhotoImage(new_img,master=mas)
    canvas.itemconfig(item,image=new_img)#itemを差し替え
    time.sleep(10)#ウィンドウ非表示の時間
    mas.deiconify()#ウィンドウを再表示する     
    time.sleep(10)#ウィンドウ表示の時間

#ボタンクリック時のイベント
def btn_click():
##    print("normal")
    root.withdraw()#ウィンドウを非表示にする

#ボタンクリック時のイベント(6割クリック無視)
def ignore_btn_click():
##    print("ignore")
    if random.random() < 0.6:
        return
    root.withdraw()#ウィンドウを非表示にする
##ここまで広告表示プログラムとして追加
    

def getPoseEvent():
 global flag_pose
 try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    params = dict()
    params["model_pose"] = "COCO" 
    params["model_folder"] = "../../../models/"
    #print(params["model_folder"])

    # Starting OpenPose(静止画の骨格抽出)
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    with open(SAVE_DIR+'\\pose.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time","nose_x","nose_y","nose_score","neck_x","neck_y","neck_score",\
                         "RShoulder_x","RShoulder_y","RShoulder_score",\
                         "RElbow_x","RElbow_y","RElbow_score","RWrist_x","RWrist_y","RWrist_score",\
                         "LShoulder_x","LShoulder_y","LShoulder_score","LElbow_x","LElbow_y","LElbow_score",\
                         "LWrist_x","LWrist_y","LWrist_score",\
                         "RHip_x","RHip_y","RHip_score","RKnee_x","RKnee_y","RKnee_score",\
                         "RAnkle_x","RAnkle_y","RAnkle_score","LHip_x","LHip_y","LHip_score",\
                         "LKnee_x","LKnee_y","LKnee_score","LAnkle_x","LAnkle_y","LAnkle_score",\
                         "REye_x","REye_y","REye_score","LEye_x","LEye_y","LEye_score","REar_x","REar_y","REar_score",\
                         "LEar_x","LEar_y","LEar_score",\
                          ])

    # キャプチャ画像を取得
    capture = cv2.VideoCapture(1)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320) # カメラ画像の横幅を設定
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) # カメラ画像の縦幅を設定    
    while(capture.isOpened()):
##        time.sleep(0.1)
        flag_pose = True
        ret, frame = capture.read()
        #eight, width, cannels = frame.shape

        # Process Image
        datum = op.Datum()
        imageToProcess = frame
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])

        # csvファイル出力
##        csvKeypoints = [1,1,1]*26
##        for i in range(26):
##            try:
##                csvKeypoints[i]  = datum.posekeypoints[0][i]
##            except:
##                csvKeypoints[i]  = [0,0,0]

        try:
        	nose = datum.poseKeypoints[0][0]
        except:
        	nose = [0,0,0]
        try:
        	neck = datum.poseKeypoints[0][1]
        except:
        	neck = [0,0,0]
        try:
        	RShoulder = datum.poseKeypoints[0][2]
        except:
        	RShoulder = [0,0,0]
        try:
        	RElbow = datum.poseKeypoints[0][3]
        except:
        	RElbow = [0,0,0]
        try:
        	RWrist = datum.poseKeypoints[0][4]
        except:
        	RWrist = [0,0,0]
        try:
        	LShoulder = datum.poseKeypoints[0][5]
        except:
        	LShoulder = [0,0,0]
        try:
        	LElbow = datum.poseKeypoints[0][6]
        except:
        	LElbow = [0,0,0]
        try:
        	LWrist = datum.poseKeypoints[0][7]
        except:
        	LWrist = [0,0,0]
        try:
        	RHip = datum.poseKeypoints[0][8]
        except:
        	RHip = [0,0,0]
        try:
        	RKnee = datum.poseKeypoints[0][9]
        except:
        	RKnee = [0,0,0]
        try:
        	RAnkle = datum.poseKeypoints[0][10]
        except:
        	RAnkle = [0,0,0]
        try:
        	LHip = datum.poseKeypoints[0][11]
        except:
        	LHip = [0,0,0]
        try:
        	LKnee = datum.poseKeypoints[0][12]
        except:
        	LKnee = [0,0,0]
        try:
        	LAnkle = datum.poseKeypoints[0][13]
        except:
        	LAnkle = [0,0,0]
        try:
        	REye = datum.poseKeypoints[0][14]
        except:
        	REye = [0,0,0]
        try:
        	LEye = datum.poseKeypoints[0][15]
        except:
        	LEye = [0,0,0]
        try:
        	REar = datum.poseKeypoints[0][16]
        except:
        	REar = [0,0,0]
        try:
        	LEar = datum.poseKeypoints[0][17]
        except:
        	LEar = [0,0,0]
        with open(SAVE_DIR+'\\pose.csv','a',newline='') as f:
            writer = csv.writer(f)
##            writer.writerow([getNowTime(),])
##            writer.writerow([getNowTime(),csvKeypoints])
            np.savetxt(f,[getNowTime()],fmt='%s',delimiter=',',newline=',')
            np.savetxt(f,[nose,neck,RShoulder,RElbow,RWrist,LShoulder,LElbow,LWrist,RHip,RKnee,RAnkle,\
                          LHip,LKnee,LAnkle,REye,LEye,REar,LEar,],\
                       fmt='%.0f', delimiter=',',newline=',')
            writer.writerow([])
        if useShowImage == True:
            # 結果をディスプレイに表示
            cv2.imshow('frame_side',datum.cvOutputData)
        # 'Q'キーで停止
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #capture.releace() #いらない
    cv2.destroyAllWindows()
 except Exception as e:
    print(e)
    sys.exit(-1)


def getEyeTracker():
  found_eyetrackers = tr.find_all_eyetrackers()
  my_eyetracker = found_eyetrackers[0]
  print("Address: " + my_eyetracker.address)
  print("Model: " + my_eyetracker.model)
  print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
  print("Serial number: " + my_eyetracker.serial_number)

  my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gazeDataCallback, as_dictionary=True)

def printEyeData(gazeData):
  SCREEN_HEIGHT = 990 # TODO 今は決め打ち
  SCREEN_WIDTH = 1440 # TODO 今は決め打ち

  right_gaze_data = gazeData['right_gaze_point_on_display_area']
  left_gaze_data = gazeData['left_gaze_point_on_display_area']
  right_pupil_data = gazeData['right_pupil_diameter']
  left_pupil_data =  gazeData['left_pupil_diameter']

  real_gaze_y = (right_gaze_data[1] + left_gaze_data[1]) / 2.0 * SCREEN_HEIGHT
  real_gaze_x = (right_gaze_data[0] + left_gaze_data[0]) / 2.0 * SCREEN_WIDTH

  # 確認用出力
#  if real_gaze_y <= SCREEN_HEIGHT / 3:
#     if real_gaze_x <= SCREEN_WIDTH / 3:
#       print('位置；左上 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif real_gaze_x <= SCREEN_WIDTH / 3 * 2:
#       print('位置；真ん中上 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif  real_gaze_x <= SCREEN_WIDTH / 3 * 3:
#       print('位置；右上 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#  elif real_gaze_y <= SCREEN_HEIGHT / 3 * 2:
#     if real_gaze_x <= SCREEN_WIDTH / 3:
#       print('位置；左真ん中 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif real_gaze_x <= SCREEN_WIDTH / 3 * 2:
#       print('位置；ど真ん中 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif  real_gaze_x <= SCREEN_WIDTH / 3 * 3:
#       print('位置；右真ん中 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#  elif real_gaze_y <= SCREEN_HEIGHT / 3 * 3:
#     if real_gaze_x <= SCREEN_WIDTH / 3:
#       print('位置；左下 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif real_gaze_x <= SCREEN_WIDTH / 3 * 2:
#       print('位置；真ん中下 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#     elif  real_gaze_x <= SCREEN_WIDTH / 3 * 3:
#       print('位置；右下 / サイズ(：', right_pupil_data, left_pupil_data, ')')
#  # else:
#  #    print('取得できていません : ' + str(real_gaze_x))
#  #print('real_gaze_x = ' + str(real_gaze_x))
#  #print('real_gaze_y = ' + str(real_gaze_y))

def gazeDataCallback(gazeData):

   right_gaze_data = gazeData['right_gaze_point_on_display_area']
   left_gaze_data = gazeData['left_gaze_point_on_display_area']
   right_gaze_validity = gazeData['right_gaze_point_validity']
   left_gaze_validity =  gazeData['left_gaze_point_validity']

   right_pupil_data = gazeData['right_pupil_diameter']
   left_pupil_data =  gazeData['left_pupil_diameter']
   right_pupil_validity = gazeData['right_pupil_validity']
   left_pupil_validity =  gazeData['left_pupil_validity']

   with open(SAVE_DIR+'\\eyePosition.csv','a',newline='') as f:
       writer = csv.writer(f)
       # 時間,右目y,左目y,右目x,左目x,右目有効度,左目有効度
       writer.writerow([getNowTime(),right_gaze_data[0],left_gaze_data[0],right_gaze_data[1],left_gaze_data[1],right_pupil_validity,left_pupil_validity])
   with open(SAVE_DIR+'\\eyePupil.csv','a',newline='') as f:
       writer = csv.writer(f)
       # 時間,右目瞳孔サイズ,左目瞳孔サイズ,右目瞳孔有効度,左目瞳有効度
       writer.writerow([getNowTime(),right_pupil_data,left_pupil_data,right_pupil_validity,left_pupil_validity])

   # 確認用出力関数:
   printEyeData(gazeData)

def getMouseEvent():
   with mouse.Listener(
      on_click=onMouseClick,
      on_move=onMouseMove) as mouseListener:
      mouseListener.join()

# マウスクリックのキーイベント
def onMouseClick(x, y, button, pressed):
   scale_factor = .5
   # クリック_プレスのみ取得
   if pressed:
      now = getNowTime() #時刻のずれをなくすためにnow,fileを同時に呼び出す
      file = getFileName() #
      screenShot = np.asarray(ImageGrab.grab())
      height, width, channels = screenShot.shape
      screenShot = cv2.cvtColor(screenShot, cv2.COLOR_BGR2RGB) #通常の色調に変更
      screenShot = cv2.circle(screenShot,(int(x),int(y)), 5, (0,0,255), -1)
      screenShot = cv2.circle(screenShot,(int(x),int(y)), 2, (255,0,0), -1)
      small = cv2.resize(screenShot, (int(width * scale_factor), int(height * scale_factor)))
      cv2.imwrite(SCREENSHOT_DIR +'\\'+ file +".jpg",small)
      with open(SAVE_DIR+'\\mouseClick.csv','a',newline='') as f:
           writer = csv.writer(f)
           writer.writerow([now,x,y])

# マウス移動のキーイベント
def onMouseMove(x, y):
   with open(SAVE_DIR+'\\mousePos.csv','a',newline='') as f:
         writer = csv.writer(f)
         writer.writerow([getNowTime(),x,y])

def getKeyboardEvent():
   with keyboard.Listener(
         on_press=onKeyboardPress,
         on_release=onKeyboardRelease) as keyboardListener:
         keyboardListener.join()

# キーボードのキーイベント
def onKeyboardPress(key):
   with open(SAVE_DIR+'\\keyboardPress.csv','a',newline='') as f:
         writer = csv.writer(f)
         try:
            writer.writerow([getNowTime(),'{0}'.format(key.char)])
         except:
            writer.writerow([getNowTime(),key])

def onKeyboardRelease(key):
   now = getNowTime()
   try:
       char = key.char
   except:
       char = ''
   with open(SAVE_DIR+'\\keyboardRelease.csv','a',newline='') as f:
       writer = csv.writer(f)
       try:
           writer.writerow([now,'{0}'.format(key.char)])
       except:
           writer.writerow([now,key])

def getCapture():
    global flag_cap
    # スケールや色などの設定
    scale_factor = .5
    green = (0,255,0)
    red = (0,0,255)
    frame_thickness = 2
    cap = cv2.VideoCapture(0)
    rekognition = boto3.client('rekognition','ap-northeast-1')

    fontscale = 1.0
    color = (0, 255, 0)
    fontface = cv2.FONT_HERSHEY_DUPLEX 
    disgusted = 0.0
    happy = 0.0
    surprised = 0.0
    angry = 0.0
    confused = 0.0
    calm = 0.0
    sad = 0.0
    while(True):
        flag_cap = True    
        # フレームをキャプチャ取得
        ret, frame = cap.read()
        height, width, channels = frame.shape
    
        # jpgに変換 画像ファイルをインターネットを介してAPIで送信するのでサイズを小さくしておく
        small = cv2.resize(frame, (int(width * scale_factor), int(height * scale_factor)))
        ret, buf = cv2.imencode('.jpg', small)
    
        # Amazon RekognitionにAPIを投げる
        faces = rekognition.detect_faces(Image={'Bytes':buf.tobytes()}, Attributes=['ALL'])
    
        with open(SAVE_DIR+'/faceInformation.csv','a',newline='') as f:
            for face in faces['FaceDetails']:
                 smile = face['Smile']['Value']
                 emotions = face['Emotions']
                 for emotion in emotions:
                     if emotion['Type'] == 'DISGUSTED':
                       disgusted = emotion['Confidence']
                     elif emotion['Type'] == 'HAPPY':
                       happy = emotion['Confidence']
                     elif emotion['Type'] == 'SURPRISED':
                      surprised = emotion['Confidence']
                     elif emotion['Type'] == 'ANGRY':
                      angry = emotion['Confidence']
                     elif emotion['Type'] == 'CONFUSED':
                      confused = emotion['Confidence']
                     elif emotion['Type'] == 'CALM':
                      calm = emotion['Confidence']
                     elif emotion['Type'] == 'SAD':
                      sad = emotion['Confidence']
                 writer = csv.writer(f)
                 writer.writerow([getNowTime(),smile,disgusted,happy,surprised,angry,confused,calm,sad])

            # 顔の周りに箱を描画する
            
            cv2.rectangle(frame,
                          (int(face['BoundingBox']['Left']*width),
                          int(face['BoundingBox']['Top']*height)),
                          (int((face['BoundingBox']['Left']+face['BoundingBox']['Width'])*width),
                          int((face['BoundingBox']['Top']+face['BoundingBox']['Height'])*height)),
                          green if smile else red, frame_thickness)
            i = 0
            emotions = ['DISGUSTED' + " : " + str(round(disgusted,2)),
                        'HAPPY    ' + " : " + str(round(happy,2)),
                        'SURPRISED' + " : " + str(round(surprised,2)),
                        'ANGRY    ' + " : " + str(round(angry,2)),
                        'CONFUSED ' + " : " + str(round(confused,2)),
                        'CALM     ' + " : " + str(round(calm,2)),
                        'SAD      ' + " : " + str(round(sad,2))]
                        
            for emotion in emotions:
               cv2.putText(frame,
                           emotion,
                           (25, 40 + (i * 25)),
                           fontface,
                           fontscale,
                           color)
               i += 1       
            # 結果をディスプレイに表示
            if useShowImage == True:
                cv2.imshow('frame', frame)
            cv2.imwrite(CAMERA_DIR +'/'+ getNowTime() +".jpg",frame)
            cv2.waitKey(1)

def preparationFiles():

   if False == os.path.isdir(RESULT_DIR):
     os.mkdir(RESULT_DIR)

   if os.path.isdir(SAVE_DIR):
     print("すでに同名のユーザが試験済みなので、ユーザ名を変更するかディレクトリの待避を実施してください")
     sys.exit(1)
   else :
     os.mkdir(SAVE_DIR)
     os.mkdir(CAMERA_DIR)
     os.mkdir(SCREENSHOT_DIR)

   with open(SAVE_DIR+'\\eyePosition.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','rightY','leftY','rightX','leftY','EffectivenessY','EffectivenessX'])
   with open(SAVE_DIR+'\\eyePupil.csv','a',newline='') as f:
       writer = csv.writer(f)
       # 時間,右目瞳孔サイズ,左目瞳孔サイズ,右目瞳孔有効度,左目瞳有効度
       writer.writerow(['time','rightSize','leftSize','EffectivenessRight','EffectivenessLeft'])
   with open(SAVE_DIR+'\\mouseClick.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','x','y'])
   with open(SAVE_DIR+'\\mousePos.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','x','y'])
   with open(SAVE_DIR+'\\keyboardPress.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','key'])
   with open(SAVE_DIR+'\\keyboardRelease.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','key'])
   with open(SAVE_DIR+'\\faceInformation.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','smile','disgusted','happy','surprised','angry','confused','calm','sad'])
   with open(SAVE_DIR+'\\advertising.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow(['time','pos','content'])

def ad_log(pos,content):
    with open(SAVE_DIR+'\\advertising.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow([getNowTime(),pos,content])

def ad_pos():
    #print("ad_pos")
    global flag_start,now
    while True:
        #print("cap:"+str(flag_cap))
        #print("pose"+str(flag_pose))
        #print("eye"+str(flag_eye))
        #カメラ起動フラグ
##            print(flag_pose)
        if flag_pose == False or flag_cap == False:
            continue
        elif flag_start == False:
            flag_start = True
            ad_start = time.perf_counter()#開始時間
            print("ad_start "+str(getNowTime()))
        #print(flag_start)
        ad_now = time.perf_counter() - ad_start
        if ad_now < 60:
            time.sleep(1)
            continue
        else:
            ad_pos_list = []
            ad_pos_list = [1,2,3,4,5,6] #上下左右中クリック虫の5種類の広告表示位置
            random.shuffle(ad_pos_list)#表示位置の順番をシャッフル
            for ad_pos in ad_pos_list:
                if ad_now > 600:#10分間
                    root.quit()#全てのウィンドウを閉じる
                    break
                
                #左に広告表示
                if ad_pos == 1:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("300x300+100+400")#ウィンドウ配置指定
                    root_canvas = tkinter.Canvas(bg = back, width=300, height=280,master=root)#canvasサイズ指定#＠＠
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_close_button.png")#ボタンにする画像を読み込み#＠＠
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=270,y=0)#＠＠
                    image = random.choice(im_sikaku_list)           
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)
                                    
                #下に広告表示
                elif ad_pos == 2:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("700x150+600+850")#ウィンドウ配置指定
                    root_canvas = tkinter.Canvas(bg = back, width=700, height=150,master=root)#canvasサイズ指定
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_close_button.png")#ボタンにする画像を読み込み
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=670,y=0)
                    image = random.choice(im_yoko_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)

                #上に広告表示
                elif ad_pos == 3:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("700x150+600+100")#ウィンドウ配置指定
                    root_canvas = tkinter.Canvas(bg = back, width=700, height=150,master=root)#canvasサイズ指定
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    root.roundedbutton.destroy()#必要ないボタンを削除
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_close_button.png")#ボタンにする画像を読み込み
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=670,y=0)
                    image = random.choice(im_yoko_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)

                #右に広告表示
                elif ad_pos == 4:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("300x280+1500+400")#ウィンドウ配置指定
                    root_canvas = tkinter.Canvas(bg = back, width=300, height=280,master=root)#canvasサイズ指定
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_close_button.png")#ボタンにする画像を読み込み
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=270,y=0)
                    image = random.choice(im_sikaku_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)

                #真ん中に広告表示
                elif ad_pos == 5:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("300x330+800+400")#ウィンドウ配置指定#＠＠
                    root_canvas = tkinter.Canvas(bg = back, width=300, height=330,master=root)#canvasサイズ指定#＠＠
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_tojiru_button.png")#ボタンにする画像を読み込み#＠＠
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=75,y=280)#＠＠
                    image = random.choice(im_sikaku_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)
                #真ん中に広告表示
                elif ad_pos == 6:
                    root.withdraw()#ウィンドウを非表示にする
                    #ウィンドウ位置を変更する
                    root.geometry("300x330+800+400")#ウィンドウ配置指定#＠＠
                    root_canvas = tkinter.Canvas(bg = back, width=300, height=330,master=root)#canvasサイズ指定#＠＠
                    root_canvas.place(x=0, y=0)#canvas位置
                    item = root_canvas.create_image(0, 0, image=img, anchor=tkinter.NW)#canvas内の画像位置
                    #ボタンを作成
                    root.loadimage = tkinter.PhotoImage(file="small_tojiru_button.png")#ボタンにする画像を読み込み#＠＠
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=ignore_btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=75,y=280)#＠＠
                    image = random.choice(im_sikaku_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)

##ここまで広告表示プログラムとして追加
                            
start = time.perf_counter() #実験開始時間を記録　#getNowTime()で使用

if __name__ == '__main__':
    try:

        preparationFiles()
        eyeTrackerListenerThread = Thread(target=getEyeTracker)
        eyeTrackerListenerThread.setDaemon(True)
        eyeTrackerListenerThread.start()

        mouseEventListenerThread = Thread(target=getMouseEvent)
        mouseEventListenerThread.setDaemon(True)
        mouseEventListenerThread.start()

        poseEventListenerThread = Thread(target=getPoseEvent)
        poseEventListenerThread.setDaemon(True)
        poseEventListenerThread.start()

        if useShowImage == False:
           keyboardEventListenerThread = Thread(target=getKeyboardEvent)
           keyboardEventListenerThread.setDaemon(True)
           keyboardEventListenerThread.start()

        advertisingDisplayThread = Thread(target=show_image)
        advertisingDisplayThread.setDaemon(True)
        advertisingDisplayThread.start()

        advertisingPositionThread = Thread(target=ad_pos)
        advertisingPositionThread.setDaemon(True)
        advertisingPositionThread.start()

        getCapture()
        #getPoseEvent()


    except KeyboardInterrupt:
        my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        my_eyetracker.unsubscribe_from(tr.EYETRACKER_PUPIL_DATA, pupil_data_callback)
        print ('Ctrl+C pressed...')
        sys.exit(0)
