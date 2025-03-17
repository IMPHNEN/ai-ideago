from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, text
from pydantic import BaseModel
from typing import Optional
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
app = FastAPI(title="Project Chat API", lifespan=lifespan)

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
    return {"status": "service start..."}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Create or get session
        chat_chain = request.app.state.chat_chain
        if not message.session_id:
            session = ChatSession(user_id=message.user_id)
            db.add(session)
            await db.commit()
            await db.refresh(session)
            session_id = session.id
            chat_chain.clear_memory()
        else:
            session_id = message.session_id
            
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
        
        if result["is_final"] and result["parsed_data"]:
            project_data = ProjectData(
                session_id=session_id,
                project_data=result["parsed_data"]
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)