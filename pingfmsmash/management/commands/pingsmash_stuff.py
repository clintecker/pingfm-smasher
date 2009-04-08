import datetime
import feedparser
import re
import string
from django.core.management.base import BaseCommand
from optparse import make_option
from pingfmsmash.models import Feed, PingFMAccount, Message

import pytz
from pytz import timezone
import urllib

from django.core.mail import send_mail
from django.conf import settings

central = timezone('US/Central')
utc = pytz.utc

class Command(BaseCommand):
    help = "Loops through feeds and determines if messages need to be sent to any PingFM accounts"
    option_list = BaseCommand.option_list + (
        make_option('--dryrun', '-D', action='store_true', dest='dryrun', default=False,
            help='Go through the motions but commit nothing to PingFM'),
        make_option('--quiet', '-q', action='store_true', dest='quiet', default=False,
            help='Don\t print anything to console'),
        make_option('--debug', '-d', action='store_true', dest='debug', default=False,
            help='Return debugging information'),
    )

    def handle(self, *args, **options):
        # Get list of PingFMAccounts
        quiet = options.get('quiet')
        entries_pulled = 0
        accounts_skipped = 0
        accounts_ready = 0
        entries_pinged = 0
        feeds_pulled = 0
        messages_added = 0
        feeds_checked = 0
        messages_sent = []
        accounts = PingFMAccount.objects.all().filter(active=True)
        for account in accounts:
            feed_list = account.feeds.all()
            for f in feed_list:
                feeds_checked += 1
                if not quiet:
                    print " - %s" % (f,)
                # Get list of feeds whose last_update + polling_rate is less than now
                if f.last_checked == None or f.last_checked + \
                datetime.timedelta(minutes=f.polling_rate) < datetime.datetime.now():
                    accounts_ready += 1
                    # Update timestamp
                    f.last_checked = datetime.datetime.now()
                    f.save()
                    if not quiet:
                        print "   * Pulling feed"
                    # Pull each feed
                    d = feedparser.parse(f.url)

                    feeds_pulled += 1
                    # Loop through feed
                    d.entries.reverse()

                    for entry in d['entries']:
                        entries_pulled += 1
                        guid = entry.id
                        m = Message.objects.filter(guid=guid, pingfm_account=account)

                        if m:
                          continue
                          
                        published = entry.updated_parsed 
                        
                        if f.tracking_codes:
                          tracking = unicode(f.tracking_codes % (account.name))
                        else:
                          tracking = ''
                          
                        if f.link_shortener:
                          url = f.link_shortener % (urllib.quote(entry.link + tracking),)
                          fh = urllib.urlopen(url)
                          d = fh.read()
                          link = d
                        else:
                          tracking = unicode(f.tracking_codes % (urllib.quote(account.name)))
                          link = entry.link + tracking
                        
                        message = u"%s - %s" % (entry.title, link)
                        #print guid, published, message
                        published_dt = datetime.datetime(
                            published[0], 
                            published[1], 
                            published[2], 
                            published[3], 
                            published[4], 
                            published[5], 
                            tzinfo=None
                        )
                        published_dt_cst = central.localize(published_dt)
                        published_dt_utc = published_dt_cst.astimezone(utc)
                        published_dt = datetime.datetime(
                            published_dt_utc.utctimetuple()[0],
                            published_dt_utc.utctimetuple()[1],
                            published_dt_utc.utctimetuple()[2],
                            published_dt_utc.utctimetuple()[3],
                            published_dt_utc.utctimetuple()[4],
                            published_dt_utc.utctimetuple()[5],
                        )
                        msg, created = Message.objects.get_or_create(
                            guid=guid, 
                            pingfm_account=account, 
                            defaults={
                                'feed': f, 
                                'pinged': published_dt,
                                'message': message,
                                'pingfm_account': account,
                        })
                        send_to_pingfm = False                      
                        if created:
                            messages_added += 1
                            send_to_pingfm, message = self.process_messages(
                                account=account,
                                message=message,
                                created=published_dt_utc,
                                options=options,
                            )
                        if send_to_pingfm:
                            try:
                                if not options.get('dryrun'):
                                    send_mail('', msg, 'clint@arstechnica.com',
                                        [account.pingfm_email], fail_silently=False)
                                    if not quiet:
                                        print "   * Sent to PingFM: '%s'" % (message,)
                                else:
                                    if not quiet:
                                        print "   * Dry run: '%s'" % (message,)
                                entries_pinged += 1
                                msg.sent_to_pingfm = True
                                msg.save()
                            except:
                                if not quiet:
                                    print "   - Failed to send to PingFM (%s)" % (e,)
                else:
                    if not quiet:
                        print "   * Checked within the last %s minutes" % (f.polling_rate)
                    accounts_skipped += 1

        if options.get('debug'):        
            return {
                'entries_pulled': entries_pulled,
                'accounts_skipped': accounts_skipped,
                'accounts_ready': accounts_ready,
                'entries_pinged': entries_pinged,
                'feeds_pulled': feeds_pulled,
                'messages_added': messages_added,
                'feeds_checked': feeds_checked,
            }
            
    def process_messages(self, account, message, created, options):
        send_to_pingfm = False
        quiet = options.get('quiet')
        
        # Prep minimum DT
        if account.minimum_datetime:
            # Stored value here is UTC
            min_dt = utc.localize(account.minimum_datetime)
        else:
            min_dt = None
            
        # Wasn't already in the db                        
        if min_dt and created <= min_dt:
            if not quiet:
                print "   * Skipped because of time restrictions"
        else:
            send_to_pingfm = True
            
        return send_to_pingfm, message