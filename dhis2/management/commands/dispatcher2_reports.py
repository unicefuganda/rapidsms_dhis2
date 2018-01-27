from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
from dhis2.h033b_reporter import H033B_Reporter
import datetime
import psycopg2
import psycopg2.extras


class Command(BaseCommand):
    help = """
    Queue mTrac messages into Dispatcher2
    """
    option_list = BaseCommand.option_list + (
        make_option("-u", "--user", dest="user"),
        make_option("-p", "--password", dest="passwd", default=""),
        make_option("-w", "--week", dest="week"),
        make_option("-y", "--year", dest="year", default=datetime.datetime.now().year),
        make_option("-d", "--date", dest="date", default=datetime.datetime.now().strftime('%Y-%m-%d')),
    )
    h033b_reporter = H033B_Reporter()
    source = 2  # id id DB
    destination = 4
    year = datetime.datetime.now().year
    week = 0
    conn = psycopg2.connect(getattr(
        settings, "DISPATCHER2_DB_CONNECTION_STRING", "dbname=dispatcher2 user=postgres host=localhost"))

    def handle(self, *args, **opts):
        self.year = opts['year']
        self.week = opts['week']  # for tracking in queue
        if opts['date']:
            self.year = opts['year']
            start_date = datetime.datetime.strptime(opts['date'], '%Y-%m-%d')
            end_date = start_date + datetime.timedelta(hours=24)
            self.year, self.week = self.get_reporting_week(start_date)
        if opts['week']:
            self.year = opts['year']
            start_date, end_date = self.get_week_days(int(self.year), int(opts['week']))
            self.year, self.week = self.get_reporting_week(start_date)

        print self.year, start_date, end_date
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT id FROM servers WHERE name in ('mtrack', 'dhis2')")
        res = cur.fetchall()
        for r in res:
            if r['id'] == 'mtrack':
                self.source = r['id']
            else:
                self.destination = r['id']
        submissions = self.get_submissions_for_week(date=end_date)
        self.queue_submissions(submissions)
        self.conn.close()

    def get_week_days(self, year, week):
        d = datetime.date(year, 1, 1)
        if(d.weekday() > 3):
            d = d + datetime.timedelta(7 - d.weekday())
        else:
            d = d - datetime.timedelta(d.weekday())
        dlt = datetime.timedelta(days=(week - 1) * 7)
        return d + dlt, d + dlt + datetime.timedelta(days=6)

    def get_reporting_week(self, date):
        """Given date, return the reporting week in the format 2016W01
        reports coming in this week are for previous one.
        """
        offset_from_last_sunday = date.weekday() + 1
        last_sunday = date - datetime.timedelta(days=offset_from_last_sunday)
        year, weeknum, _ = last_sunday.isocalendar()
        return (year, weeknum)

    def get_submissions_for_week(self, date=datetime.datetime.now()):
        last_monday = self.h033b_reporter.get_last_sunday(date) + datetime.timedelta(days=1)
        last_monday_at_midnight = datetime.datetime(
            last_monday.year, last_monday.month, last_monday.day, 0, 0, 0)
        submissions_for_last_week = self.h033b_reporter.get_submissions_in_date_range(
            last_monday_at_midnight, date)

        return submissions_for_last_week

    def queue_submissions(self, submissions):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        for sub in submissions[:50]:
            try:
                cur.execute(
                    "SELECT id, status, xml_is_well_formed(body) FROM requests "
                    " WHERE submissionid = %s AND destination  = %s FOR UPDATE NOWAIT", (
                        sub.id, self.destination))
                res = cur.fetchone()
                # do not send what already exists
                if res:
                    if not res['xml_is_well_formed']:
                        continue
                    if res['status'] != 'ready' and res['status'] != 'completed':  # not ready for processing - retry
                        cur.execute(
                            "UPDATE requests SET status = 'ready', retries = retries + 1"
                            " WHERE submissionid = %s" % sub.id)
                        self.conn.commit()
                    continue
                data = self.h033b_reporter.get_reports_data_for_submission(sub)
                xml = self.h033b_reporter.generate_xml_report(data)
                msisdn = sub.connection.identity
                facility = sub.xformsubmissionextras_set.all()[0].facility.code
                district = sub.xformsubmissionextras_set.all()[0].facility.district
                raw_msg = sub.message.text

                cur.execute(
                    "INSERT INTO requests (source, destination, body, submissionid, "
                    "week, year, ctype, raw_msg, msisdn, facility, district) "
                    "VALUES(%s, %s, %s, %s, %s, %s, 'xml', %s, %s, %s, %s)",
                    (
                        self.source, self.destination, xml, sub.id, self.week,
                        self.year, raw_msg, msisdn, facility, district))
                self.conn.commit()
            except Exception, e:
                print str(e)
