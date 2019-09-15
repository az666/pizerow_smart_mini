# -*- coding: utf-8 -*-
import thread
from picamera import PiCamera
import paho.mqtt.client as mqtt
import snowboydecoder
from aip import AipSpeech
import sys
import time
import RPi.GPIO
import serial
import requests,json
import base64
import signal
import RPi.GPIO
import serial
import sys
import os
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings()
APP_ID = '百度'
API_KEY = '百度'
SECRET_KEY = '百度'
MQTTHOST = "106.1.1.1"  #自己的MQTT服务器
MQTTPORT = 1883
MQTTID = "xiaohei"
MQTTUSER = "wenzheng"
MQTTPASSWORD = "wenzheng"
MQTTPUB_TOPIC = "xiaohei"
ALLMSG = ""
mqttClient = mqtt.Client(MQTTID)

interrupted = False
def getaccess_token():

    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4fVKa7AqDYNApi6Lz8Z2ZeMv&client_secret=gRVy9GcRRGCMiU2GgT20IbbaMu7QfA8P'

    header_1 = {'Content-Type':'application/json; charset=UTF-8'}

    request=requests.post(host,headers =header_1)

    access_token=request.json()['access_token']
    print(access_token)
    return access_token

def Speech(access_token):
    global detector
    #string = "你是不是傻".encode('utf-8')
    request_url = "http://vop.baidu.com/server_api"
    headers = { 'Content-Type' : 'application/json' }
    VOICE_RATE = 16000
    WAVE_FILE = "ddd.wav" 
    USER_ID = "zhp-fw" 
    WAVE_TYPE = "wav"
    # begin Speech
    os.system('play /home/pi/snowboy/dong.wav')
    #os.system('espeak -vzh "%s"'%"你是不是傻".encode('utf-8'))
    os.system('arecord -d 4 -r 16000 -c 1 -t wav -f S16_LE -D plughw:1,0  ddd.wav')
    f = open(WAVE_FILE, "rb") 
    speech = base64.b64encode(f.read())
    size = os.path.getsize(WAVE_FILE)
    data_json = json.dumps({"format":WAVE_TYPE, "rate":VOICE_RATE, "channel":1,"cuid":USER_ID,"token":access_token,"speech":speech,"len":size})
    #request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=data_json,headers=headers)
    print(response.text)
    if response.json().get('err_msg')=='success.':
        word = response.json().get('result')[0].encode('utf-8')
        #baidu_tts(word) #自定义对话逻辑（接入智能控制）
        if "歌" in word :
            print(word)
            os.system('mpg123 /home/pi/snowboy/woceng.mp3')
        if "你好" in word :   #http://boscdn.bpc.baidu.com/v1/developer/315e48e0-0a0d-46ab-b0d0-c217d1a77439.mp3
            #os.system('play http://boscdn.bpc.baidu.com/v1/developer/315e48e0-0a0d-46ab-b0d0-c217d1a77439.mp3')
            os.system('espeak -vzh 别说那么多没用的，赶紧学习了')
            print("123")
        if "开灯" in word:
            baidu_tts("哦几把K")  #发布MQTT详细控制硬件
            mqttClient.publish(MQTTPUB_TOPIC, "open_led", 1)
        if "关灯" in word:
            baidu_tts("已执行命令")#发布MQTT详细控制硬件
            mqttClient.publish(MQTTPUB_TOPIC, "close_led", 1)
        if "我是谁" in word:     #触发人脸识别，进行图片比对
            take_picture()
            img=open_pic()
            search(img,access_token)   
def tuling(words):   #图灵机器人对话逻辑
    url2 = "http://i.itpk.cn/api.php?api_key=6ba480f37d92f31a0fc35721721afd23&api_secret=v42o7hn8e6zr&question= 你好呀&limit=5"
    url = "http://openapi.tuling123.com/openapi/api/v2"
    api_key = "556909e7a3e04c0383c6da6408559079"
    data = {"userInfo":{"key":api_key,"userId":"wenzheng"},"info":words.encode("utf-8")}
def baidu_tts(words):
    result = client.synthesis(text = words, options={'vol':5})
    if not isinstance(result,dict):
        with open('audio.mp3','wb') as f:
            f.write(result)
        os.system('play audio.mp3')
    else:print(result)
def take_picture():
    camera.start_preview()
    time.sleep(0.5)
    camera.capture('image.jpg')
    camera.stop_preview()
def open_pic():
    f = open('image.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img
def search (img,access_token):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image":img,"image_type":"BASE64","group_id_list":"wenzheng","quality_control":"LOW","liveness_control":"NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params)
    output = response.json()
    if output['error_msg'] == 'SUCCESS':
        ##判断是否成功
        ##找到字典里的result－以及内层字典里的user_list
        user_list= output['result']['user_list']
        print(user_list)
        ##输出数据类型，发现其为列表
        ##利用列表的检索方式找到列表里的人脸检测分数－score
        score = user_list[0]['score']
        print(score)
        user = user_list[0]['user_info']
        if user == 'pengwenzheng':     #判断人脸相似度，并给予反馈
            out_wav = "你是阿正!"+ "相似度为百分之" + str(score)
            baidu_tts(out_wav)
    else:
        errormsg = output['error_msg']
        out_wav = "识别错误"+ str(errormsg)
        baidu_tts(out_wav)
def callbacks():   #自定义返回命令
    global detector
    print("Wake UP!....")
    snowboydecoder.play_audio_file() # ding
    detector.terminate()        # close
    Speech(access_token)
    wake_up()
def on_mqtt_connect():
    mqttClient.username_pw_set(MQTTUSER,MQTTPASSWORD)
    mqttClient.on_connect = on_connect
    #mqttClient.on_message = on_message # 消息到来处理函数
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_forever()   
def on_connect(mqttClient, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #打印连接状态
    #mqttClient.subscribe(MQTTSUB_TOPIC, 0)  # 接收指定服务器的消息
def signal_handler(signal, frame):
    global interrupted
    interrupted = True
def interrupt_callback():
    global interrupted
    return interrupted
def wake_up():          #离线唤醒
    global detector
    model = '/home/pi/snowboy/resources/XHXH.pmdl'
    signal.signal(signal.SIGINT, signal_handler)
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... please say wake-up word:XHXH')
    # main loop
    detector.start(detected_callback=callbacks,interrupt_check=interrupt_callback,sleep_time=0.03)
    detector.terminate()
def thread1():        #MQTT在另一个线程
    on_mqtt_connect()
if __name__ == '__main__':
    camera = PiCamera()
    access_token = getaccess_token()
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    thread.start_new_thread(thread1, ())   #开启多线程
    wake_up()
