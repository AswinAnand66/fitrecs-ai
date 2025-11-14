from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

class FitnessCoachService:
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        self.llm = OpenAI(openai_api_key=api_key, model_name=model_name)
        self.memory = ConversationBufferMemory()
        
        self.prompt = PromptTemplate(
            template="""You are an expert fitness and health coach assistant. You help users with workout advice,
            nutrition guidance, and general fitness tips. Always be encouraging and supportive, while maintaining
            professionalism and safety awareness. If a user asks about injuries or serious health concerns,
            advise them to consult a healthcare professional.

            Current conversation:
            {history}
            Human: {input}
            Assistant:""",
            input_variables=["history", "input"]
        )

        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt,
            verbose=True
        )

    async def get_response(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Get an AI response to a user message.
        """
        # If context is provided, update the conversation memory
        if context:
            for msg in context:
                if msg["type"] == "user":
                    self.memory.save_context(
                        {"input": msg["text"]},
                        {"output": ""}
                    )
                else:
                    self.memory.save_context(
                        {"input": ""},
                        {"output": msg["text"]}
                    )

        # Get response from the model
        response = await self.conversation.arun(input=message)
        return response.strip()