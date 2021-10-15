# 広告表示のみ行うプログラム
import sys
import os.path
import csv
import cv2
from PIL import ImageGrab, Image, ImageTk#advertising用に後ろ二つを追加
from threading import (Event, Thread)
import tkinter
import glob
import random
import time

# ログの取得時間をUnixTimeにするか否かのフラグ
useUnixTime = False

RESULT_DIR = 'result\\'
if len(sys.argv) == 1:
    print("実行時の引数が異常です")
    sys.exit(1)
SAVE_DIR = RESULT_DIR + sys.argv[1]

##ここから広告表示プログラムとして追加
#広告表示位置を変更するフラグ
ad_start = 0
flag = 0#今いらないかも
im_sikaku_list = []#四角画像のpathを格納
im_yoko_list = []#横長画像
sikaku_dir = "image\\small_image\\sikaku\\"
yoko_dir = "image\\small_image\\yokonaga\\"
close_dir = "image\\small_image\\close\\"
back = "white"#画像ウィンドウの背景

######### 定数定義終了 仮でTrueにしている。実験システムと合わせるときには全てFalseにする
flag_pose = True#False #openposeキャプチャ取得しているかどうかのフラグ
flag_cap = True#False #AmazonRekognition
#flag_eye = False#tobii
flag_start = False #広告開始時間のフラグ
##ここまで広告表示プログラムとして追加

def getNowTime():
    #global now
    if useUnixTime == True:
      getTime = time.perf_counter()
    else :
      getTime = (time.perf_counter() - start)
    return format(getTime,'.6f')

def preparationFiles():
    if False == os.path.isdir(RESULT_DIR):
        os.mkdir(RESULT_DIR)

    if os.path.isdir(SAVE_DIR):
        print("すでに同名のユーザが試験済みなので、ユーザ名を変更するかディレクトリの待避を実施してください")
        sys.exit(1)
    else :
        os.mkdir(SAVE_DIR)
        # os.mkdir(CAMERA_DIR)
        # os.mkdir(SCREENSHOT_DIR)
     
    with open(SAVE_DIR+'\\advertising.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time','pos','content'])



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
    root.loadimage = tkinter.PhotoImage(file=close_dir+"small_close_button.png")#ボタンにする画像を読み込み#＠＠
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
    time.sleep(10)#ウィンドウ非表示の時間#
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
    
def ad_log(pos,content):
    with open(SAVE_DIR+'\\advertising.csv','a',newline='') as f:
       writer = csv.writer(f)
       writer.writerow([getNowTime(),pos,content])

def ad_pos():
    #print("ad_pos")
    global flag_start,now
    while True:
        # print("cap:"+str(flag_cap))
        # print("pose"+str(flag_pose))
        # print("eye"+str(flag_eye))
        # カメラ起動フラグ
        # print(flag_pose)
        if flag_pose == False or flag_cap == False:
            continue
        elif flag_start == False:
            flag_start = True
            ad_start = time.perf_counter()#開始時間
            print("ad_start "+str(getNowTime()))
        #print(flag_start)
        ad_now = time.perf_counter() - ad_start
        if ad_now < 3:# 確認のため3秒後　本来は90秒後から広告
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
                    root.roundedbutton.destroy()#必要ないボタンを削除
                    #ボタンを作成
                    # root.loadimage = tkinter.PhotoImage(file=close_dir+"small_close_button.png")#ボタンにする画像を読み込み#＠＠
                    # root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    # root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    # root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    # root.roundedbutton.place(x=270,y=0)#＠＠
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
                    root.roundedbutton.destroy()#必要ないボタンを削除
                    #ボタンを作成
                    # root.loadimage = tkinter.PhotoImage(file=close_dir+"small_close_button.png")#ボタンにする画像を読み込み
                    # root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    # root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    # root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    # root.roundedbutton.place(x=670,y=0)
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
                    # root.loadimage = tkinter.PhotoImage(file=close_dir+"small_close_button.png")#ボタンにする画像を読み込み
                    # root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    # root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    # root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    # root.roundedbutton.place(x=670,y=0)
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
                    root.roundedbutton.destroy()#必要ないボタンを削除
                    #ボタンを作成
                    # root.loadimage = tkinter.PhotoImage(file=close_dir+"small_close_button.png")#ボタンにする画像を読み込み
                    # root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)#ボタン設定
                    # root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    # root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    # root.roundedbutton.place(x=270,y=0)
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
                    root.loadimage = tkinter.PhotoImage(file=close_dir+"small_tojiru_button.png")#ボタンにする画像を読み込み#＠＠
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
                    root.loadimage = tkinter.PhotoImage(file=close_dir+"small_tojiru_button.png")#ボタンにする画像を読み込み#＠＠
                    root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=ignore_btn_click)#ボタン設定
                    root.roundedbutton["bg"] = back#背景がTkinterウィンドウと同じに
                    root.roundedbutton["border"] = "0"#ボタンの境界線が削除
                    root.roundedbutton.place(x=75,y=280)#＠＠
                    image = random.choice(im_sikaku_list)
                    change_fig(root,root_canvas,item,image,img)
                    ad_log(ad_pos,image)

# main

if __name__ == '__main__':
    try:
        preparationFiles()
        start = time.perf_counter() #実験開始時間を記録　#getNowTime()で使用


        advertisingDisplayThread = Thread(target=show_image)
        advertisingDisplayThread.setDaemon(True)
        advertisingDisplayThread.start()

        # advertisingPositionThread = Thread(target=ad_pos)
        # advertisingPositionThread.setDaemon(True)
        # advertisingPositionThread.start()
        ad_pos()
   
    # Ctrl+C で終了
    except KeyboardInterrupt:
        print ('Ctrl+C pressed...')
        sys.exit(0)