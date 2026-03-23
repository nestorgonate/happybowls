import logging

from consume.reademails import ReadEmails
from repositories.emailrepository import EmailRepository
from agent.geminiapi import Gemini
import json
from datetime import datetime
class EmailService():
    def __init__(self, readEmails: ReadEmails, emailRepository: EmailRepository, gemini: Gemini):
        self.readEmails = readEmails
        self.emailRepository = emailRepository
        self.gemini = gemini
        self.logger = logging.getLogger("email_organizer")
    async def analyzeEmails(self, input):
        try:
            data = []
            vector_input = await self.gemini.vectorizeInput(input)
            async for email in self.emailRepository.searchVector(vector_input=vector_input):
                data.append ({
                    "context":"""You are a virtual assistant for a food establishment that keeps track of orders that come in via email."
                                Answer to the user input based o this email data, provide the details with deadline order.
                                Do not provide a deadline, pickup and delivery date or hour based on email data.
                                You have to follow the respective fields for each data.
                                Provide the deadline field with the delivery or pickup order in the data.
                                If the email data has pickup hour it is a pickup order.
                                If the email data has delivery hour it is a delivery order""",
                    "customer":email.customer,
                    "deadline":email.deadline,
                    "pickup":email.pickup,
                    "delivery":email.delivery
                })
            if not data:
                return []
            cleanEmail = json.dumps(data, ensure_ascii=False, indent=4)
            response = await self.gemini.generateResponse(input=input, context=cleanEmail)
            return response
        except Exception as error:
            self.logger.error(f"Can not analyze emails: {error}")
    async def getEmails(self, last_id, customer: str=None, date: datetime=None) -> list:
        try:
            emails = []
            async for email in self.emailRepository.getEmailsFromMongoDb(last_id, customer=customer, date=date):
                emails.append({
                    "idMongo": email.idMongo,
                    "id": email.id,
                    "customer":email.customer,
                    "subject": email.subject,
                    "deadline": email.deadline,
                    "estimate": email.estimate,
                    "pickup": email.pickup,
                    "delivery": email.delivery,
                    "date_email_sent": email.date_email_sent
                })
            if not emails:
                return emails
            return emails
        except Exception as error:
            self.logger.error(f"Can not get emails: {error}")
            return []
    async def updateEmail(self, id, data):
        try:
            result = await self.emailRepository.updateEmail(id=id, data=data)
            return result
        except Exception as error:
            self.logger.error(f"Can not update email: {error}")