import React, { useState, useEffect } from 'react';
import { NetworkGraph } from './components/NetworkGraph';
import { analyzeRepository } from './services/api';
import { AnalyzeResponse, NodeData } from './types';
import { type ThemeId } from './theme';
import './App.css';

const THEME_STORAGE_KEY = 'codegraph-theme';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<AnalyzeResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [theme, setTheme] = useState<ThemeId>(() => {
    try {
      const saved = localStorage.getItem(THEME_STORAGE_KEY);
      if (saved === 'light' || saved === 'dark') return saved;
    } catch (_) {}
    return 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (_) {}
  }, [theme]);

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    setLoading(true);
    setError(null);
    setGraphData(null);
    setSelectedNode(null);

    try {
      const data = await analyzeRepository(repoUrl);
      setGraphData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze repository');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const exampleRepos = [
    'https://github.com/pallets/flask',
    'https://github.com/tiangolo/fastapi',
    'https://github.com/psf/requests'
  ];

  return (
    <div className="App" data-theme={theme}>
      <header className="app-header">
        <div className="container">
          <div>
            <h1>CodeGraph</h1>
            <p className="subtitle">Dependency visualizations for any GitHub repository</p>
          </div>
          <div className="theme-toggle">
            <button
              type="button"
              className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
              onClick={() => setTheme('light')}
              title="Light mode"
            >
              Light
            </button>
            <button
              type="button"
              className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
              onClick={() => setTheme('dark')}
              title="Dark mode"
            >
              Dark
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          {/* Input Section */}
          <div className="input-section">
            <div className="input-group">
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter GitHub repository URL (e.g., https://github.com/pallets/flask)"
                className="repo-input"
                disabled={loading}
              />
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="analyze-button"
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>

            {/* Example repos */}
            <div className="examples">
              <span>Try: </span>
              {exampleRepos.map((url, idx) => (
                <button
                  key={idx}
                  onClick={() => setRepoUrl(url)}
                  className="example-link"
                  disabled={loading}
                >
                  {url.split('/').slice(-1)[0]}
                </button>
              ))}
            </div>

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}
          </div>

          {/* Loading */}
          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Cloning and analyzing repository...</p>
            </div>
          )}

          {/* Results */}
          {graphData && !loading && (
            <>
              {/* Metrics Dashboard */}
              <div className="metrics-dashboard">
                <div className="metric-card">
                  <div className="metric-value">{graphData.metrics.total_files}</div>
                  <div className="metric-label">Files</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{graphData.metrics.total_loc.toLocaleString()}</div>
                  <div className="metric-label">Lines of Code</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{graphData.metrics.avg_complexity.toFixed(1)}</div>
                  <div className="metric-label">Avg Complexity</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{graphData.edges.length}</div>
                  <div className="metric-label">Dependencies</div>
                </div>
              </div>

              {/* Search bar */}
              <div className="controls-section">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="🔍 Search files..."
                  className="search-input"
                />
                
                {selectedNode && (
                  <div className="selected-info">
                    <strong>{selectedNode.name}</strong>
                    <span> - {selectedNode.loc} lines, complexity: {selectedNode.complexity}</span>
                    <button onClick={() => setSelectedNode(null)} className="clear-btn">×</button>
                  </div>
                )}
              </div>

              {/* Graph */}
              <div className="graph-section">
                <NetworkGraph
                  theme={theme}
                  nodes={graphData.nodes}
                  edges={graphData.edges}
                  onNodeClick={setSelectedNode}
                  searchTerm={searchTerm}
                />
              </div>

              {/* Legend */}
              <div className="legend">
                <h3>Complexity</h3>
                <div className="legend-items">
                  <div className="legend-item">
                    <div className="legend-color" style={{ background: 'rgb(147, 197, 253)' }} />
                    <span>Low (0–5)</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ background: 'rgb(96, 165, 250)' }} />
                    <span>Medium (6–15)</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ background: 'rgb(29, 78, 216)' }} />
                    <span>High (15+)</span>
                  </div>
                </div>
                <p className="legend-tip">Click a node to highlight dependencies. Drag nodes to reposition. Scroll to zoom.</p>
              </div>
            </>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Built with ❤️ by <a href="https://bluekap.github.io" target="_blank" rel="noopener noreferrer">Vaibhav Goswami</a>
          {' | '}
          <a href="https://github.com/bluekap/codegraph" target="_blank" rel="noopener noreferrer">GitHub</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
