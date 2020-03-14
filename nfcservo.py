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
####################		


def nfc_imput():
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
	clf.close()	
	return idm


def database_change():
    print("NFC登録データベースを改変します。以下の選択肢から該当番号を入力してください。\n データの追加:1\n データの削除:2\n 全データの照会:3")
    number = input('該当番号>> ')

    # データの追加
    if number == str(1):
        print("名前とsuicaを登録します．")
        print("あなたの名前を教えてください。 例　Shintaro_Hasegawa")
        your_name = input('name>> ')
        print("name : " + your_name)
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
            print("registered your name and nfc card.")
        # idmがデータベースにあったら
        else:
            databese_namelist.update(person_name, idm_number, detect_time)
            print(serchresult[0] + "　　>>　　" + person_name)
            print("database was updated.")


    # データの削除
    elif number == str(2):
        print("登録データの削除をします．")
        print("削除するNFCカードをリーダーにかざしてください")
        idm_number = str(nfc_imput())
        # データベースにidm_numberがあるかどうか検索
        serchresult = databese_namelist.idm_serch(idm_number)
        #　idmがデータベースにあったら
        if serchresult is not None:
            databese_namelist.delite(idm_number)
            print("complited delete data")
        #  idmがデータベースになかったら   
        else:
            print("登録されていません")


    # データの表示
    elif number == str(3):
        print("登録されているIDの一覧を表示します．")
        datas = databese_namelist.show()
        for data in datas:
            print(data)
    else:
        print("errer")
        print("errer ¥n 半角で　1 or 2 or 3を入力して")


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



    
if __name__ == '__main__':
    try:
        databese_namelist = Databese_Namelist()
        #while 1:
            
        database_change()

    except KeyboardInterrupt:
        
        cconnection.close()
        pass
