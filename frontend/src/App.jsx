import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ThrowsList from './pages/ThrowsList'
import AnalysisPage from './pages/AnalysisPage'
import ZeroOnePage from './pages/ZeroOnePage'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ThrowsList />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/game" element={<ZeroOnePage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
