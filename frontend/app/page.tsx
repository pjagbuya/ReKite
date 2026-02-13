'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-2xl mx-auto text-center p-8">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">Re:Kite</h1>
        <p className="text-xl text-gray-600 mb-8">
          Master concepts through spaced repetition learning
        </p>
        <p className="text-gray-500 mb-8">
          A web application to help students emphasize remembering objective definitions
          using spaced repetition and AI-powered learning tools.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors font-medium"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
}
