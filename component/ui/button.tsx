'use client';

import React from 'react';

// On définit un type qui inclut les props d'un <button> standardS
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({ children, ...props }: ButtonProps) {
  return (
    <button
      // classes Tailwind ou CSS selon votre choix
      className="bg-blue-500 text-white px-4 py-2 rounded"
      {...props}
    >
      {children}
    </button>
  );
}