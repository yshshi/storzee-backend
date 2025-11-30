# utils/email_utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import smtplib, ssl
from email.message import EmailMessage
import os
from datetime import datetime
# Initialize environment variables

port = os.getenv('ZOHO_SMTP_PORT')
smtp_server = os.getenv('ZOHO_SMTP_SERVER')
username=os.getenv('ZOHO_SMTP_USERNAME')
password = os.getenv('ZOHO_SMTP_PASSWORD')
from_email = os.getenv('ZOHO_FROM_EMAIL')

# def send_otp_email(email, otp, user_name):
#     # subject = f"Ding Dong 🛎️ Hey {user_name}, your Storzee OTP is here! "
#     # from_email = 'yashofficial2001@gmail.com'
#     # to = email
#     body='''
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="UTF-8">
#   <title>Your Storezee OTP</title>
#   <style>
#     body {
#       font-family: 'Segoe UI', sans-serif;
#       background-color: #f4f6f8;
#       color: #333;
#       padding: 20px;
#     }
#     .email-container {
#       max-width: 500px;
#       margin: auto;
#       background: white;
#       border-radius: 10px;
#       box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#       padding: 30px;
#       text-align: center;
#     }
#     .logo {
#       width: 80px;
#       height: 80px;
#       margin-bottom: 10px;
#     }
#     .otp {
#       font-size: 36px;
#       font-weight: bold;
#       color: #007bff;
#       margin: 20px 0;
#     }
#     .footer {
#       margin-top: 30px;
#       font-size: 12px;
#       color: #888;
#     }
#   </style>
# </head>
# <body>
#   <div class="email-container">
#     <a href='https://postimg.cc/4nhRDnp1' target='_blank'><img src='https://storezee-bucket.s3.ap-south-1.amazonaws.com/assests/storezee_logo.png' border='0' alt='storzee-icon'/></a>
#     <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
#     <h2>Welcome to <strong>Storzee</strong> 👋</h2>
#     <p>Use the OTP below to verify your email and get started:</p>

#     <div class="otp">{{otp}}</div>

#     <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
#     <div class="footer">
#       Need help? Contact us at <a href="mailto:support@storzee.com">support@storezee.com</a>
#     </div>
#   </div>
# </body>
# </html>

# '''
#     body = body.replace('{{otp}}', otp)
#     # msg = EmailMultiAlternatives(subject, body, from_email, [to])
#     # msg.attach_alternative(body, "text/html")
#     # msg.send()
#     msg = EmailMessage()
#     msg['Subject'] = f"Ding Dong 🛎️ Hey {user_name}, your Storzee OTP is here! "
#     msg['From'] = from_email#"info@thestorezee.com"
#     msg['To'] = email
#     message = body
#     msg.set_content(message)
#     msg = EmailMessage()
    

#     try:
#       if port == 465:
#           context = ssl.create_default_context()
#           with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#               server.login(username, password)
#               server.send_message(msg)
#       elif port == 587:
#           with smtplib.SMTP(smtp_server, port) as server:
#               server.starttls()
#               server.login(username, password)
#               server.send_message(msg)
#       else:
#           print ("use 465 / 587 as port value")
#           exit()
#       print ("successfully sent")
#     except Exception as e:
#       print (e)

# def send_login_otp_email(email, otp, user_name):
#     # subject = f"Welcome back {user_name}! Use this OTP to login your Storezee account"
#     # from_email = 'yashofficial2001@gmail.com'
#     # to = email
#     body='''
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="UTF-8">
#   <title>Your Storezee OTP</title>
#   <style>
#     body {
#       font-family: 'Segoe UI', sans-serif;
#       background-color: #f4f6f8;
#       color: #333;
#       padding: 20px;
#     }
#     .email-container {
#       max-width: 500px;
#       margin: auto;
#       background: white;
#       border-radius: 10px;
#       box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#       padding: 30px;
#       text-align: center;
#     }
#     .logo {
#       width: 80px;
#       height: 80px;
#       margin-bottom: 10px;
#     }
#     .otp {
#       font-size: 36px;
#       font-weight: bold;
#       color: #007bff;
#       margin: 20px 0;
#     }
#     .footer {
#       margin-top: 30px;
#       font-size: 12px;
#       color: #888;
#     }
#   </style>
# </head>
# <body>
#   <div class="email-container">
#     <a href='https://postimg.cc/4nhRDnp1' target='_blank'><img src='https://storezee-bucket.s3.ap-south-1.amazonaws.com/assests/storezee_logo.png' border='0' alt='storzee-icon'/></a>
#     <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
#     <h2>Welcome back to <strong>Storzee</strong> {{user}} 👋</h2>
#     <p>Use the OTP below to login into your storzee account:</p>

