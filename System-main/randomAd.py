# 偶に上下バナーの単色表示で上のバナーが出ず下の表示だけしかないバグ ← 原因不明だけどset_event()で解決?
# ボタンdestroy時の穴あきは直す window作り直す ← 現状閉じるボタンと画像が重ならないように配置しているので修正していません

import time
import datetime
import random
from selenium import webdriver
from PIL import ImageGrab, Image, ImageTk
from threading import (Event, Thread)
import tkinter
import sys
import csv
import glob
import cv2
import os.path
from pynput import keyboard
import pyautogui

start_program_elapsed = time.perf_counter()
start_program_date = datetime.datetime.now()

# 下のほうで記録

# 引数確認と定数作成
RESULT_DIR = "result\\"
if len(sys.argv) == 1:
	print("実行時の引数が異常です")
	sys.exit(1)
SAVE_DIR = RESULT_DIR + sys.argv[1]

# chromedriverのパス
CHROMEDRIVER_PATH = "chromedriver_win32\chromedriver"

# 広告関連の定数
TIME_ONESET = 60
TIME_FIRSTWAITING = 60
TIME_LASTWAITING = 30
NUM_LOOP = 2

# 画像のパス
SIKAKU_DIR = "image\\small_image\\sikaku\\"
YOKO_DIR = "image\\small_image\\yokonaga\\"
CLOSE_DIR = "image\\small_image\\close\\"
SIMPLE_SIKAKU_PATH = "image\\small_image\\simple\\simple_sikaku.png"
SIMPLE_YOKO_PATH = "image\\small_image\\simple\\simple_yoko.png"

# キャンバス関連の定数
SIZE_YOKO = "700x150"
SIZE_SIKAKU = "300x280"
SIZE_ZENMEN = "300x350"
POS_JOUGE_TOP_QUIZ = "610+150" # 1920x1080
POS_JOUGE_BUTTOM_QUIZ = "810+650"
POS_JOUGE_TOP_RESULT = "610+150"
POS_JOUGE_BUTTOM_RESULT = "810+650"
POS_ZENMEN = "810+365"

# 広告種類が何通りあるかのリスト
ad_kinds = [1,2,3,4,5,6]

# 画像のパスを格納するリスト
im_sikaku_list = []
im_yoko_list = []

# ログに用いる変数
time_disp = None
time_close = None
current_ad_kind = None

# 広告の表示/非表示に用いるフラグ
flag_click = False
flag_disp = False

# 画面遷移の判定に用いるフラグ
flag_trans = False
flag_finish = False
is_result = False

# auto_clickに用いるフラグ
flag_auto_click = False

# どちらかがTrueで起動しない
flag_pose = True
flag_cap = True

# 実験開始時間を記録する変数
start = None

# キャンバスの初期設置を先に終わらせるために用いる
event = Event()
event2 = Event()

# キャンバス関連の変数
root, root = (None, None)
canvas, canvas2 = (None, None)
item, item2 = (None, None) # item = create_image()でitemのidを取得する必要あり,itemもグローバル変数にする
img, img2 = (None, None) # PhotoImageでの参照先が消えないようにグローバル変数にする必要がある

# ディレクトリの存在確認+ログファイルを作る関数
def preparation_files():
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
		writer.writerow(['time_display','time_close','pos','content','content2','start_quiz_system','start_program','start_program_date'])

# 画像のpathを四角画像と横長画像にわけてlistに格納
def get_image(image_dir):
   image_path = image_dir+'*'
   image_path_list = glob.glob(image_path)
   return image_path_list

# 経過時間取得関数
def get_elapsed_time():
	global start
	return time.perf_counter() - start

# 同期するため,mainloop()から0.5秒後に呼ばれる関数
def set_event(id):
	global event, event2
	if id == 1:
		event.set()
	else:
		event2.set()

