


from picamera import PiCamera

import time

import requests

import base64

import RPi.GPIO

import serial

import sys

import os




#获得百度API的access_token

def getaccess_token():

    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4fVKa7AqDYNApi6Lz8Z2ZeMv&client_secret=gRVy9GcRRGCMiU2GgT20IbbaMu7QfA8P'

    header_1 = {'Content-Type':'application/json; charset=UTF-8'}

    request=requests.post(host,headers =header_1)

    access_token=request.json()['access_token']

    return access_token




#拍摄当前图片

def take_picture():

    camera.start_preview()
    print("1")

    time.sleep(0.5)

    camera.capture('image.jpg')
    print("2")

    camera.stop_preview()
    print("3")




#打开工程拍摄的图片并转换成字符串

def open_pic():

    f = open('image.jpg', 'rb')

    img = base64.b64encode(f.read())

    return img




#上传到百度API进行人脸检验

def go_api(img,access_token):

    data_1 = {"image":img,'group_id':'wenzheng'}

    params_1 = {'access_token':access_token}

    header_2 = {'Content-Type':'application/x-www-form-urlencoded'}

    pic_re=requests.post('https://aip.baidubce.com/rest/2.0/face/v2/identify',params=params_1,headers=header_2,data=data_1)


    print(pic_re.text)
    

    if len(pic_re.text)>130:

        if pic_re.json()['result'][0]['scores'][0]>66:

            print(pic_re.json()['result'][0]['scores'])

            return ('yes')

        else :

            return ('no')




    else:

        print('error')

        return ('no')

    #return(pic_re.json()['result'][0]['scores'])




#点亮指示LED等

def led():

    RPi.GPIO.output(18, True)







#通过蓝牙对Arduino发出开门指令

def send():

    serial.write(bytes(2, 'UTF-8'))

    print('发出指令成功')

    serial.flushInput()




#调用相关函数进行整个程序过程

def try_api(img,access_token):

    try:

        a=go_api(img,access_token)

        if a=='yes':
            printf("11111111111111111")

            #led()

            #send()

            time.sleep(10)

            #RPi.GPIO.output(18, False)

        if a=='no':

            pass

    except:

        pass
def search (img,access_token):
    '''
    人脸搜索
    '''
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image":img,"image_type":"BASE64","group_id_list":"wenzheng","quality_control":"LOW","liveness_control":"NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params)
    test = response.json().get('score')
    print(response.json())
    print(test)
if __name__ == '__main__':

    #程序运行配置命令---------------------------------


    #os.system('sudo rfcomm bind 0 00:21:13:01:8E:1A')

    #RPi.GPIO.setmode(RPi.GPIO.BCM)

    #RPi.GPIO.setup(18, RPi.GPIO.OUT)

    #port = "/dev/rfcomm0"

    #serial = serial.Serial(port,9600)

    count=0

    #程序运行配置命令--------------------------------

    camera = PiCamera()

    access_token=getaccess_token()
    print(access_token)

    while True :

        take_picture()

        img=open_pic()
        
        search(img,access_token)
        #try_api(img,access_token)

        count=count+1

        print(count)

        #加入自动重启命令，防止程序运行时间过长死机

        if count == 2000 :

            os.system('sudo reboot')

            count = 0

#search()
