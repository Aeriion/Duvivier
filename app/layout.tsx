import { UserProvider } from '../context/UserContext'
import './globals.css'
import React from 'react'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body>
        <UserProvider>
          {children}
        </UserProvider>
      </body>
    </html>
  )
}