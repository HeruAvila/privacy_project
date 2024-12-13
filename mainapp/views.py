from datetime import datetime

import requests
from django.http import HttpResponse
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
        filtered_json = {}
        for key in info_json.keys():
            if key == "country":
                filtered_json.update({'Country': info_json[key]})
            elif key == "regionName":
                filtered_json.update({'Region Name': info_json[key]})
            elif key == "city":
                filtered_json.update({'City': info_json[key]})
            elif key == "zip":
                filtered_json.update({'Zip': info_json[key]})
            elif key == "lat":
                filtered_json.update({'Latitude': info_json[key]})
            elif key == "lon":
                filtered_json.update({'Longitude': info_json[key]})
            elif key == "timezone":
                filtered_json.update({'Timezone': info_json[key]})
            elif key == "isp":
                filtered_json.update({'ISP': info_json[key]})
            elif key == "query":
                filtered_json.update({'IP': info_json[key]})
        return filtered_json


def cookie_setter(response, visit_count, current_location, current_date,home_location):
    # https://stackoverflow.com/questions/17057536/how-to-set-cookie-and-render-template-in-django
    response.set_cookie('visit_count', visit_count,60*60*24*90) #exp in 90 days
    response.set_cookie('last_visit', current_date,60*60*24*90)
    response.set_cookie('last_location', current_location,60*60*24*90)


    response.set_cookie('home_location',home_location,60*2)
    #This will idealy be 12 hours or more but since we are going to do a demo we will keep it at 2 minutes.


def vpn_checker(current_location, home_location,visit_count):
    vpn_used = False
    print("Current Location: "+current_location)
    print("Last Location: "+home_location)
    print("Visit Count: ",visit_count)
    if(current_location == home_location or visit_count == 1):
        if(visit_count == 1):
            vpn_used = False
            return (vpn_used, 'First time visiting. You current location has been saved and will be used later on to detect VPN usage. This location can be updated every 12 hours.')
        else:
            vpn_used = False
            return (vpn_used,'VPN is not being used. Same location detected as home location.')
    else:
        c_city, c_region, c_country = current_location.split(',')
        print("Current City,Region,Country: "+c_city+", "+c_region+", "+c_country)
        h_city, h_region, h_country = home_location.split(',')
        print("Last City,Region,Country: "+h_city+", "+h_region+", "+h_country)
        if(c_city != h_city and c_region == h_region and c_country == h_country):
            vpn_used = False
            return (vpn_used, 'We detected a different city than your home location but will not treat this as a VPN usage since the region and country have not changed.')
        elif(c_region != h_region and c_country == h_country):
            vpn_used = True
            return (vpn_used, 'We have detected a different Region and same country from your home location, but we are treating this as VPN use. This may happen if you are traveling.')
        elif (c_country != h_country):
            vpn_used = True
            return (vpn_used, 'We have detected a different country of visit than your home location and will treat this as a VPN use.')

    return (vpn_used, 'Unable to determine VPN usage based on the provided data.')

def us_only(request):
    client_IP = get_ClientIP(request)
    json_info = get_ipinfo(client_IP)
    country = json_info.get('Country','Unknown')

    print(country)

    if(country == 'United States'):
        return render(request, 'mainapp/us_only.html')
    else:
        return HttpResponse("Access Denied: This page is only accessible from within the US.")

def non_us(request):
    client_IP = get_ClientIP(request)
    json_info = get_ipinfo(client_IP)
    country = json_info.get("Country")

    if(country != 'United States'):
        return render(request, 'mainapp/non_us.html')
    else:
        return HttpResponse("Access Denied: This page is only accessible from outside the US.")
def no_tor(request):
    client_IP = get_ClientIP(request)
    tor_list = getTorExits()
    tor_in_use = using_tor(client_IP, tor_list)
    if(not tor_in_use):
        return render(request, 'mainapp/tor.html')
    else:
        return HttpResponse("Access Denied: You are using TOR, this page can only be accessed when you are not using TOR.")


def check_browser_version(browser_info):
    up_to_date_json = requests.get("https://www.browsers.fyi/api/").json()
    curr_browser = browser_info.browser.version_string.split(".")[0]
    curr_name = browser_info.browser.family
    print("cur_browser: ", curr_browser)
    print("cur_name: ", curr_name)
    up_to_date_bool = False
    needed_ver = 0
    if curr_name == "Firefox":
        needed_ver = up_to_date_json['firefox']['engine_version']
        if curr_browser == needed_ver:
            up_to_date_bool = True
    elif curr_name == "Chrome":
        needed_ver = up_to_date_json['chrome']['engine_version']
        if curr_browser == needed_ver:
            up_to_date_bool = True
    elif curr_name == "Edge":
        needed_ver = up_to_date_json['edge']['engine_version']
        if curr_browser == needed_ver:
            up_to_date_bool = True
    elif curr_name == "Safari":
        needed_ver = up_to_date_json['safari']['engine_version']
        if curr_browser == needed_ver:
            up_to_date_bool = True
    else:
        return False, "We can't detect if your browser version is up to date. Make sure you're Browser is the latest version!"

    if up_to_date_bool:
        return False, "Your Browser version is up to date! Good Job!"
    else:
        s = "Your Browser version is not up to date :(. Latest Version: %s" % needed_ver
        return True, s

def index(request):
    current_date = datetime.now()
    client_IP = get_ClientIP(request)
    tor_list = getTorExits()
    tor_in_use = using_tor(client_IP, tor_list)
    json_info = get_ipinfo(client_IP)
    browser_info = get_browser_info(request)
    browser_version_bool, browser_version_string = check_browser_version(browser_info)

    #adding 1 to the vists and defaulting it to 0 if no visit
    visit_count = int(request.COOKIES.get('visit_count',0))+1
    #getting last visit date, if none then givign first time message
    last_visit = request.COOKIES.get('last_visit', 'First time visiting')

    #making a location for cookies
    location = json_info.get('City','Unknown')
    location += ', '+json_info.get('Region Name','Unknown')
    location += ', '+json_info.get('Country','Unknown')

    if(visit_count == 1 or request.COOKIES.get('home_location', 'Not Set') == 'Not Set'):
        home_location = location
    else:
        home_location = request.COOKIES.get('home_location')


    current_location = location
    last_location = request.COOKIES.get('last_location','First time visiting')

    vpn_status, vpn_message = vpn_checker(current_location,home_location,visit_count)

    context = {
        'tor_in_use': tor_in_use,
        'json_info': json_info,
        'browser_info': browser_info,
        'visit_count': visit_count,
        'last_visit': last_visit,
        'current_location': current_location,
        'last_location': last_location,
        'vpn_status':vpn_status,
        'vpn_message': vpn_message,
        'home_location': request.COOKIES.get('home_location'),
        'browser_bool': browser_version_bool,
        'browser_message': browser_version_string,
    }

    response = render(request, 'mainapp/index.html', context=context)

    cookie_setter(response,visit_count,current_location,current_date,home_location)

    return response




