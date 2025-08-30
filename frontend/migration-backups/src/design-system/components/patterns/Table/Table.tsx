import React, { useState, useMemo, useCallback } from 'react';
import { BaseComponentProps } from '../../../types';
import { Button } from '../../primitives/Button/Button';

// Polish formatting utilities
export const formatPolishCurrency = (amount: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 2,
  }).format(amount);
};

export const formatPolishDate = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(dateObj);
};

export const formatPolishDateTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj);
};

export const formatPolishNumber = (number: number): string => {
  return new Intl.NumberFormat('pl-PL').format(number);
};

// Table column definition
export interface TableColumn<T = any> {
  key: string;
  header: string;
  accessor?: keyof T | ((row: T) => any);
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  format?: 'currency' | 'date' | 'datetime' | 'number' | 'custom';
  customFormat?: (value: any, row: T) => React.ReactNode;
  className?: string;
}

// Sort configuration
export interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

// Pagination configuration
export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
}

// Table props
export interface TableProps<T = any> extends BaseComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  sortable?: boolean;
  sortConfig?: SortConfig;
  onSort?: (sortConfig: SortConfig) => void;
  pagination?: PaginationConfig;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  selectable?: boolean;
  selectedRows?: string[];
  onSelectionChange?: (selectedRows: string[]) => void;
  rowKey?: keyof T | ((row: T) => string);
  loading?: boolean;
  emptyMessage?: string;
  variant?: 'default' | 'striped' | 'bordered';
  size?: 'sm' | 'md' | 'lg';
  stickyHeader?: boolean;
}

