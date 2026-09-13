# Hospital Pharmacy Management System

A web-based **Hospital Pharmacy Management System** developed using **Flask and MySQL** to manage medicines, billing, pharmacy users, and activity records through a simple and organized interface.

##  Project Preview

 **[Click here to view the project repository](https://github.com/gayathri-manoj/hospital-pharmacy-management-system)**

> This project is currently available as source code and can be run locally by following the setup instructions below. A live deployment and downloadable executable are not currently available.

---

##  About the Project

The Hospital Pharmacy Management System is designed to simplify common pharmacy operations such as medicine inventory management, billing, user authentication, and activity tracking.

The application provides separate access levels for managers and staff members, allowing pharmacy activities to be managed through a centralized system connected to a MySQL database.

---

##  Features

###  User Authentication

* Login system for pharmacy users
* Role-based access for:

  * Manager
  * Staff
* Secure configuration using environment variables

###  Medicine Management

* Add new medicines
* View available medicines
* Track medicine quantity
* Store medicine expiry dates
* Manage medicine prices
* Delete medicine records when required

###  Billing System

* Create customer bills
* Add multiple medicines to a bill
* Calculate item subtotals
* Calculate total bill amount
* Store bill details in the database
* View and print billing information

###  Manager Dashboard

* View pharmacy summary information
* Monitor medicine inventory
* View billing-related information
* Access pharmacy activity records

###  Activity Tracking

* Record important pharmacy activities
* Store username and action details
* Track activity timestamps

---

##  Technologies Used

| Technology               | Usage                           |
| ------------------------ | ------------------------------- |
| Python                   | Backend development             |
| Flask                    | Web application framework       |
| MySQL                    | Database management             |
| HTML5                    | Frontend structure              |
| CSS3                     | User interface styling          |
| Jinja2                   | Dynamic HTML rendering          |
| `mysql-connector-python` | MySQL connectivity              |
| `python-dotenv`          | Environment variable management |

---

##  Project Structure

```text
hospital-pharmacy-management-system/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── run commands.txt
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── medicines.html
│   ├── billing.html
│   └── ...
│
├── instance/
│
└── venv/                  # Local virtual environment - not uploaded
```

> The `venv/` folder is used only for local development and should not be uploaded to GitHub.

---

##⚙️ Installation and Setup

### 1. Clone the Repository

Open PowerShell or a terminal and run:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/hospital-pharmacy-management-system.git
```

Move into the project directory:

```bash
cd hospital-pharmacy-management-system
```

---

### 2. Create a Virtual Environment

For Windows:

```powershell
py -m venv venv
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

---

### 3. Install Required Packages

Install the dependencies from `requirements.txt`:

```powershell
py -m pip install -r requirements.txt
```

---

### 4. Create the MySQL Database

Open MySQL and create the database:

```sql
CREATE DATABASE pharmacy_db;
```

The application will create the required tables when it starts.

---

### 5. Configure Environment Variables

Create a file named `.env` in the root project folder.

Copy the example environment file:

```powershell
copy .env.example .env
```

Open `.env` and enter your local configuration:

```env
FLASK_SECRET_KEY=replace_with_your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=pharmacy_db

FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

> **Security Notice:** Never upload your actual `.env` file to GitHub. It may contain database passwords and secret keys.

---

### 6. Run the Application

Start the Flask application:

```powershell
py app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

##  Demo User Roles

The application includes role-based user access.

| Role    | Access                                                            |
| ------- | ----------------------------------------------------------------- |
| Manager | Dashboard, inventory, billing, summaries, and management features |
| Staff   | Pharmacy operations and billing-related features                  |

> If demo users are created during database initialization, use the credentials configured in your local application. Change default passwords before using the system in a real environment.

---

##  Database Tables

The application uses MySQL to store the following information:

* `users` — stores login and role information
* `medicines` — stores medicine inventory details
* `activity_log` — stores user activity records
* `bills` — stores customer bill information
* `bill_items` — stores medicines included in each bill

The database itself is not included in this repository.

---

##  Security Considerations

* Database credentials are stored in `.env`.
* `.env` is excluded from Git using `.gitignore`.
* `.env.example` contains placeholder values only.
* Do not upload real patient, customer, or hospital data.
* Do not commit database passwords or secret keys.
* Change default login credentials before real-world use.
* For production deployment, user passwords should be stored using secure password hashing.
* Use a strong random Flask secret key for deployment.

---

##  Current Status

| Component                  | Status                  |
| -------------------------- | ----------------------- |
| Flask backend              | Completed               |
| MySQL database integration | Completed               |
| User login system          | Completed               |
| Medicine management        | Completed               |
| Billing system             | Completed               |
| Activity logging           | Completed               |
| Local execution            | Available               |
| Live deployment            | Not currently available |
| Downloadable `.exe`        | Not currently available |

---

##  Future Improvements

* Password hashing and stronger authentication
* Medicine search and filtering
* Low-stock medicine alerts
* Expiry-date notifications
* PDF invoice generation
* Excel report export
* Advanced manager analytics
* User and role management
* Automated database backups
* Cloud deployment
* Improved validation and error handling
* Responsive design improvements

---

##  License

This project is developed for educational and demonstration purposes.

---

##  Author

**Gayathri Manoj**

GitHub: [gayathri-manoj](https://github.com/gayathri-manoj)

---
