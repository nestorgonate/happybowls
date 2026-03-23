from app.cqrs.command import CommandSide
from app.cqrs.queries import QuerySide
from datetime import datetime
class EmailRepository():
    def __init__(self, commandSide: CommandSide, querySide: QuerySide=None):
        self.command = commandSide
        self.queryside = querySide
    async def storeManyRawEmails(self, emailsData):
        await self.command.storeManyRawEmails(emailsData=emailsData)
    async def searchVector(self, vector_input):
        async for email in self.queryside.searchVector(vector_input=vector_input):
            yield email
    async def getEmailsFromMongoDb(self, last_id, customer: str=None, date: datetime=None):
        async for email in self.queryside.getEmailsFromMongo(last_id=last_id, customer=customer, date=date):
            yield email
    async def updateEmail(self, id, data):
        return await self.command.updateEmail(id=id, data=data)