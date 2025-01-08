const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const PORT = process.env.PORT || 3001;
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*", // ou un domaine spécifique ex: ["http://localhost:3000"]
    methods: ["GET", "POST"]
  }
});

// Quand un client se connecte
io.on('connection', (socket) => {
  console.log(`Client connecté : ${socket.id}`);

  // Quand on reçoit un message
  socket.on('chatMessage', (msg) => {
    console.log(`Message reçu : ${msg}`);
    // On relaie le message à tous les clients
    io.emit('chatMessage', msg);
  });

  // Déconnexion
  socket.on('disconnect', () => {
    console.log(`Client déconnecté : ${socket.id}`);
  });
});

// Lancement du serveur
server.listen(PORT, () => {
  console.log(`Serveur Socket.IO démarré sur le port ${PORT}`);
});