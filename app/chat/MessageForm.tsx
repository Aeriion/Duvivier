'use client'

import React, { useState, useEffect } from 'react'
import { useUser } from '../../context/UserContext'
import { Button } from '../../component/ui/button'
import { Input } from '../../component/ui/input'
import { io, Socket } from 'socket.io-client'

let socket: Socket | null = null

export default function MessageForm() {
  const [message, setMessage] = useState('')
  const { username } = useUser()

  useEffect(() => {
    // On initialise la connexion Socket.IO au serveur Flask seulement une fois
    if (!socket) {
      // Adapter si ton serveur est sur une autre IP/URL
      socket = io('http://localhost:5001')
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      // On prefixe le message par le pseudo
      const fullMsg = `${username}: ${message.trim()}`
      socket?.emit('message', fullMsg)  // côté Flask, @socketio.on('message')
      setMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2 mt-4">
      <Input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Tapez votre message..."
        className="flex-grow"
      />
      <Button type="submit">Envoyer</Button>
    </form>
  )
}