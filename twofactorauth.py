import os
import pyotp
import qrcode

key = "YOUWILLNEVERGUESSTHISISYOURSECRETKEY"

uri = pyotp.totp.TOTP(key).provisioning_uri(name="Khushteg_Grewal",issuer_name="IKON_Conveyancing")
print(uri)
qrcode.make(uri).save("totp.png")

totp = pyotp.TOTP(key)

def verify_passcode(passcode):
    return totp.verify(passcode)