'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

interface NavBarProps {
  title: string;
  showBackToDashboard?: boolean;
  backPath?: string;
  rightContent?: React.ReactNode;
}

export default function NavBar({ title, showBackToDashboard = false, backPath, rightContent }: NavBarProps) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-4">
            {showBackToDashboard && (
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-600 hover:text-gray-900 font-medium cursor-pointer"
              >
                🏠 Dashboard
              </button>
            )}
            {backPath && !showBackToDashboard && (
              <button
                onClick={() => router.push(backPath)}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
            )}
            <h1 className="text-xl font-bold text-gray-900">{title}</h1>
          </div>
          <div className="flex items-center space-x-4">
            {rightContent}
            <span className="text-gray-700">Welcome, {user?.username}!</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