#     <div class="otp">{{otp}}</div>

#     <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
#     <div class="footer">
#       Need help? Contact us at <a href="mailto:support@storzee.com">support@storezee.com</a>
#     </div>
#   </div>
# </body>
# </html>

# '''
#     body = body.replace('{{otp}}', otp)
#     body = body.replace('{{user}}', user_name)
#     # msg = EmailMultiAlternatives(subject, body, from_email, [to])
#     # msg.attach_alternative(body, "text/html")
#     # msg.send()
#     msg = EmailMessage()
#     msg['Subject'] = f"Welcome back {user_name}! Use this OTP to login your Storezee account"
#     msg['From'] = from_email#"info@thestorezee.com"
#     msg['To'] = email
#     message = body
#     msg.set_content(message)
#     msg = EmailMessage()
    

#     try:
#       if int(port) == 465:
#           context = ssl.create_default_context()
#           with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#               server.login(username, password)
#               server.send_message(msg)
#       elif int(port) == 587:
#           with smtplib.SMTP(smtp_server, port) as server:
#               server.starttls()
#               server.login(username, password)
#               server.send_message(msg)
#       else:
#           print ("use 465 / 587 as port value")
#           exit()
#       print ("successfully sent")
#     except Exception as e:
#       print (e)

def send_login_otp_email(email, otp, user_name):
    body = '''
    <!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Your Storezee OTP</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f8;
      color: #333;
      padding: 20px;
    }
    .email-container {
      max-width: 500px;
      margin: auto;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 30px;
      text-align: center;
    }
    .logo {
      width: 80px;
      height: 80px;
      margin-bottom: 10px;
    }
    .otp {
      font-size: 36px;
      font-weight: bold;
      color: #007bff;
      margin: 20px 0;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      color: #888;
    }
  </style>
</head>
<body>
  <div class="email-container">
    <a href='https://postimg.cc/4nhRDnp1' target='_blank'><img src='https://storezee-bucket.s3.ap-south-1.amazonaws.com/assests/storezee_logo.png' border='0' alt='storzee-icon'/></a>
    <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
    <h2>Welcome back to <strong>Storezee</strong> {{user}} 👋</h2>
    <p>Use the OTP below to login into your Storezee account:</p>

    <div class="otp">{{otp}}</div>

    <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
    <div class="footer">
      Need help? Contact us at <a href="mailto:info@thestorezee.com">support@storezee.com</a>
    </div>
  </div>
</body>
</html>

    '''

    body = body.replace('{{otp}}', otp)
    body = body.replace('{{user}}', user_name)

    msg = EmailMessage()
    msg['Subject'] = f"Welcome back {user_name}! Use this OTP to login your Storezee account"
    msg['From'] = from_email
    msg['To'] = email

    # Add HTML body
    msg.add_alternative(body, subtype='html')

    try:
        port_int = int(port)

        if port_int == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port_int, context=context) as server:
                server.login(username, password)
                server.send_message(msg)

        elif port_int == 587:
            with smtplib.SMTP(smtp_server, port_int) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

        else:
            print("use 465 / 587 as port value")
            return

        print("Email successfully sent!")

    except Exception as e:
        print("Email error:", e)

def send_otp_email(email, otp, user_name):
    body = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Your Storezee OTP</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f8;
      color: #333;
      padding: 20px;
    }
    .email-container {
      max-width: 500px;
      margin: auto;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 30px;
      text-align: center;
    }
    .logo {
      width: 80px;
      height: 80px;
      margin-bottom: 10px;
    }
    .otp {
      font-size: 36px;
      font-weight: bold;
      color: #007bff;
      margin: 20px 0;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      color: #888;
    }
  </style>
