# CodeGraph Setup Guide

Complete setup instructions for running CodeGraph locally or deploying to production.

## 📋 Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **Docker** (optional) - [Download](https://www.docker.com/)

## 🚀 Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/bluekap/codegraph.git
cd codegraph
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open automatically at `http://localhost:3000`

### 4. Test the Application

1. Open `http://localhost:3000` in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/pallets/flask`)
3. Click "Analyze"
4. Watch the beautiful dependency graph appear!

## 🐳 Docker Setup (Alternative)

If you prefer Docker:

```bash
# From project root
docker-compose up --build

# Access the app at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🔧 Configuration

### Backend Configuration

Create `.env` file in `backend/` directory:

```env
# Optional settings
MAX_REPO_SIZE_MB=100
CACHE_ENABLED=true
LOG_LEVEL=INFO
```

### Frontend Configuration

Create `.env` file in `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## 📊 Testing with Sample Repositories

Great repositories to test with:

1. **Flask** (Small, clean): `https://github.com/pallets/flask`
2. **FastAPI** (Medium): `https://github.com/tiangolo/fastapi`
3. **Requests** (Well-structured): `https://github.com/psf/requests`
4. **Django** (Large, complex): `https://github.com/django/django`

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Problem**: `GitCommandError`
```bash
# Solution: Ensure Git is installed and in PATH
git --version
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use different port
uvicorn app.main:app --reload --port 8001
# Update REACT_APP_API_URL in frontend/.env
```

### Frontend Issues

**Problem**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Problem**: CORS errors
```bash
# Solution: Check backend CORS settings in app/main.py
# Ensure your frontend URL is in allow_origins
```

**Problem**: "No response from server"
```bash
# Solution: Verify backend is running
curl http://localhost:8000/health
```

## 🚢 Deployment

### Deploy Backend (Railway/Render)

1. Push code to GitHub
2. Connect to Railway/Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Deploy Frontend (Vercel/Netlify)

1. Push code to GitHub
2. Connect to Vercel/Netlify
3. Set build command: `npm run build`
4. Set publish directory: `build`
5. Add environment variable: `REACT_APP_API_URL=<your-backend-url>`

## 📝 Development Tips

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
# Format code
black app/
# Type checking
mypy app/
```

Frontend:
```bash
# Lint
npm run lint
# Format
npm run format
```

### Hot Reload

Both backend and frontend have hot reload enabled by default:
- Backend: Changes to Python files trigger automatic reload
- Frontend: Changes to React files trigger automatic browser refresh

## 🎨 Customization

### Modify Graph Appearance

Edit `frontend/src/components/NetworkGraph.tsx`:
- Change colors in `colorScale`
- Adjust node sizes in simulation forces
- Modify physics parameters

### Add New Metrics

1. Add metric calculation in `backend/app/analyzer/metrics.py`
2. Update `NodeData` model in `backend/app/models/schemas.py`
3. Display metric in frontend graph or dashboard

### Support More Languages

1. Add parser in `backend/app/analyzer/` (e.g., `javascript_parser.py`)
2. Update `RepositoryAnalyzer` to detect and handle new languages
3. Add language-specific metrics

## 📚 Project Structure

```
codegraph/
├── backend/
│   ├── app/
│   │   ├── analyzer/        # Core analysis logic
│   │   ├── models/          # Data models
│   │   ├── routers/         # API endpoints
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main component
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 💬 Support

- 📧 Email: vabg96@yahoo.com
- 🐛 Issues: [GitHub Issues](https://github.com/bluekap/codegraph/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/bluekap/codegraph/discussions)

---

**Happy Coding! 🎉**
