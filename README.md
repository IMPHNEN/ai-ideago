# <div align="center">🚀 IdeaGO Chat API</div>

<div align="center">
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKAr6zsTg5fu18DZgFK9t0XaMTIujwXTZmkQ&s" alt="Project Chat API Logo" width="300">
  <p><em>Intelligent project definition through conversation</em></p>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Groq-FF5A00?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/LangChain-00A3E0?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain">
</div>

## 📋 Overview

Project Chat API is an intelligent assistant that helps business creators define their projects and talent requirements through natural conversation. The system uses advanced AI to gather project details, ask relevant questions, and generate comprehensive project specifications.

### 🌟 Key Features

- **Conversational Interface**: Engage in natural dialogue to define your project
- **Intelligent Data Generation**: AI generates complete project details based on conversation
- **Persistent Memory**: Conversation history is maintained for context
- **Multilingual Support**: Primary support for Indonesian language
- **Schema Validation**: Ensures all project data follows required format
- **Asynchronous Processing**: Fast, non-blocking API responses

## 🛠️ Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **Groq LLM**: Powerful language model for natural conversation
- **SQLite**: Lightweight database for persistent storage
- **LangChain**: Framework for building LLM applications
- **Pydantic**: Data validation and settings management

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-chat-api.git
cd project-chat-api
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

4. Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
GROQ_MODEL_NAME=mixtral-8x7b-32768
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
        "total": 5000000,
        "from": 2000000
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
    "talent": {
      "id": "4b1c2a85-2c9b-4765-8a9c-2a5b3d4c5e6f",
      "name": "Desainer dan Pengembang Platform E-Learning",
      "description": "Desainer dan pengembang yang berpengalaman dalam membuat platform e-learning yang interaktif dan menarik.",
      "requirements": [
        "Pengalaman dengan React.js",
        "Pengalaman dengan Node.js",
        "Pengalaman dengan MongoDB",
        "Pengalaman dengan layanan cloud seperti AWS atau Google Cloud"
      ],
      "budget": 3000000,
      "experience": "intermediate",
      "payment": "fixed",
      "status": "open",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-01-01T00:00:00.000Z"
    }
  }
}
```

## 🔄 Workflow

1. **Start Conversation**: Send a message describing your project idea
2. **Answer Questions**: The AI will ask questions to gather missing details
3. **Confirm Details**: When satisfied, respond with "oke" or "ok"
4. **Receive Project Data**: The system will generate complete project specifications

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
