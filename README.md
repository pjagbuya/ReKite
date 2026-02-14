# Re:Kite

A web application for spaced repetition learning, similar to Anki, helping students master objective definitions through AI-powered study tools.

## Features

- **User Authentication**: Simple username and password-based signup and login
- **Spaced Repetition System (SRS)**: Python backend for intelligent review scheduling
- **AI Integration**: Sentence-BERT and Deepgram API support (coming soon)
- **Modern Frontend**: Next.js with TypeScript and Tailwind CSS
- **State Management**: Zustand for handling UI timers, progress bars, and live audio feedback
- **Database**: Supabase PostgreSQL for cloud-hosted database

## Tech Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **UI Components**: React with client-side rendering for interactive features

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL (cloud-hosted)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Supabase account (free tier available at https://supabase.com)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pjagbuya/ReKite.git
cd ReKite
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Supabase database
# 1. Create a free Supabase project at https://supabase.com
# 2. Get your connection string from Settings > Database > Connection String (Transaction mode)
# 3. Create a .env file in the backend directory with:
#    DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-x-region.pooler.supabase.com:6543/postgres

# Create database tables
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local
# Edit .env.local if needed (defaults to http://localhost:8000)
```

## Running the Application

### Start the Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

1. Navigate to `http://localhost:3000`
2. Click "Sign Up" to create a new account
3. Enter a username (min 3 characters) and password (min 6 characters)
4. After signup, you'll be redirected to login
5. Sign in with your credentials
6. Access your dashboard to start learning!

## Project Structure

```
ReKite/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth_utils.py        # Authentication utilities
│   ├── routers/
│   │   └── auth.py          # Authentication endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Landing page
│   │   ├── login/           # Login page
│   │   ├── signup/          # Signup page
│   │   └── dashboard/       # Dashboard (protected)
│   ├── lib/
│   │   └── auth-store.ts    # Zustand authentication store
│   ├── package.json         # Node dependencies
│   └── .env.local           # Environment variables
│
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create a new user account
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/me` - Get current user info (requires token)

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check endpoint

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation:
- Visit `http://localhost:8000/docs` for interactive Swagger UI
- SQLAlchemy ORM connected to Supabase PostgreSQL
- JWT authentication with secure password hashing using bcrypt
- Database migrations handled through SQLAlchemy's `create_all()`

### Frontend Development

The frontend uses Next.js App Router with:
- TypeScript for type safety
- Tailwind CSS for styling
- Zustand for state management with persistence
- Client-side rendering for authentication pages

## Future Enhancements

- [ ] Sentence-BERT integration for semantic similarity
- [ ] Deepgram API for audio transcription and feedback
- [ ] Spaced repetition algorithm implementation
- [ ] Flashcard creation and management
- [ ] Progress tracking and statistics
- [ ] Audio recording and playback
- [ ] Study session timers
- [ ] Progress bars for learning goals
- [ ] Live audio feedback during study sessions

## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication
- CORS is configured to allow frontend access
- Change the `SECRET_KEY` in production!
- Use environment variables for sensitive data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.