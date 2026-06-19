import { useState } from 'react'
import { AIRecommendationCard } from './AIRecommendationCard'

type HomePageProps = {
  preferences: { destination: string; travelStyle: string; budget: string }
  setPreferences: React.Dispatch<React.SetStateAction<{ destination: string; travelStyle: string; budget: string }>>
}

const exampleRecommendations = [
  {
    title: 'Paris in Spring',
    summary: 'A four-day experience curated for culture lovers with boutique stays, museum highlights, and riverfront dining.',
    eta: '3 min read',
  },
  {
    title: 'Pacific Coast Road Trip',
    summary: 'A flexible itinerary from San Francisco to San Diego with coastal hikes, local markets, and boutique hotels.',
    eta: '4 min read',
  },
  {
    title: 'Tokyo Weekend Refresh',
    summary: 'A smart blend of art, dining, and unplugged city discovery for travelers who value design and efficiency.',
    eta: '3 min read',
  },
]

export function HomePage({ preferences, setPreferences }: HomePageProps) {
  const [destination, setDestination] = useState(preferences.destination)

  function handleUpdatePreferences() {
    setPreferences({ ...preferences, destination })
  }

  return (
    <section className="home-page">
      <div className="hero-panel">
        <div>
          <p className="eyebrow">AI-Powered Travel Planning</p>
          <h1>Plan your next trip with personalized recommendations and fast bookings.</h1>
          <p className="hero-copy">
            Discover tailored destinations, build a day-by-day itinerary, and book travel almost instantly with AI guidance.
          </p>
          <div className="input-group">
            <label htmlFor="destination">Preferred destination</label>
            <input
              id="destination"
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
              placeholder="Tokyo, Lisbon, or Costa Rica"
            />
            <button className="primary-button" type="button" onClick={handleUpdatePreferences}>Update</button>
          </div>
        </div>
      </div>

      <div className="recommendations-block">
        <div className="section-header">
          <h2>Travel ideas tuned to your style</h2>
          <p>Start from smart suggestions and customize every stop before you book.</p>
        </div>
        <div className="recommendation-grid">
          {exampleRecommendations.map((item) => (
            <AIRecommendationCard key={item.title} title={item.title} summary={item.summary} eta={item.eta} />
          ))}
        </div>
      </div>
    </section>
  )
}