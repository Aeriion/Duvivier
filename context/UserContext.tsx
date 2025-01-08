'use client';

import React, { createContext, useState, useContext, ReactNode } from 'react';

type UserContextType = {
  username: string;
  setUsername: (name: string) => void;
};

const UserContext = createContext<UserContextType>({
  username: '',
  setUsername: () => {},
});

export function UserProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState('');

  return (
    <UserContext.Provider value={{ username, setUsername }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}