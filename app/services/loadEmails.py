from app.consume.reademails import ReadEmails
from app.repositories.emailrepository import EmailRepository
from app.agent.geminiapi import Gemini
import logging
import json
from datetime import datetime
class LoadEmails():
    """
    Method to stored emails in mongodb
    """
    def __init__(self, readEmails: ReadEmails, emailRepository: EmailRepository, gemini: Gemini):
        self.readEmails = readEmails
        self.emailRepository = emailRepository
        self.gemini = gemini
        self.date = datetime.today()
        self.year = self.date.year
        self.month = self.date.month
        self.today_context = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger("email_organizer")
    async def checkEmails(self):
        try:
            #Read emails through ReadEmails class
            emails = self.readEmails.readEmails()
            if not emails:
                self.logger.info("No new emails\n")
                return
            #Unir contenido del pdf y body email para vectorizarlos juntos y usarlos como contexto del chat de gemini
            raw_data = []
            for email in emails:
                pdf_text = email["pdf_content"]
                combined_text = f"Email body: {email["body"]}\nPdf content: {pdf_text}"
                raw_data.append(combined_text)
            vector_data = await self.gemini.vectorizeDocument(raw_data=raw_data)
            if isinstance(vector_data, list) and len(vector_data) == 1 and len(emails) > 1:
                vector_data = vector_data[0]
            #Process emails to extract data
            extracted_data = []
            contextGemini = f"""
                            You are a restaurant assistant. Analyze the provided email and extract data.
                            IMPORTANT: Return ONLY a SINGLE JSON OBJECT. 
                            Do NOT wrap it in a list []. Do NOT use markdown code blocks.
                            Rules:
                            If the year for the deadline is not specified, assume {self.year}
                            If the month for the deadline is not sepecified, assume {self.month}
                            If a value is unknown, use an empty string "" (not null).
                            Your output must be ONLY the JSON object.
                            Do not include any wrapper keys like "action", "text", or "output".
                            Do not use Markdown code blocks (e.g., ```json).
                            The very first character of your response must be {{ and the last must be }}.
                            Your output MUST be a valid JSON object.
                            NEVER output text, greetings, explanations, apologies, or any character before or after the {{}} brackets.
                            If you can not find some data just write no data found in the respective field
                            If you find links to an external website realted to orders attach it to estimate field
                            Format JSON:
                            {{
                                "sender": "sender name or email",
                                "subject": "email subject line",
                                "deadline": "date of order found in email body or email pdf in YYYY-MM-DD HH:MM:SS format",
                                "customer": "customer name found in email sender",
                                "estimate": "food or items ordered",
                                "pickup": "hour of the deadline in email body or email pdf HH:MM:SS format or empty",
                                "delivery": "hour of the deadline in email body or email pdf HH:MM:SS format or empty",
                                "date_email_sent": "YYYY-MM-DD HH:MM:SS"
                            }}
                            """
            #Add vector_data to email data
            for email, vector in zip(emails, vector_data):
                clean_vector = vector[0] if isinstance(vector, list) and isinstance(vector[0], list) else vector
                #Extract subect email and body email as string to send to gemini
                email_date = email.get("date_email_sent", "Unknown")
                prompt_input = (f"Context: Today is {self.today_context}. Use this to calculate relative dates.\n"
                                f"Email Date: {email_date}\n"
                                f"Subject: {email['subject']}\n"
                                f"Sender: {email['sender']}\n"
                                f"Email body: {email['body']}"
                                f"Email pdf: {email["pdf_content"]}")
                response_str = await self.gemini.generateResponse(input=prompt_input, context=contextGemini)
                #Clean the gemini response and convert to dict
                try:
                    clean_json = response_str.replace("```json", "").replace("```", "").strip()
                    json_to_dict = json.loads(clean_json)
                    #Fix the output of Gemini in case of wrong type
                    if isinstance(json_to_dict, list):
                        json_to_dict = json_to_dict[0] if json_to_dict else None
                    if json_to_dict:
                        json_to_dict["vector_data"] = clean_vector
                        json_to_dict["id"] = email["id"]
                        if not json_to_dict.get("date_email_sent"):
                            json_to_dict["date_email_sent"] = email_date
                        extracted_data.append(json_to_dict)
                except Exception as error:
                    self.logger.error(f"Error parsing Gemini response to JSON: {error}")
            if extracted_data:
                self.logger.info(f"Storing {len(extracted_data)} emails in MongoDB")
                self.logger.info(f"Sample doc keys: {list(extracted_data[0].keys())}")
                self.logger.info(f"vector_data type: {type(extracted_data[0]['vector_data'])}, len: {len(extracted_data[0]['vector_data'])}")
                await self.emailRepository.storeManyRawEmails(emailsData=extracted_data)
        except Exception as error:
            self.logger.error(f"Can not load emails: {error}")