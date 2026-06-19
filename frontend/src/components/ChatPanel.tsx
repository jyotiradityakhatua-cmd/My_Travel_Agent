import { useEffect, useState } from 'react'
import { getChatHistory, sendChatMessage } from '../api/api'

type ChatPanelProps = {
  userId: string
}

type Message = {
  id: string
  role: 'user' | 'assistant'
  text: string
}

export function ChatPanel({ userId }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [chatId, setChatId] = useState<string>('')
  const [draft, setDraft] = useState('Tell me the ideal 3-day trip plan for my next vacation.')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!chatId) return

    getChatHistory(chatId)
      .then((history) => {
        setMessages(
          history.map((item: any) => ({
            id: String(item.id),
            role: item.role,
            text: item.message,
          })),
        )
      })
      .catch(() => {
        // ignore initial history failures for now
      })
  }, [chatId])

  async function handleSend() {
    if (!draft.trim()) return
    setError(null)
    setIsSending(true)

    const userMessage: Message = {
      id: `u-${Date.now()}`,
      role: 'user',
      text: draft,
    }

    setMessages((current) => [...current, userMessage])
    setDraft('')

    try {
      const { response, chatId: newChatId } = await sendChatMessage(userId, userMessage.text, chatId || undefined)
      if (newChatId) {
        setChatId(newChatId)
      }

      setMessages((current) => [
        ...current,
        {
          id: `a-${Date.now()}`,
          role: 'assistant',
          text: response,
        },
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to send message')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="section-card chat-panel">
      <div className="section-header">
        <div>
          <h2>AI travel assistant</h2>
          <p>Ask about flights, hotels, or itinerary suggestions and get a smart response from the backend.</p>
        </div>
      </div>

      <div className="chat-history">
        {messages.length === 0 && <p className="empty-state">Type anything to start your trip planning conversation.</p>}
        {messages.map((message) => (
          <div key={message.id} className={`chat-message chat-message--${message.role}`}>
            <div className="chat-message__label">{message.role === 'user' ? 'You' : 'AI'}</div>
            <div>{message.text}</div>
          </div>
        ))}
      </div>

      {error && <div className="api-error">{error}</div>}

      <div className="chat-input-row">
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask the assistant for travel recommendations"
          disabled={isSending}
        />
        <button className="primary-button" type="button" onClick={handleSend} disabled={isSending || !draft.trim()}>
          {isSending ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  )
}