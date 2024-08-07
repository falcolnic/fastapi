import math, random

def generate_OTP() :
 
    # Declare a digits variable  
    # which stores all digits 
    digits = "0123456789"
    otp = ""
 
   # length of password can be changed
   # by changing value in range
   
    for i in range(6) :
        otp += digits[math.floor(random.random() * 10)]
 
    return otp