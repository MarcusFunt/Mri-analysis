import React, { useState } from 'react';
import { uploadZip, startAnalyze, getResult } from './api';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState('');
  const [result, setResult] = useState<any>(null);

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
        <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
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
            <p><strong>{result.normal ? 'Normal' : 'Abnormal'}</strong> ({Math.round(result.confidence * 100)}%)</p>
            <ul>
              {result.findings.map((f: string, i: number) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
            <div>
              <a href={result.downloads.dicom_sr}>DICOM SR</a><br/>
              {result.downloads.dicom_seg && <a href={result.downloads.dicom_seg}>DICOM SEG</a>}<br/>
              <a href={result.downloads.json}>JSON</a>
            </div>
            <p style={{ marginTop: '1rem' }}>AI-generated. Research use only.</p>
          </div>
        )}
      </div>
    </div>
  );
}
