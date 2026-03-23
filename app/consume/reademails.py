from googleapiclient.errors import HttpError
import logging
import base64
from app.core.utils import clean_html
from datetime import datetime
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from app.core.utils import get_senders
from app.consume.emailclient import EmailAPI
from app.core.utils import read_bytes_pdf
class ReadEmails():
    def __init__(self, emailAPI: EmailAPI):
        self.emailAPI = emailAPI
        self.emailClient = self.emailAPI.getEmailClient()
        self.logger = logging.getLogger("email_organizer")
        self.last_email_id = None
    def processEmail(self, emailID):
        #Get one email by their ID
        email = self.emailClient.users().messages().get(
            userId="me", id=emailID
        ).execute()
        #Payload is a dict of email data
        payload = email.get("payload", {})
        headers = payload.get("headers", [])
        date = next((h["value"] for h in headers if h["name"] == "Date"), "")
        date_parse = parsedate_to_datetime(date)
        nyc_zone = ZoneInfo("America/New_York")
        dt_nyc = date_parse.astimezone(nyc_zone)
        data = {
            "id": emailID,
            "sender": next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
            "subject": next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject'),
            "body": "",
            "vector_data":"",
            "pdf_content": None,
            "date_email_sent":dt_nyc
        }
        parts = payload.get("parts", [])
        if not parts:
            body_data = payload.get("body", {}).get("data", "")
        for part in parts:
            mimeType = part.get("mimeType")
            body = part.get("body", {})
            if mimeType == "text/plain" and "data" in body:
                body_data = body.get("data")
                data["body"] = clean_html(base64.urlsafe_b64decode(body_data).decode("utf-8"))
            elif mimeType == "application/pdf":
                attachment_id = body.get("attachmentId")
                if attachment_id:
                    attachment = self.emailClient.users().messages().attachments().get(
                        userId="me", messageId=emailID, id=attachment_id
                    ).execute()
                    pdf_raw_data = base64.urlsafe_b64decode(attachment["data"])
                    pdf_text = read_bytes_pdf(pdf_raw_data)
                    data["pdf_content"] = pdf_text
        #Mark the email as read to avoid read the email again
        self.emailClient.users().messages().batchModify(
            userId="me",
            body={
                "ids": [emailID],
                "removeLabelIds": ["UNREAD"]
            }
        ).execute()
        return data
    def readEmails(self):
        senders = get_senders()
        self.logger.info("Senders recieved")
        #Output = from:email OR from:email
        from_filter = f"({' OR '.join([f'from:{sender}' for sender in senders])})"
        try:
            results = self.emailClient.users().messages().list(
                userId="me", q=f"is:unread in:inbox {from_filter}", maxResults=10
            ).execute()
            emails = results.get("messages", [])
            if not emails:
                return []
            newEmails = []
            for email in emails:
                #Avoid duplicates
                if email["id"] == self.last_email_id:
                    break
                emaildata = self.processEmail(email["id"])
                newEmails.append(emaildata)
            #Update the last email id
            self.last_email_id = emails[0]["id"]
            return newEmails
        except HttpError as error:
            self.logger.error(f"Error in readEmails: {error}")
            return []