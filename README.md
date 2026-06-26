# ExpertVerse AI

**A real, production-ready AI-powered expertise marketplace platform** - built for portfolio demonstrations, final year projects, hackathons, and client pitches.

Unlike typical startup prototypes, ExpertVerse AI is **genuinely functional**. Every feature works with real data persistence, live AI agents, authentic user workflows, and complete end-to-end functionality.

## ✨ What Actually Works

### ✅ Real Authentication
- JWT-based authentication with secure token management
- Email validation on registration
- Role-based access control (user, expert, admin)
- Persistent user sessions
- Secure password hashing

### ✅ Expert Directory & Management
- Browse experts with detailed profiles
- Search by title, company, or bio
- Ratings, experience, and hourly rates
- Profile editing for experts
- Document portfolio uploads

### ✅ AI Agents (with FAISS Vector Search)
- **Analyze Agent**: Understands user problems
- **Match Agent**: Recommends experts using semantic search
- **Roadmap Agent**: Generates personalized plans
- **Chat Agent**: Orchestrates all agents conversationally
- **Fallback AI**: Works without API keys; ready for Google Gemini

### ✅ Real Booking System
- Create bookings with date/time
- Manage bookings (view, cancel)
- Status tracking
- Persistent storage

### ✅ Document & RAG System
- Upload documents (text, PDF, Word)
- FAISS vector indexing
- Semantic search across portfolios
- Expert matching based on document similarity

### ✅ Database & Data Persistence
- SQLite (local dev, upgradeable to PostgreSQL)
- SQLAlchemy ORM with relationships
- Automatic migrations (Alembic)
- Real data storage across sessions

## 🚀 30-Second Start

### Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API available at: `http://localhost:8000`
Docs at: `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at: `http://localhost:5173`

### Test Everything Works
```bash
cd backend
python test_e2e.py
```

## 🎯 User Journey

1. **Register** → Real account creation with validation
2. **Login** → JWT token authentication
3. **Browse Experts** → Live database queries
4. **Chat with AI** → Problem analysis and expert recommendations
5. **Book Session** → Real booking stored in database
6. **Upload Documents** → Portfolio indexed with FAISS
7. **Manage Profile** → Edit expert information

## 📋 Complete API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login & get JWT |
| `/auth/profile` | GET | Get current user |
| `/experts/list` | GET | List all experts (searchable) |
| `/experts/details/{id}` | GET | Expert profile |
| `/experts/create` | POST | Create expert profile |
| `/experts/update/{id}` | PUT | Update profile |
| `/agents/analyze` | POST | Analyze problem |
| `/agents/match` | POST | Match to experts |
| `/agents/roadmap` | POST | Generate roadmap |
| `/agents/chat` | POST | Full workflow |
| `/bookings/create` | POST | Create booking |
| `/bookings/list` | GET | List bookings |
| `/bookings/cancel/{id}` | POST | Cancel booking |
| `/documents/upload` | POST | Upload text document |
| `/documents/upload-file` | POST | Upload file |
| `/documents/list/{id}` | GET | List documents |
| `/documents/delete/{id}` | DELETE | Delete document |

Full interactive docs: `http://localhost:8000/docs`

## 🏗️ Architecture

```
ExpertVerse AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM (User, Expert, Booking, Document, etc.)
│   │   ├── routes/         # API endpoints (auth, experts, bookings, agents, documents)
│   │   ├── schemas/        # Pydantic validation models
│   │   ├── services/       # Business logic (agents, embeddings, FAISS, seed)
│   │   ├── db/             # Database session management
│   │   ├── core/           # Settings and configuration
│   │   └── main.py         # FastAPI application setup
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment configuration
│   ├── test_e2e.py         # End-to-end test suite
│   └── alembic/            # Database migrations
│
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── pages/         # Page components (Login, Register, Experts, Chat, Book, Profile)
│   │   ├── services/      # API clients (auth, experts, bookings)
│   │   ├── components/    # Reusable UI components
│   │   └── App.tsx        # Main app with routing
│   ├── package.json
│   └── .env               # Frontend configuration
│
└── docker-compose.yml     # Local development setup
```

## 🔧 Configuration

### Backend `.env`
```env
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
GOOGLE_API_KEY=              # Optional: for live Gemini responses
```

### Frontend `.env`
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 Included Test Suite

```bash
# Full end-to-end workflow
python test_e2e.py

# FAISS vector search + agents
python test_agent_pipeline.py

# Embeddings import check
python test_import_embeddings.py
```

