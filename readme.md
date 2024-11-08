# Finance Management System - Backend

This repository contains the backend for the **Finance Management System**, an admin-focused application for tracking and managing financial records and expenses. The backend is responsible for handling data storage, financial record processing, and providing endpoints for data visualization on the frontend.

---

## Features

- **Finance Record Management**: Supports creating, updating, and deleting financial records, including saving invoice images.
- **Expense Analytics**:
  - Provides data on expenses for the current and previous years and quarters.
  - Retrieves latest expenses and expense categories for frontend dashboard visualization.
- **Data Export**:
  - Enables exporting individual or all expense records for reporting.

---

## Getting Started

Follow these instructions to set up and run the backend application locally.

### Prerequisites

- Python 3.8+
- FastAPI
- SQLAlchemy (for database management)
- Pillow (for handling image uploads)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/uzair02/codeaza_backend-FastAPI.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd codeaza_backend
   ```
3. **Set up a virtual environment**:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows use `env\Scripts\activate`
   ```
4. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Add environment variables**: Create a `.env` file in the root directory with the necessary environment variables (e.g., database URL).

---

## Environment Variables

Your `.env` file should include:

```
DATABASE_URL=your_database_url
# Add any additional environment variables here
```

---

## Running the Backend

To start the backend server:

1. **Navigate to the project directory**:
   ```bash
   cd backend
   ```
2. **Run the backend application**:
   ```bash
   uvicorn src.main:backend_app --reload
   ```

The backend will be accessible at `http://127.0.0.1:8000`.

---

**Project developed by Chemsa Technologies**

## Technologies Used

- **FastAPI**: For building APIs
- **SQLAlchemy**: ORM for database management
- **Pillow**: For image handling
- **Uvicorn**: ASGI server to run FastAPI applications
