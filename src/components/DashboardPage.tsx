import { useMemo } from 'react'
import { ChatPanel } from './ChatPanel'

type DashboardPageProps = {
  user: { user_id: string; username: string } | null
  preferences: { destination: string; travelStyle: string; budget: string }
}

const sampleTrips = [
  {
    title: 'Mediterranean Escape',
    destination: 'Barcelona, Spain',
    dates: 'May 18 - May 24',
    status: 'Draft',
  },
  {
    title: 'Kyoto Highlights',
    destination: 'Kyoto, Japan',
    dates: 'Jul 10 - Jul 16',
    status: 'Confirmed',
  },
]

export function DashboardPage({ user, preferences }: DashboardPageProps) {
  const greeting = useMemo(() => (user ? `Hey ${user.username},` : 'Welcome,'), [user])

  return (
    <section className="dashboard-page">
      <div className="dashboard-hero">
        <div>
          <p className="eyebrow">Trip center</p>
          <h1>{greeting} keep your travel planning organized.</h1>
          <p className="hero-copy">
            Link flight options, hotel stays, and itinerary smartly with AI-powered planning suggestions.
          </p>
        </div>
        <div className="profile-card">
          <p>Travel strategy</p>
          <strong>{preferences.travelStyle}</strong>
          <small>Budget: {preferences.budget}</small>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="section-card dash-summary">
          <div className="section-header">
            <div>
              <h2>Your latest trip plans</h2>
              <p>Review saved journeys and continue your planning workflow.</p>
            </div>
            <button className="primary-button">Create new trip</button>
          </div>

          <div className="trip-table">
            {sampleTrips.map((trip) => (
              <div key={trip.title} className="trip-row">
                <div>
                  <h3>{trip.title}</h3>
                  <p>{trip.destination}</p>
                </div>
                <div>
                  <span>{trip.dates}</span>
                  <span className="status-pill">{trip.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {user && <ChatPanel userId={user.user_id} />}
      </div>
    </section>
  )
}