# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Site

from functions import get_status_text, get_report_data




class IndexView(generic.ListView):
    template_name = 'sites/index.html'
    context_object_name = 'all_sites'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        all_sites = Site.objects.all()
        res_array = []
        for site in all_sites:
            site_report_data = get_report_data(site)
            res_array.append({
                "site_object": site,
                "report_data": site_report_data
            })

        return res_array
        # return Site.objects.filter(
        #     pub_date__lte=timezone.now()
        # ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Site
    template_name = 'sites/detail.html'
    context_object_name = 'report_data'


    def get_object(self):
        site = super(DetailView, self).get_object()
        report_data = get_report_data(site)
        return report_data


class ResultsView(generic.DetailView):
    model = Site
    template_name = 'sites/results.html'