<div align="center">

# KanMind - Kanban Board API

*A comprehensive, high-performance REST API for a Kanban board application, built with Django and Django REST Framework*

<br>

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg?style=for-the-badge)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red.svg?style=for-the-badge)](https://www.django-rest-framework.org/)

</div>

---

## Overview

KanMind allows users to create project boards, manage tasks, assign reviewers, and collaborate seamlessly through comments. Designed with performance and security in mind.

## Features

- **User Authentication:** Secure access to all endpoints via token authentication
- **Board Management:** Create, update, view, and delete project boards with dynamic member control
- **Task Management:** Full CRUD operations for tasks featuring multiple statuses (`to-do`, `in-progress`, `review`, `done`) and priorities (`low`, `medium`, `high`)
- **Advanced Assignments:** Assign tasks to specific members, request reviews, and filter via specialized endpoints (`assigned-to-me`, `reviewing`)
- **Commenting System:** Collaborate on tasks with a chronologically ordered commenting system
- **High Performance:** Heavily optimized database queries utilizing `annotate()`, `Count()`, and `select_related()` to eliminate N+1 query problems

## Technologies Used

- **Language:** Python 3.12+
- **Framework:** Django & Django REST Framework (DRF)
- **Database:** SQLite (Default, easily configurable)

## Project Structure

```text
KanMind/
│
├── core/                  # Centralized Django settings and main URL routing
├── kanmind_app/           # Domain logic application
│   └── api/               # API layer (views.py, serializers.py, urls.py, permissions.py)
└── requirements.txt       # Project dependencies
```

## Installation & Setup

> **Note:** On macOS and Linux, you may need to use `python3` and `pip3` instead of `python` and `pip`.

### 1. Clone the repository
```bash
git clone https://github.com/nico-leitz/KanMind.git
cd KanMind
```

### 2. Create and activate a virtual environment
- **Windows (Command Prompt / PowerShell):**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
*(Make sure `(.venv)` appears at the beginning of your terminal line)*

### 3. Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Generate a secure Secret Key
Create your local `.env` configuration file automatically:
```bash
python -c "from django.core.management.utils import get_random_secret_key as k; open('.env', 'w').write('SECRET_KEY=' + chr(39) + k() + chr(39) + chr(10))"
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver
```
The API is now running locally at `http://127.0.0.1:8000/api/`. Keep this terminal window open!

---

## Core API Endpoints

*All endpoints require authentication.*

### Boards
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/boards/` | List all boards the user owns or is a member of |
| `POST` | `/api/boards/` | Create a new board |
| `GET` | `/api/boards/{id}/` | Retrieve a specific board with all its tasks |
| `PATCH` | `/api/boards/{id}/` | Update board members or title |
| `DELETE` | `/api/boards/{id}/` | Delete a board (Owner only) |

### Tasks
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/tasks/` | Create a new task within a board |
| `PATCH` | `/api/tasks/{id}/` | Update task details or status |
| `DELETE` | `/api/tasks/{id}/` | Delete a task |
| `GET` | `/api/tasks/assigned-to-me/` | List all tasks assigned to the current user |
| `GET` | `/api/tasks/reviewing/` | List all tasks the current user is reviewing |

### Comments & Utilities
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/tasks/{task_id}/comments/` | List all comments for a task |
| `POST` | `/api/tasks/{task_id}/comments/` | Add a comment to a task |
| `DELETE` | `/api/tasks/{task_id}/comments/{comment_id}/` | Delete a specific comment (Author only) |
| `GET` | `/api/email-check/?email=...` | Check if a user exists by their email address |

---
