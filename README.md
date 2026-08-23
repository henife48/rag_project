<img width="1891" height="872" alt="Ekran görüntüsü 2026-08-24 005949" src="https://github.com/user-attachments/assets/eaf09355-81f9-4932-b497-2c58bba94de2" />
# 📚 StudyMate

### AI-Powered Academic Study Assistant

StudyMate, öğrencilerin ders dokümanlarını yükleyerek bu içerikler üzerinden soru sorabildiği, flashcard'larla çalışabildiği ve çalışma performansını takip edebildiği **RAG tabanlı bir akademik çalışma asistanıdır.**

---

## ✨ Features

* 📄 **Document Upload** — PDF, TXT ve Markdown dosyalarını yükleme
* 🤖 **AI Tutor** — Ders içerikleri üzerinden soru-cevap
* 🎴 **Smart Flashcards** — Ders konularına göre flashcard ile çalışma
* 🔄 **Card Rotation** — Daha önce gösterilen kartları hariç tutarak yeni kartlar getirme
* 📊 **Study Tracking** — Çalışma süresi, skor ve performans takibi
* 🗂️ **Document Management** — Yüklenen ders notlarını listeleme ve silme
* 🌙 **Study-focused UI** — Çalışmaya odaklanan sade ve modern arayüz

---

## 🧠 How It Works

StudyMate, yüklenen ders dokümanlarını işleyerek kullanıcı sorularında ilgili içeriği kullanır.

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

Bu yapı, öğrencinin genel bir AI cevabı yerine **kendi ders materyalleri üzerinden çalışmasına** odaklanır.

---

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **SQLite**
* **PyPDF**
* **HTML / CSS / JavaScript**
* **Regex**
* **Git / GitHub**

---

## 📂 Project Structure

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

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/henife48/rag_project.git
cd rag_project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 📌 Project Status

**Completed MVP**

StudyMate is a functional academic study assistant with document management, RAG-based question answering, flashcards, and study tracking.

