from langchain_openai import ChatOpenAI
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

# Schema definitions with updated talent array and budget fields
PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "slug": {"type": "string"},
                "description": {"type": "string"},
                "image": {"type": "string"},
                "budget": {
                    "type": "object",
                    "properties": {
                        "minimum": {"type": "number"},  # minimum funds needed to start project
                        "total": {"type": "number"},    # funds already obtained
                        "from": {"type": "number", }  # total funding required
                    },
                    "required": ["minimum", "total", "from"]
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
        "talents": {
            "type": "array",
            "items": {
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
            },
            "minItems": 1
        }
    },
    "required": ["project", "talents"]
}

# Specific keywords to trigger project generation
SUBMIT_KEYWORDS = [
    "#submit", "#generate", "#selesai",  # Basic submission keywords
    "#save", "#simpan", "#finish",       # Alternative submission words
    "#done", "#complete", "#end",        # Completion keywords
    "#kirim", "#buat", "#create"         # Creation keywords
]

class ProjectChatChain:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.parser = JsonOutputParser(schema=PROJECT_SCHEMA)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Yang Chatting-an, a creative and proactive business creator assistant who helps users by providing detailed project suggestions based on their simple descriptions.

IMPORTANT: Do NOT generate any project data JSON until the user specifically uses one of these keywords: "#submit", "#generate", or "#selesai".

Your role is to:
1. Listen to the user's basic project idea
2. Proactively suggest detailed and realistic project specifications including:
   - Comprehensive project scope and features
   - Realistic budget estimations
   - Required talent roles and expertise levels
   - Reasonable project timeline
3. Ask for user's feedback on your suggestions
4. Refine the suggestions based on their feedback
5. Only generate the final JSON when they use a submit keyword

Conversation style:
- Speak in Indonesian language
- Be friendly, creative, and professional
- Make realistic suggestions based on market standards
- Don't ask users about technical details or budget - suggest them instead
- Present suggestions in an easy-to-understand way
- Remember previous feedback and adjust suggestions accordingly

When suggesting project details:
- Base budget on market rates and project complexity
- Suggest appropriate talent roles and experience levels
- Propose realistic timelines
- Include all necessary project components
- Break down suggestions into clear sections

When the user uses a submit keyword (#submit, #generate, #selesai, or other variance):
- Generate a complete JSON with your final suggested specifications
- Include all technical details (UUIDs, slugs, dates)
- Ensure budget and timeline are realistic
- Include all necessary talent roles

Current conversation context: {chat_history}
"""),
            ("human", "{input}"),
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
            # Check if this is a submit request
            is_submit = any(keyword in message.lower() for keyword in SUBMIT_KEYWORDS)
            
            # Generate response from LLM
            response = await self.chain.apredict(input=message)
            
            # If this is a submit request, generate project data
            if is_submit:
                try:
                    # Try to extract JSON from the response
                    try:
                        parsed_data = self.parser.parse(response)
                    except Exception as e:
                        print_exc()
                        print(f"Error parsing LLM response as JSON: {str(e)}")
                        
                        # Get conversation history as a string
                        history_messages = self.memory.chat_memory.messages
                        conversation_history = "\n\n".join([f"{msg.type}: {msg.content}" for msg in history_messages])
                        
                        # If parsing fails, ask LLM to generate complete data with specific instructions
                        completion_prompt = f"""Based on our conversation, generate a complete JSON response following this exact schema. This is critical for the project management system to work properly.

Important points about the schema:
1. The "project" object needs all required fields exactly as shown
2. The "talents" field must be an ARRAY of talent objects (even if there's only one talent)
3. The budget fields mean:
   - "minimum": minimum funds needed to START the project
   - "total": amount of funds ALREADY OBTAINED
   - "from": TOTAL funding required for the entire project

Schema:
{json.dumps(PROJECT_SCHEMA, indent=2)}

Conversation history:
{conversation_history}

Make sure to:
1. Generate valid UUIDs for all ID fields
2. Create proper slugs from titles
3. Use ISO format for all dates (e.g., "2024-01-01T00:00:00.000Z")
4. Include multiple talents if different roles are mentioned
5. Set appropriate experience levels and payment types
6. Format all JSON values with the correct data types

Respond ONLY with the complete JSON object, nothing else.
"""
                        # Make a direct call to the LLM for JSON generation
                        completion_response = self.llm.predict(completion_prompt)
                        
                        # Clean response to ensure it's valid JSON
                        # Remove any markdown code blocks or extra text
                        cleaned_response = self._extract_json_from_text(completion_response)
                        
                        # Parse the cleaned JSON
                        parsed_data = json.loads(cleaned_response)
                        
                        # Validate against our schema
                        self._validate_project_data(parsed_data)
                    
                    return {
                        "response": "Baik, saya telah menyimpan detail project Anda. Apakah ada yang bisa saya bantu lagi?",
                        "parsed_data": parsed_data,
                        "is_final": True
                    }
                except Exception as e:
                    print_exc()
                    print(f"Failed to generate project data: {str(e)}")
                    return {
                        "response": "Maaf, saya gagal membuat data project. Mohon berikan informasi lebih lengkap tentang project Anda dan gunakan #submit untuk menyimpan.",
                        "parsed_data": None,
                        "is_final": False
                    }
            
            # Regular conversation response
            return {
                "response": response,
                "parsed_data": None,
                "is_final": False
            }
            
        except Exception as e:
            print_exc()
            raise Exception(f"Error processing message: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text that might contain markdown or other text"""
        # Try to find JSON between code blocks first
        import re
        json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
        matches = re.findall(json_pattern, text)
        
        if matches:
            # Return the first match that parses as valid JSON
            for match in matches:
                try:
                    # Validate by parsing
                    json.loads(match.strip())
                    return match.strip()
                except Exception as _:
                    continue
        
        # If no valid JSON found in code blocks, try to extract using brackets
        try:
            # Find the first opening brace and the last closing brace
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = text[start:end]
                # Validate by parsing
                json.loads(json_text)
                return json_text
        except Exception as _:
            pass
        
        # If all else fails, return the original text
        return text
    
    def _validate_project_data(self, data: Dict) -> None:
        """Validate project data against our schema and make corrections if needed"""
        # Check if project exists
        if "project" not in data:
            raise ValueError("Project data must contain a 'project' object")
        
        # Ensure talents is an array
        if "talent" in data and "talents" not in data:
            # Convert single talent to talents array
            data["talents"] = [data["talent"]]
            del data["talent"]
        elif "talents" not in data:
            raise ValueError("Project data must contain a 'talents' array")
        
        # Ensure talents is an array even if it was provided as a single object
        if not isinstance(data["talents"], list):
            data["talents"] = [data["talents"]]
        
        # Basic validation
        if not data["talents"]:
            raise ValueError("Project must have at least one talent")
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear() 