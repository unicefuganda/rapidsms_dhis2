from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
from dhis2.h033b_reporter import H033B_Reporter
import datetime
import psycopg2
import psycopg2.extras


class Command(BaseCommand):
    help = """Producer management command for mTrac-DHIS2 PGQ implementation
    - PGQ is used as a job queue in place of celery
    - A seperate DB (with PGQ bindings installed) is mainted to keep the queues
    - for starters the DB is named skytools
    """
    option_list = BaseCommand.option_list + (
        make_option("-u", "--user", dest="user"),
        make_option("-p", "--password", dest="passwd", default=""),
        make_option("-w", "--week", dest="week"),
        make_option("-y", "--year", dest="year", default=datetime.datetime.now().year),
        make_option("-d", "--date", dest="date", default=datetime.datetime.now().strftime('%Y-%m-%d')),
    )
    EVENT_FIELDS = ['time', 'type', 'data', 'extra1']
    QUEUE_NAME = 'dhis2api'
    h033b_reporter = H033B_Reporter()
    serverid = 1
    year = datetime.datetime.now().year
    week = 0
    conn = psycopg2.connect(getattr(
        settings, "PGQ_DB_CONNECTION_STRING", "dbname=skytools user=postgres"))

    def handle(self, *args, **opts):
        self.year = opts['year']
        self.week = opts['week']  # for tracking in queue
        if opts['date']:
            year = opts['year']
            start_date = datetime.datetime.strptime(opts['date'], '%Y-%m-%d')
            end_date = start_date + datetime.timedelta(hours=24)
        if opts['week']:
            year = opts['year']
            start_date, end_date = self.get_week_days(int(year), int(opts['week']))
        #print year, start_date, end_date
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT id FROM servers WHERE name = 'dhis2'")
        res = cur.fetchone()
        if res:
            self.serverid = res['id']
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

    def get_submissions_for_week(self, date=datetime.datetime.now()):
        last_monday = self.h033b_reporter.get_last_sunday(date) + datetime.timedelta(days=1)
        last_monday_at_midnight = datetime.datetime(
            last_monday.year, last_monday.month, last_monday.day, 0, 0, 0)
        submissions_for_last_week = self.h033b_reporter.get_submissions_in_date_range(
            last_monday_at_midnight, date)

        return submissions_for_last_week

    def log_submission_status(self, subid, status="", status_code="", errmsg=""):
        cur = self.conn.cursor()
        q = (
            "INSERT INTO submissions_log (submission_id, status, status_code, errmsg)"
            " VALUES (%s, %s, %s, %s)")
        cur.execute(q, [subid, status, status_code, errmsg])
        self.conn.commit()

    def get_already_sent_submissions(self, start_date, end_date):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        q = ("SELECT distinct submission_id FROM submissions_log WHERE status = %s AND cdate BETWEEN %s AND %s")
        cur.execute(q, ['SUCCESS', start_date, end_date])
        return [r['submission_id'] for r in cur.fetchall()]

    def queue_submissions(self, submissions):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        for sub in submissions:
            try:
                cur.execute(
                    "SELECT id, status, xml_is_well_formed(request_body) "
                    "FROM requests where submissionid = %s FOR UPDATE NOWAIT" % sub.id)
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
                cur.execute(
                    "INSERT INTO requests (serverid, request_body, submissionid, week, year) "
                    "VALUES(%s, %s, %s, %s, %s)", (self.serverid, xml, sub.id, self.week, self.year))
            except Exception, e:
                cur.execute(
                    "INSERT INTO requests(serverid, submissionid, status, statuscode, "
                    " errmsg, week, year) "
                    "VALUES(%s, %s, %s, %s, %s, %s, %s)", (
                        self.serverid, sub.id, 'failed', 'ERROR4', str(e), self.week, self.year))
        self.conn.commit()
