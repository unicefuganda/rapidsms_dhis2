#!/usr/bin/env python
from django.template import Context, Template
from django.template.loader import get_template
import urllib2, base64

class H033B_Reporter(object):
  URL     = "http://dhis/api/dataValueSets"
  HEADERS = {
      'Content-type': 'application/xml',
      'Authorization': 'Basic ' + base64.b64encode("api:P@ssw0rd")
  }

  @classmethod
  def send(self, data):
    request = urllib2.Request(self.URL, data = data, headers = self.HEADERS)
    request.get_method = lambda: "POST"
    return urllib2.urlopen(request)

  @classmethod
  def submit(self, data):
    template = get_template("h033b_reporter.xml")
    data = template.render(Context(data))
    return self.send(data)