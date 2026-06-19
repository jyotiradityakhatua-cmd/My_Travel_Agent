const flightOptions = [
  {
    id: 'flight-1',
    route: 'SFO → LAX',
    airline: 'West Coast Air',
    price: '$219',
    details: 'Direct, 1h 20m, morning departure',
  },
  {
    id: 'flight-2',
    route: 'SFO → PDX',
    airline: 'Air Pacific',
    price: '$245',
    details: 'One stop, 2h 45m',
  },
]

import { useState } from 'react'

const hotelOptions = [
  {
    id: 'hotel-1',
    name: 'Harbor View Suites',
    price: '$179/night',
    features: 'Breakfast included, downtown walkability',
  },
  {
    id: 'hotel-2',
    name: 'Artisan Loft Hotel',
    price: '$214/night',
    features: 'Rooftop lounge, wellness center',
  },
]

export function BookingPage() {
  const [selectedOffer, setSelectedOffer] = useState('')

  return (
    <section className="booking-page">
      <div className="section-header">
        <div>
          <p className="eyebrow">Booking hub</p>
          <h1>Review travel offers and lock in your next stay.</h1>
        </div>
        <p className="hero-copy">These curated options are designed to match your itinerary and budget preferences.</p>
      </div>

      <div className="booking-grid">
        <div className="section-card booking-panel">
          <h2>Featured flight options</h2>
          {flightOptions.map((option) => (
            <div key={option.id} className="booking-card">
              <div>
                <strong>{option.route}</strong>
                <p>{option.airline}</p>
                <small>{option.details}</small>
              </div>
              <div>
                <span className="price-tag">{option.price}</span>
                <button className="primary-button" type="button" onClick={() => setSelectedOffer(`${option.route} selected`)}>
                  Select
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="section-card booking-panel">
          <h2>Top hotels</h2>
          {hotelOptions.map((hotel) => (
            <div key={hotel.id} className="booking-card">
              <div>
                <strong>{hotel.name}</strong>
                <p>{hotel.features}</p>
              </div>
              <div>
                <span className="price-tag">{hotel.price}</span>
                <button className="secondary-button" type="button" onClick={() => setSelectedOffer(`${hotel.name} selected`)}>
                  View details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedOffer && <div className="selection-note">{selectedOffer}</div>}
    </section>
  )
}