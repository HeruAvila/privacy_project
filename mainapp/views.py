from datetime import datetime

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


def cookie_setter(response, visit_count, current_location, current_date):
    # https://stackoverflow.com/questions/17057536/how-to-set-cookie-and-render-template-in-django
    response.set_cookie('visit_count', visit_count)
    response.set_cookie('last_visit', current_date)
    response.set_cookie('last_location', current_location)


def vpn_checker(current_location, last_location,visit_count):
    vpn_used = False
    print("Current Location: "+current_location)
    print("Last Location: "+last_location)
    print("Visit Count: ",visit_count)
    if(current_location == last_location or visit_count == 1):
        if(visit_count == 1):
            vpn_used = False
            return (vpn_used, 'First time visiting. You current location has been saved and will be used later on to detect VPN usage.')
        else:
            vpn_used = False
            return (vpn_used,'VPN is not being used. Same location detected as last time.')
    else:
        c_city, c_region, c_country = current_location.split(',')
        print("Current City,Region,Country: "+c_city+", "+c_region+", "+c_country)
        l_city, l_region, l_country = last_location.split(',')
        print("Last City,Region,Country: "+l_city+", "+l_region+", "+l_country)
        if(c_city != l_city and c_region == l_region and c_country == l_country):
            vpn_used = False
            return (vpn_used, 'We detected a different city than your previous visits but will not treat this as a VPN usage since the region and country have not changed.')
        elif(c_region != l_region and c_country == l_country):
            vpn_used = True
            return (vpn_used, 'We have detected a different Region and same country, but we are treating this as VPN use. This may happen if you are traveling.')
        elif (c_country == l_country):
            vpn_used = True
            return (vpn_used, 'We have detected a different country of vist than before and will treat this as a VPN use.')

    return (vpn_used, 'Unable to determine VPN usage based on the provided data.')


def index(request):
    current_date = datetime.now()
    client_IP = get_ClientIP(request)
    tor_list = getTorExits()
    tor_in_use = using_tor(client_IP, tor_list)
    json_info = get_ipinfo(client_IP)
    browser_info = get_browser_info(request)

    #adding 1 to the vists and defaulting it to 0 if no visit
    visit_count = int(request.COOKIES.get('visit_count',0))+1
    #getting last visit date, if none then givign first time message
    last_visit = request.COOKIES.get('last_visit', 'First time visiting')

    #making a location for cookies
    location = json_info.get('City','Unknown')
    location += ', '+json_info.get('Region Name','Unknown')
    location += ', '+json_info.get('Country','Unknown')

    current_location = location
    last_location = request.COOKIES.get('last_location','First time visiting')

    vpn_status, vpn_message = vpn_checker(current_location,last_location,visit_count)

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
    }

    response = render(request, 'mainapp/index.html', context=context)

    cookie_setter(response,visit_count,current_location,current_date)

    return response




