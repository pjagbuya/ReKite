'use client';

import NavBar from '@/components/NavBar';

interface LoadingPageProps {
  title?: string;
  showBackToDashboard?: boolean;
}

export default function LoadingPage({ title = 'Loading...', showBackToDashboard = false }: LoadingPageProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar title={title} showBackToDashboard={showBackToDashboard} />
      
      <main className="max-w-7xl mx-auto py-12 px-4">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
          <p className="text-gray-600 text-lg">Loading...</p>
        </div>
      </main>
    </div>
  );
}
