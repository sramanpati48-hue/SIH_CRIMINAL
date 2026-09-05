"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

type Role = 'ADMINISTRATOR' | 'INVESTIGATOR' | 'ANALYST' | 'REVIEWER';

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Keep token in memory outside React state as well to inject into API calls
let memoryToken: string | null = null;

export const setMemoryToken = (token: string | null) => {
  memoryToken = token;
};

export const getMemoryToken = () => {
  return memoryToken;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const router = useRouter();

  const login = useCallback((newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    setMemoryToken(newToken);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    setMemoryToken(null);
    router.push('/login');
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
