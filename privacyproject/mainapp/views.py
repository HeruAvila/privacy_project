import json
import requests
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    client_ip = request.META.get('REMOTE_ADDR')
    ip_api_url = 'http://ip-api.com/json/%s' % client_ip
    info_json = {}
    try:
        ip_response = requests.get(ip_api_url)

        if ip_response.status_code == 200:
            info_json = ip_response.json()
            print(info_json)
        else:
            print('Error: ', ip_response.status_code)
    finally:
        return HttpResponse("Test Page. Client IP: %s" % client_ip)
