import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import ArticleInput from './components/ArticleInput'
import AnalysisStatus from './components/AnalysisStatus'
import ResultsView from './components/ResultsView'
import HistoryList from './components/HistoryList'
import { Container, Box, Typography, Paper } from '@mui/material'
import { postAnalyze, getStatus, getResults, getHistory } from './api'

function App() {
  const [status, setStatus] = useState('Idle')
  const [polling, setPolling] = useState(false)
  const [results, setResults] = useState(null)
  const [history, setHistoryState] = useState([])
  const [error, setError] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [userId] = useState('demo-user') // Replace with real user logic

  useEffect(() => {
    // Load history on mount
    getHistory(userId)
      .then(setHistoryState)
      .catch(() => setHistoryState([]))
  }, [userId])

  useEffect(() => {
    let interval
    if (polling && jobId) {
      interval = setInterval(async () => {
        try {
          const { status: jobStatus } = await getStatus(jobId)
          setStatus(jobStatus)
          if (jobStatus === 'complete') {
            clearInterval(interval)
            setPolling(false)
            const res = await getResults(jobId)
            setResults(res)
            // Optionally refresh history
            getHistory(userId).then(setHistoryState)
          }
        } catch (err) {
          setError('Error polling job status')
          setPolling(false)
          clearInterval(interval)
        }
      }, 1500)
    }
    return () => clearInterval(interval)
  }, [polling, jobId, userId])

  const handleAnalyze = async (input) => {
    setStatus('Submitting...')
    setPolling(false)
    setResults(null)
    setError(null)
    try {
      const { jobId } = await postAnalyze(input)
      setJobId(jobId)
      setStatus('Queued')
      setPolling(true)
    } catch (err) {
      setError('Failed to submit article')
      setStatus('Idle')
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" align="center" gutterBottom>Biased Analyzer</Typography>
        <ArticleInput onSubmit={handleAnalyze} />
        <AnalysisStatus status={status} polling={polling} error={error} />
        <ResultsView results={results} />
        <Typography variant="h6" sx={{ mt: 4 }}>History</Typography>
        <HistoryList history={history} />
      </Paper>
    </Container>
  )
}

export default App
