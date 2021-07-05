import json
import urllib.request
import time

text = 'HLR'  # текст сообщения
apikey = '5654C9J6C27451UR702ZIBNCPIKWLN44LI1721D4FJ9H7EM83PFMMH53CAE08S6F'


def send_hlr(phone):
    try:
        url = f"http://smspilot.ru/api.php?send={text}&to={phone}&apikey={apikey}&format=json"
        j = json.loads(urllib.request.urlopen(url).read())
        count = 0
        while j.get('send') is None or j.get('send')[0] is None or j.get('send')[0].get('server_id') is None \
                and count < 20:
            time.sleep(3)
            j = json.loads(urllib.request.urlopen(url).read())
            count = count + 1
        server_id = j['send'][0]['server_id']
        return server_id
    except Exception:
        return None


def get_hlr_result(server_id):
    try:
        url = f"https://smspilot.ru/api.php?check={server_id}&apikey={apikey}&format=json"
        j = json.loads(urllib.request.urlopen(url).read())
        count = 0
        while j.get('check') is None or j.get('check')[0] is None or j.get('check')[0].get('status') is None\
                or j.get('check')[0].get('status') == 0 or j.get('check')[0].get('status') == 1 and count < 20:
            time.sleep(3)
            j = json.loads(urllib.request.urlopen(url).read())
            count = count + 1
        status = int(j['check'][0]['status'])
        # while status == 0 or status == 1:
        #     j = json.loads(urllib.request.urlopen(url2).read())
        #     status = int(j['check'][0]['status'])
        return status
    except Exception:
        return None
