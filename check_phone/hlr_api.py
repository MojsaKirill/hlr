import json
import urllib.request

text = 'HLR'  # текст сообщения
apikey = '5654C9J6C27451UR702ZIBNCPIKWLN44LI1721D4FJ9H7EM83PFMMH53CAE08S6F'


def send_hlr(phone):
    url = f"http://smspilot.ru/api.php?send={text}&to={phone}&apikey={apikey}&format=json"
    j = json.loads(urllib.request.urlopen(url).read())
    print(j)
    server_id = j['send'][0]['server_id']
    return server_id


def get_hlr_result(server_id):
    url = f"https://smspilot.ru/api.php?check={server_id}&apikey={apikey}&format=json"
    j = json.loads(urllib.request.urlopen(url).read())
    print(j)
    status = int(j['check'][0]['status'])
    # while status == 0 or status == 1:
    #     j = json.loads(urllib.request.urlopen(url2).read())
    #     status = int(j['check'][0]['status'])
    return status
