# Create your views here.
import codecs
import csv
import time

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

import check_phone.hlr_api as hlr
from check_phone.file_reader import get_values
from check_phone.models import Request, Requests, TempRequest, Price, User


class HLRRes:
    def __init__(self, phone, server_id=None, status_code=None, status=None):
        self.phone = phone
        self.server_id = server_id
        self.status_code = status_code
        self.status = status


class PhoneView(LoginRequiredMixin, View):
    login_url = '/login'
    index_template = 'index.html'
    result_template = 'accept_request.html'

    def get(self, request):
        user = request.user
        return render(request, self.index_template, {"user_b": user.balance})

    def post(self, request):
        user = request.user
        if not request.FILES:
            return redirect('/')
        file = request.FILES['file'].file
        phones = get_values(file)
        user_price = user.sale_price
        if user_price == 0:
            price = Price.objects.first()
            user_price = price.default_price
        price = len(phones) * user_price
        tr = TempRequest(user_id=user.id, price=price)
        tr.set_phones(phones)
        tr.save()
        return render(request, self.result_template, {"tempRequest": tr, "user_b": user.balance})


class AcceptView(LoginRequiredMixin, View):
    login_url = '/login'
    index_template = 'index.html'
    result_template = 'result.html'
    error_template = 'balance_error.html'

    def get(self, request, id):
        user = request.user
        temp_req = TempRequest.objects.get(id=id)
        if user.balance < temp_req.price:
            return render(request, self.error_template)
        user.balance = user.balance - temp_req.price
        User.objects.filter(id=user.id).update(balance=user.balance)
        phones = temp_req.get_phones()
        hlr_results = []
        user_id = request.user.id
        requests = Requests.objects.create(user_id=user_id)
        for phone in phones:
            r = Request.objects.filter(phone=phone).first()
            if r is None:
                hlr_server_id = hlr.send_hlr(phone)
                if hlr_server_id is not None:
                    hlr_results.append(HLRRes(phone=phone, server_id=hlr.send_hlr(phone)))
            else:
                hlr_results.append(HLRRes(phone=r.phone, status_code=r.hlr_status_code, status=r.hlr_status))
        time.sleep(10)
        for hlr_res in hlr_results:
            if hlr_res.server_id is not None:
                hlr_res.status_code = hlr.get_hlr_result(hlr_res.server_id)
            if hlr_res.status_code is None:
                    hlr_res.status = 'Ошибка сервера'
            if hlr_res.status_code == -2:
                hlr_res.status = 'Неправильный номер'
            if hlr_res.status_code == -1:
                hlr_res.status = 'Номер не обсуживается'
            if hlr_res.status_code == -0:
                hlr_res.status = 'Запрос принят'
            if hlr_res.status_code == 1:
                hlr_res.status = 'Запрос передан оператору'
            if hlr_res.status_code == 2:
                hlr_res.status = 'Номер обсуживается'
            Request.objects.create(requests_id=requests.id, phone=hlr_res.phone, hlr_status=hlr_res.status,
                                   hlr_status_code=hlr_res.status_code)
        return render(request, self.result_template,
                      {"result": hlr_results, "user_b": user.balance, "r_id": requests.id})


class DeniedView(LoginRequiredMixin, View):
    login_url = '/login'
    index_template = 'index.html'

    def get(self, request, id):
        tr = TempRequest.objects.get(id=id)
        tr.delete()
        return redirect('/')


class MyLoginView(LoginView):

    def form_valid(self, form):
        if self.request.recaptcha_is_valid:
            login(self.request, form.get_user())
            return HttpResponseRedirect("/")
        return render(self.request, 'registration/login.html', self.get_context_data())


class RequestsView(LoginRequiredMixin, View):
    login_url = '/login'
    result_template = 'requests.html'

    def get(self, request):
        user = request.user
        requests = Requests.objects.filter(user_id=1).order_by('-request_date').all()
        return render(request, self.result_template,
                      {"result": requests, "user_b": user.balance})


class DownloadView(LoginRequiredMixin, View):
    def get(self, request, id):
        requests = Request.objects.filter(requests_id=id).all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result.csv"'
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=';')

        for request in requests:
            writer.writerow([request.phone, request.hlr_status])

        return response


class RequestView(LoginRequiredMixin, View):
    login_url = '/login'
    result_template = 'request.html'

    def get(self, request, id):
        user = request.user
        return render(request, self.result_template,
                      {"result": Request.objects.filter(requests_id=id).all(), "user_b": user.balance, "r_id": id})
