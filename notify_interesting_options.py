import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dateutil import parser
from jinja2 import Environment, FileSystemLoader
from supabase import Client, create_client
import os


def notify_interesting_options(supabase: Client):
    response = supabase.table('puts_opportunities').select('*').limit(20).execute()
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('notify_interesting_options.html')

    now = datetime.now()
    data = map(lambda x: {
        **x,
        'days_until_expire': (datetime.strptime(x['expiration'], '%Y-%m-%d') - now).days,
        'updated_at': parser.parse(x['updated_at']).strftime('%Y-%m-%d %X')
    }, response.data)

    output = template.render(data=data)
    send_over_email(output)
    with open('/tmp/output.html', 'w') as f:
        f.write(output)

def send_over_email(body):
    email_credentials = os.environ.get('EMAIL_CREDENTIALS', None)
    email_server = os.environ.get('EMAIL_SERVER', 'smtp.gmail.com:587')
    email_sender = os.environ.get('EMAIL_SENDER', 'mailer@sznapka.pl')
    email_recipient = os.environ.get('EMAIL_RECIPIENT', None)

    message = MIMEMultipart('mixed')
    message['From'] = 'Options Analyzer <{}>'.format(email_sender)
    message['To'] = email_recipient
    message['Subject'] = 'Stock opportunities'
    body = MIMEText(body, 'html')
    message.attach(body)

    server, port = email_server.split(':')
    user, passwd = email_credentials.split(':')
    with smtplib.SMTP(server, port) as server:
        server.starttls()
        server.login(user, passwd)
        server.sendmail(email_sender, email_recipient, message.as_string())
        server.quit()


if __name__ == '__main__':
    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )
    notify_interesting_options(supabase)
