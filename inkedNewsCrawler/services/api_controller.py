
LOCAL_API_MODE = True

if LOCAL_API_MODE:
    BASE_SERVER_URL = "http://127.0.0.1:8000/"
else:
    BASE_SERVER_URL = "http://nginx-lb-429321543.ap-northeast-2.elb.amazonaws.com/"