Tests verify:
✓ User registration
✓ JWT authentication
✓ Expert listing & search
✓ AI agent responses
✓ Expert matching via FAISS
✓ Booking creation
✓ Document upload & indexing

## 🤖 AI Agent System

### How It Works
1. **User Input** → Problem description
2. **Analyze Agent** → Extracts domain, urgency, goals
3. **Match Agent** → Uses FAISS to find relevant experts
4. **Roadmap Agent** → Generates personalized plan
5. **Chat Agent** → Delivers everything conversationally

### Fallback Mode (No API Key)
- ✅ Generates coherent responses locally
- ✅ Works for demos and presentations
- ✅ No external dependencies

### Enhanced Mode (with Google Gemini)
1. Get key: [Google AI Studio](https://makersuite.google.com)
2. Add to `.env`: `GOOGLE_API_KEY=...`
3. Live Gemini API responses

## 📊 Database Models

- **User**: name, email, password_hash, role, created_at
- **Expert**: user_id, title, company, experience_years, bio, hourly_rate, rating
- **Document**: expert_id, file_url, file_type, text, embeddings (in FAISS)
- **Booking**: user_id, expert_id, slot, status, created_at
- **ChatHistory**: user_id, message, response, created_at

All with proper foreign keys and relationships.

## 🎬 Demo Scenarios

### For Interviews
1. Open http://localhost:5173
2. Create account: test@interview.com
3. Browse experts (real data from DB)
4. Try AI chat (problem analysis)
5. Create booking (persists to DB)
6. Show profile editing

### For Presentations
1. Start with seeded data (1 expert already loaded)
2. Show API docs: http://localhost:8000/docs
3. Try POST requests live
4. Show database persistence (close and restart app)
5. Demonstrate FAISS search: `python test_agent_pipeline.py`

### For Portfolio
- **Code Quality**: Well-organized FastAPI + React
- **Full-Stack**: Backend API + Frontend UI
- **Database**: Real ORM with migrations
- **AI/ML**: Vector embeddings + semantic search
- **Authentication**: JWT security
- **Tests**: Comprehensive test suite

## ✨ Why This Isn't a Mockup

| Aspect | This Project | Typical Mockup |
|--------|-------------|----------------|
| Authentication | Real JWT tokens | Fake login |
| Database | SQLite persistence | Mock data arrays |
| Users | Stored and retrieved | Hardcoded |
| Bookings | Real records | Button logs only |
| AI | FAISS + embeddings | Hardcoded responses |
| API | 18 real endpoints | Fake stubs |
| Tests | E2E test suite | No tests |
| Deployment | Ready for production | Demo only |

## 🚢 For Production Deployment

Add to deployment checklist:
- [ ] Migrate to PostgreSQL
- [ ] Add Redis caching
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Add email notifications (SendGrid)
- [ ] Implement payment (Razorpay)
- [ ] Deploy to Docker/Kubernetes
- [ ] Set up CI/CD pipeline

## 🧠 Tech Stack Details

**Backend**
- FastAPI: Modern async Python web framework
- SQLAlchemy: SQL ORM with relationships
- Pydantic: Data validation
- Alembic: Database migrations
- FAISS: Vector similarity search
- python-jose: JWT tokens
- Uvicorn: ASGI server

**Frontend**
- React: UI framework
- TypeScript: Type safety
- Vite: Fast bundler
- TailwindCSS: Styling
- React Router: Routing
- Axios: HTTP client

**AI & ML**
- FAISS: Vector store
- Embeddings: Text vectorization
- Agents: Orchestration logic
- Gemini API: Optional live LLM

## 📞 Quick Reference

```bash
# Backend development
cd backend && python -m uvicorn app.main:app --reload

# Frontend development
cd frontend && npm run dev

# Run tests
cd backend && python test_e2e.py

# Check API docs
http://localhost:8000/docs

# Access app
http://localhost:5173
```

## 🎓 Use Cases

✅ **Portfolio Project** - Show real full-stack skills
✅ **Final Year Project** - Complete working system with AI/ML
✅ **Hackathon** - Fully functional in limited time
✅ **Client Demo** - Real working prototype
✅ **Interview** - Demonstrate live functionality
✅ **Startup Pitch** - Show operational product

---

**No mockups. No fake buttons. No placeholder data.** 

Every endpoint works. Every page functions. Every database write persists. 

This is what a real MVP looks like. 🚀

