from django.core.management.base import BaseCommand
from optparse import make_option
from django.contrib.auth.models import User
#from django.conf import settings
from dhis2.reports_submission_tasks import submit_reports_now_task
from dhis2.h033b_reporter import H033B_Reporter
import datetime


class Command(BaseCommand):
    help = """Submit Reports of given week to DHIS2"""
    option_list = BaseCommand.option_list + (
        make_option("-u", "--user", dest="user"),
        make_option("-p", "--password", dest="passwd", default=""),
        make_option("-w", "--week", dest="week"),
        make_option("-y", "--year", dest="year", default=datetime.datetime.now().year),
        make_option("-d", "--date", dest="date", default=datetime.datetime.now().strftime('%Y-%m-%d')),
    )

    def handle(self, *args, **opts):
        user = User.objects.filter(username=opts['user'])
        if not user:
            print "Unknown User:", opts['user']
            return
        if not user[0].check_password(opts['passwd']):
            print "Invalid Passowrd"
            return

        if opts['date']:
            year = opts['year']
            start_date = datetime.datetime.strptime(opts['date'], '%Y-%m-%d')
            end_date = start_date + datetime.timedelta(hours=24)
        if opts['week']:
            year = opts['year']
            start_date, end_date = self.get_week_days(int(year), int(opts['week']))
        print year, start_date, end_date

        h033b_reporter = H033B_Reporter()
        submissions = h033b_reporter.get_submissions_in_date_range(start_date, end_date)
        submit_reports_now_task.delay(submissions)

    def get_week_days(self, year, week):
        d = datetime.date(year, 1, 1)
        if(d.weekday() > 3):
            d = d + datetime.timedelta(7 - d.weekday())
        else:
            d = d - datetime.timedelta(d.weekday())
        dlt = datetime.timedelta(days=(week - 1) * 7)
        return d + dlt, d + dlt + datetime.timedelta(days=6)
