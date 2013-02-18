from lettuce import *
from dhis2.h033b_reporter import *
import datetime

@step(u'Report data must have all valid fields')
def get_reports_data_for_submission(self):
  submission = XFormSubmission.objects.filter(id=416117)[0]
  attribute_values = {319: 206, 320: 229, 321: 0, 322: 0}
  submission_time  = datetime.datetime(2013, 2, 5, 14, 53, 57, 616928)
    
  data  = H033B_Reporter.get_reports_data_for_submission(submission)

  assert data['orgUnit'] == 515
  assert data['completeDate'] == submission_time
  for eav_id in data['dataValues'] : 
    assert data['dataValues'][eav_id] == attribute_values[eav_id]

@step(u'Must fetch all submissions made within the specified period')
def get_submissions_in_date_range(self):
  from_date = datetime.datetime(2011, 12, 18, 00, 00, 00)
  to_date = datetime.datetime(2011, 12, 19, 23, 59, 59)
  submissions_in_period  = H033B_Reporter.get_submissions_in_date_range(from_date,to_date)
  assert len(submissions_in_period) == 314
  
