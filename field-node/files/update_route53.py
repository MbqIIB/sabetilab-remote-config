#!/usr/bin/env python

# based on: https://gist.github.com/vrypan/4341878

import os, sys
import socket
from datetime import datetime

# set the AWS vars before we import boto
os.environ["AWS_ACCESS_KEY_ID"] = "AKIAIDFXMO2NPUFYCHQQ" #"{{aws_access_key_id}}"
os.environ["AWS_SECRET_ACCESS_KEY"] = "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" #"{{aws_secret_access_key}}"

from area53 import route53
from boto.route53.exception import DNSServerError
import requests

import dns.resolver #dnspython

domain = "sabeti-aws.net" #'{{domain_name}}'
subdomain = socket.gethostname()

def get_public_ip():
    # equivalent to:
    # dig TXT +short o-o.myaddr.l.google.com @ns1.google.com | awk -F'"' '{ print $2}'
    resolver = dns.resolver.Resolver()
    resolver.nameservers=[ socket.gethostbyname('ns1.google.com') ]
    return str(resolver.query('o-o.myaddr.l.google.com', 'TXT')[0]).replace('"','')

fqdn = '%s.%s' % (subdomain, domain)
zone = route53.get_zone(domain)
arec = zone.get_a(fqdn)
new_value = get_public_ip()
datestr = '"P6112; Last update %s."' % datetime.utcnow().strftime('%Y-%m-%d %H:%M')

if arec:
        old_value = arec.resource_records[0]

        if old_value == new_value:
                print('%s is current. (%s)' % (fqdn, new_value))
                sys.exit(0)

        print('Updating %s: %s -> %s' % (fqdn, old_value, new_value))

        try:
                zone.update_a(fqdn, new_value, 300)
                zone.update_txt(fqdn, datestr, 300)

        except DNSServerError:
                # This can happen if the record did not already exist. Let's
                # try to add_a in case that's the case here.
                zone.add_a(fqdn, new_value, 300)
                zone.add_txt(fqdn, datestr, 300)
else:
        zone.add_a(fqdn, new_value, 300)
        zone.add_txt(fqdn, datestr, 300)