

import smtplib

gmail_user = "notification_manager@alfagenos.com"
gmail_password = "1234-qwer" 

sent_from = gmail_user
to = ['juan.ramirez.villegas@correounivalle.edu.co']
subject = 'OMG Super Important Message'
body = """Hey, what's up?\n\n- You"""

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    server = smtplib.SMTP_SSL("mail.privateemail.com", 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print ('Email sent!')
except IOError as e:
    print ('Something went wrong...  \n'+str(e))