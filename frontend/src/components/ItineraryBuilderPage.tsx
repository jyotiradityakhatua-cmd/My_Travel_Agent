import { useState } from 'react'
import {
  DndContext,
  DragEndEvent,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  arrayMove,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

const defaultItinerary = [
  { id: 'day-1', label: 'Landing & Local Dinner', description: 'Arrive, settle in, and enjoy a guided food walk.' },
  { id: 'day-2', label: 'City Highlights', description: 'Visit museums, markets, and riverside viewpoints.' },
  { id: 'day-3', label: 'Outdoor Escape', description: 'Take a coastal hike and a relaxed sunset sail.' },
]

function SortableItem({ id, label, description }: { id: string; label: string; description: string }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div className="itinerary-item" ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div>
        <strong>{label}</strong>
        <p>{description}</p>
      </div>
      <span className="drag-handle">⇅</span>
    </div>
  )
}

export function ItineraryBuilderPage() {
  const [planItems, setPlanItems] = useState(defaultItinerary)
  const [newStop, setNewStop] = useState('Sunset beach walk')
  const sensors = useSensors(useSensor(PointerSensor))

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (over && active.id !== over.id) {
      setPlanItems((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  function addStop() {
    const id = `day-${planItems.length + 1}`
    setPlanItems((items) => [...items, { id, label: newStop, description: 'Custom stop added to your day-by-day plan.' }])
    setNewStop('')
  }

  return (
    <section className="itinerary-page">
      <div className="section-header">
        <div>
          <p className="eyebrow">Interactive itinerary</p>
          <h1>Build your trip step-by-step with drag and drop ease.</h1>
        </div>
        <p className="hero-copy">
          Rearrange daily experiences, add custom stops, and keep your route aligned with what matters most.
        </p>
      </div>

      <div className="itinerary-grid">
        <div className="itinerary-panel">
          <div className="panel-header">
            <h2>Trip sequence</h2>
            <p>Drag items to reorder your schedule—from arrival to departure.</p>
          </div>
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={planItems.map((item) => item.id)} strategy={verticalListSortingStrategy}>
              {planItems.map((item) => (
                <SortableItem key={item.id} id={item.id} label={item.label} description={item.description} />
              ))}
            </SortableContext>
          </DndContext>

          <div className="add-stop">
            <label htmlFor="new-stop">Add a new stop</label>
            <input id="new-stop" value={newStop} onChange={(event) => setNewStop(event.target.value)} placeholder="E.g. Afternoon cooking class" />
            <button className="primary-button" type="button" onClick={addStop} disabled={!newStop.trim()}>Add stop</button>
          </div>
        </div>

        <div className="itinerary-details">
          <div className="section-card">
            <h2>Plan details</h2>
            <p>Keep your core itinerary details visible while you adjust timing and activities.</p>
            <dl>
              <div>
                <dt>Trip length</dt>
                <dd>3 days</dd>
              </div>
              <div>
                <dt>Recommended region</dt>
                <dd>Bay Area coastal route</dd>
              </div>
              <div>
                <dt>Top priority</dt>
                <dd>Local food & city culture</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </section>
  )
}