import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===========================================================================
# emails Class
# ===========================================================================
class emails():

  def __init__(self, **params):
    self.core = None
    self.mopidy = None
    self.verbose = False
    self.logging = False
    self.volume = 0

    if 'core' in params:
      self.core = params['core']

    if 'mopidy' in params:
      self.mopidy = params['mopidy']

    if 'logging' in params:
      self.logging = params['logging']
    else:
      if self.core != None:
        logging_level: int = constant.DEBUG_LEVELS['DEBUG']
      else:
        logging_level: int = self.core.getDebugLevelFromText(self.core.readConf("level", "logging", 'INFO'))
          
  def send(self, body, subject, to):

    sender_email = "morphee@pochot.com"
    
    smtp_user = self.core.readConf('smtp_user', 'email', "dummy@gmail.com")
    smtp_password = self.core.readConf('smtp_password', 'email', "dummy")
    smtp_server = self.core.readConf('smtp_server', 'email', "smtp.gmail.com")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to
    
    text = body
    html = """\
    <html>
      <body>
        <p>""" + body + """</p>
      </body>
    </html>
    """
    
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(smtp_user, smtp_password)
        server.sendmail(
          sender_email, to, message.as_string()
        )

    except Exception as e:
        print(e)
    finally:
        server.quit() 
    
    #with smtplib.SMTP_SSL(server, 465, context=context) as server:
    #  server.login(sender_email, password)
    #  server.sendmail(
    #    sender_email, receiver_email, message.as_string()
    #  )