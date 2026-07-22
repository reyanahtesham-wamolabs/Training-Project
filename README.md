# Smart Task Platform

A full-stack collaborative project and task management application built with **FastAPI**, **SQLAlchemy (Async)**, **Alembic**, and **React 19 (Vite)** with a custom **Glassmorphism UI** design system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Database Migrations](#database-migrations)
- [API Overview](#api-overview)
- [License](#license)

---

## 🚀 Overview

This platform empowers teams to manage projects, organize tasks, assign team roles, track activity logs, and communicate in real time via team chat. It features role-based access control (RBAC), fine-grained privacy settings, task dependency tracking, and interactive task boards.

---

## ✨ Key Features

### 📁 Project Management
- **Workspaces & Categories**: Create and organize projects across categories (e.g., In-House, Upwork, US-Based, Pak Profile).
- **Tagging & Filtering**: Assign custom tags to projects for easy filtering and organization.
- **Archive System**: Archive and unarchive completed or inactive projects with audit logging.

### 📋 Task Tracking & Board
- **Schedule & Due Dates**: Track task start schedules and due dates cleanly across project detail and global board views.
- **Priority & Status Management**: Categorize tasks by priority (`high`, `medium`, `low`) and status (`todo`, `in_progress`, `done`).
- **Prerequisites & Dependencies**: Define task dependencies to enforce proper workflow completion.
- **User Assignments**: Assign and unassign team members to tasks with role-based permission checks.

### 👥 Team Management & Single Source of Truth Roles
- **Team Membership**: Add and remove members from project team workspaces.
- **Project Roles**: Manage per-project roles (`Project Admin` vs `Project Member`) directly during team member addition.
- **Role Hierarchy**: Comprehensive permission management across Overall Admins, Managers, Project Admins, and Members.

### 💬 Real-Time Collaboration & Auditing
- **WebSockets Team Chat**: Instant, real-time messaging within project team rooms.
- **Task Comments & Replies**: Threaded discussions on individual tasks.
- **Audit Logs**: Activity logging for key actions (project edits, archiving, task updates).
- **Notification System**: User notifications for task assignments and team updates.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (AsyncIO with `asyncpg` / `aiosqlite`)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Real-Time**: WebSockets
- **Server**: [Uvicorn](https://www.uvicorn.org/)

### Frontend
- **Framework**: [React 19](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: Vanilla CSS with Custom CSS Variables & Glassmorphism Design System
- **Icons & Typography**: Google Fonts (*Inter* & *Outfit*)

---

## 📂 Project Architecture

```text
Project/
├── backend/
│   ├── alembic/              # Database migration scripts & versions
│   ├── dependencies/         # FastAPI dependencies (auth, DB session)
│   ├── helper_functions/     # Utility functions & validators
│   ├── models/               # Pydantic request/response schemas
│   ├── repository/           # Database CRUD operations
│   ├── router/               # API route endpoints
│   ├── schema/               # SQLAlchemy ORM models & enums
│   ├── services/             # Business logic layer
│   ├── app.py                # FastAPI application entrypoint
│   └── alembic.ini           # Alembic configuration
├── frontend/
│   ├── src/
│   │   ├── components/       # React UI components & modals
│   │   ├── services/         # API integration layer
│   │   ├── App.jsx           # Main application state & routing
│   │   └── index.css         # Custom Glassmorphism design tokens & styles
│   ├── package.json          # Frontend dependencies & scripts
│   └── vite.config.js        # Vite build configuration
├── requirements.txt          # Python backend dependencies
└── README.md                 # Project documentation
```

---

## 🏁 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Python**: `3.10+`
- **Node.js**: `18.0+`
- **npm**: `9.0+`

---

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables**:
   Ensure `.env` exists in the `backend/` directory with your database connection configuration:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./sql_app.db
   SECRET_KEY=your_secret_key_here
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   The web app will run locally at [http://localhost:5173](http://localhost:5173).

4. **Build for production**:
   ```bash
   npm run build
   ```

---

## 🗄️ Database Migrations

Database schema changes are managed via Alembic:

- **Create a new migration**:
  ```bash
  cd backend
  alembic revision -m "description_of_changes"
  ```
- **Apply migrations**:
  ```bash
  cd backend
  alembic upgrade head
  ```
- **Rollback last migration**:
  ```bash
  cd backend
  alembic downgrade -1
  ```

---

## 🔌 API Overview

| Router | Base Path | Description |
| :--- | :--- | :--- |
| **Authentication** | `/Auth` | User register, login, profile management, privacy settings |
| **Project** | `/project` | Create, update, list, and archive projects |
| **Task** | `/task` | Task CRUD, prerequisite linking, schedule/due dates |
| **User** | `/User` | User management, status toggles, task assignments |
| **Team** | `/Team` | Team creation, member additions with roles, real-time chat WS |
| **Comment** | `/comment` | Threaded task comments and replies |
| **Activity** | `/activity` | System activity and audit log retrieval |
| **Notification** | `/Notification` | User notification status and updates |

---

## 📄 License

This project is licensed under the MIT License.
