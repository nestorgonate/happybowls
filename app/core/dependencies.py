from app.services.emailservice import EmailService
from app.consume.emailclient import EmailAPI
from app.consume.reademails import ReadEmails
from app.repositories.emailrepository import EmailRepository
from app.agent.geminiapi import Gemini
from app.cqrs.command import CommandSide
from app.cqrs.queries import QuerySide
from app.core.database import Mongo
from app.services.loadEmails import LoadEmails
def getEmailService():
    emailAPI = EmailAPI()
    readEmails = ReadEmails(emailAPI=emailAPI)
    mongo = Mongo()
    commandSide = CommandSide(mongo=mongo)
    querySide = QuerySide(mongo=mongo)
    emailRepository = EmailRepository(commandSide=commandSide, querySide=querySide)
    gemini = Gemini()
    emailService = EmailService(readEmails=readEmails, emailRepository=emailRepository, gemini=gemini)
    return emailService
def getLoadEmailService():
    mongo = Mongo()
    commandSide = CommandSide(mongo=mongo)
    emailAPI = EmailAPI()
    readEmails = ReadEmails(emailAPI=emailAPI)
    emailRepository = EmailRepository(commandSide=commandSide)
    gemini = Gemini()
    loadEmails = LoadEmails(readEmails=readEmails, emailRepository=emailRepository, gemini=gemini)
    return loadEmails