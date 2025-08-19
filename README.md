# 💰 Nawin Asokan - Budget Planner App

The **Budget Planner App** is a Django-based web application designed to help users manage their income and expenses effectively.  
It provides a **dashboard view, transaction tracking, and user management system** with authentication and role-based access.

---

## 🚀 Features

- **User Authentication**
  - Register, login, and logout functionality.
  - Role-based access for admin and users.

- **Dashboard**
  - Overview of income, expenses, and balance.

- **Transactions**
  - Add, edit, and delete transactions.
  - Categorize income and expenses.
  - View transaction history.

- **User Management**
  - Admin can manage registered users.
  - User-friendly forms with Django templates.

- **Responsive UI**
  - Reusable `navbar` and `sidebar`.
  - Mobile and desktop friendly.

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap, Django Templates
- **Database:** SQLite (default, can be switched to PostgreSQL/MySQL)
- **Forms & Validation:** Django Forms
- **Authentication:** Django’s built-in auth system

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/nawinasokan-budget_app.git
cd nawinasokan-budget_app
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🐳 Run with Docker (Optional)

You can also run this project inside Docker.

### 1. Build Docker Image

```bash
docker build -t budget_app .
```

### 2. Run Container

```bash
docker run -d -p 8000:8000 --name budget_app_container budget_app
```

### 3. Restart Container

```bash
docker restart budget_app_container
```

---

## ✅ Testing

To run tests:

```bash
python manage.py test
```

---

## 📬 Contact

- **Name:** Nawin Asokan  
- **Role:** Full Stack Python Developer  
- **Email:** [nawinasokan16@gmail.com]  
- **GitHub:** [https://github.com/nawinasokan] 
- **LinkedIn:** [https://linkedin.com/in/naiwn-a-dev]  

## 🌐 Live Url
**Visit the Website:** [https://budget-app-ddms.onrender.com/]