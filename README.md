# CodeGraph 🕸️

> Beautiful, interactive dependency visualizations for any GitHub repository

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)
[![D3.js](https://img.shields.io/badge/d3.js-v7-orange.svg)](https://d3js.org/)

## ✨ Features

- 🎨 **Interactive Network Visualization** - Force-directed graph with smooth physics simulation
- 🔍 **Smart Dependency Analysis** - Analyzes Python imports and file relationships
- 📊 **Complexity Metrics** - Color-coded nodes based on cyclomatic complexity
- 🎯 **Intelligent Highlighting** - Click nodes to trace dependency chains
- 🔎 **Search & Filter** - Quickly find specific files or modules
- 📸 **Export Ready** - Generate shareable HTML reports
- ⚡ **Fast & Efficient** - Caches analysis results for quick re-renders

## 🎬 Demo

![CodeGraph Demo](docs/demo.gif)

*Analyzing the Flask repository - watch dependencies come alive!*

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/bluekap/codegraph.git
cd codegraph

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running Locally

```bash
# Terminal 1 - Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Start frontend
cd frontend
npm start
```

Visit `http://localhost:3000` and paste any GitHub repo URL!

## 🏗️ Architecture

```
codegraph/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── analyzer/       # Repository analysis engine
│   │   │   ├── git_handler.py
│   │   │   ├── dependency_parser.py
│   │   │   └── metrics.py
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   └── main.py         # FastAPI app
│   └── requirements.txt
├── frontend/                # React + D3.js frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── NetworkGraph.tsx    # D3.js visualization
│   │   │   ├── Controls.tsx        # Search/filter UI
│   │   │   └── Tooltip.tsx         # Node details
│   │   ├── services/       # API client
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml       # Container orchestration
└── README.md
```

## 🎨 Visualizations

### 1. Dependency Network
- **Nodes**: Files/modules sized by lines of code
- **Edges**: Import relationships with directional arrows
- **Colors**: Complexity heatmap (green → yellow → red)
- **Physics**: Force-directed layout with collision detection

### 2. Interactive Features
- **Hover**: View file metrics (LOC, complexity, imports)
- **Click**: Highlight dependency chains
- **Drag**: Reposition nodes manually
- **Zoom**: Explore large codebases
- **Search**: Filter by filename or module

## 📊 Metrics Analyzed

- **Lines of Code** (LOC) per file
- **Cyclomatic Complexity** using Radon
- **Import Dependencies** (direct and transitive)
- **Module Coupling** strength
- **Change Frequency** (git history)
- **File Size** distribution

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern async Python web framework
- GitPython - Git repository interaction
- Radon - Code complexity metrics
- NetworkX - Graph algorithms
- AST - Python import parsing

**Frontend:**
- React 18 - UI framework
- TypeScript - Type safety
- D3.js v7 - Data visualization
- Tailwind CSS - Styling
- Axios - API client

**DevOps:**
- Docker & Docker Compose
- GitHub Actions - CI/CD
- pytest - Backend testing
- Jest - Frontend testing

## 📝 API Endpoints

### Analyze Repository
```http
POST /api/analyze
Content-Type: application/json

{
  "repo_url": "https://github.com/pallets/flask"
}

Response:
{
  "nodes": [
    {
      "id": "flask/app.py",
      "loc": 250,
      "complexity": 12,
      "language": "python"
    }
  ],
  "edges": [
    {
      "source": "flask/app.py",
      "target": "flask/helpers.py"
    }
  ],
  "metrics": {
    "total_files": 45,
    "total_loc": 12500,
    "avg_complexity": 8.3
  }
}
```

## 🎯 Roadmap

- [x] Core dependency analysis
- [x] Interactive D3.js visualization
- [x] Python import parsing
- [ ] Multi-language support (JavaScript, Java, Go)
- [ ] GitHub API integration (no cloning needed)
- [ ] Historical analysis (code evolution over time)
- [ ] Team collaboration features
- [ ] VS Code extension
- [ ] CLI tool for CI/CD integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Sourcetrail](https://www.sourcetrail.com/) and [Gource](https://gource.io/)
- Built with amazing open-source tools
- D3.js force simulation examples by Mike Bostock

## 📧 Contact

**Vaibhav Goswami**
- Portfolio: [bluekap.github.io](https://bluekap.github.io)
- GitHub: [@bluekap](https://github.com/bluekap)
- Email: vabg96@yahoo.com

---

⭐ **Star this repo if you find it useful!** ⭐
