# -*- coding: utf-8 -*-

from .models import Site
import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
import re
import socket
from urlparse import urlparse

def get_status_text(status_num):
    statuses = {
        0: {
            "level": "info",
            "text": "Неизвестный статус."
        },

        1: {
            "level": "good",
            "text": "Сайт в разработке и закрыт от индексации."
        },

        2: {
            "level": "bad",
            "text": "Сайт в разработке, но индексируется. Срочно закрыть!"
        },

        3: {
            "level": "bad",
            "text": "Сайт в разработке, но не найден файл robots.txt. Необходимо создать файл и закрыть сайт от индексации!"
        },

        4: {
            "level": "warning",
            "text": "Сайт сдан, но не найден файл robots.txt. Желательно создать данный файл и прописать необходимые инструкции."
        },

        5: {
            "level": "bad",
            "text": "Сайт сдан, но закрыт от индексации. Срочно открыть!"
        },

        6: {
            "level": "good",
            "text": "Сайт сдан и открыт для индексации."
        },

        7: {
            "level": "warning",
            "text": "Сайт сдан, но dev площадка не закрыта."
        },

        8: {
            "level": "warning",
            "text": "Сайт сдан, но dev_url редиректит хрен пойми куда."
        }
    }

    if statuses[status_num]:
        res_obj = statuses[status_num]
    else:
        res_obj = {}

    return res_obj





def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0


def get_report_data(site):

    # https://docs.python.org/2/library/re.html
    # https://regex101.com/r/oQ2jS7/1

    report_data = {}
    sites = Site.objects.all()
    # return site.object
    # for s in site:
    #     report_data[s] = site[s]

    # return self.pk_url_kwarg
    # return site
    report_data["site_object"] = site

    s = site.dev_url
    urls_to_check = {
        "dev": site.dev_url,
        "prod": site.prod_url
    }

    ## Callback function invoked when header data is ready
    def header(buf):
        import sys
        sys.stdout.write(buf)
        # Returning None implies that all bytes were written

    for env in urls_to_check:
        s = urls_to_check[env]
        url = urlparse(s)

        if not hostname_resolves(url.netloc):
            rep_data_env["not_resolves"] = True

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, s)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.perform()

        effective_url = c.getinfo(c.EFFECTIVE_URL)
        if urls_to_check[env] != effective_url:
            report_data[env + "_effective_url"] = effective_url
            report_data[env + "_effective_url_ip"] = c.getinfo(c.PRIMARY_IP)

    urls_to_check = {
        "dev": report_data.get("dev_effective_url") or site.dev_url,
        "prod": report_data.get("prod_effective_url") or site.prod_url
    }

    for env in urls_to_check:
        s = urls_to_check[env]

        url = urlparse(s)
        rep_data_env = {}

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, s)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, 1)
        # c.setopt(c.HEADERFUNCTION, header)
        c.perform()

        resp_code = c.getinfo(c.RESPONSE_CODE)
        rep_data_env["response_code"] = resp_code
        rep_data_env["ip"] = c.getinfo(c.PRIMARY_IP)

        if resp_code == 200:
            buffer = BytesIO()

            r_txt_url = s
            parsed_uri = urlparse(r_txt_url)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            r_txt_url = domain + "robots.txt"

            c.setopt(c.URL, r_txt_url)
            rep_data_env["r_txt_url"] = r_txt_url
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            resp_code_2 = c.getinfo(c.RESPONSE_CODE)

            rep_data_env["robots_txt_response_code"] = resp_code_2
            if resp_code_2 == 200:
                robots = buffer.getvalue()
                p = re.compile("(?<!\#)(?<!.)Disallow:\s*\/(?![\w\R\?\*])", re.IGNORECASE)
                rep_data_env["found_disallow"] = len(p.findall(robots)) > 0
                rep_data_env["robots_txt_value"] = robots
            # c.close()

        c.close()

        report_data[env] = rep_data_env

    in_production = report_data.get("dev")["ip"] == report_data.get("prod")["ip"]
    if not in_production and site.moved_to_external == True:
        in_production = True
    report_data["in_production"] = in_production

    r_txt_resp_prod = report_data["prod"].get("robots_txt_response_code")
    r_txt_resp_dev = report_data["dev"].get("robots_txt_response_code")
    dev_closed = report_data["dev"]["response_code"] != 200
    if report_data.get("dev_effective_url"):
        parsed_uri = urlparse(report_data["dev_effective_url"])
        domain1 = '{uri.netloc}'.format(uri=parsed_uri)
        parsed_uri = urlparse(site.dev_url)
        domain2 = '{uri.netloc}'.format(uri=parsed_uri)
        # dev_redirect_external = report_data["dev_effective_url_ip"] != report_data["dev"]["ip"]
        dev_redirect_external = domain1 != domain2
    else:
        dev_redirect_external = False
    report_data["dev_redirect_external"] = dev_redirect_external

    if in_production:

        if r_txt_resp_prod == 404:
            report_data["status_code"] = 4

        elif r_txt_resp_prod == 200:
            if report_data["prod"].get("found_disallow"):
                report_data["status_code"] = 5
            else:
                if dev_redirect_external:
                    report_data["status_code"] = 8

                else:
                    if dev_closed:
                        report_data["status_code"] = 6
                    else:
                        report_data["status_code"] = 7

        else:
            report_data["status_code"] = 0

    else:
        if r_txt_resp_dev == 404:
            report_data["status_code"] = 3

        elif r_txt_resp_dev == 200:
            if report_data["dev"].get("found_disallow"):
                report_data["status_code"] = 1
            else:
                report_data["status_code"] = 2

        else:
            report_data["status_code"] = 0

    # global get_status_text
    report_data["status_level"] = get_status_text(report_data["status_code"]).get("level")
    report_data["status_text"] = get_status_text(report_data["status_code"]).get("text")

    return report_data