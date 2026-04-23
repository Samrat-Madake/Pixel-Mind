import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { ThemeToggleProvider } from './theme/ThemeContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeToggleProvider>
      <App />
    </ThemeToggleProvider>
  </StrictMode>,
)
