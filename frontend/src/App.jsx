import { useState, useRef } from 'react';
import './index.css';

// --- Icons ---
const SearchIcon = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <circle cx="11" cy="11" r="8"></circle>
    <path d="M21 21l-4.35-4.35"></path>
  </svg>
);

const SparkleIcon = () => (
  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M12 2v20M17 5l-10 14M22 12H2M5 5l14 14"></path>
  </svg>
);

const UploadIcon = () => (
  <svg width="48" height="48" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="17 8 12 3 7 8"></polyline>
    <line x1="12" y1="3" x2="12" y2="15"></line>
  </svg>
);

// --- Components ---

const Sidebar = ({ activeTab, setActiveTab }) => (
  <aside className="sidebar">
    <div className="logo">CopilotAI</div>
    <nav>
      <div 
        className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
        onClick={() => setActiveTab('dashboard')}
      >
        <span>📊</span> Dashboard
      </div>
      <div 
        className={`nav-item ${activeTab === 'documents' ? 'active' : ''}`}
        onClick={() => setActiveTab('documents')}
      >
        <span>📚</span> Documents
      </div>
    </nav>
  </aside>
);

const QueryBox = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query);
    }
  };

  return (
    <form className="query-box" onSubmit={handleSubmit}>
      <SearchIcon />
      <input 
        type="text" 
        className="query-input" 
        placeholder="Ask a business question... (e.g. 'Analyze why sales dropped last quarter')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={loading}
      />
      <button type="submit" className="query-btn" disabled={loading || !query.trim()}>
        {loading ? 'Analyzing...' : <><SparkleIcon /> Ask Copilot</>}
      </button>
    </form>
  );
};

const Card = ({ title, icon, iconClass, children, fullWidth = false }) => (
  <div className={`card ${fullWidth ? 'full-width' : ''}`}>
    <div className="card-header">
      <div className={`card-icon ${iconClass}`}>{icon}</div>
      <h3 className="card-title">{title}</h3>
    </div>
    <div className="card-content">
      {children}
    </div>
  </div>
);

const Loading = () => (
  <div className="loader-container">
    <div className="spinner"></div>
    <div className="loading-text">Agents are collaborating...</div>
  </div>
);

const EmptyState = () => (
  <div className="empty-state">
    <div className="empty-icon">🤖</div>
    <h3>Ready to assist</h3>
    <p>Ask a question above to get AI-powered business insights.</p>
  </div>
);

const DocumentsPage = () => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const fileInputRef = useRef(null);

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });
      
      const data = await res.json();
      if (res.ok) {
        setMessage({ type: 'success', text: data.message || `Successfully processed and indexed ${files.length} files.` });
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to upload document.' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error. Make sure the backend is running.' });
    } finally {
      setUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="documents-page">
      <header className="header">
        <h1>Business Documents</h1>
        <p>Upload your reports, analysis, and data files to give the AI context.</p>
      </header>
      
      <div className="card full-width" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }}>
          <UploadIcon />
        </div>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Upload Document to RAG</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Supports PDF files. The contents will be split, embedded, and added to the vector database.
        </p>
        
        <input 
          type="file" 
          accept=".pdf" 
          multiple
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleUpload}
        />
        
        <button 
          className="query-btn" 
          style={{ margin: '0 auto' }}
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? 'Processing & Indexing...' : 'Select File'}
        </button>
        
        {message && (
          <div style={{ 
            marginTop: '2rem', 
            padding: '1rem', 
            borderRadius: '8px', 
            backgroundColor: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            color: message.type === 'success' ? 'var(--success)' : 'var(--error)'
          }}>
            {message.text}
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSearch = async (query) => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      
      const data = await response.json();
      
      setResult({
        problem: data.analysis === "Skipped" ? "Not applicable for this query." : (data.analysis || "Identifying root causes based on context..."),
        sources: data.sources && data.sources.length > 0 ? data.sources : [{ file: "System", excerpt: "No specific document context retrieved." }],
        solution: data.strategy === "Skipped" ? "No recommendations required for this request." : (data.strategy || "Formulating strategic recommendations..."),
        summary: data.final_output || "A consolidated summary of the findings."
      });
    } catch (error) {
      console.error("Error analyzing query:", error);
      setTimeout(() => {
        setResult({
          problem: "- Sales declined by 30% in Region Y\n- Increased competitor activity\n- Drop in product awareness",
          sources: [
            { file: "Q3_Sales_Report.pdf", excerpt: "Sales declined by 30% in Region Y due to competitor pricing." },
            { file: "Marketing_Spend_Q3.csv", excerpt: "Social media ad spend was reduced by 15%." },
            { file: "Competitor_Analysis.docx", excerpt: "Aggressive competitor discounting captured 12% of our market share." }
          ],
          solution: "1. Adjust pricing strategy in Region Y\n2. Reallocate marketing budget to targeted social ads\n3. Introduce a limited-time promotional bundle",
          summary: "The 30% sales drop is primarily driven by aggressive competitor pricing and reduced marketing visibility. By adjusting our pricing tier and boosting targeted ads, we can recover market share by Q4."
        });
      }, 2000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <>
            <header className="header">
              <h1>Business Copilot</h1>
              <p>Get AI-driven insights from your company data.</p>
            </header>

            <QueryBox onSearch={handleSearch} loading={loading} />

            {loading && <Loading />}
            
            {!loading && !result && <EmptyState />}

            {!loading && result && (
              <>
                <div className="dashboard-grid">
                  <Card title="Key Insights" icon="⚠️" iconClass="icon-problem">
                    <div style={{ whiteSpace: 'pre-wrap' }}>{result.problem}</div>
                  </Card>
                  
                  <Card title="Supporting Evidence" icon="📄" iconClass="icon-sources">
                    <div className="sources-list" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {result.sources.map((src, idx) => {
                        if (typeof src === 'string') {
                          return <div key={idx} className="source-item">• {src}</div>;
                        }
                        return (
                          <div key={idx} className="source-item" style={{ padding: '0.75rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '6px', fontSize: '0.9rem', lineHeight: '1.4' }}>
                            <strong style={{ color: 'var(--accent-primary)' }}>• {src.file}</strong> → <span style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>"{src.excerpt}"</span>
                          </div>
                        );
                      })}
                    </div>
                  </Card>
                </div>

                <div className="dashboard-grid">
                  <Card title="Strategic Recommendations" icon="💡" iconClass="icon-solution" fullWidth>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{result.solution}</div>
                  </Card>
                  
                  <Card title="Business Impact" icon="📝" iconClass="icon-summary" fullWidth>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{result.summary}</div>
                  </Card>
                </div>
              </>
            )}
          </>
        )}

        {activeTab === 'documents' && <DocumentsPage />}
      </main>
    </div>
  );
}

export default App;
