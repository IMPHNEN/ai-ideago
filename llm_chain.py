from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from typing import Dict
import os
import json
from dotenv import load_dotenv
from traceback import print_exc

# Load environment variables
load_dotenv()

# Schema definitions
PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "slug": {"type": "string"},
                "description": {"type": "string", "nullable": True},
                "image": {"type": "string"},
                "budget": {
                    "type": "object",
                    "properties": {
                        "minimum": {"type": "number"},
                        "total": {"type": "number"},
                        "from": {"type": "number", "nullable": True}
                    },
                    "required": ["minimum", "total"]
                },
                "duration": {
                    "type": "object",
                    "properties": {
                        "total": {"type": "number"},
                        "type": {"type": "string"}
                    },
                    "required": ["total", "type"]
                },
                "published": {"type": "boolean"},
                "status": {"type": "string", "enum": ["created", "progress", "done"]},
                "fundsStatus": {"type": "string", "enum": ["pending", "active", "completed", "cancelled"]},
                "fundsUntil": {"type": "string", "format": "date-time"},
                "isFixed": {"type": "boolean"},
                "viewed": {"type": "number"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "title", "slug", "image", "budget", "duration", "published", "status", "fundsStatus", "fundsUntil", "isFixed", "viewed", "createdAt", "updatedAt"]
        },
        "talent": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string", "nullable": True},
                "requirements": {"type": "array", "items": {"type": "string"}, "nullable": True},
                "budget": {"type": "number"},
                "experience": {"type": "string", "enum": ["entry", "intermediate", "expert"]},
                "payment": {"type": "string", "enum": ["fixed", "hourly"]},
                "status": {"type": "string", "enum": ["open", "filled", "closed"]},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "name", "budget", "experience", "payment", "status", "createdAt", "updatedAt"]
        }
    },
    "required": ["project", "talent"]
}

class ProjectChatChain:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME")
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.parser = JsonOutputParser(schema=PROJECT_SCHEMA)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Yang Chatting-an, a business creator assistant. Your role is to help users define their projects and talent requirements in detail.

When users describe their project, engage in a conversation to gather all necessary details. Ask relevant questions to fill in any missing information.

For each user message:
1. If it's a new project description or additional information:
   - Analyze the information provided
   - Ask specific questions about missing required fields from the schema
   - Focus on one or two missing fields at a time to keep the conversation natural
   - Provide suggestions based on the information given

2. If the user confirms (says "oke", "ok", "yes", "good"):
   - Generate a complete JSON response following the schema
   - For any missing information, analyze the conversation history and make intelligent assumptions based on:
     * Project context and domain
     * Industry standards and best practices
     * Similar projects discussed
     * User's preferences and constraints mentioned
   - Generate appropriate values for technical fields:
     * Create UUIDs for IDs
     * Generate slugs from titles
     * Set current timestamps for dates
     * Calculate reasonable budgets based on project scope
     * Determine appropriate durations based on complexity
     * Set status fields based on project context
   - Ensure all generated data is coherent and consistent with the project's nature

Remember to:
- Keep responses focused on the current question or topic
- Don't repeat previous conversation history
- Be concise but thorough in gathering information
- Use Indonesian language for responses
- Ensure all generated data is realistic and contextually appropriate

Current conversation context: {chat_history}
"""),
            ("human", "{input}")
        ])
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
    
    async def process_message(self, message: str, session_id: str) -> Dict:
        """Process a message and return the response"""
        try:
            # Generate response from LLM
            response = await self.chain.apredict(input=message)
            
            # Check if user is satisfied
            if any(confirmation in message.lower() for confirmation in ["oke", "ok", "yes", "good"]):
                try:
                    # Try to parse the response as JSON
                    try:
                        parsed_data = self.parser.parse(response)
                    except Exception as _:
                        print_exc()
                        # If parsing fails, ask LLM to generate complete data
                        completion_prompt = f"""Based on our conversation about the project, please generate a complete JSON response following the schema. Include all required fields and make intelligent assumptions for any missing information. Use the following format:

{json.dumps(PROJECT_SCHEMA, indent=2)}

Remember to:
1. Generate UUIDs for IDs
2. Create slugs from titles
3. Use ISO format for dates
4. Make realistic assumptions based on the project context
5. Ensure all required fields are included
6. Keep the data coherent and consistent

Previous conversation: {self.memory.chat_memory.messages}"""
                        
                        completion_response = self.llm.predict(completion_prompt)
                        parsed_data = self.parser.parse(completion_response)
                    
                    return {
                        "response": "Baik, saya telah menyimpan detail project Anda. Apakah ada yang bisa saya bantu lagi?",
                        "parsed_data": parsed_data,
                        "is_final": True
                    }
                except Exception as _:
                    print_exc()
                    return {
                        "response": "Maaf, saya masih membutuhkan beberapa informasi penting untuk melengkapi detail project. " + response,
                        "parsed_data": None,
                        "is_final": False
                    }
            
            return {
                "response": response,
                "parsed_data": None,
                "is_final": False
            }
            
        except Exception as e:
            print_exc()
            raise Exception(f"Error processing message: {str(e)}")
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear() 