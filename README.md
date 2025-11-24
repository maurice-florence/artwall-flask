# Artwall Flask

A Python Flask application for managing and displaying creative content using Firebase Realtime Database, with a Masonry grid layout and HTMX for dynamic content loading.

## Features

- **Server-Side Rendering**: Flask + Jinja2 templates for stable, SEO-friendly pages
- **Dynamic Content Loading**: HTMX-powered infinite scroll without heavy JavaScript frameworks
- **Masonry Grid Layout**: Pinterest-style responsive grid using Masonry.js
- **Firebase Integration**: Firebase Realtime Database with cursor-based pagination
- **ENEX Import**: Import notes from Evernote export files with streaming XML parsing
- **Authentication**: Firebase Authentication with session cookies
- **Content Sanitization**: XSS protection for user-generated content

## Project Structure

```text
artwall-flask/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions
│   ├── blueprints/              # Modular routes
│   │   ├── main/                # Main pages
│   │   ├── api/                 # HTMX endpoints
│   │   ├── auth/                # Authentication
│   │   ├── projects/            # Project CRUD
│   │   └── ingest/              # ENEX uploads
│   ├── services/                # Business logic
│   │   ├── firebase_service.py  # Firebase operations
│   │   └── parser_service.py    # ENEX parsing
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── components/          # Reusable macros
│   │   └── partials/            # HTMX fragments
│   └── static/                  # CSS & JavaScript
├── config.py                    # Configuration
├── run.py                       # Entry point
├── requirements.txt             # Dependencies
└── .env.example                 # Environment template
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/maurice-florence/artwall-flask.git
cd artwall-flask
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your Firebase credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Firebase project details:

- Download your Firebase service account JSON from Firebase Console
- Update `GOOGLE_APPLICATION_CREDENTIALS` with the path to your JSON file
- Set `FIREBASE_DATABASE_URL` to your Firebase Realtime Database URL

### 5. Run the Application

```powershell
python run.py
```

Visit `http://localhost:5000` in your browser.

## Firebase Setup

1. Create a Firebase project at <https://console.firebase.google.com>
2. Enable Firebase Realtime Database
3. Enable Firebase Authentication (Email/Password and Google)
4. Download service account credentials:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file securely (DO NOT commit to Git)

## Usage

### Importing Notes from Evernote

1. Export your notes from Evernote as `.enex` files
2. Navigate to `/ingest` in the application
3. Upload your `.enex` file
4. The system will parse and import all notes with their content, tags, and timestamps

### Viewing Content

- The homepage displays your content in a responsive Masonry grid
- Click "Load More" to fetch additional posts using cursor-based pagination
- Images are automatically embedded and optimized

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8 .
```

## Architecture

This application follows the "hypermedia-driven" architecture pattern:

- **No SPA Complexity**: Server generates complete HTML, eliminating hydration errors
- **HTMX for Interactivity**: Dynamic content loading without heavy JavaScript
- **Cursor-Based Pagination**: Efficient pagination for Firebase Realtime Database
- **Streaming XML Parser**: Memory-efficient ENEX processing using `iterparse`
- **Content Sanitization**: XSS prevention using `bleach` library

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Docker

```bash
docker build -t artwall-flask .
docker run -p 8000:8000 --env-file .env artwall-flask
```

## License

MIT License

## Contributing

Pull requests are welcome! Please ensure all tests pass before submitting.
