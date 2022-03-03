# gcloud app deploy --project bcrs-service-auction

import time

import flask
import gspread

app = flask.Flask(__name__)
TEST = False
YEAR=2022

SERVICE_ACCOUNT = 'bcrs-service-auction-bbc421114be9.json'
if TEST:
    SHEET_ID = '1Z98iRhwFatXvF7kyfvuMeQAuoBvRi7wxAR5oIHvLPMw'
    SHEET_TAB = 'sheet1'
    PERSON_COL = 'Person'
    SERVICE_COL = 'Color'
    BUYER_COL = 'Buyer'
else:
    SHEET_ID = '1EFbAa6jDoJHx4x0CFMOajv8zAKDglqTOmeXRYVXw_jE'
    SHEET_TAB = 'responses'
    PERSON_COL = 'Name'
    SERVICE_COL = 'Service offered'
    BUYER_COL = 'Buyer'


@app.route('/')
def index():
    return flask.render_template('index.html', year=YEAR)


@app.route('/cards')
def cards():
    return cards_generic('cards.html')


@app.route('/raw_cards')
def raw_cards():
    return cards_generic('raw_cards.html')


def cards_generic(template):
    page = int(flask.request.args.get('page', 0))
    services = get_services()
    page = page % ((len(services) + 8) // 9)

    def size(service):
        if len(service) < 100:
            return ''
        elif len(service) < 200:
            return 'style="font-size: 85%"'
        else:
            return 'style="font-size: 75%"'

    return flask.render_template(template, cards=services, page=page, enumerate=enumerate, size=size, year=YEAR)


@app.route('/list')
def list():
    services = get_services()
    return flask.render_template('list.html', cards=services, enumerate=enumerate, size=lambda x: '', year=YEAR)


@app.route('/one')
def one():
    return flask.render_template(
        'one.html',
        service=flask.request.args.get('service'),
        person=flask.request.args.get('person'),
        size=lambda x: '',
        year=YEAR)


_last_result = []
_last_timestamp = 0

def get_services(refresh_rate=10):
  global _last_result, _last_timestamp
  if time.time() - _last_timestamp > refresh_rate:
      try:
          print("Really fetching... ", time.time() - _last_timestamp)
          _last_result = really_get_services()
      except Exception as exn:
          print("Exception", exn)
          pass
      _last_timestamp = time.time()
  return _last_result


def really_get_services():
  gc = gspread.service_account(SERVICE_ACCOUNT)
  w = gc.open_by_key(SHEET_ID)
  return [
      (ix, row[SERVICE_COL], row[PERSON_COL])
      for ix, row in enumerate(w.worksheet(SHEET_TAB).get_all_records())
      if not row.get(BUYER_COL)]
