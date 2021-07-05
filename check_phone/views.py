# Create your views here.
import codecs
import csv
import threading
import time

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

import check_phone.hlr_api as hlr
from check_phone.file_reader import get_values
from check_phone.hlr_theard import worker
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
    result_template = 'request.html'
    error_template = 'balance_error.html'

    def get(self, request, id):
        user = request.user
        temp_req = TempRequest.objects.get(id=id)
        if user.balance < temp_req.price:
            return render(request, self.error_template, {"user_b": user.balance})
        user.balance = user.balance - temp_req.price
        User.objects.filter(id=user.id).update(balance=user.balance)
        phones = temp_req.get_phones()
        user_id = request.user.id
        requests = Requests.objects.create(user_id=user_id)
        for phone in phones:
            Request.objects.create(requests_id=requests.id, phone=phone, hlr_status="Обрабатывается",
                                   hlr_status_code=5)
        t = threading.Thread(target=worker, args=(requests.id, ))
        t.start()
        return redirect(f'/request/{requests.id}')


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
                      {"result": Request.objects.filter(requests_id=id).all().order_by('-id'), "user_b": user.balance, "r_id": id})
