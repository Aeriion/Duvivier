'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '../../context/UserContext'
import MessageList from './MessageList'
import MessageForm from './MessageForm'

export default function ChatPage() {
  const { username } = useUser()
  const router = useRouter()

  useEffect(() => {
    // Si pas de pseudo dans le UserContext, on retourne à l'accueil
    if (!username) {
      router.push('/')
    }
  }, [username, router])

  // Empêche l’affichage si pas de pseudo
  if (!username) {
    return null
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Chat en direct</h1>
        </div>
      </header>
      <main className="flex-grow container mx-auto py-6 px-4 sm:px-6 lg:px-8 flex flex-col">
        <MessageList />
        <MessageForm />
      </main>
    </div>
  )
}
