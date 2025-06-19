import axios from 'axios';

const API_BASE = '/api'; // Adjust as needed for backend proxy

export async function postAnalyze(input) {
  const formData = new FormData();
  if (input.url) formData.append('url', input.url);
  if (input.file && input.file.length > 0) formData.append('file', input.file[0]);
  const res = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data; // { jobId }
}

export async function getStatus(jobId) {
  const res = await axios.get(`${API_BASE}/status/${jobId}`);
  return res.data; // { status }
}

export async function getResults(jobId) {
  const res = await axios.get(`${API_BASE}/results/${jobId}`);
  return res.data; // { bias_score, bias_label, sentiment_score, sentiment_label, language_flags }
}

export async function getHistory(userId) {
  const res = await axios.get(`${API_BASE}/history`, { params: { userId } });
  return res.data; // [{...}]
} 