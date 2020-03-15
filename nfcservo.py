#!/usr/bin/env python
#! -*- coding:utf-8 -*-
import binascii
import nfc

import RPi.GPIO as GPIO
import datetime
import time
import sqlite3
import datetime
import time
import threading
import ctypes


###### NFC readerの設定 ######
# Suica待ち受けの1サイクル秒
TIME_cycle = 1.0
# Suica待ち受けの反応インターバル秒
TIME_interval = 0.2
# タッチされてから次の待ち受けを開始するまで無効化する秒
TIME_wait = 3

# NFC接続リクエストのための準備
# 212F(FeliCa)で設定
target_req_suica = nfc.clf.RemoteTarget("212F")
# スイカ指定(コメントアウトでiDとかにも対応．なお，iphoneのスイカには非対応になる．)
target_req_suica.sensf_req = bytearray.fromhex("0000030000")
##########################

###### GPIOの設定 #######
#「GPIO4出力」でPWMインスタンスを作成する。
#GPIO.PWM( [ピン番号] , [周波数Hz] )
#SG92RはPWMサイクル:20ms(=50Hz), 制御パルス:0.5ms〜2.4ms, (=2.5%〜12%)。
SERVO_GPIO = 4  #Raspberyy Piのサーボモータと接続詞ているGPIOのピン番号
SERVO_PWM = 50 #サーボモータのPWMサイクル値(SG-90の場合、20ms=50Hz)
SERVO_OPEN =10.85  #時にサーボモータに渡すデューティサイクル値(鍵に合わせて変更)
SERVO_CLOSE =4.55 #施錠時にサーボモータに渡すデューティサイクル値(鍵に合わせて変更)
SERVO_wait = 7.7 #施錠時にサーボモータに渡すデューティサイクル値(鍵に合わせて変更)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_GPIO, GPIO.OUT)
##########################

###### 鍵の設定 #######
# 鍵の状態を保管w
status = ""
db_change_signal = "off"
####################		


