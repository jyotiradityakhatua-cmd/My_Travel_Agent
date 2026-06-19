type AIRecommendationCardProps = {
  title: string
  summary: string
  eta: string
}

export function AIRecommendationCard({ title, summary, eta }: AIRecommendationCardProps) {
  return (
    <article className="recommendation-card">
      <div className="recommendation-card__meta">
        <span className="chip">AI suggestion</span>
        <span>{eta}</span>
      </div>
      <h3>{title}</h3>
      <p>{summary}</p>
      <button className="secondary-button">Save idea</button>
    </article>
  )
}