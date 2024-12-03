from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    client_ip = request.META.get('REMOTE_ADDR')
    return HttpResponse("Test Page. Client IP: %s" % client_ip)