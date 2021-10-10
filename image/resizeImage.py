#画像サイズをリサイズする
# -*- coding: utf8 -*-
from PIL import Image
import matplotlib.pyplot as plt


width = 300 #リサイズ後の縦ピクセル数
height = 280 #リサイズ後の横ピクセル数
IMAGE_DIR = "original_image\\sikaku"
OUTPUT_DIR = "small_image\\sikaku"
image_name = "carrirup_navi.png" #リサイズ前の画像名
resize_name = "small"+image_name#リサイズ後の画像名


#画像の読み込み
image_view = Image.open(IMAGE_DIR+image_name)

#画像を表示して確認
plt.imshow(image_view)

#画像のリサイズ
resize_view = image_view.resize((width, height))

#リサイズした画像を表示して確認
plt.imshow(resize_view)

#リサイズした画像を名前をつけて保存
resize_view.save(OUTPUT_DIR+resize_name)
