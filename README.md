# 🎓 Kyubee Project

**Kyubee** is an educational platform designed to revolutionize how students and educators interact with academic content. It not only serves as a **repository for course questions and notes** but also introduces intelligent **question extraction** and **tagging mechanisms** to enhance learning and revision.

---

## 🧠 Why Kyubee?

Traditional note-reading is often passive and inefficient. Kyubee changes that by:

* **Extracting questions** directly from uploaded notes.
* Allowing users to **tag questions** by topic, difficulty, chapter, etc.
* Encouraging **active recall** and **self-quizzing** — proven methods for effective studying.
* Helping students **sort and filter** questions for targeted revision.

---

## 🌟 Core Features

✅ **Automatic Question Extraction**
Upload notes and let Kyubee intelligently identify potential questions from the content.

🏷️ **Custom Tags for Each Question**
Add and use tags like `#MCQ`, `#Unit1`, `#HighPriority`, `#Exam2024` to organize and retrieve questions quickly.

📁 **Centralized Repository**
Browse and contribute questions and notes across multiple subjects and courses.

📚 **Collaborative Notes Sharing**
Both educators and students can upload notes that benefit the whole community.

🔍 **Course-Based Filtering**
Quickly find relevant questions or notes using filters for course name, topic, or tags.

---

## 🛠 Tech Stack

| Area         | Tech                                    |
| ------------ | --------------------------------------- |
| **Frontend** | HTML, SCSS, Tailwind CSS                |
| **Backend**  | Python (Flask)                          |
| **Extras**   | Node.js, Custom Python Processing Tools |

---

## 🚀 Getting Started

### 1. Clone the Project

```bash
git clone https://github.com/nm2re/kyubee_project.git
cd kyubee_project
```

### 2. Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
python app.py
```

Now visit `http://localhost:5000` in your browser.

---

## 📁 Project Structure

```
kyubee_project/
├── app.py                 # Main application entry point
├── zfile_processing/      # File/question processing scripts
├── static/                # CSS, JS, and media files
├── templates/             # HTML templates (Jinja2)
├── instance/, migrations/ # App configuration and DB support
├── test.py, tt.py, gen.py # Supporting scripts
├── tailwind.config.js     # Tailwind CSS setup
├── requirements.txt       # Python packages
└── README.md              # This file!
```
