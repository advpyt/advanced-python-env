# Library Management System

This is a simple Django project for managing a small library.  Users can browse a catalogue of books, borrow and return them, and view their borrowing history.  Administrators can manage categories, books and borrowing records through the Django admin interface.

## Features

- **Book catalogue** with filtering by category.
- **Borrow/return workflow** with due dates and overdue status highlighting.
- **User history** showing current and past borrows.
- **REST API** supporting CRUD operations on books (`GET`, `POST`, `PUT`, `DELETE`).
- **Responsive templates** using Django Template Language and a clean CSS design.

## Running the project locally

1. **Create a virtual environment** (Python 3.12 is recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # On Windows use: .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser** so you can log into the admin panel:

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` in your browser to see the catalogue and `http://127.0.0.1:8000/admin/` to manage data.

## REST API

The API is available under the `api/` prefix.  You can interact with it using `curl`, Postman or any HTTP client.

### List and create books

* **GET /api/books/** – return a list of books.
* **POST /api/books/** – create a new book.  Payload fields:
  - `title` (string, required)
  - `author` (string, required)
  - `category_id` (integer, required) – ID of an existing category
  - `total_copies` (integer, optional, default 1)

### Retrieve, update and delete a book

* **GET /api/books/<id>/** – return details of a single book.
* **PUT /api/books/<id>/** – update fields of a book.  You can send any combination of `title`, `author`, `category_id`, or `total_copies`.  When reducing `total_copies`, ensure you are not setting it below the number of currently borrowed copies.
* **DELETE /api/books/<id>/** – delete a book.  Deletion is only allowed if no copies are currently borrowed.

## Deployment instructions (free tier)

You can deploy this project to a free hosting provider such as [Render](https://render.com), [Railway](https://railway.app) or [PythonAnywhere](https://www.pythonanywhere.com/).  The steps below outline a typical deployment to Render:

1. **Push your code to GitHub**.  Create a repository in your GitHub organisation or user account and push the `library_project` folder.

2. **Create a new web service on Render**:
   - Choose **New Web Service** and connect your GitHub repo.
   - Select **Build and run from Dockerfile** or **Python (Django)**.  For simple deployments, the Python build pack works well.
   - Set environment variables:
     - `DJANGO_SECRET_KEY` – a random secret key
     - `PYTHON_VERSION` – `3.12`
     - `DATABASE_URL` – automatically provided if you enable a free PostgreSQL instance
   - Configure the build and start commands.  For example:
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn config.wsgi:application --log-file -`

3. **Configure the database**.  Render offers a free PostgreSQL tier.  After provisioning, copy the database URL into your environment variables and update `config/settings.py` to use it.  Alternatively, on PythonAnywhere you can use the built‑in SQLite database for small projects.

4. **Migrate and create a superuser** on the deployed environment.  This can be done from the Render shell or via a management command.

Once deployment completes, your application will be accessible at the URL provided by the hosting provider.

## Team workflow and commits

This repository is developed by a team of four members.  To ensure clear division of work and visibility in Git history, each member should commit their changes with descriptive messages and their own author identity.  For example:

| Member | Responsibility | Example commit message |
|-------|---------------|-----------------------|
| **1 – Backend/Models** | Designed models, migrations and business logic. | `feat(models): implement Book, Category and Borrow models` |
| **2 – Admin/Data** | Registered models in the admin, created initial data via the admin interface. | `feat(admin): customise admin list display and filters` |
| **3 – Frontend/Templates** | Implemented templates with loops and conditionals, added CSS styling. | `feat(templates): add book list and detail templates with styling` |
| **4 – API/Deployment** | Added REST API endpoints (`GET`, `POST`, `PUT`, `DELETE`) and wrote deployment documentation. | `feat(api): implement book detail endpoint with PUT/DELETE` |

Each member should configure their Git user name and email before committing:

```bash
git config user.name "Member Name"
git config user.email "member@example.com"
```

After completing your part, run:

```bash
git add .
git commit -m "<Your commit message>"
git push origin main
```

## License

This project is provided for educational purposes.  Feel free to use and adapt it as needed.