# 初期設定関数1 canvas関連まとめてクラス検討
def set_canvas():
	
	global root, canvas, item, im_sikaku_list, img
	
	root = tkinter.Tk()
	root.title("test1")
	root.geometry("800x450+250+250")	# 作成するwindowサイズ+x+y
	root.overrideredirect(1) # ウィンドウ上部のバー(閉じる・最小化ボタンなど)を削除
	root.attributes("-topmost", True) # 常に最前面に配置する

	img = ImageTk.PhotoImage(file=im_sikaku_list[0], master=root) # とりあえず適当な画像

	#キャンバスエリア
	canvas = tkinter.Canvas(root,width=1920,height=1080,bg="white") # 一番大きな広告のサイズに合わせる 大きいほうが良い

	item = canvas.create_image(0, 0, image=img, anchor=tkinter.NW) # canvas.create_imageは１つのキャンバスにつき１回呼び出すだけで良い?

	#キャンバスバインド
	canvas.place(x=0, y=0)#Canvasの配置(windowサイズからの座標)
	
	### RoundedButton(parent, width, height, cornerradius, padding, fillcolor, background, command)
	# 必要かどうか
	root.loadimage = tkinter.PhotoImage(file=CLOSE_DIR+"small_tojiru_button.png", master=root) # ボタンにする画像を読み込み
	root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=btn_click)
	root.roundedbutton["bg"] = "white" # 背景がTkinterウィンドウと同じに
	root.roundedbutton["border"] = "0" # ボタンの境界線が削除
	root.roundedbutton.place(x=75,y=280)
	
	root.withdraw() # 非表示ではじめる
	
	root.after(500, set_event, 1)
	
	root.mainloop()

# 初期設置関数2 Toplevel()に気が付かず2つめのメインウィンドウ作成しています 時間があれば修正
def set_canvas2():
	
	global root2, canvas2, item2, im_sikaku_list, img2

	root2 = tkinter.Tk()
	root2.title("test2")
	root2.geometry("800x450+500+500")
	root2.overrideredirect(1)
	root2.attributes("-topmost", True)
	
	img2 = ImageTk.PhotoImage(file=im_sikaku_list[0], master=root2)

	#キャンバスエリア
	canvas2 = tkinter.Canvas(root2,width=1920,height=1080,bg="white")

	item2 = canvas2.create_image(0, 0, image=img2, anchor=tkinter.NW)

	#キャンバスバインド
	canvas2.place(x=0, y=0)
	
	root2.loadimage = tkinter.PhotoImage(file=CLOSE_DIR+"small_tojiru_button.png", master=root2)
	root2.roundedbutton = tkinter.Button(root2, image=root2.loadimage, command=btn_click)
	root2.roundedbutton["bg"] = "white"
	root2.roundedbutton["border"] = "0"
	root2.roundedbutton.place(x=75,y=280)
	
	root2.withdraw()
	
	root2.after(500, set_event, 2)
	
	root2.mainloop()

# 閉じるボタンコマンド
def btn_click():
	global root, flag_click, time_close, flag_disp
	time_close = get_elapsed_time()
	root.withdraw()
	flag_disp = False
	flag_click = True

# 閉じるボタンコマンド(6割クリック無視)
def ignore_btn_click():
	global root, flag_click, time_close, flag_disp
	if random.random() < 0.6:
		return
	time_close = get_elapsed_time()
	root.withdraw()
	flag_disp = False
	flag_click = True

# on_release関数に呼び出される関数
def autoClick():
	global flag_auto_click
	#pyautogui.click(800,800) # 既にウェブサイト上で名前入力+enterを押して開始が実装済み
	flag_auto_click = True

# キーボードリスナーのon_release時に呼び出される関数
def on_release(key):
	if key == keyboard.Key.enter:
		print('autoClick!')
		autoClick()
		return False

# ログ出力関数
def ad_log(times, pos, content, content2=""):
	with open(SAVE_DIR + '\\advertising.csv', 'a', newline='') as f:
		writer = csv.writer(f)
		c = content.replace("image\\small_image\\", "")
		c2 = content2.replace("image\\small_image\\", "")
		writer.writerow([times[0],times[1],pos,c,c2])

