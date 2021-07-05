import check_phone.hlr_api as hlr
from check_phone.models import Request, Requests


def worker(requests_id):
    requests = Requests.objects.get(id=requests_id)
    requests_phone = Request.objects.all().filter(requests_id=requests.id)
    status = {}
    for req in requests_phone:
        r = Request.objects.filter(phone=req.phone).first()
        if r is None:
            hlr_server_id = hlr.send_hlr(req.phone)
            if hlr_server_id is not None:
                status_code = hlr.get_hlr_result(hlr_server_id)
                if status_code == -2:
                    status = 'Неправильный номер'
                if status_code == -1:
                    status = 'Номер не обсуживается'
                if status_code == -0:
                    status = 'Запрос принят'
                if status_code == 1:
                    status = 'Запрос передан оператору'
                if status_code == 2:
                    status = 'Номер обсуживается'
                Requests.objects.filter(id=req.id).update(hlr_status=status, hlr_status_code=status_code)
            else:
                Request.objects.filter(id=req.id).update(hlr_status="Ошибка")
        else:
            Request.objects.filter(id=req.id).update(hlr_status=r.hlr_status, hlr_status_code=r.hlr_status_code)
