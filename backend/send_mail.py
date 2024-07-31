import re
import ast
import time
import smtplib
import cProfile

import sys
import logging
import datetime
import pandas as pd
import streamlit as st

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication

from configs import credentials


class MailUtils:
    def __init__(self):
        self.receivers_email_id = "rajashwin733@gmail.com"

    def get_help_with_orders(
        self,
        userid,
        orderid,
        query,
        attachment=None,
    ):
        message = MIMEMultipart()

        message["To"] = self.receivers_email_id
        message["From"] = st.secrets["sender_email_id"] 

        message["Subject"] = f"Help Requested with Order Id: #{orderid}"

        br_mail_body = (
            "Dear Support Team,\n\n"
            + "You have received a new support request from a user. Please find the details of the query below:"
            + "\n\nOrder Id: #"
            + str(orderid)
            + "\nUser Id: "
            + str(userid)
            + "\n\nQuery:\n"
            + str(query)
            + "\n\nPlease address this issue as soon as possible and keep the user informed about the progress and resolution."
            + "\n\nBest Regards,\n Support Management System"
        )

        message.attach(MIMEText(br_mail_body, "plain", "utf-8"))

        if attachment:
            pdf_filename = attachment

            pdf_attachment = open(pdf_filename, "rb").read()

            pdf_part = MIMEBase("application", "octet-stream")
            pdf_part.set_payload(pdf_attachment)

            encoders.encode_base64(pdf_part)

            display_pdf_filename = pdf_filename.replace("exports/generated_pdf/", "")
            display_pdf_filename = " ".join(
                word.capitalize() for word in display_pdf_filename.split("_")
            )

            pdf_part.add_header(
                "Content-Disposition", f"attachment; filename={display_pdf_filename}"
            )

            message.attach(pdf_part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.ehlo()

        server.login(st.secrets["sender_email_id"], st.secrets["sender_email_password"]  )
        text = message.as_string()

        server.sendmail(st.secrets["sender_email_id"], self.receivers_email_id, text)
        server.quit()
