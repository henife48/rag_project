<img width="1891" height="872" alt="Ekran görüntüsü 2026-08-24 005949" src="https://github.com/user-attachments/assets/2057d7d4-18d1-46df-aecd-75227e8538d6" />

# AI-Powered Academic Study Assistant

[svg](https://github.com/henife48/rag_project#ai-powered-academic-study-assistant)

StudyMate is a **RAG-based academic study assistant** that allows students to upload their course documents, ask questions based on these materials, study with flashcards, and track their study performance.

---

## ✨ Features

[svg](https://github.com/henife48/rag_project#-features)

* 📄 **Document Upload** — Upload PDF, TXT, and Markdown files
* 🤖 **AI Tutor** — Ask questions and get answers based on course content
* 🎴 **Smart Flashcards** — Study with flashcards based on course topics
* 🔄 **Card Rotation** — Retrieve new cards while excluding previously shown cards
* 📊 **Study Tracking** — Track study time, scores, and performance
* 🗂️ **Document Management** — List and delete uploaded course notes
* 🌙 **Study-focused UI** — A simple and modern interface focused on studying

---

## 🧠 How It Works

[svg](https://github.com/henife48/rag_project#-how-it-works)

StudyMate processes uploaded course documents and uses relevant content when answering user questions.

```text
Course Document
      ↓
Text Extraction
      ↓
Text Cleaning
      ↓
Document Storage
      ↓
User Question
      ↓
Relevant Content
      ↓
Answer

```

**svg**

This structure focuses on helping students study using **their own course materials** instead of receiving a generic AI-generated answer.

---

## 🛠️ Tech Stack

[svg](https://github.com/henife48/rag_project#%EF%B8%8F-tech-stack)

* **Python**
* **Flask**
* **SQLite**
* **PyPDF**
* **HTML / CSS / JavaScript**
* **Regex**
* **Git / GitHub**

---

## 📂 Project Structure

[svg](https://github.com/henife48/rag_project#-project-structure)

```text
rag_project/
│
├── app.py
├── requirements.txt
├── studymate.db
│
├── documents/
│   └── course documents
│
└── templates/
    └── index.html

```

**svg**

---

## 🚀 Installation

[svg](https://github.com/henife48/rag_project#-installation)

### 1. Clone the repository

[svg](https://github.com/henife48/rag_project#1-clone-the-repository)

```bash
git clone https://github.com/henife48/rag_project.git
cd rag_project
```

**svg**

### 2. Install dependencies

[svg](https://github.com/henife48/rag_project#2-install-dependencies)

```bash
pip install -r requirements.txt
```

**svg**

### 3. Run the application

[svg](https://github.com/henife48/rag_project#3-run-the-application)

```bash
python app.py
```

**svg**

Then open:

```text
http://127.0.0.1:5000

```

**svg**

---

## 📌 Project Status

[svg](https://github.com/henife48/rag_project#-project-status)

**Completed MVP**

StudyMate is a functional academic study assistant with document management, RAG-based question answering, flashcards, and study tracking.
