'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';
import NavBar from '@/components/NavBar';
import LoadingPage from '@/components/LoadingPage';

interface Deck {
  id: number;
  name: string;
  description: string | null;
  card_count: number;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, logout } = useAuthStore();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewDeck, setShowNewDeck] = useState(false);
  const [newDeckName, setNewDeckName] = useState('');
  const [newDeckDescription, setNewDeckDescription] = useState('');
  
  const fetchDecks = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/decks/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        setDecks(data);
      }
    } catch (error) {
      console.error('Failed to fetch decks:', error);
    } finally {
      setLoading(false);
    }
  }, [token, logout, router]);
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else {
      fetchDecks();
    }
  }, [isAuthenticated, router, fetchDecks]);



  const createDeck = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/decks/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newDeckName,
          description: newDeckDescription || null,
        }),
      });
      
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      
      if (response.ok) {
        setNewDeckName('');
        setNewDeckDescription('');
        setShowNewDeck(false);
        fetchDecks();
      }
    } catch (error) {
      console.error('Failed to create deck:', error);
    }
  };

  const resetDeckProgress = async (deckId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Reset all progress for this deck? This cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/progress/deck/${deckId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      
      if (response.ok) {
        alert('Deck progress reset successfully!');
        fetchDecks();
      }
    } catch (error) {
      console.error('Failed to reset deck progress:', error);
      alert('Failed to reset progress');
    }
  };

  if (!isAuthenticated || loading) {
    return <LoadingPage title="Re:Kite" />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar title="Re:Kite" />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">My Decks</h2>
            <button
              onClick={() => setShowNewDeck(!showNewDeck)}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              + New Deck
            </button>
          </div>

          {showNewDeck && (
            <div className="bg-white p-6 rounded-lg shadow mb-6">
              <h3 className="text-lg text-gray-900 font-semibold mb-4">Create New Deck</h3>
              <form onSubmit={createDeck}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Deck Name *
                  </label>
                  <input
                    type="text"
                    value={newDeckName}
                    onChange={(e) => setNewDeckName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newDeckDescription}
                    onChange={(e) => setNewDeckDescription(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
                    rows={3}
                  />
                </div>
                <div className="flex space-x-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNewDeck(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {decks.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow text-center">
              <p className="text-gray-600">No decks yet. Create your first deck to get started!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {decks.map((deck) => (
                <div
                  key={deck.id}
                  onClick={() => router.push(`/deck/${deck.id}`)}
                  className="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition-shadow"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{deck.name}</h3>
                  {deck.description && (
                    <p className="text-gray-600 mb-4 text-sm">{deck.description}</p>
                  )}
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>{deck.card_count} cards</span>
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/study/${deck.id}`);
                        }}
                        className="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
                      >
                        Study
                      </button>
                      <button
                        onClick={(e) => resetDeckProgress(deck.id, e)}
                        className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                        title="Reset progress"
                      >
                        🔄
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
