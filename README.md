# PharmaShelf

PharmaShelf is a modern web application for managing pharmacy drug information, stock levels, and medication safety in a clean and predictable way. It is designed for internal use by pharmacies, clinics, and healthcare teams who need a simple but reliable system to keep their formulary organized.

With PharmaShelf, pharmacists and admins can:

- Maintain a centralized catalog of drugs with categories, active ingredients, and dosage forms
- Track stock levels and quickly see which items are in stock, out of stock, or running low
- Define alternative drugs to support therapeutic substitution and continuity of care
- Record and check drug–drug interactions to reduce the risk of unsafe combinations
- Manage users with role-based access control and clear separation between admins and pharmacists
- Monitor the overall status of the system through a dashboard with key pharmacy metrics

The goal of PharmaShelf is to provide a focused, easy-to-use tool that covers the core workflows of a small to medium pharmacy without the complexity of a full hospital information system.

---

## Features

### Authentication & Users

- Custom `User` model
- Fields:
  - `name`
  - `email`
  - `password_hash` (bcrypt)
  - `role` (`"admin"` or `"pharmacist"`)
  - `is_active` (boolean)
- Passwords stored using bcrypt hashing
- Only active users can log in
- New registrations are created as `pharmacist` by default
- Roles:
  - **admin**
    - Manage drugs (add, edit, update stock)
    - Manage categories
    - Manage users (change role, enable/disable)
    - Manage drug interactions
  - **pharmacist**
    - View/search drugs
    - View drug details and alternatives
    - Use interaction checker

---

### Drugs & Catalog

- Drugs Catalog page:
  - Search by name (`q` query parameter)
  - Filter by category
  - Checkbox “In stock only” (filters to `stock_quantity > 0`)
  - Manual pagination (page size 10) using Django queryset slicing
- Drug details page:
  - Category, active ingredient, dosage form
  - Stock badge:
    - **In Stock (N)** when `stock_quantity > 0`
    - **Out of Stock** when `stock_quantity == 0`
  - Admin-only: update stock quantity directly from details page
  - “Created by” and “Created at” metadata

---

### Alternatives & Interactions

- **Alternatives**
  - `DrugAlternative` model links a drug to its alternative drugs
  - Alternatives listed in the drug details page
  - Each alternative shows:
    - Category
    - Stock status with badges
    - Optional note


- **Drug–Drug Interactions**
  - `DrugInteraction` model holds interactions between two drugs
  - Interaction checker page:
    - Select two drugs and check whether an interaction is defined
  - Admin-only:
    - Add new interactions

---

### User Management

Admin-only User Management page:

- List all users with:
  - Name
  - Email
  - Role (`admin` / `pharmacist`)
  - Status (Active / Disabled)
- Change user role via dropdown
- Activate or deactivate users via checkbox
- Update changes with a single action button per user

SweetAlert2 notifications are used to provide clear feedback when user settings are updated.

---

### Dashboard

Admin dashboard provides an overview of the system, including:

- **Total drugs**
- **Drugs in stock**
- **Drugs out of stock**
- **Total categories**
- **Total users**
- **Active users**

A Chart.js pie chart displays:

- Top 5 categories by number of drugs
- “Other” bucket for the remaining categories

---

### Email Notifications

- When a drug’s stock is updated to `0`, an email notification is sent to all admin users
- Implemented with **SendGrid Email API**
- API keys and email settings are read from environment variables defined in `.env`
- HTML email template located at `templates/emails/out_of_stock.html`

---

### UI / UX

- Responsive layout built with **Bootstrap 5**
- Dark header bar (navbar):
  - Left: hamburger button to toggle sidebar
  - Center/left: PharmaShelf brand (with logo support)
  - Right: user avatar with initials + username + dropdown menu
- Sidebar navigation:
  - Dashboard
  - Drugs Catalog
  - Add Drug (admin)
  - Categories (admin)
  - Interaction Checker
  - Add Interaction (admin)
  - User Management (admin)
  - About PharmaShelf
- Global footer:
  - “PharmaShelf” text and link to **About PharmaShelf**
