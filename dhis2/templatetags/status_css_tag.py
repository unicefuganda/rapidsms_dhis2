from django import template
from dhis2.models import Dhis2_Reports_Report_Task_Log ,Dhis2_Reports_Submissions_Log

register = template.Library()

TASK_STATUS_CSS_MAPPING = {
  Dhis2_Reports_Report_Task_Log.RUNNING : 'warning',
  Dhis2_Reports_Report_Task_Log.FAILED  : 'error',
  Dhis2_Reports_Report_Task_Log.SUCCESS : 'success'
}



SUBMISSION_STATUS_CSS_MAPPING = {
  Dhis2_Reports_Submissions_Log.SUCCESS                   : 'success',
  Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA   : 'info',
  Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED   : 'warning',
  Dhis2_Reports_Submissions_Log.ERROR                     : 'error'
}



@register.simple_tag
def get_task_css(status):
  return TASK_STATUS_CSS_MAPPING[status]
  
@register.simple_tag
def get_submission_css(status):
  return SUBMISSION_STATUS_CSS_MAPPING[status]


  
  