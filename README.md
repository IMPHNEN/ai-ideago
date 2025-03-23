# <div align="center">🚀 IdeaGO Chat API</div>

<div align="center">
  <img src="https://i.pinimg.com/736x/d9/f7/94/d9f79474001c33eaee83e02b6cc52eab.jpg" alt="IdeaGO Chat API Logo" width="300">
  <p><em>Intelligent project definition through conversation</em></p>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/LangChain-00A3E0?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
</div>

## 📋 Overview

IdeaGO Chat API is an intelligent assistant that helps business creators define their projects and talent requirements through natural conversation. The system uses advanced AI to gather project details, ask relevant questions, and generate comprehensive project specifications.

### 🌟 Key Features

- **Conversational Interface**: Engage in natural dialogue to define your project
- **Intelligent Data Generation**: AI generates complete project details based on conversation
- **Multiple Talent Support**: Define multiple roles and requirements for your project
- **Persistent Memory**: Conversation history is maintained for context
- **Multilingual Support**: Primary support for Indonesian language
- **Schema Validation**: Ensures all project data follows required format
- **Asynchronous Processing**: Fast, non-blocking API responses

## 🛠️ Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **OpenAI**: Powerful language model (GPT-4o) for natural conversation
- **SQLite**: Lightweight database for persistent storage
- **LangChain**: Framework for building LLM applications
- **Pydantic**: Data validation and settings management

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ideago-chat-api.git
cd ideago-chat-api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL_NAME=gpt-4o
```

### Running the Application

Start the FastAPI server:
```bash
python app.py
```

The server will run at `http://localhost:8000`

## 📚 API Documentation

### POST /chat

Start or continue a chat conversation to define project details.

#### Request

```json
{
  "user_id": "string",
  "session_id": "string (optional)",
  "content": "string"
}
```

#### Response

```json
{
  "session_id": "string",
  "messages": {
    "role": "string",
    "content": "string"
  },
  "project_data": "object (optional)"
}
```

## 📝 Example Usage

### Example Request

```json
{
  "user_id": "test-12",
  "session_id": "2",
  "content": "Hi, saya ingin memulai proyek baru untuk membuat platform e-learning. Bisakah kamu membantu saya membuat detail proyeknya?, Main Goal or Objective: Tujuan utama dari platform e-learning ini adalah untuk menyediakan akses pendidikan berkualitas tinggi dengan cara yang fleksibel dan terjangkau. Saya ingin platform ini menjadi solusi bagi orang-orang yang ingin belajar keterampilan baru atau meningkatkan pengetahuan mereka tanpa harus menghadiri kelas fisik. Target Audience: Target audiensnya adalah profesional yang bekerja, mahasiswa, dan individu yang ingin belajar mandiri. Fokusnya adalah pada orang-orang yang sibuk dan membutuhkan fleksibilitas dalam jadwal belajar mereka. Features: Saya membayangkan platform ini memiliki fitur-fitur berikut: Video lectures dengan kualitas tinggi. Kuis interaktif untuk menguji pemahaman. Forum diskusi untuk interaksi antar pengguna. Sertifikat kelulusan setelah menyelesaikan kursus. Kemampuan untuk belajar secara offline (mengunduh materi). Technology or Programming Language Preferences: Saya lebih memilih teknologi modern seperti React.js untuk frontend, Node.js untuk backend, dan MongoDB untuk database. Saya juga ingin menggunakan layanan cloud seperti AWS atau Google Cloud untuk hosting. Expected Number of Users in the First Year: Saya memperkirakan platform ini akan memiliki sekitar 10.000 pengguna dalam tahun pertama, dengan pertumbuhan yang stabil setiap bulannya."
}
```

### Final Submission Request

To finalize and generate the project data, include one of the special keywords:

```json
{
  "user_id": "test-12", 
  "session_id": "2",
  "content": "#submit"
}
```

### Example Response

```json
{
  "session_id": "2",
  "messages": {
    "role": "assistant",
    "content": "Baik, saya telah menyimpan detail project Anda. Apakah ada yang bisa saya bantu lagi?"
  },
  "project_data": {
    "project": {
      "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "title": "Platform E-Learning",
      "slug": "platform-e-learning",
      "description": "Platform e-learning untuk menyediakan akses pendidikan berkualitas tinggi dengan cara yang fleksibel dan terjangkau.",
      "image": "https://example.com/platform-e-learning-logo.png",
      "budget": {
        "minimum": 1000000,
        "total": 2000000,
        "from": 5000000
      },
      "duration": {
        "total": 12,
        "type": "months"
      },
      "published": true,
      "status": "created",
      "fundsStatus": "pending",
      "fundsUntil": "2024-12-31T23:59:59.999Z",
      "isFixed": false,
      "viewed": 0,
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z"
    },
    "talents": [
      {
        "id": "4b1c2a85-2c9b-4765-8a9c-2a5b3d4c5e6f",
        "name": "Frontend Developer",
        "description": "Pengembang yang berpengalaman dalam membuat UI/UX platform e-learning dengan React.js",
        "requirements": [
          "Pengalaman dengan React.js",
          "Kemampuan desain UI/UX",
          "Pengalaman dengan integrasi API"
        ],
        "budget": 2000000,
        "experience": "intermediate",
        "payment": "fixed",
        "status": "open",
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z"
      },
      {
        "id": "5c2d3b96-3d9c-4876-9b0d-3c4d5e6f7g8h",
        "name": "Backend Developer",
        "description": "Pengembang backend yang berpengalaman dengan Node.js dan MongoDB",
        "requirements": [
          "Pengalaman dengan Node.js",
          "Pengalaman dengan MongoDB",
          "Kemampuan cloud deployment"
        ],
        "budget": 2500000,
        "experience": "expert",
        "payment": "fixed",
        "status": "open",
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z"
      }
    ]
  }
}
```

## 🔄 Improved Workflow

1. **Start Conversation**: Send a message describing your project idea
2. **Answer Questions**: The AI will ask questions to gather missing details
3. **Complete Discussion**: Continue the conversation until you've shared all relevant details
4. **Submit Project**: Use one of the special keywords to finalize your project:
   - `#submit`
   - `#generate`
   - `#selesai`
5. **Receive Project Data**: The system will generate complete project specifications with multiple talents if needed

## 💡 Budget Field Definitions

- **minimum**: Minimum funds needed to start the project
- **total**: Amount of funds already obtained
- **from**: Total funding required for the entire project

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
