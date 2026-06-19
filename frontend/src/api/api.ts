const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/chat'

function parseChatResponse(raw: string) {
  const marker = '<!--CHAT_ID:'
  const markerIndex = raw.lastIndexOf(marker)
  let chatId = ''
  let response = raw

  if (markerIndex >= 0) {
    const tail = raw.substring(markerIndex + marker.length)
    const endIndex = tail.indexOf('-->')
    chatId = endIndex >= 0 ? tail.substring(0, endIndex) : tail
    response = raw.substring(0, markerIndex).trim()
  }

  return { response, chatId }
}

async function safeJson(response: Response) {
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `${response.status} ${response.statusText}`)
  }
  return response.json()
}

export async function loginUser(username: string, password: string) {
  const params = new URLSearchParams({ username, password })
  const response = await fetch(`${API_BASE}/login?${params.toString()}`, {
    method: 'POST',
  })
  return safeJson(response)
}

export async function registerUser(username: string, password: string) {
  const params = new URLSearchParams({ username, password })
  const response = await fetch(`${API_BASE}/register?${params.toString()}`, {
    method: 'POST',
  })
  return safeJson(response)
}

export async function sendChatMessage(userId: string, message: string, chatId?: string) {
  const body = { user_id: userId, message }
  if (chatId) {
    Object.assign(body, { chat_id: chatId })
  }

  const response = await fetch(`${API_BASE}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `${response.status} ${response.statusText}`)
  }

  const raw = await response.text()
  return parseChatResponse(raw)
}

export async function getUserChats(userId: string) {
  const response = await fetch(`${API_BASE}/users/${encodeURIComponent(userId)}/chats`)
  return safeJson(response)
}

export async function getChatHistory(chatId: string) {
  const response = await fetch(`${API_BASE}/history/${encodeURIComponent(chatId)}`)
  return safeJson(response)
}