import snowboydecoder
import sys
import time
import requests
import base64
import signal

interrupted = False

def getaccess_token():

    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=4fVKa7AqDYNApi6Lz8Z2ZeMv&client_secret=gRVy9GcRRGCMiU2GgT20IbbaMu7QfA8P'

    header_1 = {'Content-Type':'application/json; charset=UTF-8'}

    request=requests.post(host,headers =header_1)

    access_token=request.json()['access_token']
    print(access_token)
    return access_token
def search (img,access_token):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image":img,"image_type":"BASE64","group_id_list":"wenzheng","quality_control":"LOW","liveness_control":"NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params)
    test = response.json().get('score')
    print(response.json())
    print(test)

def callbacks():
    print("Wake UP!....")
    snowboydecoder.play_audio_file()
    detector.terminate()
    print("Close snowboy...")
    signal.signal(signal.SIGINT, signal_handler)
    
def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
getaccess_token()
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
def wake_up():

    
    global detector
    model = 'snowboy.pmdl'  #  唤醒词为 SnowBoy
    # capture SIGINT signal, e.g., Ctrl+C
    
    signal.signal(signal.SIGINT, signal_handler)

    # 唤醒词检测函数，调整sensitivity参数可修改唤醒词检测的准确性
    
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    
    print('Listening... please say wake-up word:SnowBoy')
    # main loop
    # 回调函数 
    detected_callback=snowboydecoder.play_audio_file 
    # 修改回调函数可实现我们想要的功能
    
    detector.start(detected_callback=callbacks,      # 自定义回调函数
                   
    interrupt_check=interrupt_callback,
                   
    sleep_time=0.03)
    # 释放资源
    
    detector.terminate()


if __name__ == '__main__':


     wake_up()
