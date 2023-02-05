# raspi_smartlock
Raspberry Piを使った簡易的なスマートロックです．NFCリーダーにSuicaをかざすと鍵を解錠・施錠できます．
 
# DEMO
https://user-images.githubusercontent.com/41606073/216840401-f0499e54-4477-43a9-966a-bd5864d0711d.mp4
 
# Features
* iPhoneなどの「mobile Suica」に対応
* プログラムの一部変更(コメントアウト)でiDなどのカードにも対応可能
* 歯車を工夫することによって歯車を連動して回さないため、物理鍵を使用するときに負荷がかからない
 
# Requirement
* nfcpy 1.0.3
* sqlite3 
* RPi.GPIO

# Installation
```bash
#　念の為pipのインストール
sudo apt install python-pip
sudo apt intall python3-pip

# nfcpyのインストール
sudo pip install nfcpy
sudo pip3 install nfcpy

# sqlite3のインストール
sudo apt install sqlite3

# sqlite browserのインストール
sudo apt install sqlitebrowser

# nfcpy設定
python -m nfc
#上記のコマンドを入力すると，下記のコマンドを入力するように表示される．(これにより，sudoなしで実行可能になる．)
sudo sh -c 'echo SUBSYSTEM==\"usb\", ACTION==\"add\ ATTRS{idVendor}==\"054c\", ATTRS{idProduct}==\"06c1\", GROUP=\"plugdev\" >> /etc/udev/rules.d/nfcdev.rules'
sudo udevadm control -R
```
 
# Usage
以下の部品で動作の確認をしています。
* Raspberry pi 3 (Raspberry pi zeroでも可)
* MG996Rモーダー
* ソニー製NFCリーダー
* 3Dプリンタ製の本体(body,thumb_turn, stick, gear_large, gear_small)


## raspberry pi3 model BのGPIOピンに以下のように配線をする．
### モーター
GPIO4 : 信号線(黄色)
5V PWA : 5V線(赤色)
GND    : GND線(黒色)
### スイッチ
GPIO3とGND

## 実行方法
以下のコマンドで実行する．
最初にnfcの読み込み状態となる．この時，登録済みSuicaをNFCリーダーにタッチするとモーターが動く．
また，スイッチを押すと，名前とSuica情報を保存するデータベース操作モードに移行する．表示されるコメントに従って登録などすればOK.
```bash
git clone https://github.com/zusizusi/raspi_smartlock.git
python3 nfcservo.py
```
 
# Note
## Raspiが起動したら自動実行する方法
### 1 .shファイルを作製
```bash
nano autorun.sh
```
autorun.shの中身
```bash
#!/bin/sh
python3 nfcservo.py
```
autorun.shを保存後，実行権限を付与
```bash
chmod +x autorun.sh
```
### 2 自動実行用のフォルダ作製
```bash
cd .config
mkdir autostart
cd autostart
```
### 3 設定ファイルの作成
```bash
nano nfcservo.desktop
```
nfcservo.desktopの内容
```bash
[Desktop Entry]
Exec=lxterminal -e /home/pi/autorun.sh
Type=Application
Name=Nfcservo
Terminal=true
```


# Author
* 作成者 : zusi
 
# License
"raspi_smartlock" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
 
"raspi_smartlock" is Confidential.
