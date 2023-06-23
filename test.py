import twilio
import random
from twilio.rest import Client

otp = random.randint(1000,9999)
print("Your OTP is -",otp)

account_sid = 'AC9e7afa8cac2bf723d775a4490bed7f21'
auth_token = 'c2068e5f30a5562de0aa8d37588e7124'

client = Client(account_sid,auth_token)

message = client.messages.create(
         body='Hi Im Shri. Your Secure Device OTP is - ' + str(otp),
         from_='+15417222908',
         to='+91'
     )

user_otp = int(input("Enter the received OTP: "))
if(user_otp == otp):
    print("WELCOME")
else:
    print(";(")


#