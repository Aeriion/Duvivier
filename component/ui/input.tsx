'use client';

import React from 'react';

// On définit un type qui inclut les props d'un <input> standard
type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function Input(props: InputProps) {
  return (
    <input
      className="border p-2"
      {...props}
    />
  );
}