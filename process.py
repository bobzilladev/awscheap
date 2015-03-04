#!/usr/bin/python

from collections import defaultdict
import json
import os
import re
import sys

files = []
full = False
if len(sys.argv) > 1:
  for i in range(1, len(sys.argv)):
    if sys.argv[i] == '--full':
      full = True
    else:
      files.append(sys.argv[i])
else:
  print "need json args"
  sys.exit(-1)

# {u'OfferingType': u'Medium Utilization', u'AvailabilityZone': u'ap-northeast-1b', u'InstanceTenancy': u'default', u'UsagePrice': 0.121, u'RecurringCharges': [], u'Marketplace': True, u'InstanceType': u'c3.xlarge', u'CurrencyCode': u'USD', u'ProductDescription': u'Linux/UNIX', u'FixedPrice': 100.0, u'Duration': 5184000, u'ReservedInstancesOfferingId': u'13fc93e2-5827-4a94-b006-03f1a46f426b', u'PricingDetails': [{u'Count': 1, u'Price': 100.0}]}
headers = ['OfferingType', 'AvailabilityZone', 'InstanceTenancy', 'ProductDescription', 'Months', 'Count', 'FixedPrice', 'Recurring', 'Price', 'ImpliedPrice', 'RackRate', 'Savings', 'SavingsPercent']

instancePrice = dict()
instancePrice['c1.medium'] = 0.13
instancePrice['c1.xlarge'] = 0.52
instancePrice['m1.small'] = 0.044
instancePrice['m1.medium'] = 0.087
instancePrice['m1.large'] = 0.175
instancePrice['m1.xlarge'] = 0.35
instancePrice['m2.xlarge'] = 0.245
instancePrice['m2.2xlarge'] = 0.49
instancePrice['m2.4xlarge'] = 0.98
instancePrice['c3.large'] = 0.105
instancePrice['c3.xlarge'] = 0.210
instancePrice['c3.2xlarge'] = 0.420
instancePrice['m3.medium'] = 0.07
instancePrice['m3.large'] = 0.14
instancePrice['m3.xlarge'] = 0.28
instancePrice['r3.large'] = 0.175
instancePrice['r3.xlarge'] = 0.35
instancePrice['r3.2xlarge'] = 0.7
instancePrice['i2.xlarge'] = 0.853
instancePrice['i2.2xlarge'] = 1.705
instancePrice['i2.4xlarge'] = 3.41
instancePrice['i2.8xlarge'] = 6.82
instancePrice['hi1.4xlarge'] = 3.1

html_files = []

for filer in files:
  #realm = re.sub(r'\.json', '', filer)
  #realm = re.sub(r'^.*/', '', realm)
  print "file: {}".format(filer)
  json_data=open(filer).read()
  data = json.loads(json_data)
  ris = data.get('ReservedInstancesOfferings')
  if ris:
    output_name = re.sub(r'json', 'html', filer)
    o = open(output_name, 'w')
    o.write("<html><body>\n")
    o.write('<table border = "1" cellspacing="0" cellpadding="2">')

    # header
    o.write("<tr>\n")
    for header in headers:
      o.write("<th>{}</th>\n".format(header))
    o.write("</tr>\n")

    # marketplace data
    has_data = False
    for ri in ris:
      if not ri['Marketplace']:
        continue
      if not ri['ProductDescription'].startswith('Linux/UNIX'):
        continue

      has_data = True
      # print "marketplace: {}".format(ri)
      for price in ri['PricingDetails']:
        ri['Count'] = price['Count']
        ri['Price'] = price['Price']
        
        ri['RackRate'] = instancePrice[ri['InstanceType']]

        hours = (ri['Duration']) / 60 / 60
        days = hours / 24
        months = days / 30
        ri['Months'] = months
        amort_price = ri['Price'] / hours
        recurring_charges = 0
        if ri['RecurringCharges']:
          if len(ri['RecurringCharges']) > 1:
            print "too many charges: {}".format(ri)
            sys.exit()
          if ri['RecurringCharges'][0]['Frequency'] != 'Hourly':
            print "Unhandled freq: {}".format(ri)
            sys.exit()
          recurring_charges = ri['RecurringCharges'][0]['Amount']
        ri['Recurring'] = recurring_charges + ri['UsagePrice']
        implied_price = amort_price + ri['UsagePrice'] + recurring_charges
        ri['ImpliedPrice'] = round(implied_price,4)

        savings_hour = ri['RackRate'] - implied_price
        ri['Savings'] = "{} / mo".format(round(savings_hour * 24 * 30, 2))
        ri['SavingsPercent'] = "{} %".format(round((savings_hour*100)/ri['RackRate'], 1))

        o.write("<tr>")
        for header in headers:
          raw_field = ri[header]
          field = raw_field

          o.write("<td>{}</td>".format(field))
        o.write("</tr>")

    # footer
    o.write("</table>\n")
    o.write("</body></html>\n")
    o.close()

    if has_data:
      html_file = re.sub('html/', '', output_name)
      html_files.append(html_file)
    else:
      print "deleting {}".format(output_name)
      os.remove(output_name)

o = open('html/index.html', 'w')

o.write('<html><head><title>AWS Cheap</title></head><body>')
o.write('AWS Cheap<p>')

for html_file in html_files:
  o.write('<a href="{}">{}</a><br>'.format(html_file, html_file))
  o.write("\n")

o.write('</body></html>')
o.close()

print "done"
