"use client";

import React, { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { usePathname, useRouter } from 'next/navigation';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !user && pathname !== '/login') {
      router.push('/login');
    }
  }, [user, mounted, router, pathname]);

  // Set up API error interceptor globally or in api.ts
  // For session expiry, if API returns 401, we logout. 
  // We can hook window.addEventListener('unauthorized', logout) in a global way if we want.

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };
    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, [logout]);


  if (!mounted) return null;
  if (!user && pathname !== '/login') return null;

  return <>{children}</>;
};

export const Providers = ({ children }: { children: React.ReactNode }) => {
  return (
    <AuthProvider>
      <ProtectedRoute>
        {children}
      </ProtectedRoute>
    </AuthProvider>
  );
};
