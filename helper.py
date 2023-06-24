import twilio
import random
from twilio.rest import Client
from datetime import date, datetime, timedelta


#helper functions

def otp_generation():
    return random.randint(1000, 9999)


def send_otp(phone_number,otp):

    account_sid = 'AC9e7afa8cac2bf723d775a4490bed7f21'
    auth_token = 'c2068e5f30a5562de0aa8d37588e7124'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body='Hi Im Shri. Your Secure Device OTP for Covid Vaccination is - ' + str(otp),
        from_='+15417222908',
        to='+91' + str(phone_number)
    )


def curr_date():
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    return formatted_date

def next_n_days(n):
    current = datetime.now().date()
    next_n_dates = []
    for i in range(1, n+1):
        x = timedelta(days=i)
        future_date = current + x
        formatted = future_date.strftime("%Y-%m-%d")
        next_n_dates.append(formatted)
    return next_n_dates


