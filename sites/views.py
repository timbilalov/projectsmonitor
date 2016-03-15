from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Site

import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
import re
import socket
from urlparse import urlparse


class IndexView(generic.ListView):
    template_name = 'sites/index.html'
    context_object_name = 'all_sites'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Site.objects.all()
        # return Site.objects.filter(
        #     pub_date__lte=timezone.now()
        # ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Site
    template_name = 'sites/detail.html'
    context_object_name = 'report_data'


    def get_object(self):

        def hostname_resolves(hostname):
            try:
                socket.gethostbyname(hostname)
                return 1
            except socket.error:
                return 0

        # https://docs.python.org/2/library/re.html
        # https://regex101.com/r/oQ2jS7/1

        report_data = {}
        sites = Site.objects.all()
        # return site.object
        # for s in site:
        #     report_data[s] = site[s]

        # return self.pk_url_kwarg
        site = super(DetailView, self).get_object()
        # return site
        report_data["site_object"] = site

        s = site.dev_url
        urls_to_check = {
            "dev": site.dev_url,
            "prod": site.prod_url
        }

        for env in urls_to_check:
            s = urls_to_check[env]

            url = urlparse(s)
            rep_data_env = {}
            if not hostname_resolves(url.netloc):
                rep_data_env["not_resolves"] = True

            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, s)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()

            resp_code = c.getinfo(c.RESPONSE_CODE)
            rep_data_env["response_code"] = resp_code

            if resp_code == 200:
                buffer = BytesIO()
                c.setopt(c.URL, s + "robots.txt")
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

        return report_data

    # def get_queryset(self):
    #     """
    #     Excludes any questions that aren't published yet.
    #     """
    #     return Site.objects.all()
    #     # return Site.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Site
    template_name = 'sites/results.html'