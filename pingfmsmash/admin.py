from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pingfmsmash.models import Message, Feed, PingFMAccount

class MessageAdmin(admin.ModelAdmin):
    list_display = ('feed', 'message', 'pinged', 'sent_to_pingfm')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'last_checked', 'polling_rate')

class PingFMAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'pingfm_email', 'minimum_datetime', 'active')
   
admin.site.register(Message, MessageAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(PingFMAccount, PingFMAccountAdmin)
