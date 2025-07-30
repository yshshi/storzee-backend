# utils/email_utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_otp_email(email, otp, user_name):
    subject = f"Ding Dong 🛎️ Hey {user_name}, your Storzee OTP is here! "
    from_email = 'yashofficial2001@gmail.com'
    to = email
    body='''
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
    <a href="https://ibb.co/HfNb3QJ1"><img src="https://i.ibb.co/HfNb3QJ1/Whats-App-Image-2025-07-15-at-10-37-41.jpg" alt="Whats-App-Image-2025-07-15-at-10-37-41" border="0" /></a>
    <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
    <h2>Welcome to <strong>Storzee</strong> 👋</h2>
    <p>Use the OTP below to verify your email and get started:</p>

    <div class="otp">{{otp}}</div>

    <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
    <div class="footer">
      Need help? Contact us at <a href="mailto:support@storzee.com">support@storezee.com</a>
    </div>
  </div>
</body>
</html>

'''
    body = body.replace('{{otp}}', otp)
    msg = EmailMultiAlternatives(subject, body, from_email, [to])
    msg.attach_alternative(body, "text/html")
    msg.send()

def send_login_otp_email(email, otp, user_name):
    subject = f"Welcome back {user_name}! Use this OTP to login your Storezee account"
    from_email = 'yashofficial2001@gmail.com'
    to = email
    body='''
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
    <a href="https://ibb.co/HfNb3QJ1"><img src="https://i.ibb.co/HfNb3QJ1/Whats-App-Image-2025-07-15-at-10-37-41.jpg" alt="Whats-App-Image-2025-07-15-at-10-37-41" border="0" /></a>
    <!-- <img src="https://ibb.co/HfNb3QJ1" alt="Storezee Shathi" class="logo"> -->
    <h2>Welcome back to <strong>Storzee</strong> {{user}} 👋</h2>
    <p>Use the OTP below to login into your storzee account:</p>

    <div class="otp">{{otp}}</div>

    <p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
    
    <div class="footer">
      Need help? Contact us at <a href="mailto:support@storzee.com">support@storezee.com</a>
    </div>
  </div>
</body>
</html>

'''
    body = body.replace('{{otp}}', otp)
    body = body.replace('{{user}}', user_name)
    msg = EmailMultiAlternatives(subject, body, from_email, [to])
    msg.attach_alternative(body, "text/html")
    msg.send()

    