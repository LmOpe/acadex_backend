# 🎓 Acadex – Academic Quiz & Assessment Backend

**Acadex** is a backend API for a web-based academic quiz and assessment platform. It is built using **Django**, **Django REST Framework (DRF)**, and **PostgreSQL**, providing a secure, scalable, and modular backend for managing users, courses, quizzes, scheduling, results, and reporting—ideal for schools, universities, or independent educators.

---

## 🚀 Features

- **Role-Based Access Control** (Student, Lecturer, Admin)
- **Course Management** – Lecturers can create courses that students can join
- **Quiz Creation & Scheduling** – Quizzes are tied to courses with time-based access
- **Real-Time Results** – Students get immediate feedback after submission
- **Performance Analytics** – Automatic result aggregation per student and course
- **No Academic Session Dependency** – Fully flexible and reusable course structure
- **Secure API** with token-based authentication (JWT or DRF Tokens)

---

## 🛠️ Tech Stack

- **Language:** Python
- **Framework:** Django
- **API:** Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT(via `djangorestframework-simplejwt`)
- **Other Libraries:** Django CORS Headers, Django Environ, etc.

---

## 📁 Project Structure

```bash
acadex/
│
├── acadex/               # Core project config
├── accounts/             # User authentication & role management
├── courses/              # Course and registration models
├── quizzes/              # Quiz, Question, Answer, Schedule logic
├── results/              # Student attempts, results, and analytics
├── manage.py
└── requirements.txt
````

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/LmOpe/acadex.git
cd acadex
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the root of the project and add:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/acadex_db
```

> Requires `django-environ` or similar if using `.env` loading

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```
---

## 📡 API Endpoints Overview

| Endpoint                  | Method | Role     | Description                        |
| ------------------------- | ------ | -------- | ---------------------------------- |
| `/api/auth/register/`     | POST   | All      | Register as a user
| `/api/auth/login/`        | POST   | All      | Login and get access token         |
| `/api/courses/`           | GET    | Student  | View available courses             |
| `/api/courses/`           | POST   | Lecturer | Create a course                    |
| `/api/courses/register/`  | POST   | Student  | Register for a course              |
| `/api/quizzes/`           | POST   | Lecturer | Create quiz with schedule          |
| `/api/quizzes/<id>/take/` | POST   | Student  | Submit quiz answers                |
| `/api/results/`           | GET    | Student  | View own quiz results              |
| `/api/results/aggregate/` | GET    | Lecturer | View aggregated course performance |

> More detailed documentation available via Swagger UI

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request.

---

## 📬 Contact

For inquiries or collaborations:

* 📧 Email: [lawalmuhammedope@gmail.com](mailto:lawalmuhammedope@gmail.com)
* 🌐 GitHub: [LmOpe](https://github.com/LmOpe)
