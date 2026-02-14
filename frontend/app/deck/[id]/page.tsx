'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';
import NavBar from '@/components/NavBar';
import LoadingPage from '@/components/LoadingPage';

interface Card {
  id: number;
  concept: string;
  definition: string;
  next_review: string | null;
}

interface Deck {
  id: number;
  name: string;
  description: string | null;
  card_count: number;
}

export default function DeckPage() {
  const router = useRouter();
  const params = useParams();
  const deckId = params.id as string;
  const { isAuthenticated, token, logout } = useAuthStore();
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewCard, setShowNewCard] = useState(false);
  const [newConcept, setNewConcept] = useState('');
  const [newDefinition, setNewDefinition] = useState('');
  
  const fetchDeck = useCallback(async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/decks/${deckId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      if (response.ok) {
        const data = await response.json();
        setDeck(data);
      }
    } catch (error) {
      console.error('Failed to fetch deck:', error);
    }
  }, [deckId, token, logout, router]);

  const fetchCards = useCallback(async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cards/deck/${deckId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      if (response.ok) {
        const data = await response.json();
        setCards(data);
      }
    } catch (error) {
      console.error('Failed to fetch cards:', error);
    } finally {
      setLoading(false);
    }
  }, [deckId, token, logout, router]);
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else {
      fetchDeck();
      fetchCards();
    }
  }, [isAuthenticated, deckId, router, fetchDeck, fetchCards]);





  const createCard = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cards/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            deck_id: parseInt(deckId),
            concept: newConcept,
            definition: newDefinition,
          }),
        }
      );
      
      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      
      if (response.ok) {
        setNewConcept('');
        setNewDefinition('');
        setShowNewCard(false);
        fetchCards();
        fetchDeck();
      }
    } catch (error) {
      console.error('Failed to create card:', error);
    }
  };

  const resetCardProgress = async (cardId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Reset progress for this card?')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/progress/card/${cardId}`,
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
        alert('Card progress reset successfully!');
      }
    } catch (error) {
      console.error('Failed to reset card progress:', error);
      alert('Failed to reset progress');
    }
  };

  const deleteCard = async (cardId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this card? This cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/cards/${cardId}`,
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
        alert('Card deleted successfully!');
        fetchCards();
        fetchDeck();
      } else {
        alert('Failed to delete card');
      }
    } catch (error) {
      console.error('Failed to delete card:', error);
      alert('Failed to delete card');
    }
  };

  const deleteDeck = async () => {
    if (!confirm('Are you sure you want to delete this entire deck? This will delete all cards and cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/decks/${deckId}`,
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
        alert('Deck deleted successfully!');
        router.push('/dashboard');
      } else {
        alert('Failed to delete deck');
      }
    } catch (error) {
      console.error('Failed to delete deck:', error);
      alert('Failed to delete deck');
    }
  };

  if (!isAuthenticated || loading) {
    return <LoadingPage title="Deck" showBackToDashboard={true} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar 
        title={deck?.name || 'Deck'} 
        showBackToDashboard={true}
        rightContent={
          <div className="flex space-x-2">
            <button
              onClick={() => router.push(`/study/${deckId}`)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Start Studying
            </button>
            <button
              onClick={deleteDeck}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              title="Delete deck"
            >
              Delete Deck
            </button>
          </div>
        }
      />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {deck?.description && (
            <p className="text-gray-600 mb-6">{deck.description}</p>
          )}

          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Cards ({deck?.card_count || 0})
            </h2>
            <button
              onClick={() => setShowNewCard(!showNewCard)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              + New Card
            </button>
          </div>

          {showNewCard && (
            <div className="bg-white p-6 rounded-lg shadow mb-6">
              <h3 className="text-lg text-gray-900 font-semibold mb-4">Create New Card</h3>
              <form onSubmit={createCard}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Concept/Term *
                  </label>
                  <input
                    type="text"
                    value={newConcept}
                    onChange={(e) => setNewConcept(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
                    placeholder="e.g., Photosynthesis"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Definition *
                  </label>
                  <textarea
                    value={newDefinition}
                    onChange={(e) => setNewDefinition(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
                    rows={4}
                    placeholder="e.g., The process by which plants convert light energy into chemical energy"
                    required
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
                    onClick={() => setShowNewCard(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {cards.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow text-center">
              <p className="text-gray-600">No cards yet. Create your first card to get started!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cards.map((card) => (
                <div key={card.id} className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{card.concept}</h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/study/${deckId}?cardId=${card.id}`);
                        }}
                        className="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
                      >
                        Study
                      </button>
                      <button
                        onClick={(e) => resetCardProgress(card.id, e)}
                        className="px-3 py-1 bg-orange-600 text-white rounded-md hover:bg-orange-700 text-sm"
                        title="Reset progress"
                      >
                        🔄
                      </button>
                      <button
                        onClick={(e) => deleteCard(card.id, e)}
                        className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                        title="Delete card"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-600">{card.definition}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
