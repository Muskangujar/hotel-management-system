# 🏨 Hotel Management System  

A **basic Hotel Management System** built with **Python (Flask), MySQL, HTML, CSS**.  
This project allows hotel staff to manage customers, rooms, and bookings in a simple web interface.  

---

## ✨ Features  

- **Customer Management** – Add, view, and delete customers  
- **Room Management** – Add rooms, set type & price, manage availability  
- **Booking Management** – Assign customers to rooms, check-in & check-out  
- **Automatic Room Status** – Updates to *Occupied* or *Available* based on bookings  
- **Continuous IDs in UI** – Even if database IDs skip, UI shows clean serial numbers  
- **Flask + MySQL** – Backend handles all CRUD operations with a connected database  

---

## 🛠️ Tech Stack  

- **Frontend**: HTML, CSS (Bootstrap for styling)  
- **Backend**: Python (Flask framework)  
- **Database**: MySQL  
- **Tools**: MySQL Workbench, VS Code, Git/GitHub  

---

## 📂 Project Structure  

```
hotel-management/
│
├── app.py               # Flask backend (Python)
├── requirements.txt     # Python dependencies
├── static/              # CSS, JS, images
│   └── style.css
├── templates/           # HTML frontend pages
│   ├── index.html
│   ├── customers.html
│   ├── rooms.html
│   └── bookings.html
└── database/            # SQL scripts
    └── hotel_schema.sql
```

---

## 🚀 Getting Started  

### 1. Clone the repository  
```bash
git clone https://github.com/your-username/hotel-management-system.git
cd hotel-management-system
```

### 2. Set up virtual environment (optional but recommended)  
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Mac/Linux
```

### 3. Install dependencies  
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL Database  
- Open MySQL Workbench  
- Create a new database `hotel_db`  
- Run the script inside `database/hotel_schema.sql`  

### 5. Run the Flask App  
```bash
python app.py
```
Then open `http://127.0.0.1:5000/` in your browser.  

---

## 🚧 Future Enhancements  
- Add **search & filter** for customers and bookings  
- Room types with images and descriptions  
- User authentication (admin/staff login)  
- AI-based **room recommendation system** for customers  

---
