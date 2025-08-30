import React from 'react';
import { cn } from '../../../utils/cn';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  onClick?: () => void;
  current?: boolean;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
  separator?: React.ReactNode;
  maxItems?: number;
  testId?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  className,
  separator = '/',
  maxItems,
  testId,
}) => {
  const processedItems = maxItems && items.length > maxItems
    ? [
        items[0],
        { label: '...', href: undefined, onClick: undefined },
        ...items.slice(-(maxItems - 2))
      ]
    : items;

  const renderItem = (item: BreadcrumbItem, index: number, isLast: boolean) => {
    const itemClasses = cn(
      'text-sm',
      item.current || isLast
        ? 'text-neutral-900 font-medium'
        : 'text-neutral-600 hover:text-neutral-900',
      (item.href || item.onClick) && !item.current && !isLast && 'cursor-pointer transition-colors'
    );

    const content = (
      <span className={itemClasses}>
        {item.label}
      </span>
    );

    if (item.href && !item.current && !isLast) {
      return (
        <a
          key={index}
          href={item.href}
          className="focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
          aria-current={item.current ? 'page' : undefined}
        >
          {content}
        </a>
      );
    }

    if (item.onClick && !item.current && !isLast) {
      return (
        <button
          key={index}
          onClick={item.onClick}
          className="focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
          aria-current={item.current ? 'page' : undefined}
        >
          {content}
        </button>
      );
    }

    return (
      <span
        key={index}
        aria-current={item.current || isLast ? 'page' : undefined}
      >
        {content}
      </span>
    );
  };

  const renderSeparator = (index: number) => (
    <span
      key={`separator-${index}`}
      className="text-neutral-400 mx-2 select-none"
      aria-hidden="true"
    >
      {separator}
    </span>
  );

  return (
    <nav
      className={cn('flex items-center space-x-0', className)}
      aria-label="Breadcrumb"
      data-testid={testId}
    >
      <ol className="flex items-center">
        {processedItems.map((item, index) => {
          const isLast = index === processedItems.length - 1;
          
          return (
            <li key={index} className="flex items-center">
              {renderItem(item, index, isLast)}
              {!isLast && renderSeparator(index)}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

Breadcrumb.displayName = 'Breadcrumb';