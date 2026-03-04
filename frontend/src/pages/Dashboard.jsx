import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: '2rem' }}>
        <h1 style={{ marginTop: 0 }}>Dashboard</h1>
        <p>Hello, <strong>{user?.username}</strong>. You’re authenticated via JWT in HttpOnly cookies.</p>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
          Email: {user?.email || '—'}
        </p>
        <button type="button" className="btn btn-secondary" onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </div>
  )
}
