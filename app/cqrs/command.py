from app.core.database import Mongo
import logging
from pymongo.errors import DuplicateKeyError, BulkWriteError
class CommandSide():
    def __init__(self, mongo: Mongo):
        self.mongo = mongo
        self.logger = logging.getLogger("email_organizer")
    async def storeManyRawEmails(self, emailsData):
        if not emailsData:
            self.logger.warning("There is no email data")
            return
        collection = self.mongo.getMongoCollection("raw_emails")
        try:
            await collection.create_index("id", unique=True)
            result = await collection.insert_many(emailsData, ordered=False)
            print(result)
            self.logger.info(f"{len(result.inserted_ids)} emails stored.")
        except DuplicateKeyError:
            self.logger.log(level=1, msg="Avoiding duplicate emails")
        except BulkWriteError:
             self.logger.log(level=1, msg="Avoiding duplicate emails")
        except Exception as error:
                self.logger.error(f"Exception in storeManyRawEmails: {error}")
    async def updateEmail(self, id, data):
        collection = self.mongo.getMongoCollection("raw_emails")
        cursor = await collection.update_one(
            {"id":id},
            {"$set": data}
        )
        return cursor