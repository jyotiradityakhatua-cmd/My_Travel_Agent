import { Link } from 'react-router-dom'

type NavBarProps = {
  user: { user_id: string; username: string } | null
  onLogout: () => void
}

export function NavBar({ user, onLogout }: NavBarProps) {
  return (
    <header className="navbar">
      <div className="logo">AI Travel Planner</div>
      <nav className="nav-links">
        <Link to="/">Discover</Link>
        <Link to="/dashboard">Trip Center</Link>
        <Link to="/itinerary">Itinerary</Link>
        <Link to="/booking">Bookings</Link>
      </nav>
      <div className="nav-user">
        {user ? (
          <>
            <span>Welcome, {user.username}</span>
            <button className="secondary-button" onClick={onLogout}>Sign out</button>
          </>
        ) : (
          <Link to="/login" className="primary-button">Sign in</Link>
        )}
      </div>
    </header>
  )
}