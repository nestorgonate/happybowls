from core.database import Mongo
import logging
from models.email import Email
from datetime import datetime, timedelta
from bson import ObjectId
class QuerySide():
    def __init__(self, mongo: Mongo):
        self.mongo = mongo
        self.logger = logging.getLogger("email_organizer")
    async def getEmailsFromMongo(self, last_id, customer=None, date: datetime=None):
        collection = self.mongo.getMongoCollection("raw_emails")
        query = {}
        if customer:
            query["customer"] = {
                    "$regex": customer
                }
        if date:
            # 1. Convertimos el objeto datetime a String exacto (YYYY-MM-DD)
            # Si tus strings en Mongo tienen otro formato, cámbialo aquí
            date_str = date.strftime("%Y-%m-%d") 

            if date.hour == 0 and date.minute == 0 and date.second == 0:
                # Buscamos todos los que EMPIECEN con esa fecha (así evitamos líos de horas)
                query["deadline"] = {"$regex": f"^{date_str}"}
            else:
                # Si buscas una hora exacta, el string debe coincidir letra por letra
                full_date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                query["deadline"] = full_date_str
        if last_id and last_id.strip() != "":
            IdObjectID = ObjectId(last_id)
            query["_id"] = {
                "$lt":IdObjectID
            }
        cursor = collection.find(query).sort("_id", -1).limit(5)
        async for document in cursor:
            document["_id"] = str(document["_id"])
            yield Email(**document)
    async def searchVector(self, vector_input, limit=5):
        collection = self.mongo.getMongoCollection("raw_emails")
        pipeline = [{
            "$vectorSearch":{
                "index":"vector_index",
                "path":"vector_data",
                "queryVector":vector_input,
                "numCandidates":100,
                "limit":limit
            }
        },
            {
                "$project":{
                    "_id":{"$toString":"$_id"},
                    "id":"$id",
                    "body":1,
                    "subject":1,
                    "sender":1,
                    "vector_data":1,
                    "deadline":1,
                    "customer":1,
                    "estimate":1,
                    "pickup":1,
                    "delivery":1,
                    "date_email_sent":1,
                    "score":{"$meta":"vectorSearchScore"}
                }
            }
        ]
        cursor = collection.aggregate(pipeline=pipeline)
        async for document in cursor:
            try:
                yield Email(**document)
            except Exception as error:
                self.logger.error(f"Can't do searchVector: {error}")