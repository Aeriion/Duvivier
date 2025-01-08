'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '../context/UserContext'

export default function HomePage() {
  const [tempUsername, setTempUsername] = useState('')
  const { setUsername } = useUser()
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (tempUsername.trim()) {
      setUsername(tempUsername.trim())
      router.push('/chat')  // on va sur la page de chat
    }
  }

  return (
    <main className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">Bienvenue sur le Chat</h1>
      <form onSubmit={handleSubmit} className="space-x-2">
        <input
          type="text"
          placeholder="Entrez votre pseudo..."
          value={tempUsername}
          onChange={(e) => setTempUsername(e.target.value)}
          className="border rounded p-2"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Continuer
        </button>
      </form>
    </main>
  )
}