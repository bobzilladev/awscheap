#!/usr/bin/python

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
headers = ['OfferingType', 'AvailabilityZone', 'InstanceTenancy', 'UsagePrice', 'RecurringCharges', 'ProductDescription', 'FixedPrice', 'Duration', 'PricingDetails']

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
    o.write("<table border = \"1\">\n")

    # header
    o.write("<tr>\n")
    for header in headers:
      o.write("<th>{}</th>\n".format(header))
    o.write("</tr>\n")

    # data
    has_data = False
    for ri in ris:
      if ri['Marketplace']:
        has_data = True
        # print "marketplace: {}".format(ri)
        o.write("<tr>")
        for header in headers:
          raw_field = ri[header]
          if header == 'RecurringCharges':
            field = ''
            if raw_field:
              for charge in raw_field:
                field += "{}/{}".format(charge['Amount'], charge['Frequency'])
          else:
            field = raw_field

          o.write("<td>{}</td>".format(field))
        o.write("</tr>")

    # footer
    o.write("</table>\n")
    o.write("</body></html>\n")
    o.close()

    if not has_data:
      print "deleteing {}".format(output_name)
      os.remove(output_name)



print "done"
