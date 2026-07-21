import { useEffect, useMemo, useState } from 'react';
import { CornerstoneViewer } from './components/CornerstoneViewer';

const API_BASE = 'http://127.0.0.1:8000';

interface StudySummary {
  folder: string;
  number_of_images: number;
  is_complete: boolean;
  missing_views: string[];
  patient_name?: string | null;
  study_date?: string | null;
  study_uid?: string | null;
}

interface StudyResponse {
  folder: string;
  summary: StudySummary;
}

function App() {
  const [folder, setFolder] = useState('/home/eloygarcia/Escritorio/Datasets/vinDr/physionet.org/files/vindr-mammo/1.0.0/images/004426a40da27ef22a866538b772ac44');
  const [study, setStudy] = useState<StudyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadStudy = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/studies/load?folder=${encodeURIComponent(folder)}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to load study');
      }

      const data = await response.json();
      setStudy(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  const summary = useMemo(() => study?.summary, [study]);

  useEffect(() => {
    void loadStudy();
  }, []);

  return (
    <div className="app-shell">
      <header>
        <h1>Preprocessing DICOM Viewer</h1>
        <p>Minimal React + API example for browsing mammography studies.</p>
      </header>

      <section className="controls">
        <input value={folder} onChange={(event) => setFolder(event.target.value)} />
        <button onClick={() => void loadStudy()} disabled={loading}>
          {loading ? 'Loading…' : 'Load study'}
        </button>
      </section>

      {error && <div className="error">{error}</div>}

      {summary && (
        <section className="card">
          <h2>Study summary</h2>
          <ul>
            <li><strong>Folder:</strong> {summary.folder}</li>
            <li><strong>Images:</strong> {summary.number_of_images}</li>
            <li><strong>Complete:</strong> {summary.is_complete ? 'Yes' : 'No'}</li>
            <li><strong>Missing views:</strong> {summary.missing_views.join(', ') || 'None'}</li>
            <li><strong>Patient:</strong> {summary.patient_name || 'N/A'}</li>
            <li><strong>Study date:</strong> {summary.study_date || 'N/A'}</li>
          </ul>
        </section>
      )}

      <section className="card viewer-placeholder">
        <h2>Viewer</h2>
        <CornerstoneViewer imageUrl={study ? `${API_BASE}/studies/image?folder=${encodeURIComponent(study.folder)}` : undefined} />
      </section>
    </div>
  );
}

export default App;
