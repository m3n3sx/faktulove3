import React, { useState, useEffect } from 'react';
import { cn } from '../../../utils/cn';

export interface SidebarProps {
  children: React.ReactNode;
  className?: string;
  isCollapsed?: boolean;
  onToggle?: (collapsed: boolean) => void;
  collapsible?: boolean;
  width?: string;
  collapsedWidth?: string;
  position?: 'left' | 'right';
  overlay?: boolean;
  testId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  children,
  className,
  isCollapsed: controlledCollapsed,
  onToggle,
  collapsible = true,
  width = '16rem',
  collapsedWidth = '4rem',
  position = 'left',
  overlay = false,
  testId,
}) => {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  
  const isCollapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;

  const handleToggle = () => {
    const newCollapsed = !isCollapsed;
    if (controlledCollapsed === undefined) {
      setInternalCollapsed(newCollapsed);
    }
    onToggle?.(newCollapsed);
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && overlay && !isCollapsed) {
        handleToggle();
      }
    };

    if (overlay) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [overlay, isCollapsed]);

  const getSidebarClasses = () => {
    const classes = [
      'flex',
      'flex-col',
      'bg-white',
      'border-neutral-200',
      'transition-all',
      'duration-300',
      'ease-in-out',
    ];

    if (position === 'left') {
      classes.push('border-r');
    } else {
      classes.push('border-l');
    }

    if (overlay) {
      classes.push('fixed', 'top-0', 'bottom-0', 'z-50');
      if (position === 'left') {
        classes.push('left-0');
      } else {
        classes.push('right-0');
      }
      
      if (isCollapsed) {
        classes.push('-translate-x-full');
      } else {
        classes.push('translate-x-0');
      }
    } else {
      classes.push('relative');
    }

    return classes.join(' ');
  };

  const sidebarStyle: React.CSSProperties = {
    width: overlay ? width : (isCollapsed ? collapsedWidth : width),
  };

  return (
    <>
      {overlay && !isCollapsed && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={handleToggle}
          data-testid={`${testId}-overlay`}
        />
      )}
      
      <aside
        className={cn(getSidebarClasses(), className)}
        style={sidebarStyle}
        data-testid={testId}
        data-collapsed={isCollapsed}
      >
        {collapsible && (
          <button
            onClick={handleToggle}
            className={cn(
              'flex items-center justify-center',
              'p-2 m-2',
              'text-neutral-600 hover:text-neutral-900',
              'hover:bg-neutral-100',
              'rounded-md',
              'transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-primary-500'
            )}
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            data-testid={`${testId}-toggle`}
          >
            <svg
              className={cn(
                'w-5 h-5 transition-transform duration-200',
                isCollapsed ? 'rotate-180' : 'rotate-0',
                position === 'right' && 'rotate-180'
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
        )}
        
        <div className={cn('flex-1 overflow-y-auto', isCollapsed && 'px-2')}>
          {children}
        </div>
      </aside>
    </>
  );
};

Sidebar.displayName = 'Sidebar';