// Table component
export const Table = <T extends Record<string, any>>({
  data,
  columns,
  sortable = true,
  sortConfig,
  onSort,
  pagination,
  onPageChange,
  onPageSizeChange,
  selectable = false,
  selectedRows = [],
  onSelectionChange,
  rowKey = 'id',
  loading = false,
  emptyMessage = 'Brak danych do wyświetlenia',
  variant = 'default',
  size = 'md',
  stickyHeader = false,
  className = '',
  testId = 'table',
  ...props
}: TableProps<T>) => {
  const [internalSortConfig, setInternalSortConfig] = useState<SortConfig | null>(null);

  // Get row key
  const getRowKey = useCallback((row: T): string => {
    if (typeof rowKey === 'function') {
      return rowKey(row);
    }
    return String(row[rowKey]);
  }, [rowKey]);

  // Handle sorting
  const handleSort = useCallback((columnKey: string) => {
    if (!sortable) return;

    const currentSort = sortConfig || internalSortConfig;
    const newDirection = 
      currentSort?.key === columnKey && currentSort.direction === 'asc' 
        ? 'desc' 
        : 'asc';

    const newSortConfig = { key: columnKey, direction: newDirection };

    if (onSort) {
      onSort(newSortConfig);
    } else {
      setInternalSortConfig(newSortConfig);
    }
  }, [sortable, sortConfig, internalSortConfig, onSort]);

  // Sort data if needed
  const sortedData = useMemo(() => {
    const currentSort = sortConfig || internalSortConfig;
    if (!currentSort || !sortable) return data;

    const column = columns.find(col => col.key === currentSort.key);
    if (!column) return data;

    return [...data].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (column.accessor) {
        if (typeof column.accessor === 'function') {
          aValue = column.accessor(a);
          bValue = column.accessor(b);
        } else {
          aValue = a[column.accessor];
          bValue = b[column.accessor];
        }
      } else {
        aValue = a[column.key];
        bValue = b[column.key];
      }

      // Handle null/undefined values
      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      // Convert to comparable values
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      let comparison = 0;
      if (aValue > bValue) comparison = 1;
      if (aValue < bValue) comparison = -1;

      return currentSort.direction === 'desc' ? -comparison : comparison;
    });
  }, [data, columns, sortConfig, internalSortConfig, sortable]);

  // Handle row selection
  const handleRowSelection = useCallback((rowId: string, selected: boolean) => {
    if (!onSelectionChange) return;

    const newSelection = selected
      ? [...selectedRows, rowId]
      : selectedRows.filter(id => id !== rowId);

    onSelectionChange(newSelection);
  }, [selectedRows, onSelectionChange]);

  const handleSelectAll = useCallback((selected: boolean) => {
    if (!onSelectionChange) return;

    const newSelection = selected
      ? sortedData.map(row => getRowKey(row))
      : [];

    onSelectionChange(newSelection);
  }, [sortedData, getRowKey, onSelectionChange]);

  // Format cell value
  const formatCellValue = useCallback((value: any, column: TableColumn<T>, row: T): React.ReactNode => {
    if (value == null) return '-';

    if (column.customFormat) {
      return column.customFormat(value, row);
    }

    switch (column.format) {
      case 'currency':
        return formatPolishCurrency(Number(value));
      case 'date':
        return formatPolishDate(value);
      case 'datetime':
        return formatPolishDateTime(value);
      case 'number':
        return formatPolishNumber(Number(value));
      default:
        return String(value);
    }
  }, []);

  // Get cell value
  const getCellValue = useCallback((row: T, column: TableColumn<T>): any => {
    if (column.accessor) {
      if (typeof column.accessor === 'function') {
        return column.accessor(row);
      }
      return row[column.accessor];
    }
    return row[column.key];
  }, []);

  // Table variant styles
  const variantClasses = {
    default: 'border border-neutral-200',
    striped: 'border border-neutral-200',
    bordered: 'border-2 border-neutral-300',
  };

  // Table size styles
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  const cellPadding = {
    sm: 'px-3 py-2',
    md: 'px-4 py-3',
    lg: 'px-6 py-4',
  };

  const currentSort = sortConfig || internalSortConfig;
  const allSelected = selectedRows.length === sortedData.length && sortedData.length > 0;
  const someSelected = selectedRows.length > 0 && selectedRows.length < sortedData.length;

  return (
    <div className={`overflow-hidden rounded-lg ${className}`} data-testid={testId} {...props}>
      {/* Table container with horizontal scroll */}
      <div className="overflow-x-auto">
        <table className={`min-w-full ${variantClasses[variant]} ${sizeClasses[size]}`}>
          {/* Table header */}
          <thead className={`bg-neutral-50 ${stickyHeader ? 'sticky top-0 z-10' : ''}`}>
            <tr>
              {/* Selection column */}
              {selectable && (
                <th className={`${cellPadding[size]} text-left`}>
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(input) => {
                      if (input) input.indeterminate = someSelected;
                    }}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    aria-label="Zaznacz wszystkie wiersze"
                  />
                </th>
              )}

              {/* Column headers */}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`${cellPadding[size]} text-left font-semibold text-neutral-900 ${
                    column.align === 'center' ? 'text-center' :
                    column.align === 'right' ? 'text-right' : ''
                  } ${column.className || ''}`}
                  style={{ width: column.width }}
                >
                  {column.sortable !== false && sortable ? (
                    <button
                      type="button"
                      onClick={() => handleSort(column.key)}
                      className="flex items-center gap-1 hover:text-primary-600 focus:outline-none focus:text-primary-600"
                      aria-label={`Sortuj według ${column.header}`}
                    >
                      <span>{column.header}</span>
                      <span className="text-neutral-400">
                        {currentSort?.key === column.key ? (
                          currentSort.direction === 'asc' ? '↑' : '↓'
                        ) : (
                          '↕'
                        )}
                      </span>
                    </button>
                  ) : (
                    column.header
                  )}
                </th>
              ))}
            </tr>
          </thead>

          {/* Table body */}
          <tbody className="bg-white divide-y divide-neutral-200">
            {loading ? (
              <tr>
                <td
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  className={`${cellPadding[size]} text-center text-neutral-500`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    Ładowanie...
                  </div>
                </td>
              </tr>
            ) : sortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  className={`${cellPadding[size]} text-center text-neutral-500`}
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((row, index) => {
                const rowId = getRowKey(row);
                const isSelected = selectedRows.includes(rowId);
                const isEven = index % 2 === 0;

                return (
                  <tr
                    key={rowId}
                    className={`
                      ${variant === 'striped' && !isEven ? 'bg-neutral-50' : ''}
                      ${isSelected ? 'bg-primary-50' : ''}
                      hover:bg-neutral-50 transition-colors
                    `}
                  >
                    {/* Selection cell */}
                    {selectable && (
                      <td className={cellPadding[size]}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={(e) => handleRowSelection(rowId, e.target.checked)}
                          className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                          aria-label={`Zaznacz wiersz ${index + 1}`}
                        />
                      </td>
                    )}

                    {/* Data cells */}
                    {columns.map((column) => {
                      const cellValue = getCellValue(row, column);
                      const formattedValue = formatCellValue(cellValue, column, row);

                      return (
                        <td
                          key={column.key}
                          className={`${cellPadding[size]} ${
                            column.align === 'center' ? 'text-center' :
                            column.align === 'right' ? 'text-right' : ''
                          } ${column.className || ''}`}
                        >
                          {formattedValue}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <TablePagination
          pagination={pagination}
          onPageChange={onPageChange}
          onPageSizeChange={onPageSizeChange}
        />
      )}
    </div>
  );
};

// Pagination component
interface TablePaginationProps {
  pagination: PaginationConfig;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
}

const TablePagination: React.FC<TablePaginationProps> = ({
  pagination,
  onPageChange,
  onPageSizeChange,
}) => {
  const { page, pageSize, total } = pagination;
  const totalPages = Math.ceil(total / pageSize);
  const startItem = (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages && onPageChange) {
      onPageChange(newPage);
    }
  };

  const handlePageSizeChange = (newPageSize: number) => {
    if (onPageSizeChange) {
      onPageSizeChange(newPageSize);
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);

      if (page > 3) {
        pages.push('...');
      }

      const start = Math.max(2, page - 1);
      const end = Math.min(totalPages - 1, page + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (page < totalPages - 2) {
        pages.push('...');
      }

      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <div className="bg-white px-4 py-3 border-t border-neutral-200 sm:px-6">
      <div className="flex items-center justify-between">
        {/* Results info */}
        <div className="flex items-center gap-4">
          <p className="text-sm text-neutral-700">
            Wyświetlanie <span className="font-medium">{startItem}</span> do{' '}
            <span className="font-medium">{endItem}</span> z{' '}
            <span className="font-medium">{total}</span> wyników
          </p>

          {/* Page size selector */}
          {onPageSizeChange && (
            <div className="flex items-center gap-2">
              <label htmlFor="pageSize" className="text-sm text-neutral-700">
                Wierszy na stronę:
              </label>
              <select
                id="pageSize"
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="border border-neutral-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          )}
        </div>

        {/* Pagination controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            aria-label="Poprzednia strona"
          >
            Poprzednia
          </Button>

          <div className="flex items-center gap-1">
            {getPageNumbers().map((pageNum, index) => (
              <React.Fragment key={index}>
                {pageNum === '...' ? (
                  <span className="px-2 py-1 text-neutral-500">...</span>
                ) : (
                  <button
                    type="button"
                    onClick={() => handlePageChange(pageNum as number)}
                    className={`px-3 py-1 text-sm rounded-md transition-colors ${
                      pageNum === page
                        ? 'bg-primary-600 text-white'
                        : 'text-neutral-700 hover:bg-neutral-100'
                    }`}
                    aria-label={`Strona ${pageNum}`}
                    aria-current={pageNum === page ? 'page' : undefined}
                  >
                    {pageNum}
                  </button>
                )}
              </React.Fragment>
            ))}
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
            aria-label="Następna strona"
          >
            Następna
          </Button>
        </div>
      </div>
    </div>
  );
};