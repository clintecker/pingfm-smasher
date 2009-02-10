from django.db import models
from django.db.models import permalink
from django.utils.translation import gettext_lazy as _

class Feed(models.Model):
    """A feed of blog posts"""
    name = models.CharField(blank=True,  max_length=80)
    url = models.URLField(_('url'), blank=True, verify_exists=False)
    last_checked = models.DateTimeField(_('last checked'), blank=True, null=True)
    polling_rate = models.IntegerField(_('polling rate'), blank=True, null=True, default=15)

    class Meta:
        ordering = ['-last_checked',]
        verbose_name, verbose_name_plural = _('feed'), _('feeds')

    def __unicode__(self):
        return self.name

    def _get_absolute_url(self):
        return ('feed_detail', (), {})
    get_absolute_url = permalink(_get_absolute_url)

class PingFMAccount(models.Model):
    """A Twitter account is fed by multiple twitter feeds"""
    name = models.CharField(blank=True,  max_length=80)
    pingfm_email = models.EmailField(_('pingfm email'), help_text="The PingFM email posting account you want to send updates to")
    minimum_datetime = models.DateTimeField(_('minimum datetime'), help_text='Do not smash items that occured before this date/time', blank=True, null=True)    
    active = models.BooleanField(_('active'), default=True)
    feeds = models.ManyToManyField(Feed)

    class Meta:
        ordering = ['pingfm_email',]
        verbose_name, verbose_name_plural = _('PingFM account'), _('PingFM accounts')

    def __unicode__(self):
        return self.name

    def _get_absolute_url(self):
        return ('pingfmaccount_detail', (), {})
    get_absolute_url = permalink(_get_absolute_url)

class Message(models.Model):
    """A tweet, essentially. Used for caching, mostly."""
    feed = models.ForeignKey(Feed)
    pingfm_account = models.ForeignKey(PingFMAccount)
    pinged = models.DateTimeField(_('published'), blank=True, null=True)
    guid = models.CharField(_('guid'), blank=True,  max_length=255)
    message = models.CharField(_('message'), blank=True,  max_length=200)
    sent_to_pingfm = models.BooleanField(_('sent to PingFM'), default=False)

    class Meta:
        ordering = ['-pinged',]
        verbose_name, verbose_name_plural = _('message'), _('messages')

    def __unicode__(self):
        return self.message

    def _get_absolute_url(self):
        return ('message_detail', (), {})
    get_absolute_url = permalink(_get_absolute_url)