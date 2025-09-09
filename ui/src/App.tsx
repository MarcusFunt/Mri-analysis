import React, { useState, useRef } from 'react';
import { uploadZip, startAnalyze, getResult } from './api';
import './App.css';

function DropZone({ onFile, onBrowse, fileName }: { onFile: (f: File) => void; onBrowse: () => void; fileName?: string }) {
  const [over, setOver] = useState(false);
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
    setOver(false);
  };
  return (
    <div
      className={`drop-zone ${over ? 'over' : ''}`}
      onDragOver={e => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={handleDrop}
      onClick={onBrowse}
    >
      {fileName || 'Drag & drop study zip here or click to browse'}
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState('');
  const [result, setResult] = useState<any>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const handleFile = (f: File | null) => setFile(f);

  const handleUpload = async () => {
    if (file) {
      const id = await uploadZip(file);
      setJobId(id);
    }
  };

  const handleAnalyze = async () => {
    if (!jobId) return;
    await startAnalyze(jobId);
    poll(jobId);
  };

  const poll = async (id: string) => {
    let done = false;
    while (!done) {
      const r = await getResult(id);
      if (r.state === 'done') {
        setResult(r);
        done = true;
      } else {
        await new Promise(res => setTimeout(res, 2000));
      }
    }
  };

  return (
    <div style={{ display: 'flex', gap: '2rem', padding: '1rem' }}>
      <div style={{ flex: 1 }}>
        <h2>Upload Study</h2>
        <DropZone onFile={handleFile} onBrowse={() => fileInput.current?.click()} fileName={file?.name} />
        <input
          type="file"
          ref={fileInput}
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files?.[0] || null)}
        />
        <div>
          <button onClick={handleUpload} disabled={!file}>Upload</button>
          <button onClick={handleAnalyze} disabled={!jobId}>Analyze</button>
        </div>
        {jobId && <p>Job ID: {jobId}</p>}
      </div>
      <div style={{ flex: 2 }}>
        {result && (
          <div>
            <h2>Impression</h2>
            <p>{result.impression}</p>
            <p className="result-status">
              <span className={`pill ${result.normal ? 'normal' : 'abnormal'}`}>{result.normal ? 'Normal' : 'Abnormal'}</span>
              {new Intl.NumberFormat(undefined, { style: 'percent', maximumFractionDigits: 1 }).format(result.confidence)}
            </p>
            <ul>
              {result.findings.map((f: string, i: number) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
            {Array.isArray(result.downloads?.thumbnails) && result.downloads.thumbnails.length > 0 && (
              <div className="thumbnails">
                {result.downloads.thumbnails.map((url: string, i: number) => (
                  <img key={i} src={url} alt={`thumbnail-${i}`} />
                ))}
              </div>
            )}
            <div>
              <a href={result.downloads.dicom_sr}>DICOM SR</a><br />
              {result.downloads.dicom_seg && <a href={result.downloads.dicom_seg}>DICOM SEG</a>}<br />
              <a href={result.downloads.json}>JSON</a>
            </div>
            <p style={{ marginTop: '1rem' }}>AI-generated. Research use only.</p>
          </div>
        )}
      </div>
    </div>
  );
}
