from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pingfmsmash.models import Message, Feed, PingFMAccount

class MessageAdmin(admin.ModelAdmin):
    list_display = ('feed', 'message', 'pinged', 'sent_to_pingfm')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'link_shortener', 'tracking_codes', 'last_checked',)

class PingFMAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'pingfm_email', 'pingfm_user_key', 'prefer_api', 'minimum_datetime', 'active')
   
admin.site.register(Message, MessageAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(PingFMAccount, PingFMAccountAdmin)
