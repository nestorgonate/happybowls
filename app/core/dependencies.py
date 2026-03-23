from services.emailservice import EmailService
from consume.emailclient import EmailAPI
from consume.reademails import ReadEmails
from repositories.emailrepository import EmailRepository
from agent.geminiapi import Gemini
from cqrs.command import CommandSide
from cqrs.queries import QuerySide
from core.database import Mongo
from services.loadEmails import LoadEmails
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