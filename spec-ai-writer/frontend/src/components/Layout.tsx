import { Outlet, Link, useLocation } from 'react-router';
import { FileText, LayoutDashboard, Settings as SettingsIcon } from 'lucide-react';
import clsx from 'clsx';
import { version } from '../../package.json';

export default function Layout() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-primary-500" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Spec AIライター
                  </h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    仕様駆動開発
                  </p>
                </div>
              </Link>

              <nav className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className={clsx(
                    'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive('/dashboard')
                      ? 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-100'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  )}
                >
                  <LayoutDashboard className="h-4 w-4" />
                  <span>ダッシュボード</span>
                </Link>
                <Link
                  to="/settings"
                  className={clsx(
                    'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive('/settings')
                      ? 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-100'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  )}
                >
                  <SettingsIcon className="h-4 w-4" />
                  <span>設定</span>
                </Link>
              </nav>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                v{version}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            © 2026 Spec AIライター
          </p>
        </div>
      </footer>
    </div>
  );
}
