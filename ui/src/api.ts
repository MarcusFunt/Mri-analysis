export async function uploadZip(file: File): Promise<string> {
  const form = new FormData();
  form.append('study', file);
  const res = await fetch('/upload', { method: 'POST', body: form });
  const data = await res.json();
  return data.job_id as string;
}

export async function startAnalyze(jobId: string): Promise<void> {
  await fetch(`/analyze/${jobId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ anatomy: 'brain' })
  });
}

export async function getResult(jobId: string) {
  const res = await fetch(`/result/${jobId}`);
  return res.json();
}