- **SweetAlert2** used for success/error notifications (e.g. updating stock, adding/editing drugs, changing user roles)
- **Chart.js** used to render the dashboard chart

---

## Tech Stack

- **Backend**: Python, Django
- **Database**:
  - MySQL supported via Django database configuration
- **Authentication**: Custom `User` model + bcrypt password hashing
- **Frontend**: HTML, CSS, Bootstrap 5, Chart.js, SweetAlert2
- **Email**: SendGrid Email API
- **Configuration**: `.env` file using `python-dotenv` and `os.environ` in `settings.py`

---

## Getting Started

### Prerequisites

- Python 3.x
- Git
- (Optional) MySQL Server if you want to use MySQL instead of SQLite

---

### 1. Clone the repository

~~~bash
git clone https://github.com/YOUR_USERNAME/pharmashelf.git
cd pharmashelf
~~~

---

### 2. Create and activate a virtual environment

On Windows:

~~~bash
python -m venv env
env\Scripts\activate
~~~

On macOS/Linux:

~~~bash
python3 -m venv env
source env/bin/activate
~~~

---

### 3. Install dependencies

~~~bash
pip install -r requirements.txt
~~~

If you don’t have a `requirements.txt` yet, you can generate one with:

~~~bash
pip freeze > requirements.txt
~~~

---

### 4. Configure environment variables

Create a `.env` file in the project root (next to `manage.py`) and add configuration values, for example:

~~~env
DB_NAME=database name
DB_USER=database username
DB_PASSWORD=database password
DB_HOST=localhost
DB_PORT=3306
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=sendgrid_email
~~~

Then, in `settings.py`, read these values using `os.environ[...]` and configure the `DATABASES` setting.

---

### 5. Apply migrations

~~~bash
python manage.py migrate
~~~

This creates all tables for the custom user model, drugs, categories, alternatives, interactions, etc.

---

### 6. Create an initial admin user

PharmaShelf uses its own user model and login views.

For development, a simple approach is:

1. Start the development server (see next step)
2. Visit the registration/sign-up page in the browser and create a user
3. Use either:
   - The Django shell, or
   - Direct database access

to set that user as admin and active:

~~~bash
python manage.py shell
~~~

~~~python
from app_name.models import User  # replace app_name with your actual app name
u = User.objects.get(email="your_email@example.com")
u.role = "admin"
u.is_active = True
u.save()
~~~

After that, you can log in as this admin user and manage other accounts from the **User Management** page.

---

### 7. Run the development server

~~~bash
python manage.py runserver
~~~

Open in the browser:

~~~text
http://127.0.0.1:8000/
~~~

Log in and explore:

- Dashboard
- Drugs Catalog
- Drug details and stock updates
- Alternatives and interactions
- User Management
- About PharmaShelf

---

## Project Structure (high level)

A typical layout looks like:

~~~text
pharmashelf/
├─ manage.py
├─ pharmashelf/          # Django project settings, URLs, WSGI/ASGI
└─ app_name/             # Main application (replace with actual app name)
   ├─ models.py          # User, Category, Drug, DrugAlternative, DrugInteraction
   ├─ views.py           # All view functions for pages and actions
   ├─ urls.py            # URL patterns for the app
   ├─ templates/
   │  ├─ dashboard.html
   │  ├─ drugs.html
   │  ├─ drug_details.html
   │  ├─ add_drug.html
   │  ├─ edit_drug.html
   │  ├─ user_management.html
   │  ├─ interaction_checker.html
   │  ├─ add_interaction.html
   │  ├─ about.html
   │  ├─ auth/           # login / register templates
   │  └─ emails/
   │     └─ out_of_stock.html
   └─ static/
      ├─ css/
      │  └─ style.css
      └─ js/
         └─ scripts.js
~~~



---

## Possible Future Enhancements

Some potential next steps for PharmaShelf:

- Audit log for critical changes (stock updates, role changes, new interactions)
- Export drugs list and interactions as CSV/Excel
- Support for multiple locations/branches
- More advanced interaction logic (severity levels, recommendations)
- Integration with external drug databases or APIs