</head>
<body>
  <div class="email-container">
    <a href='https://postimg.cc/4nhRDnp1' target='_blank'><img src='https://storezee-bucket.s3.ap-south-1.amazonaws.com/assests/storezee_logo.png' border='0' alt='storzee-icon'/></a>
    <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
    <h2>Welcome to <strong>Storezee</strong> 👋</h2>
    <p>Use the OTP below to verify your email and get started:</p>

    <div class="otp">{{otp}}</div>

    <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
    <div class="footer">
      Need help? Contact us at <a href="mailto:info@thestorezee.com">info@thestorezee.com</a>
    </div>
  </div>
</body>
</html>

    '''

    body = body.replace('{{otp}}', otp)

    msg = EmailMessage()
    msg['Subject'] = f"Ding Dong 🛎️ Hey {user_name}, your Storezee OTP is here!"
    msg['From'] = from_email
    msg['To'] = email

    # Add HTML body
    msg.add_alternative(body, subtype='html')

    try:
        port_int = int(port)

        if port_int == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port_int, context=context) as server:
                server.login(username, password)
                server.send_message(msg)

        elif port_int == 587:
            with smtplib.SMTP(smtp_server, port_int) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

        else:
            print("use 465 / 587 as port value")
            return

        print("Email successfully sent!")

    except Exception as e:
        print("Email error:", e)


def send_return_confirmation_email(email, user_name, booking_id, phone, amount):
    body = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Return Confirmation</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f8;
      color: #333;
      padding: 20px;
    }
    .email-container {
      max-width: 650px;
      margin: auto;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 30px;
    }
    h2 {
      color: #007bff;
      font-size: 24px;
      margin-bottom: 10px;
    }
    p {
      font-size: 15px;
      color: #444;
      line-height: 1.6;
      margin-bottom: 8px;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      text-align: center;
      color: #888;
    }
    .logo {
      width: 80px;
      height: 80px;
      margin-bottom: 10px;
      display: block;
      margin-left: auto;
      margin-right: auto;
    }
  </style>
</head>
<body>
  <div class="email-container">

    <img class="logo" src="https://storezee-bucket.s3.ap-south-1.amazonaws.com/assests/storezee_logo.png" alt="Storezee Logo"/>

    <h2>Your Luggage Has Been Returned ✔️</h2>

    <p>Dear <strong>{{name}}</strong>,</p>

    <p>Your stored items have been successfully returned from <strong>Storezee</strong>.</p>

    <p><strong>Booking ID:</strong> {{booking_id}}</p>
    <p><strong>Phone:</strong> {{phone}}</p>
    <p><strong>Email:</strong> {{email}}</p>
    <p><strong>Final Amount:</strong> ₹{{amount}}</p>

    <p>Thank you for trusting Storezee with your luggage. We hope you had a smooth experience.</p>

    <div class="footer">
      Storezee © {{year}}
    </div>

  </div>
</body>
</html>
    '''

    # Replace template values
    body = body.replace('{{name}}', user_name)
    body = body.replace('{{booking_id}}', str(booking_id))
    body = body.replace('{{phone}}', phone)
    body = body.replace('{{email}}', email)
    body = body.replace('{{amount}}', str(amount))
    body = body.replace('{{year}}', str(datetime.now().year))

    msg = EmailMessage()
    msg['Subject'] = f"Hey {user_name}, your Storezee return confirmation is here ✔️"
    msg['From'] = from_email
    msg['To'] = email

    msg.add_alternative(body, subtype='html')

    try:
        port_int = int(port)

        if port_int == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port_int, context=context) as server:
                server.login(username, password)
                server.send_message(msg)

        elif port_int == 587:
            with smtplib.SMTP(smtp_server, port_int) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

        else:
            print("use 465 / 587 as port value")
            return

        print("Email successfully sent!")

    except Exception as e:
        print("Email error:", e)
