import sys
import pgq
import requests
import psycopg2
import xpath
from xml.dom.minidom import parseString
from conf import CONFIG


class Dhis2ApiConsumer(pgq.Consumer):
    conn = psycopg2.connect("dbname=skytools user=postgres")

    def __init__(self, args):
        pgq.Consumer.__init__(self, "dhis2api_app", "src_db", args)

    def process_event(self, src_db, ev):
        if ev.ev_type == 'submission':
            self.log.info('Sending Submission %s!' % ev.ev_extra1)
            try:
                resp = self.post_data(ev.ev_data)
                ret, resp_val = self.parse_response(resp.text)
                if ret:
                    self.log_submission_status(ev.ev_extra1, status="SUCCESS", status_code=200, errmsg="%s" % resp_val)
                else:
                    self.log_submission_status(ev.ev_extra1, status="FAILED", status_code=404, errmsg="%s" % resp.text)
            except Exception, e:
                self.log_submission_status(ev.ev_extra1, status="ERROR", status_code=401, errmsg="%s" % str(e))
        ev.tag_done()

    def post_data(self, data):
        headers = {'Content-Type': 'application/xml'}
        return requests.post(
            CONFIG['dhis2_url'], data=data,
            auth=(CONFIG['username'], CONFIG['password']), headers=headers)

    def parse_response(self, resp):
        resp_dict = {"imported": 0, "ignored": 0, "updated": 0}
        try:
            doc = parseString(resp)
            status = xpath.findvalue('//status', doc)
            imported = xpath.findvalue('//dataValueCount[1]/@imported', doc)
            ignored = xpath.findvalue('//dataValueCount[1]/@ignored', doc)
            updated = xpath.findvalue('//dataValueCount[1]/@updated', doc)
            #conflicts = xpath.find('//conflict', doc)
            resp_dict = {"status": status, "imported": imported, "ignored": ignored, "updated": updated}
        except Exception, e:
            return False, "%s" % str(e)
        return True, "Imp:%(imported)s, Ign:%(ignored)s, Up:%(updated)s" % resp_dict

    def log_submission_status(self, subid, status="", status_code="", errmsg=""):
        cur = self.conn.cursor()
        q = (
            "INSERT INTO submissions_log (submission_id, status, status_code, errmsg)"
            " VALUES (%s, %s, %s, %s)")
        cur.execute(q, [subid, status, status_code, errmsg])
        self.conn.commit()

if __name__ == '__main__':
    script = Dhis2ApiConsumer(sys.argv[1:])
    script.start()
