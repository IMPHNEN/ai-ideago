from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, text
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv
from llm_chain import ProjectChatChain
from traceback import print_exc
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./chat.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.chat_chain = ProjectChatChain()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Create FastAPI app
app = FastAPI(title="IdeaGO Chat API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database models
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectData(Base):
    __tablename__ = "project_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    project_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models
class MessageCreate(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    content: str

class Message(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    session_id: str
    messages: Message
    project_data: Optional[dict] = None

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Routes
@app.get("/")
async def root():
    return {"status": "IdeaGO Chat API is running", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get the chat chain from app state
        chat_chain = request.app.state.chat_chain
        
        # Create or get session
        if not message.session_id:
            session = ChatSession(user_id=message.user_id)
            db.add(session)
            await db.commit()
            await db.refresh(session)
            session_id = session.id
            chat_chain.clear_memory()
        else:
            session_id = message.session_id
            
            # When continuing a conversation, load previous messages into memory
            query = text("SELECT role, content FROM chat_messages WHERE session_id = :session_id ORDER BY created_at ASC")
            result = await db.execute(query, {"session_id": session_id})
            previous_messages = result.fetchall()
            
            # Only initialize memory if it's empty
            if not chat_chain.memory.chat_memory.messages and previous_messages:
                print(f"Loading {len(previous_messages)} previous messages into memory")
                # Load past messages into memory
                from langchain.schema import HumanMessage, AIMessage
                
                for role, content in previous_messages:
                    if role == "user":
                        chat_chain.memory.chat_memory.add_message(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_chain.memory.chat_memory.add_message(AIMessage(content=content))
            
        # Store user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=message.content
        )
        db.add(user_message)
        
        # Process message with LLM chain
        result = await chat_chain.process_message(message.content, session_id)
        
        # Store assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=result["response"]
        )
        db.add(assistant_message)
        
        # If we have parsed data, store it
        if result["is_final"] and result["parsed_data"]:
            # Ensure proper structure for talents
            data = result["parsed_data"]
            
            # Convert "talent" to "talents" array if needed
            if "talent" in data and "talents" not in data:
                data["talents"] = [data["talent"]]
                del data["talent"]
            elif not isinstance(data.get("talents", []), list):
                data["talents"] = [data["talents"]]
            
            # Store the updated data
            project_data = ProjectData(
                session_id=session_id,
                project_data=data
            )
            db.add(project_data)
        
        await db.commit()
        
        # Get project data if it exists
        query = text("SELECT project_data FROM project_data WHERE session_id = :session_id ORDER BY created_at DESC LIMIT 1")
        result_project = await db.execute(query, {"session_id": session_id})
        project_data_row = result_project.first()
        
        # Parse project data from JSON string if it exists
        project_data = None
        if project_data_row and project_data_row[0]:
            try:
                if isinstance(project_data_row[0], str):
                    project_data = json.loads(project_data_row[0])
                else:
                    project_data = project_data_row[0]
                
                # Ensure proper structure for talents
                if "talent" in project_data and "talents" not in project_data:
                    project_data["talents"] = [project_data["talent"]]
                    del project_data["talent"]
                elif not isinstance(project_data.get("talents", []), list):
                    project_data["talents"] = [project_data["talents"]]
                
            except json.JSONDecodeError:
                print_exc()
                project_data = None
        
        return ChatResponse(
            session_id=session_id,
            messages=Message(
                role="assistant",
                content=result["response"]
            ),
            project_data=project_data
        )
        
    except Exception as e:
        print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_includes=["*.py"],
        reload_excludes=["__pycache__/*", ".*", "*.pyc"]
    )