# 広告表示関数
def display_ad(ad_kind, im_yoko_path, im_sikaku_path):
	global root, root2, canvas, canvas2, item, item2, CLOSE_DIR, POS_ZENMEN, \
	POS_JOUGE_TOP_QUIZ, POS_JOUGE_BUTTOM_QUIZ, POS_JOUGE_TOP_RESULT, POS_JOUGE_BUTTOM_RESULT, \
	SIZE_YOKO, SIZE_SIKAKU, flag_disp, img, img2, SIZE_ZENMEN
	
	# 表示場所やボタンの設定
	pos, pos2 = (None, None)
	geo = None
	if ad_kind == 1 or ad_kind == 2: # 上下
		root.roundedbutton.destroy() # pack(), pack_forget()に置き換えられるかも コマンドの書き換えだけできれば
		root2.roundedbutton.destroy()
		if is_result == True:
			pos = POS_JOUGE_BUTTOM_RESULT
			pos2 = POS_JOUGE_TOP_RESULT
		else:
			pos = POS_JOUGE_BUTTOM_QUIZ
			pos2 = POS_JOUGE_TOP_QUIZ
		geo = SIZE_SIKAKU + "+" + pos
	else:
		if ad_kind == 3 or ad_kind == 4:
			com = btn_click
		else:
			com = ignore_btn_click
		root.loadimage = tkinter.PhotoImage(file=CLOSE_DIR+"small_tojiru_button.png", master=root)
		root.roundedbutton = tkinter.Button(root, image=root.loadimage, command=com)
		root.roundedbutton["bg"] = "white"
		root.roundedbutton["border"] = "0"
		root.roundedbutton.place(x=75,y=280)
		pos = POS_ZENMEN
		pos2 = pos
		geo = SIZE_ZENMEN+ "+" + pos
	
	geo2 = SIZE_YOKO + "+" + pos2
	root.geometry(geo)
	root2.geometry(geo2)
	img = ImageTk.PhotoImage(file=im_sikaku_path, master=root)
	img2 = ImageTk.PhotoImage(file=im_yoko_path, master=root2)
	print(img2)
	print(type(img2))
	canvas.itemconfig(item, image=img)
	canvas2.itemconfig(item2, image=img2)
	
	canvas.place()
	canvas2.place()
	
	root.deiconify()
	if ad_kind == 1 or ad_kind == 2:
		root2.deiconify()
	
	flag_disp = True

# 広告非表示 + それに伴う処理をまとめた関数
def hide_ad(im_yoko_path, im_sikaku_path):
	global flag_disp, time_disp, time_close, root, root2, current_ad_kind
	
	root.withdraw()
	root2.withdraw()
	
	time_close = get_elapsed_time()
	times = (time_disp, time_close)
	
	if current_ad_kind == 1 or current_ad_kind == 2:
		ad_log(times, current_ad_kind, im_sikaku_path, im_yoko_path)
	else:
		ad_log(times, current_ad_kind, im_sikaku_path)
	
	flag_disp = False

