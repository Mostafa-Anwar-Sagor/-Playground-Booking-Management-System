# 🏟️ Playground Booking Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0+-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**A comprehensive, modern web application for managing playground bookings with real-time features, multi-role dashboards, and seamless payment integration.**

[Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Playground Booking Management System** is a full-stack web application designed to streamline the process of booking sports playgrounds and facilities. It provides a seamless experience for customers to discover, book, and manage playground reservations while offering powerful tools for playground owners and administrators to manage their businesses.

### Key Highlights

- 🎨 **Modern Dark Theme UI** - Beautiful, responsive design with smooth animations
- 🔐 **Role-Based Access Control** - Separate dashboards for Users, Owners, and Admins
- ⚡ **Real-Time Updates** - Live booking status and availability tracking
- 💳 **Flexible Payment System** - Multiple payment methods with receipt verification
- 📊 **Advanced Analytics** - Comprehensive insights and reporting for business owners
- 📱 **Mobile-First Design** - Fully responsive across all devices

---

## ✨ Features

### 👤 For Customers (Users)
- **Browse & Search** - Explore playgrounds by location, sport type, price, and availability
- **Smart Booking** - Real-time slot availability with instant booking confirmation
- **Booking History** - Track all past and upcoming reservations
- **Profile Management** - Manage personal information and preferences
- **Notifications** - Receive updates on booking status and promotions
- **Reviews & Ratings** - Share experiences and read others' reviews

### 🏢 For Playground Owners
- **Business Dashboard** - Comprehensive overview of revenue, bookings, and performance
- **Playground Management** - Add, edit, and manage multiple playgrounds
- **Booking Requests** - Accept, reject, or manage booking requests
- **Revenue Analytics** - Detailed financial reports and trends
- **Customer Communication** - Built-in messaging system
- **Custom Pricing** - Set different prices for time slots and special days
- **Payment Methods** - Configure bank details, QR codes, and payment options

### 👨‍💼 For Administrators
- **Platform Overview** - Monitor entire platform statistics
- **User Management** - Manage all users, owners, and their access
- **Partner Applications** - Review and approve new playground partners
- **Payment Verification** - Verify payment receipts and manage transactions
- **Playground Oversight** - Activate, deactivate, or manage all playgrounds
- **System Reports** - Generate comprehensive platform reports

### 🔧 Technical Features
- **RESTful APIs** - Clean, well-documented API endpoints
- **JWT Authentication** - Secure token-based authentication
- **Real-Time Updates** - WebSocket support for live notifications
- **Image Optimization** - Automatic image processing and storage
- **Search & Filtering** - Advanced search with multiple filters
- **Export Capabilities** - Export data to CSV/PDF formats

---

## 📸 Screenshots

<div align="center">

### 🏠 Homepage
![Homepage](screenshots/home%20page%20.png)

### 👤 User Dashboard
![User Dashboard](screenshots/user%20dashboard.png)

### 🏢 Owner Dashboard
![Owner Dashboard](screenshots/owner%20dashboard.png)

### 🛡️ Admin Panel
![Admin Panel](screenshots/admin%20panel.png)

### 🔍 Browse Playgrounds
![Browse Playgrounds](screenshots/browse%20playground.png)

### ➕ Register Playground
![Register Playground](screenshots/register%20playground.png)

### ℹ️ About Page
![About Page](screenshots/about.png)

### 👥 User Management
![User Profile](screenshots/user.png)

</div>

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core programming language |
| **Django 4.2+** | Web framework |
| **Django REST Framework** | API development |
| **SQLite/PostgreSQL** | Database |
| **Pillow** | Image processing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | Structure & styling |
| **TailwindCSS** | Utility-first CSS framework |
| **JavaScript (ES6+)** | Interactivity |
| **Font Awesome** | Icons |
| **Chart.js** | Analytics visualizations |

### Tools & Services
| Technology | Purpose |
|------------|---------|
| **Git** | Version control |
| **VS Code** | Development environment |
| **Postman** | API testing |

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Node.js (for TailwindCSS compilation)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mostafa-Anwar-Sagor/-Playground-Booking-Management-System.git
   cd playground_booking_system
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv playground_venv
   playground_venv\Scripts\activate

   # Linux/Mac
   python3 -m venv playground_venv
   source playground_venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - Main Site: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin-panel/`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgres://user:password@localhost:5432/playground_db

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### TailwindCSS Setup (for development)

```bash
cd frontend
npm install
npm run build
```

---

## 📖 Usage

### User Roles & Access

| Role | Default Credentials | Dashboard URL |
|------|---------------------|---------------|
| Admin | admin@playgroundhub.com / Admin@123 | `/admin-panel/` |
| Owner | owner@playgroundhub.com / Owner@123 | `/owner-dashboard/` |
| User | user@playgroundhub.com / User@123 | `/dashboard/` |

### User Flow

1. **Register** → Create an account as a regular user
2. **Browse** → Search and explore available playgrounds
3. **Book** → Select time slots and complete booking
4. **Pay** → Upload payment receipt or pay online
5. **Confirm** → Admin verifies payment, booking confirmed

### Become a Partner (Playground Owner)

1. Navigate to "Become a Partner" page
2. Fill out the partner application form
3. Wait for admin approval
4. Once approved, access Owner Dashboard
5. Add your playgrounds and start receiving bookings

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/logout/` | User logout |
| GET | `/api/auth/profile/` | Get user profile |

### Playground Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/playgrounds/` | List all playgrounds |
| GET | `/api/playgrounds/{id}/` | Get playground details |
| POST | `/api/playgrounds/` | Create playground (Owner) |
| PUT | `/api/playgrounds/{id}/` | Update playground (Owner) |
| DELETE | `/api/playgrounds/{id}/` | Delete playground (Owner) |

### Booking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookings/` | List user bookings |
| POST | `/api/bookings/` | Create new booking |
| GET | `/api/bookings/{id}/` | Get booking details |
| PATCH | `/api/bookings/{id}/cancel/` | Cancel booking |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin-panel/api/stats/` | Platform statistics |
| GET | `/admin-panel/api/users/` | List all users |
| GET | `/admin-panel/api/bookings/` | List all bookings |
| POST | `/admin-panel/api/payments/verify/` | Verify payment |

---

## 📁 Project Structure

```
playground_booking_system/
├── accounts/              # User authentication & profiles
│   ├── models.py         # User model
│   ├── views.py          # Dashboard views
│   ├── urls.py           # URL routing
│   └── dashboard_api.py  # Dashboard APIs
│
├── playgrounds/          # Playground management
│   ├── models.py         # Playground, Sports, Amenities
│   ├── views.py          # Playground views
│   └── urls.py           # URL routing
│
├── bookings/             # Booking management
│   ├── models.py         # Booking model
│   ├── views.py          # Booking views
│   └── checkout_views.py # Payment processing
│
├── adminpanel/           # Admin dashboard
│   ├── views.py          # Admin views
│   └── api_views.py      # Admin APIs
│
├── notifications/        # Notification system
│   ├── models.py         # Notification model
│   └── api_views.py      # Notification APIs
│
├── api/                  # API endpoints
│   ├── urls.py           # API routing
│   └── *.py              # Various API modules
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard/        # Dashboard templates
│   ├── playground/       # Playground templates
│   └── components/       # Reusable components
│
├── static/               # Static files (CSS, JS)
├── media/                # User uploads
├── screenshots/          # Demo screenshots
│
├── manage.py             # Django management
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use meaningful variable/function names
- Write docstrings for functions and classes
- Add comments for complex logic

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mostafa Anwar Sagor**

- GitHub: [@Mostafa-Anwar-Sagor](https://github.com/Mostafa-Anwar-Sagor)

---

## 🙏 Acknowledgments

- Django community for the excellent framework
- TailwindCSS for the utility-first CSS approach
- Font Awesome for the beautiful icons
- All contributors and testers

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by Mostafa Anwar Sagor

</div>
