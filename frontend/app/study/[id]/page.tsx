'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';
import NavBar from '@/components/NavBar';
import LoadingPage from '@/components/LoadingPage';

interface Card {
  id: number;
  concept: string;
  definition: string;
}

interface StudyResponse {
  card: Card | null;
  deck_name: string;
  cards_remaining: number;
}

interface ReviewResult {
  similarity_score: number;
  matched_keywords: string[];
  highlighted_user_answer: string;
  highlighted_definition: string;
}

export default function StudyPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const deckId = params.id as string;
  const cardId = searchParams.get('cardId'); // Get cardId from URL params
  const isSingleCardMode = !!cardId; // True if studying a specific card
  const { isAuthenticated, token, logout } = useAuthStore();
  
  const [currentCard, setCurrentCard] = useState<Card | null>(null);
  const [deckName, setDeckName] = useState('');
  const [cardsRemaining, setCardsRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [processing, setProcessing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [selectedQuality, setSelectedQuality] = useState<number | null>(null);
  const [paraphrases, setParaphrases] = useState<string[]>([]);
  const [showParaphrases, setShowParaphrases] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const fetchSingleCard = useCallback(async (cardIdToFetch: string) => {
    setLoading(true);
    setShowResults(false);
    setTranscription('');
    setReviewResult(null);
    setSelectedQuality(null);
    setParaphrases([]);
    setShowParaphrases(false);
    
    try {
      // Fetch the card
      const cardResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/card/${cardIdToFetch}`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      
      if (cardResponse.status === 401) {
        logout();
        router.push('/login');
        return;
      }
      
      if (cardResponse.ok) {
        const cardData = await cardResponse.json();
        setCurrentCard(cardData);
        setCardsRemaining(0);
        
        // Fetch deck info to get the deck name
        const deckResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/decks/${deckId}`,
          {
            headers: { 'Authorization': `Bearer ${token}` },
          }
        );
        
        if (deckResponse.ok) {
          const deckData = await deckResponse.json();
          setDeckName(deckData.name);
        }
      }
    } catch (error) {
      console.error('Failed to fetch card:', error);
    } finally {
      setLoading(false);
    }
  }, [token, deckId, logout, router]);

  const fetchNextCard = useCallback(async () => {
    setLoading(true);
    setShowResults(false);
    setTranscription('');
    setReviewResult(null);
    setSelectedQuality(null);
    setParaphrases([]);
    setShowParaphrases(false);
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/deck/${deckId}/next`,
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
        const data: StudyResponse = await response.json();
        setCurrentCard(data.card);
        setDeckName(data.deck_name);
        setCardsRemaining(data.cards_remaining);
      }
    } catch (error) {
      console.error('Failed to fetch next card:', error);
    } finally {
      setLoading(false);
    }
  }, [deckId, token, logout, router]);
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    
    // If cardId exists, fetch single card; otherwise fetch next card from deck
    if (isSingleCardMode && cardId) {
      fetchSingleCard(cardId);
    } else {
      fetchNextCard();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isSingleCardMode, cardId]);



  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    setProcessing(true);
    
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(',')[1];
        
        if (!base64Audio) {
          throw new Error('Failed to convert audio');
        }

        // Transcribe
        const transcribeResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/transcribe`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ audio_base64: base64Audio }),
          }
        );

        if (transcribeResponse.status === 401) {
          logout();
          router.push('/login');
          return;
        }

        if (transcribeResponse.ok) {
          const transcribeData = await transcribeResponse.json();
          setTranscription(transcribeData.transcript);
          
          // Evaluate answer
          await evaluateAnswer(transcribeData.transcript);
        }
      };
    } catch (error) {
      console.error('Transcription failed:', error);
      alert('Transcription failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const evaluateAnswer = async (userAnswer: string) => {
    if (!currentCard) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/evaluate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            user_answer: userAnswer,
            correct_definition: currentCard.definition,
          }),
        }
      );

      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }

      if (response.ok) {
        const result = await response.json();
        setReviewResult(result);
        setShowResults(true);
        
        // Suggest quality based on similarity
        const suggestedQuality = getSuggestedQuality(result.similarity_score);
        setSelectedQuality(suggestedQuality);
        
        // Fetch paraphrases
        await fetchParaphrases(currentCard.definition);
      }
    } catch (error) {
      console.error('Evaluation failed:', error);
    }
  };

  const getSuggestedQuality = (score: number): number => {
    if (score >= 0.85) return 3; // Easy
    if (score >= 0.70) return 2; // Normal
    if (score >= 0.50) return 1; // Hard
    return 0; // Again
  };

  const fetchParaphrases = async (definition: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/paraphrase`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ definition }),
        }
      );

      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setParaphrases(data.paraphrases);
      }
    } catch (error) {
      console.error('Failed to fetch paraphrases:', error);
    }
  };

  const submitReview = async (quality: number) => {
    if (!currentCard || !transcription) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/study/review`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            card_id: currentCard.id,
            user_answer: transcription,
            quality: quality,
          }),
        }
      );

      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }

      // If single card mode, go back to deck view
      if (isSingleCardMode) {
        router.push(`/deck/${deckId}`);
      } else {
        // Otherwise, move to next card in deck study mode
        fetchNextCard();
      }
    } catch (error) {
      console.error('Failed to submit review:', error);
    }
  };

  if (!isAuthenticated || loading) {
    return <LoadingPage title="Study Session" showBackToDashboard={true} />;
  }

  if (!currentCard) {
    // In single card mode, if no card, redirect back to deck
    if (isSingleCardMode) {
      router.push(`/deck/${deckId}`);
      return null;
    }
    
    // In deck study mode, show completion message
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4">🎉 All Done!</h2>
          <p className="text-gray-600 mb-6">No more cards to review in {deckName} right now.</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar 
        title={deckName || 'Study'} 
        showBackToDashboard={true}
        rightContent={
          !isSingleCardMode && (
            <span className="text-gray-600">
              {cardsRemaining} card{cardsRemaining !== 1 ? 's' : ''} remaining
            </span>
          )
        }
      />

      <main className="max-w-4xl mx-auto py-12 px-4">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          {!showResults ? (
            <>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Define: {currentCard.concept}
                </h2>
                <p className="text-gray-600">
                  Click the microphone button and speak your answer
                </p>
              </div>

              <div className="flex flex-col items-center space-y-6">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={processing}
                  className={`w-32 h-32 rounded-full flex items-center justify-center text-white text-4xl transition-all ${
                    isRecording
                      ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                      : processing
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  }`}
                >
                  {processing ? '⏳' : isRecording ? '⏹' : '🎤'}
                </button>

                {processing && (
                  <p className="text-gray-600">Processing your answer...</p>
                )}

                {transcription && !showResults && (
                  <div className="w-full bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Your answer:</p>
                    <p className="text-gray-900">{transcription}</p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Results</h3>
                
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-700 font-medium">Similarity Score</span>
                    <span className="text-2xl font-bold text-indigo-600">
                      {((reviewResult?.similarity_score || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-indigo-600 h-4 rounded-full transition-all"
                      style={{ width: `${(reviewResult?.similarity_score || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-2">Your Answer:</p>
                    <p
                      className="text-gray-900"
                      dangerouslySetInnerHTML={{ __html: reviewResult?.highlighted_user_answer || transcription }}
                    />
                  </div>

                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-2">Correct Definition:</p>
                    <p
                      className="text-gray-900"
                      dangerouslySetInnerHTML={{ __html: reviewResult?.highlighted_definition || currentCard.definition }}
                    />
                  </div>

                  {reviewResult && reviewResult.matched_keywords.length > 0 && (
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-2">Matched Keywords:</p>
                      <div className="flex flex-wrap gap-2">
                        {reviewResult.matched_keywords.map((keyword, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-yellow-200 text-yellow-900 rounded-full text-sm"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Paraphrases Section */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-3">
                    <p className="text-sm font-medium text-gray-700">Alternative Meanings:</p>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setShowParaphrases(!showParaphrases)}
                        className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm"
                      >
                        {showParaphrases ? 'Hide' : 'Show'}
                      </button>
                      {showParaphrases && currentCard && (
                        <button
                          onClick={() => fetchParaphrases(currentCard.definition)}
                          className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm"
                          title="Get new paraphrases"
                        >
                          🔄 Refresh
                        </button>
                      )}
                    </div>
                  </div>
                  {showParaphrases && (
                    <div className="space-y-2 mt-3">
                      {paraphrases.length > 0 ? (
                        paraphrases.map((paraphrase, index) => (
                          <div key={index} className="bg-white p-3 rounded-md border border-purple-200">
                            <p className="text-gray-700">{index + 1}. {paraphrase}</p>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-600 text-sm italic">Loading paraphrases...</p>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  <p className="text-gray-700 font-medium mb-3">How did you do?</p>
                  <div className="grid grid-cols-4 gap-3">
                    <button
                      onClick={() => submitReview(0)}
                      className="px-4 py-3 rounded-lg font-medium transition-all bg-black text-white hover:bg-gray-800"
                    >
                      Again
                    </button>
                    <button
                      onClick={() => submitReview(1)}
                      className="px-4 py-3 rounded-lg font-medium transition-all bg-red-600 text-white hover:bg-red-700"
                    >
                      Hard
                    </button>
                    <button
                      onClick={() => submitReview(2)}
                      className="px-4 py-3 rounded-lg font-medium transition-all bg-orange-500 text-white hover:bg-orange-600"
                    >
                      Normal
                    </button>
                    <button
                      onClick={() => submitReview(3)}
                      className="px-4 py-3 rounded-lg font-medium transition-all bg-green-600 text-white hover:bg-green-700"
                    >
                      Easy
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      <style jsx>{`
        mark {
          background-color: #fef08a;
          padding: 2px 4px;
          border-radius: 3px;
        }
      `}</style>
    </div>
  );
}
