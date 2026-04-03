import requests
import qrcode
import os
import smtplib
from email.message import EmailMessage

CONFIG = {
    "AUTH_TOKEN": "Basic SUQ0cmJvc1ZqeXJTN1FLTTVWRUI6dTh1bVhoSWUyeUNlb0dzcXMxZjY3U0M0c1JJcU5HWjkwcTI5SDlUUQ==",
    "ACCOUNT_ID": "4140",
    "CHANNEL_ID": 4979,
    "PROVIDER": "m-pesa",
    "CALLBACK_URL": "https://yourdomain.com/callback"
}

class PayHeroSTK:

    def __init__(self, config):
        self.config = config
        self.base_url = "https://backend.payhero.co.ke/api/v2"


    def _make_request(self, endpoint, method="POST", params=None, payload=None):

        url = f"{self.base_url}/{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.config["AUTH_TOKEN"]
        }

        try:

            if method == "POST":
                response = requests.post(url, headers=headers, json=payload)

            if method == "GET":
                response = requests.get(url, headers=headers, params=params)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException:

            return None


    def initiate_stk_push(self, phone_number, amount, reference, customer_name):

        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]

        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": self.config["CHANNEL_ID"],
            "provider": self.config["PROVIDER"],
            "external_reference": reference,
            "customer_name": customer_name,
            "callback_url": self.config["CALLBACK_URL"],
            "account_id": self.config["ACCOUNT_ID"]
        }

        return self._make_request("payments", payload=payload)


    def check_payment_status(self, reference):

        params = {"reference": reference}

        return self._make_request("transaction-status", method="GET", params=params)



def generate_ticket(name, phone, tournament, amount, reference, mpesa_code):

    os.makedirs("tickets", exist_ok=True)

    filename = f"tickets/{reference}.png"

    ticket_data = f"""
THE KNOCKOUT - CARLIX GROUP
--------------------------
Name: {name}
Phone: {phone}
Tournament: {tournament}
Amount: KES {amount}
Ticket Ref: {reference}
M-Pesa Code: {mpesa_code}
"""

    qr = qrcode.make(ticket_data)

    qr.save(filename)

    return filename



import smtplib
from email.message import EmailMessage

def send_ticket_email(to_email, name, tournament, reference, qr_path):

    sender_email = "carlixgroup@zohomail.com"
    sender_password = "rMgvTyBXvzet"

    msg = EmailMessage()
    msg["Subject"] = f"{tournament} Ticket - THE KNOCKOUT"
    msg["From"] = sender_email
    msg["To"] = to_email

    msg.set_content("Your ticket is ready")

    msg.add_alternative(f"""
    <html>
    <body style="margin:0; padding:0; background:#0a0f1f; font-family:Arial, sans-serif; color:#ffffff;">

        <div style="max-width:600px; margin:auto; padding:20px;">

            <!-- LOGO -->
            <div style="text-align:center; margin-bottom:20px;">
                <img src="cid:logo" width="120"/>
            </div>

            <!-- TITLE -->
            <h1 style="text-align:center; color:#00d4ff; margin-bottom:10px;">
                THE KNOCKOUT
            </h1>

            <p style="text-align:center; color:#aaa;">
                Carlix Group Tournament Series
            </p>

            <!-- CARD -->
            <div style="
                background:#121a33;
                border-radius:12px;
                padding:20px;
                margin-top:20px;
                box-shadow:0 0 20px rgba(0,212,255,0.2);
            ">

                <h2 style="color:#00d4ff;">🎟 Your Ticket</h2>

                <p>Hello <b>{name}</b>,</p>

                <p>Your ticket has been successfully generated.</p>

                <hr style="border:1px solid #1e2a4a;">

                <p><b>🎮 Tournament:</b> {tournament}</p>
                <p><b>🆔 Ticket Ref:</b> {reference}</p>

                <div style="text-align:center; margin:25px 0;">
                    <p style="color:#aaa;">Scan at entrance</p>
                    <img src="cid:qr_code" width="180"/>
                </div>

            </div>

            <!-- FOOTER -->
            <div style="text-align:center; margin-top:25px; font-size:12px; color:#888;">
                <p>This is an automated ticket from Carlix Group.</p>
                <p>© 2026 Carlix Group. All rights reserved.</p>
            </div>

        </div>

    </body>
    </html>
    """, subtype="html")

    # Attach QR
    with open(qr_path, "rb") as f:
        msg.get_payload()[1].add_related(
            f.read(),
            maintype="image",
            subtype="png",
            cid="qr_code"
        )

    # Attach LOGO
    with open("static/logo.png", "rb") as f:
        msg.get_payload()[1].add_related(
            f.read(),
            maintype="image",
            subtype="png",
            cid="logo"
        )

    try:
        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print("✅ Beautiful email sent")

    except Exception as e:
        print("❌ Email failed:", e)