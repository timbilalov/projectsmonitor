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
    context_object_name = 'site'

    # sites = [
    #     "http://bitell.itsoft.su/",
    #     "http://venarus.itsft.ru/",
    #     "http://bitell.ru/",
    #     "http://amurbosch.com/",
    #     "http://new.bss-bigtool.ru/",
    #     "http://forus.itsft.ru/",
    #     "http://itsoft.ru/"
    # ]


    # def get():
    #     pass


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

        for site in sites:
            s = site.dev_url
            if report_data.get("_ all sites") == None:
                report_data["_ all sites"] = 1
            else:
                report_data["_ all sites"] += 1

            # print "\n\n" + s

            url = urlparse(s)
            # print url
            if not hostname_resolves(url.netloc):
                # print "not resolves"

                if report_data.get("not resolves") == None:
                    report_data["not resolves"] = 1
                else:
                    report_data["not resolves"] += 1

                continue

            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, s)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()

            # HTTP response code, e.g. 200.
            resp_code = c.getinfo(c.RESPONSE_CODE)
            if resp_code == 200:
                # print s + "robots.txt"
                buffer = BytesIO()
                c.setopt(c.URL, s + "robots.txt")
                c.setopt(c.WRITEDATA, buffer)
                c.perform()
                if c.getinfo(c.RESPONSE_CODE) == 200:
                    robots = buffer.getvalue()
                    # print(robots)
                    # p = re.compile("(?<!\#\s|.)disallow:\s*\/(?![\w\R\?\*])", re.IGNORECASE)
                    p = re.compile("(?<!\#)(?<!.)Disallow:\s*\/(?![\w\R\?\*])", re.IGNORECASE)
                    # m = p.search(robots)
                    # m.group(0)
                    if len(p.findall(robots)) > 0:
                        # print "Found 'Disallow: /' string in robots.txt. Site closed for one or all robots."

                        if report_data.get("disallow") == None:
                            report_data["disallow"] = 1
                        else:
                            report_data["disallow"] += 1
                    else:
                        # print "Site opened for all robots."

                        if report_data.get("allow") == None:
                            report_data["allow"] = 1
                        else:
                            report_data["allow"] += 1

                    c.close()
                # else:
                #     print s + "robots.txt response code: " + str(c.getinfo(c.RESPONSE_CODE))

            # else:
            #     print('Status: %d' % resp_code)

            if report_data.get(str(resp_code)) == None:
                report_data[str(resp_code)] = 1
            else:
                report_data[str(resp_code)] += 1


            # Elapsed time for the transfer.
            # print('Status: %f' % c.getinfo(c.TOTAL_TIME))

            # getinfo must be called before close.
            c.close()

        # print report_data
        return report_data
        # return sites

    # def get_queryset(self):
    #     """
    #     Excludes any questions that aren't published yet.
    #     """
    #     return Site.objects.all()
    #     # return Site.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Site
    template_name = 'sites/results.html'