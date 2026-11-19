# DANotes Backend

REST API for the DANotes Angular application, built with Django and Django REST Framework.
It stores notes in a SQLite database and provides the CRUD endpoints the frontend uses
to create, edit, mark, trash, restore and delete notes.

This project is set up for local development only.

## Technology Stack

- Python 3.14
- Django 6.1
- Django REST Framework 3.18
- django-cors-headers 4.9
- SQLite

## Features

- Create, list, retrieve, update (PUT and PATCH) and delete notes
- Mark and unmark notes (`marked` field)
- Move notes to the trash and restore them (`trash` field); trashed notes stay in the database
- Permanent deletion with `DELETE`
- Input validation through a DRF model serializer
- CORS restricted to the Angular development server
- Notes are listed in the Django admin

## Installation

Clone the repository:

```bash
git clone git@github.com:kamycoding/da-notes-backend.git
cd da-notes-backend
```

### Virtual Environment

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

### Environment Variables

Settings are read from a `.env` file in the project root. Copy the example file:

```bash
cp .env.example .env
```

Generate a secret key and put it in `.env` as the value of `DJANGO_SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes | none | Django secret key. The server refuses to start without it. |
| `DJANGO_DEBUG` | no | `False` | Set to `True` for local development. |
| `DJANGO_ALLOWED_HOSTS` | no | `127.0.0.1,localhost` | Comma-separated list of allowed hosts. |

Variables already set in the shell take precedence over the values in `.env`.
Never commit the `.env` file; it is listed in `.gitignore`.

### Database Migrations

```bash
python manage.py migrate
```

Optionally create an admin user to manage notes at `http://127.0.0.1:8000/admin/`:

```bash
python manage.py createsuperuser
```

### Starting the Server

```bash
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/notes/`.

## API Endpoints

| Method | Endpoint | Description | Success status |
|---|---|---|---|
| GET | `/notes/` | List all notes | 200 |
| POST | `/notes/` | Create a note | 201 |
| GET | `/notes/{id}/` | Retrieve a note | 200 |
| PUT | `/notes/{id}/` | Replace a note | 200 |
| PATCH | `/notes/{id}/` | Update individual fields | 200 |
| DELETE | `/notes/{id}/` | Delete a note permanently | 204 |

Unknown IDs return `404`. Invalid input returns `400` with field-level error messages.

The list endpoint returns a plain JSON array (no pagination), ordered by ID.

### Note Object

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Read-only, assigned by the server |
| `title` | string | Required, not blank, max. 255 characters |
| `content` | string | Required, may be an empty string |
| `marked` | boolean | Optional, defaults to `false` |
| `trash` | boolean | Optional, defaults to `false` |

## Example Requests

Create a note:

```bash
curl -X POST http://127.0.0.1:8000/notes/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping", "content": "Milk and bread", "marked": false, "trash": false}'
```

```json
{"id": 1, "title": "Shopping", "content": "Milk and bread", "marked": false, "trash": false}
```

List all notes:

```bash
curl http://127.0.0.1:8000/notes/
```

Update a note (this is what the Angular frontend sends for every change):

```bash
curl -X PUT http://127.0.0.1:8000/notes/1/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "title": "Shopping", "content": "Milk, bread, eggs", "marked": true, "trash": false}'
```

Move a note to the trash:

```bash
curl -X PATCH http://127.0.0.1:8000/notes/1/ \
  -H "Content-Type: application/json" \
  -d '{"trash": true}'
```

Delete a note permanently:

```bash
curl -X DELETE http://127.0.0.1:8000/notes/1/
```

## Running Tests

```bash
python manage.py test
```

The tests in `notes/tests.py` cover all CRUD operations, marking, trash and restore,
validation errors, 404 responses, the list response format and the CORS configuration.

## Frontend Integration

The backend is meant to be used with the
[DANotes Angular frontend](https://github.com/Developer-Akademie-AA/da_notes_frontend_teilnehmer).
No changes to the frontend are needed; its service already points to
`http://127.0.0.1:8000/notes/`.

1. Start the backend with `python manage.py runserver`.
2. In a separate directory, clone and start the frontend:

   ```bash
   git clone https://github.com/Developer-Akademie-AA/da_notes_frontend_teilnehmer.git da-notes-frontend
   cd da-notes-frontend
   npm install
   npm start
   ```

3. Open `http://localhost:4200/`.

The frontend uses `PUT /notes/{id}/` with the complete note for editing, marking,
moving to trash and restoring, and `DELETE /notes/{id}/` for permanent deletion.

CORS requests are allowed from `http://localhost:4200` and `http://127.0.0.1:4200`.
To use another origin, add it to `CORS_ALLOWED_ORIGINS` in `core/settings.py`.

## Project Structure

```text
da-notes-backend/
├── core/                 Django project configuration
│   ├── settings.py       Settings, .env loading, CORS
│   ├── urls.py           Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── notes/                Notes app
│   ├── migrations/
│   ├── admin.py          Admin registration
│   ├── apps.py
│   ├── models.py         Note model
│   ├── serializers.py    NoteSerializer
│   ├── views.py          NoteViewSet
│   ├── urls.py           Router for /notes/
│   └── tests.py          API tests
├── .env.example          Template for local environment variables
├── manage.py
├── requirements.txt
└── README.md
```
