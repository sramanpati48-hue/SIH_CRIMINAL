"use client";

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { ShieldAlert, LogIn, Lock } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await api.login(username, password);
      login(response.access_token, response.user);
    } catch (err: any) {
      setError(err.message || 'Failed to login. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-lg shadow-2xl p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="h-12 w-12 bg-blue-500/10 text-blue-500 rounded-full flex items-center justify-center mb-4">
            <ShieldAlert size={28} />
          </div>
          <h1 className="text-2xl font-semibold text-slate-100">SIH 26189</h1>
          <p className="text-slate-400 text-sm mt-1">Criminal Network Analysis System</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-md text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Username
            </label>
            <input
              type="text"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. test_investigator"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-md pl-4 pr-10 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <Lock size={16} className="absolute right-3 top-3 text-slate-500" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 rounded-md flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
            ) : (
              <>
                <LogIn size={18} className="mr-2" />
                Sign In
              </>
            )}
          </button>
        </form>
        
        <div className="mt-8 pt-6 border-t border-slate-800 text-xs text-slate-500 text-center">
          Prototype Mode: Use test credentials <br/>
          (test_admin, test_investigator, test_analyst, test_reviewer)<br/>
          Password: testpassword
        </div>
      </div>
    </div>
  );
}
