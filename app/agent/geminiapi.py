from google import genai
from google.genai import types
from google.genai.types import EmbedContentConfig
import logging
class Gemini():
    def __init__(self):
        self.geminiClient = genai.Client()
        self.logger = logging.getLogger("email_organizer")
    async def generateResponse(self, input, context):
        response = self.geminiClient.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=f"""
                You are an assistant that helps to track orders for a food business.
                Answer to the following question based on this emails data: {context}.\n
                Do not include the domain email in the response, only the name of the sender.
                Do not answer with markdown format.
                You have to draft an answer in paragraph easy to understand with specific details.
                """,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
            contents=input
        )
        return response.text
    async def vectorizeDocument(self, raw_data):
        try:
            self.logger.info("Vectorizing document")
            if not raw_data:
                return [0.0] * 768
            vector = self.geminiClient.models.embed_content(
                model="gemini-embedding-001",
                contents=raw_data,
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768
                )
            )
            #Extract the first index of the list vector
            return [item.values for item in vector.embeddings]
        except Exception as error:
            self.logger.error(f"Can not vectorize document: {error}")
    async def vectorizeInput(self, raw_input):
        if not raw_input:
            return [0.0] * 768
        vector = self.geminiClient.models.embed_content(
            model="gemini-embedding-001",
            contents=raw_input,
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768
            )
        )
        return vector.embeddings[0].values