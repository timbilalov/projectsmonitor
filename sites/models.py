from django.db import models


class Site(models.Model):
    caption = models.CharField(max_length=200)
    dev_url = models.CharField(max_length=200)
    prod_url = models.CharField(max_length=200)
    moved_to_external = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ignored = models.BooleanField(default=False)