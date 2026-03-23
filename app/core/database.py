from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
class Mongo():
    def __init__(self):
        self.logger = logging.getLogger("email_organizer")
        self.databaseURL = os.getenv("DATABASE_URL")
    def getMongoCollection(self, collection):
        try:
            client = AsyncIOMotorClient(self.databaseURL)
            db = client["emails"]
            collection = db[collection]
            return collection
        except Exception as error:
            self.logger.exception(f"Exception in getMongoClient: {error}")