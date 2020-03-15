# raspi_smartlock
Raspberry Piを使った簡易的なスマートロックです．NFCリーダーにSuicaをかざすと鍵を解錠・施錠できます．
 
# DEMO
後で追加
 
# Features
・iPhoneなどの「mobile Suica」に対応
・プログラムの一部変更(コメントアウト)でiDなどのカードにも対応可能
 
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
 
# Author

* 作成者 : zusi
* 所属   : 
* E-mail: 
 
# License
"raspi_smartlock" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
 
"raspi_smartlock" is Confidential.