import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Breadcrumb } from '../Breadcrumb/Breadcrumb';

describe('Breadcrumb Component', () => {
  const mockItems = [
    { label: 'Home', href: '/' },
    { label: 'Products', href: '/products' },
    { label: 'Electronics', href: '/products/electronics' },
    { label: 'Laptop', current: true },
  ];

  it('renders all breadcrumb items', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const breadcrumb = screen.getByTestId('test-breadcrumb');
    expect(breadcrumb).toBeInTheDocument();

    mockItems.forEach((item) => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
    });
  });

  it('renders separators between items', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const separators = screen.getAllByText('/');
    expect(separators).toHaveLength(mockItems.length - 1);
  });

  it('renders custom separator', () => {
    render(
      <Breadcrumb 
        items={mockItems} 
        separator=">" 
        testId="test-breadcrumb" 
      />
    );

    const separators = screen.getAllByText('>');
    expect(separators).toHaveLength(mockItems.length - 1);
  });

  it('renders links for items with href', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const homeLink = screen.getByRole('link', { name: 'Home' });
    expect(homeLink).toHaveAttribute('href', '/');

    const productsLink = screen.getByRole('link', { name: 'Products' });
    expect(productsLink).toHaveAttribute('href', '/products');
  });

  it('renders buttons for items with onClick', () => {
    const handleClick = jest.fn();
    const itemsWithClick = [
      { label: 'Home', onClick: handleClick },
      { label: 'Current', current: true },
    ];

    render(<Breadcrumb items={itemsWithClick} testId="test-breadcrumb" />);

    const homeButton = screen.getByRole('button', { name: 'Home' });
    expect(homeButton).toBeInTheDocument();

    fireEvent.click(homeButton);
    expect(handleClick).toHaveBeenCalled();
  });

  it('marks current item with aria-current', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const currentItem = screen.getByText('Laptop');
    expect(currentItem.closest('span')).toHaveAttribute('aria-current', 'page');
  });

  it('marks last item with aria-current when no current item specified', () => {
    const itemsWithoutCurrent = mockItems.map(item => ({ ...item, current: undefined }));
    
    render(<Breadcrumb items={itemsWithoutCurrent} testId="test-breadcrumb" />);

    const lastItem = screen.getByText('Laptop');
    expect(lastItem.closest('span')).toHaveAttribute('aria-current', 'page');
  });

  it('truncates items when maxItems is specified', () => {
    render(
      <Breadcrumb 
        items={mockItems} 
        maxItems={3} 
        testId="test-breadcrumb" 
      />
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('...')).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
    expect(screen.getByText('Laptop')).toBeInTheDocument();
    expect(screen.queryByText('Products')).not.toBeInTheDocument();
  });

  it('does not truncate when items length is less than maxItems', () => {
    const shortItems = mockItems.slice(0, 2);
    
    render(
      <Breadcrumb 
        items={shortItems} 
        maxItems={5} 
        testId="test-breadcrumb" 
      />
    );

    expect(screen.queryByText('...')).not.toBeInTheDocument();
    shortItems.forEach((item) => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
    });
  });

  it('applies custom className', () => {
    render(
      <Breadcrumb 
        items={mockItems} 
        className="custom-class" 
        testId="test-breadcrumb" 
      />
    );

    const breadcrumb = screen.getByTestId('test-breadcrumb');
    expect(breadcrumb).toHaveClass('custom-class');
  });

  it('has proper accessibility attributes', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const nav = screen.getByTestId('test-breadcrumb');
    expect(nav).toHaveAttribute('aria-label', 'Breadcrumb');

    const list = screen.getByRole('list');
    expect(list).toBeInTheDocument();

    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(mockItems.length);
  });

  it('handles empty items array', () => {
    render(<Breadcrumb items={[]} testId="test-breadcrumb" />);

    const breadcrumb = screen.getByTestId('test-breadcrumb');
    expect(breadcrumb).toBeInTheDocument();

    const listItems = screen.queryAllByRole('listitem');
    expect(listItems).toHaveLength(0);
  });

  it('applies correct styling to current and non-current items', () => {
    render(<Breadcrumb items={mockItems} testId="test-breadcrumb" />);

    const homeItem = screen.getByText('Home');
    const currentItem = screen.getByText('Laptop');

    expect(homeItem).toHaveClass('text-neutral-600');
    expect(currentItem).toHaveClass('text-neutral-900', 'font-medium');
  });
});