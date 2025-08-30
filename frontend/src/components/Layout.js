import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Upload, 
  FileText, 
  BarChart3, 
  Settings, 
  Menu, 
  X,
  Zap,
  User
} from 'lucide-react';
import { Container, Button } from '../design-system';
import { ThemeControls } from '../design-system/components/patterns/ThemeControls/ThemeControls';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Upload Documents', href: '/upload', icon: Upload },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Statistics', href: '/statistics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-background-secondary">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-background-inverse bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-background-primary shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-border-default">
          <div className="flex items-center space-x-2">
            <Zap className="w-8 h-8 text-primary-600" />
            <span className="text-xl font-bold text-text-primary">FaktuLove</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="w-6 h-6" />
          </Button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200
                    ${isActive(item.href)
                      ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600'
                      : 'text-text-secondary hover:bg-background-hover hover:text-text-primary'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className={`
                    mr-3 h-5 w-5 transition-colors duration-200
                    ${isActive(item.href) ? 'text-primary-600' : 'text-text-muted group-hover:text-text-secondary'}
                  `} />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Theme Controls */}
        <div className="absolute bottom-20 left-0 right-0 p-4 border-t border-border-default">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-text-primary">Motyw</span>
            <ThemeControls compact showAdvanced />
          </div>
        </div>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border-default">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">User</p>
              <p className="text-xs text-text-secondary truncate">user@faktulove.com</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-background-primary shadow-sm border-b border-border-default lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu className="w-6 h-6" />
            </Button>
            <div className="flex items-center space-x-2">
              <Zap className="w-6 h-6 text-primary-600" />
              <span className="text-lg font-bold text-text-primary">FaktuLove</span>
            </div>
            <ThemeControls compact />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="py-6">
            <Container maxWidth="7xl">
              {children}
            </Container>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
