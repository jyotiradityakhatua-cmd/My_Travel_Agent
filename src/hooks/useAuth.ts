import { useState } from 'react'

type User = { user_id: string; username: string } | null

export function useAuth() {
  const [user, setUser] = useState<User>(null)

  function login(userData: User) {
    setUser(userData)
  }

  function logout() {
    setUser(null)
  }

  return { user, login, logout }
}