# 📚 Academic Thesis & Paper Submission System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)](https://www.sqlalchemy.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg?style=for-the-badge)](LICENSE)

## License

Copyright © 2026 Umar Ajmal. All Rights Reserved.

This source code is publicly available for viewing and educational
reference purposes only.

No permission is granted to copy, reproduce, modify, distribute,
publish, sublicense, sell, or use this code or substantial portions
of this code for commercial or production purposes without prior
written permission from the copyright holder.

For commercial use, redistribution, modification, or any other use
beyond viewing and learning, please contact the copyright holder
for written permission.

---

A web-based **Academic Paper & Thesis Submission and Peer-Review Management System** designed for universities, research symposiums, journals, and academic institutions. The platform facilitates end-to-end peer-review workflows connecting **Authors**, **Expert Reviewers**, and **System Administrators**.

---

## 🌟 Key Capabilities & Highlights

- 📝 **Author Submission Portal**: Submit research papers and theses with metadata (Title, Abstract, Keywords, Paper Type) and secure document upload (PDF / DOCX up to 16MB).
- 🔍 **Peer-Review Assignment Engine**: Administrators assign papers to registered expert reviewers while enforcing maximum concurrent review limits (`max_papers`).
- ⚖️ **Structured Review Evaluation**: Reviewers evaluate manuscripts with decisions (`Accepted`, `Rejected`, `Accept with Revision`), detailed critique reports, and structured rejection rationales.
- 🔐 **Role-Based Access Control**: Dedicated panels for `Admin`, `Author`, and `Reviewer` with session security powered by Flask-Login.
- 📧 **Token-Based Password Reset**: Secure email password recovery mechanism via Flask-Mail with time-limited JWT/itsdangerous tokens.
- 📁 **Secure Document Handler**: Filename sanitization via Werkzeug `secure_filename` with timestamp prefixing to prevent collisions and directory traversal vulnerabilities.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Flask | Lightweight Python WSGI web application framework |
| **Database ORM** | Flask-SQLAlchemy | Relational object-relational mapping (SQLite / MySQL) |
| **Authentication** | Flask-Login | User session management and protected route handlers |
| **Forms & Validation** | Flask-WTF / WTForms | Form rendering, CSRF protection, and field validation |
| **Email Service** | Flask-Mail | SMTP integration for password reset notifications |
| **Security & Hashing** | Werkzeug | Secure password hashing (pbkdf2 / sha256) |
| **File Management** | Werkzeug Utilities | Secure file uploads, MIME type checks, and file streaming |

---

## 👥 User Roles & Access Architecture

| Role | Accessible Views | Primary Responsibilities |
| :--- | :--- | :--- |
| 👑 **Administrator** | `/admin_panel`, `/manage_submissions`, `/check_users` | Oversee all submissions, manage reviewer workloads, assign papers |
| ✍️ **Author** | `/author_panel`, `/submit_thesis`, `/check_status` | Submit new papers/theses, monitor review status, download submissions |
| 🔬 **Reviewer** | `/reviewer_panel`, `/submit_review/<id>` | Access assigned manuscripts, evaluate content, submit formal review reports |

---

## 🧩 Core Modules & Workflows

### 1. Authentication & Profile Management
- Separate registration flows for Authors and Reviewers
- Reviewer profile setup with academic qualification, specialization, and paper workload capacity (`max_papers`)
- Email password reset workflow with encrypted token verification

### 2. Thesis & Paper Submission Workflow
- Upload validation: restricted to `.pdf` and `.docx` formats (16MB maximum payload)
- Metadata capture: Title, Abstract, Keywords (up to 5 tags), Paper Type
- Automated status progression: `Submitted` ➔ `Under Review` ➔ `Accepted` / `Rejected` / `Accepted with Revision`

### 3. Review Assignment & Workload Management
- Administrative inspection of all uploaded papers and available reviewers
- Automated workload ceiling check preventing assignment if reviewer has reached `max_papers` limit
- Duplicate assignment prevention

### 4. Evaluation & Review Submission
- Dedicated review submission form with decision toggle
- Mandatory rejection reason logging when recommending rejection or revisions
- Automatic paper status update and review timestamping upon submission

---

## 📁 Repository Directory Structure

```text
Thesis-Submission-System/
├── app/
│   ├── __init__.py          🚀 Flask application factory & extension setup
│   ├── config.py            ⚙️ Configuration settings & upload paths
│   ├── decorators.py        🔒 Role-based access control decorators
│   ├── forms.py             📝 WTForms definitions & validation rules
│   ├── models.py            🗄️ SQLAlchemy database models
│   ├── routes.py            🔌 Blueprint route handlers & controllers
│   ├── static/              🎨 CSS styles, JavaScript, and upload directory
│   └── templates/           🌐 Jinja2 HTML templates
├── create_admin.py          👑 CLI utility to seed administrator accounts
├── requirements.txt         📦 Python package dependencies
├── run.py                   🚀 Application startup entrypoint
├── setup.sh                 ⚙️ Environment initialization script
├── LICENSE                  📄 Proprietary License
└── README.md                📖 Documentation
```

---

## 📄 License & Ownership

Developed and owned by **Muhammad Umar Ajmal**.  
Repository: [https://github.com/UmarAjmal/Thesis-Submission-System.git](https://github.com/UmarAjmal/Thesis-Submission-System.git)

**Copyright © 2026 Umar Ajmal. All Rights Reserved.**  
This source code is proprietary and confidential. Strictly for viewing and educational evaluation. For commercial licensing, institutional deployment, or customization inquiries, please contact the author. Refer to the [LICENSE](LICENSE) file for full legal terms.
