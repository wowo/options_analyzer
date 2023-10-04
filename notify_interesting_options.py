from datetime import datetime
import dateutil
from dateutil import parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from supabase import Client, create_client
import os
import pytz
import smtplib


def _jinja2_filter_short_date(date, fmt=None):
    if date is None:
        return ''
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    return native.strftime('%y-%m-%d')


def notify_interesting_options(supabase: Client, recipient: str):
    response = supabase.table('puts_opportunities').select('*').limit(20).execute()
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['short_date'] = _jinja2_filter_short_date
    template = env.get_template('notify_interesting_options_email.html')

    now = datetime.now()
    cest = pytz.timezone('Europe/Warsaw')

    data = map(lambda x: {
        **x,
        'percentage_change': 100 * ((x['current_price'] - x['previous_close']) / x['previous_close']),
        'days_until_expire': (datetime.strptime(x['expiration'], '%Y-%m-%d') - now).days,
        'updated_at': parser.parse(x['updated_at']).astimezone(cest).strftime('%y-%m-%d<br>%X')
    }, response.data)

    output = template.render(data=data)
    send_over_email(output, recipient)
    with open('/tmp/output.html', 'w') as f:
        f.write(output)


def send_over_email(body: str, recipient: str):
    email_credentials = os.environ.get('EMAIL_CREDENTIALS', None)
    email_server = os.environ.get('EMAIL_SERVER', 'smtp.gmail.com:587')
    email_sender = os.environ.get('EMAIL_SENDER', 'mailer@sznapka.pl')

    message = MIMEMultipart('mixed')
    message['From'] = 'Options Analyzer <{}>'.format(email_sender)
    message['To'] = recipient
    message['Subject'] = f'Stock opportunities {datetime.now():%Y-%m-%d}'
    body = MIMEText(body, 'html')
    message.attach(body)

    server, port = email_server.split(':')
    user, passwd = email_credentials.split(':')
    with smtplib.SMTP(server, port) as server:
        server.starttls()
        server.login(user, passwd)
        server.sendmail(email_sender, recipient, message.as_string())
        server.quit()


if __name__ == '__main__':
    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )
    notify_interesting_options(supabase)
