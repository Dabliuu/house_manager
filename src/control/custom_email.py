

import smtplib

sending_email = "notification_manager@alfagenos.com"
sending_password = "1234-qwer" 

def send_email(
    electric = {"cost":460, "value":430.4},
    water = {"cost":340, "value":300.4},
    email = 'juan.ramirez.villegas@correounivalle.edu.co'
):

    sent_from = sending_email
    to = [email] # list of emails to send
    subject = 'House Manager bill notification'
    body = """
    This is an automated message.
    Remember to pay your bills:
    Electric bill: %s COP
    Watter bill:  %s COP
    """ % (
        electric["cost"] * electric["value"], 
        water["cost"] * water["value"]
        )

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL("mail.privateemail.com", 465)
        server.ehlo()
        server.login(sending_email, sending_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print ('Email sent!')
    except IOError as e:
        print ('Something went wrong...  \n'+str(e))