def main_sub():
	
	global start, CHROMEDRIVER_PATH, ad_kinds, TIME_ONESET, TIME_FIRSTWAITING, TIME_LASTWAITING, NUM_LOOP, \
	flag_trans, flag_finish, is_result, event, event2, root, root2, canvas, canvas2, item, item2, \
	SIMPLE_SIKAKU_PATH, SIMPLE_YOKO_PATH, flag_click, flag_disp, time_disp, current_ad_kind, \
	start_program_elapsed, start_program_date
	
	while flag_pose == False or flag_cap == False:
		pass
	
	setcount = 0
	
	# どこかしらで待つ
	event.wait()
	event2.wait()
	
	options = webdriver.ChromeOptions()
	options.add_experimental_option("excludeSwitches", ['enable-automation'])
	driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
	driver.maximize_window()
	driver.get("http://3.134.34.102/")
	
		
	# auto_click処理
	keyboard_listener = keyboard.Listener(on_release=on_release)
	keyboard_listener.start()
	while flag_auto_click == False:
		pass
	
	# クイズスタート時のタイムスタンプ & 記録
	start = time.perf_counter()
	with open(SAVE_DIR + '\\advertising.csv', 'a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['','','','','',str(start),str(start_program_elapsed),str(start_program_date),"."+str(start_program_date.microsecond)])

	print("wait " + str(TIME_FIRSTWAITING) + " second")
	while get_elapsed_time() < TIME_FIRSTWAITING: # 最初待機
		pass

	print(str(TIME_ONESET/2) + " close " + str(TIME_ONESET/2) + " disp")
	for i in range(NUM_LOOP):
		random.shuffle(ad_kinds)
		#ad_kinds = [1,6,5,3,2,4] # デバッグ用
		while get_elapsed_time() < TIME_ONESET*len(ad_kinds) * (i+1) + TIME_FIRSTWAITING:
			elapsed = get_elapsed_time()
			if elapsed >= TIME_ONESET*len(ad_kinds) * (i+1) + TIME_FIRSTWAITING: # 一応
				break
			cur_url = driver.current_url
			if r"http://3.134.34.102/question?result=" in cur_url:  # リザルト画面
				if is_result == False:
					flag_trans = True
				else:
					flag_trans = False
				is_result = True
			elif r"http://3.134.34.102/question" in cur_url: # クイズ画面
				if is_result == True:
					flag_trans = True
				else:
					flag_trans = False
				is_result = False
			elif r"http://3.134.34.102/result" == cur_url: # 終了画面 一応
				flag_finish = True
			
			# リザルト画面になった時
			if flag_finish == True:
				break;
			
			# 前面系で閉じるボタンが押された時の処理
			if flag_click == True:
				times = (time_disp, time_close)
				ad_log(times, current_ad_kind, im_sikaku_path)
				flag_click = False
			
			setcount = int( (elapsed-TIME_FIRSTWAITING) / TIME_ONESET ) + 1
			
			#if elapsed - int(elapsed) <= 0.01: # デバッグ用
			#	print(elapsed)
			#	print(setcount)
			#	print(ad_kinds[setcount-(len(ad_kinds)*i)-1])
			
			if 0 <= (elapsed-TIME_FIRSTWAITING) % TIME_ONESET and \
			(elapsed-TIME_FIRSTWAITING) % TIME_ONESET < TIME_ONESET / 2: # 無刺激区間
				if flag_disp == True and flag_trans == True:
					hide_ad(im_yoko_path, im_sikaku_path)
			
			else: # 刺激区間
				suf = setcount - len(ad_kinds)*i - 1 # ad_kindsの添え字
				
				# 前面系広告表示が残っている状態で次の広告刺激区間を跨いだ時
				if flag_disp == True and current_ad_kind != ad_kinds[suf] and \
				not(current_ad_kind == 1 or current_ad_kind == 2):
					hide_ad(im_yoko_path, im_sikaku_path)
				
				if flag_trans != True: # 画面遷移なしでは変動なし
					continue
				
				# 非表示
				if flag_disp == True: # 既に広告が表示されている場合
					hide_ad(im_yoko_path, im_sikaku_path)
				
				# 表示
				if ad_kinds[suf] == 1 or ad_kinds[suf] == 2 or is_result == False: # 上下バナーor前面時クイズ画面の時
					current_ad_kind = ad_kinds[suf]
					# 画像設定
					im_yoko_path, im_sikaku_path = (None, None) # グローバル変数にしたほうが良いかも
					if ad_kinds[suf] % 2 == 0: # ランダム画像
						im_yoko_path = random.choice(im_yoko_list)
						im_sikaku_path = random.choice(im_sikaku_list)
					else: # 単色?
						im_yoko_path = SIMPLE_YOKO_PATH
						im_sikaku_path = SIMPLE_SIKAKU_PATH

					display_ad(ad_kinds[suf], im_yoko_path, im_sikaku_path)
					time_disp = get_elapsed_time()
		if flag_finish == True:
			break;
	
	if flag_finish != True:
		print("wait " + str(TIME_LASTWAITING))
		while get_elapsed_time() < TIME_FIRSTWAITING + TIME_ONESET*len(ad_kinds)*NUM_LOOP + TIME_LASTWAITING: # 最後待機
			pass

	print("finish")
	while True:
		pass

# main

if __name__ == '__main__': # コマンドラインから実行された場合
	
	im_sikaku_list = get_image(SIKAKU_DIR)
	im_yoko_list = get_image(YOKO_DIR)
	
	try:
		preparation_files()
		
		advertisingDisplayThread = Thread(target=set_canvas)
		advertisingDisplayThread.setDaemon(True)
		advertisingDisplayThread.start()
        
		advertisingDisplayThread2 = Thread(target=set_canvas2)
		advertisingDisplayThread2.setDaemon(True)
		advertisingDisplayThread2.start()
		
		main_sub()
	
	# Ctrl+C で終了
	except KeyboardInterrupt:
		print ('Ctrl+C pressed...')
		sys.exit(0)