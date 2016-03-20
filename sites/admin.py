from django.contrib import admin

from .models import Site



class SiteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['caption']}),
        (None,               {'fields': ['dev_url']}),
        (None,               {'fields': ['prod_url']}),
        (None,               {'fields': ['moved_to_external']}),
        (None,               {'fields': ['ignored']}),
        # ('Date information', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]
    # inlines = [ChoiceInline]
    list_display = ('caption', 'dev_url', 'prod_url', 'moved_to_external', 'ignored', 'created_at', 'updated_at')
    # list_filter = ['pub_date']
    search_fields = ['caption']

admin.site.register(Site, SiteAdmin)