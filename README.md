# 🤖 FAQ Chatbot using Flask & NLP

## 📌 Project Overview

This project is an AI-powered FAQ Chatbot built using **Python, Flask, and Natural Language Processing (NLTK)**.
It automatically matches user questions with the most relevant FAQ and returns accurate responses using similarity-based matching techniques.

This project was developed as part of the **CodeAlpha Artificial Intelligence Internship (Task 2: Chatbot for FAQs)**.

---

## 🚀 Features

* AI-based FAQ chatbot
* NLP-based text preprocessing (tokenization, cleaning)
* Similarity matching using FAQ engine
* Flask-based web application
* REST API endpoints for chatbot interaction
* Interactive chat UI (HTML/CSS/JS)

---

## 🛠️ Tech Stack

* Python
* Flask
* NLTK (Natural Language Processing)
* HTML, CSS, JavaScript
* Git & GitHub

---

## 📂 Project Structure

```
faq_chatbot/
│
├── app.py
├── nlp/
│   ├── similarity_engine.py
│   └── nlp_processor.py
├── templates/
│   └── index.html
├── static/
│   └── (CSS/JS files)
```

---

## ⚙️ How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CodeAlpha_Chatbot_faq.git
cd CodeAlpha_Chatbot_faq
```

### 2. Install dependencies

```bash
pip install flask nltk
```

### 3. Run the application

```bash
python app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000
```

---

## 📡 API Endpoints

### 🔹 Chat API

`POST /api/chat`

Request:

```json
{
  "message": "What is your return policy?"
}
```

Response:

```json
{
  "answer": "Our return policy is ...",
  "confidence": 0.85
}
```

### 🔹 FAQ List

`GET /api/faqs`

### 🔹 Health Check

`GET /api/health`

---

## 🎯 Internship Task

This project fulfills:

✔ Task 2: Chatbot for FAQs (CodeAlpha Internship)
✔ NLP preprocessing using NLTK
✔ Similarity-based intent matching
✔ Flask web application with API support

---

## 📈 Future Improvements

* Add AI/ML model for better intent detection
* Integrate database (MySQL / MongoDB)
* Improve UI design
* Deploy on cloud (Render / Heroku)

---
## 🖼️ Project Screenshots

<p align="center">
  <img src="static/images/chatbot1.png" width="400"/>
  <img src="static/images/chatbot2.png" width="400"/>
</p>
## 👩‍💻 Author

**Saba Ashraf**
AI & Python Developer | Student at IBIT
GitHub: https://github.com/sabaashraf27

---

## ⭐ Acknowledgment

Special thanks to **CodeAlpha** for providing this AI Internship opportunity.


## 🖼️ Project Screenshots

### Chatbot UI 1
![Chatbot UI 1](static/images/chatbot1.png)

### Chatbot UI 2
![Chatbot UI 2](static/images/chatbot2.png)