def nfc_imput():
    global db_change_signal
    # USBに接続されたNFCリーダに接続してインスタンス化
    clf = nfc.ContactlessFrontend('usb')
    while True:
        # Suica待ち受け開始
        # clf.sense( [リモートターゲット], [検索回数], [検索の間隔] )
        target_res = clf.sense(target_req_suica, iterations=int(TIME_cycle//TIME_interval)+1 , interval=TIME_interval)
        if target_res is not None: 
            #tag = nfc.tag.tt3.Type3Tag(clf, target_res)
            #なんか仕様変わったっぽい？↓なら動いた
            tag = nfc.tag.activate_tt3(clf, target_res)
            tag.sys = 3
            #IDmを取り出す
            idm = binascii.hexlify(tag.idm)
            #print('Suica detected. idm = ' + str(idm))
            break
        if db_change_signal == "on":
            idm = "db_change"
            break
        
        
    clf.close()	
    return idm


def database_change(waitinput):
    global db_change_signal
    #print("NFC登録データベースを改変します。以下の選択肢から該当番号を入力してください。\n データの追加:1\n データの削除:2\n 全データの照会:3")
    number = waitinput
    #number = input('該当番号>> ')

    # データの追加
    if number == str(1):
        print("名前とsuicaを登録します．")
        print("あなたの名前を教えてください。 例　Shintaro_Hasegawa")
        your_name = input('name>> ')
        print("name : " + your_name)
        db_change_signal = "off"
        print("登録するNFCカードをリーダーにかざしてください")
        idm = nfc_imput()

        person_name = str(your_name)
        idm_number = str(idm)
        detect_time = str(time.time())
        print("[登録内容]" + " name:" + person_name + ", idm:" + idm_number + ", time:" + detect_time)
        # データベースにidm_numberがあるかどうか検索
        serchresult = databese_namelist.idm_serch(idm_number)
        # idmがデータベースになかったら
        if serchresult == None:
            databese_namelist.insert(person_name, idm_number, detect_time)
            print(">>> registered your name and nfc card.")
        # idmがデータベースにあったら
        else:
            databese_namelist.update(person_name, idm_number, detect_time)
            print(serchresult[0] + "　　>>　　" + person_name)
            print(">>> database was updated.")


    # データの削除
    elif number == str(2):
        print("登録データの削除をします．")
        db_change_signal = "off"
        print("削除するNFCカードをリーダーにかざしてください")
        idm_number = str(nfc_imput())
        # データベースにidm_numberがあるかどうか検索
        serchresult = databese_namelist.idm_serch(idm_number)
        #　idmがデータベースにあったら
        if serchresult is not None:
            databese_namelist.delite(idm_number)
            print(">>> Data deletion completed")
        #  idmがデータベースになかったら   
        else:
            print(">>> このNFCカードは登録されていません")


    # データの表示
    elif number == str(3):
        print("登録されているIDの一覧を表示します．")
        db_change_signal = "off"
        datas = databese_namelist.show()
        for data in datas:
            print(data)
    else:
        print("errer")
        print("半角で　1 or 2 or 3を入力して")
    
    time.sleep(5)
    



class Databese_Namelist():
    def __init__(self):
        self.dbpath = '/home/pi/nfcname.db'
        self.connection = sqlite3.connect(self.dbpath)
        self.connection.isolation_level = None # 自動コミット
        self.cursor = self.connection.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS namelist(person_name TEXT NOT NULL, idm_number TEXT NOT NULL primary key, detect_time TEXT NOT NULL)'
        self.cursor.execute(sql)
        # コミット
        self.connection.commit()
    
    def idm_serch(self,idm_number):
        connection=self.connection
        cursor=self.cursor
        # データベースにidm_numberがあるかどうか検索
        sql = "select * from namelist where idm_number = ?"
        datas = (idm_number,) #タプル型で渡す
        result =  connection.execute(sql, datas).fetchone()
        connection.commit() 
        return result


    def insert(self,person_name, idm_number, detect_time):
        connection=self.connection
        cursor=self.cursor
        sql = 'INSERT INTO namelist (person_name, idm_number, detect_time) VALUES (?,?,?)'
        datas = (person_name, idm_number, detect_time,)
        connection.execute(sql, datas)
        connection.commit() 


    def update(self,person_name, idm_number, detect_time):
        connection=self.connection
        cursor=self.cursor
        sql = "UPDATE namelist SET person_name = ?, detect_time = ? WHERE idm_number = ?"
        datas = (person_name, detect_time, idm_number,)
        connection.execute(sql, datas)
        connection.commit() 
        #print(datas)

    def delite(self,idm_number):
        connection=self.connection
        cursor=self.cursor
        sql = "delete from namelist where idm_number = ?"
        datas = (idm_number,)
        connection.execute(sql, datas)
        connection.commit() 


    def show(self):
        connection=self.connection
        cursor=self.cursor
        sql = "SELECT * FROM namelist"
        ### *は全カラムを意味．namelistはテーブル名
        ### レコード毎の全カラムの値を含むタプルのリストとして抽出される
        datas = connection.execute(sql).fetchall()
        connection.commit() 
        return datas



# サーボ関係
class ServoCon:

    def control_key(dc):
        servo = GPIO.PWM(SERVO_GPIO, SERVO_PWM)
        servo.start(0.0)
        servo.ChangeDutyCycle(dc)
        time.sleep(0.3) #モータが動き終わるまで待ち
        servo.stop()


    def open_key():
        global status
        ServoCon.control_key(SERVO_OPEN)
        time.sleep(0.5)       
        ServoCon.control_key(SERVO_wait)
        time.sleep(0.5) 
        status = "open"
        return status
        servo.stop()


    def close_key():
        global status
        ServoCon.control_key(SERVO_CLOSE)
        time.sleep(0.5)       
        ServoCon.control_key(SERVO_wait)
        time.sleep(0.5)
        status = "close"
        return status
        servo.stop()


    def get_status():
        global status
        return status
        servo.stop()

def nfcservo():
    global imput_number

    print ('NFC waiting...')
    idm = nfc_imput()
    if idm == "db_change":
        database_change(imput_number)

        return
    # 特定のIDmだった場合のアクション
    # データベースにidm_numberがあるかどうか検索
    serchresult = databese_namelist.idm_serch(str(idm))
    # idmがデータベースになかったら
    if serchresult == None:
        print(str(idm) + "は登録されていません")
        # logを記録する

        time.sleep(1)
        
    elif serchresult[1] == str(idm):
        print("【 " + serchresult[0] + "の登録済みid : " + serchresult[1] + "】")
        
        # 現在の状態を記録
        before_status = ServoCon.get_status()
        
        if before_status == "open":
            ServoCon.close_key()
        elif before_status == "close":
            ServoCon.open_key()
        print("status : " + before_status + ">>>>>" + ServoCon.get_status())
        
        # logを記録する
        #file = open(file_log,'a')
        #file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ", " + result[0]+ ", " + str(idm) + ", " + before_status + ">>>" + ServoCon.get_status() + "\n")
        #file.close()

        # 念のため１秒まつ
        time.sleep(1)    
        
    else:
        print("errer")

def waitcount():
    global db_change_signal
    global imput_number
    print("NFC登録データベースを改変します。以下の選択肢から該当番号を入力してください。\n データの追加:1\n データの削除:2\n 全データの照会:3")
    number = input('該当番号>> ')
    if number == str(1) or str(2) or str(3):
        db_change_signal = "on"
        #print(db_change_signal)
        imput_number = number
        
    else:
        print("errer")
        print("半角で　1 or 2 or 3を入力して")
        
        
    
if __name__ == '__main__':
    try:
        # 最初にオープン状態にする
        ServoCon.control_key(SERVO_OPEN)
        status = "open"
        databese_namelist = Databese_Namelist()

        
        # logを記録する
        #file = open(file_log,'a')
        #file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ", nfcservo.py_START\n")
        #file.close()
        
        while True:
            #nfcservo_thread = threading.Thread(target=nfcservo)
            waitcount_thread = threading.Thread(target=waitcount)

            #nfcservo_thread.start()
            waitcount_thread.start()
            #nfcservo_thread.join()
            #waitcount_thread.join()

            nfcservo()

    except KeyboardInterrupt:
        GPIO.cleanup()
        waitcount_thread.kill()
        #cconnection.close()
        pass
