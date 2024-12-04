import requests
from django.shortcuts import render
from user_agents import parse
def get_browser_info(request):
    #citation: https://stackoverflow.com/questions/2669294/how-to-detect-browser-type-in-django
    browser_info = request.META.get('HTTP_USER_AGENT')
    parsed = parse(browser_info)
    return parsed
def get_ClientIP(request):
    #citation: https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return client_ip

def getTorExits():
    list = requests.get('https://check.torproject.org/torbulkexitlist')
    if list.status_code == 200:
        return set(list.text.splitlines())
    else:
        print('Error getting the list of exit nodes. Error is: ',list.status_code)

def using_tor(client_ip, tor_ip_list):
    using_tor = False
    if client_ip in tor_ip_list:
        using_tor = True
        print("Using TOR")
    else:
        using_tor = False
        print("Not using TOR")

    return using_tor

def get_ipinfo(client_ip):
    ip_api_url = 'http://ip-api.com/json/%s' % client_ip
    info_json = {}
    try:
        ip_response = requests.get(ip_api_url)

        if ip_response.status_code == 200:
            info_json = ip_response.json()
        else:
            print('Error: ', ip_response.status_code)
    finally:
        return info_json

def index(request):
    client_IP = get_ClientIP(request)
    tor_list = getTorExits()
    tor_in_use = using_tor(client_IP, tor_list)
    json_info = get_ipinfo(client_IP)
    browser_info = get_browser_info(request)
    return render(request, 'mainapp/index.html',
                  context={'tor_in_use': tor_in_use,
                           'json_info': json_info,
                           'browser_info':browser_info,
                           })




