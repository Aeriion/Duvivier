'use client'

import React, { useState, useEffect } from 'react'
import { io, Socket } from 'socket.io-client'

// On se sert de la même instance, ou on en crée une ?
let socket: Socket | null = null

export default function MessageList() {
  const [messages, setMessages] = useState<string[]>([])

  useEffect(() => {
    if (!socket) {
      socket = io('http://localhost:5001')
    }
    // Écouter l’événement 'message' renvoyé par Flask (socketio.send(msg))
    socket.on('message', (msg: string) => {
      setMessages((prev) => [...prev, msg])
    })

    // Cleanup pour éviter les doublons
    return () => {
      socket?.off('message')
    }
  }, [])

  return (
    <div className="flex flex-col flex-grow bg-white p-4 overflow-auto">
      {messages.map((m, index) => (
        <div key={index} className="my-1">
          {m}
        </div>
      ))}
    </div>
  )
}