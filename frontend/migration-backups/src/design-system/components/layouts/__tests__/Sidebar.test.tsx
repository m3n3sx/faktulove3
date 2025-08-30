import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../Sidebar/Sidebar';

describe('Sidebar Component', () => {
  it('renders children correctly', () => {
    render(
      <Sidebar testId="test-sidebar">
        <div>Sidebar Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveTextContent('Sidebar Content');
  });

  it('applies default classes', () => {
    render(
      <Sidebar testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveClass('flex', 'flex-col', 'bg-white', 'border-r', 'relative');
  });

  it('renders toggle button when collapsible', () => {
    render(
      <Sidebar collapsible testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const toggleButton = screen.getByTestId('test-sidebar-toggle');
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton).toHaveAttribute('aria-label', 'Collapse sidebar');
  });

  it('does not render toggle button when not collapsible', () => {
    render(
      <Sidebar collapsible={false} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const toggleButton = screen.queryByTestId('test-sidebar-toggle');
    expect(toggleButton).not.toBeInTheDocument();
  });

  it('toggles collapsed state when toggle button is clicked', () => {
    const onToggle = jest.fn();
    
    render(
      <Sidebar onToggle={onToggle} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const toggleButton = screen.getByTestId('test-sidebar-toggle');
    const sidebar = screen.getByTestId('test-sidebar');

    expect(sidebar).toHaveAttribute('data-collapsed', 'false');

    fireEvent.click(toggleButton);

    expect(onToggle).toHaveBeenCalledWith(true);
    expect(sidebar).toHaveAttribute('data-collapsed', 'true');
  });

  it('uses controlled collapsed state', () => {
    const { rerender } = render(
      <Sidebar isCollapsed={false} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveAttribute('data-collapsed', 'false');

    rerender(
      <Sidebar isCollapsed={true} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    expect(sidebar).toHaveAttribute('data-collapsed', 'true');
  });

  it('applies right position classes', () => {
    render(
      <Sidebar position="right" testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveClass('border-l');
    expect(sidebar).not.toHaveClass('border-r');
  });

  it('applies overlay classes when overlay is true', () => {
    render(
      <Sidebar overlay testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveClass('fixed', 'top-0', 'bottom-0', 'z-50', 'left-0');
  });

  it('renders overlay backdrop when overlay and not collapsed', () => {
    render(
      <Sidebar overlay isCollapsed={false} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const overlay = screen.getByTestId('test-sidebar-overlay');
    expect(overlay).toBeInTheDocument();
    expect(overlay).toHaveClass('fixed', 'inset-0', 'bg-black', 'bg-opacity-50');
  });

  it('does not render overlay backdrop when collapsed', () => {
    render(
      <Sidebar overlay isCollapsed={true} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const overlay = screen.queryByTestId('test-sidebar-overlay');
    expect(overlay).not.toBeInTheDocument();
  });

  it('closes overlay when backdrop is clicked', () => {
    const onToggle = jest.fn();
    
    render(
      <Sidebar overlay isCollapsed={false} onToggle={onToggle} testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const overlay = screen.getByTestId('test-sidebar-overlay');
    fireEvent.click(overlay);

    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it('applies custom className', () => {
    render(
      <Sidebar className="custom-class" testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveClass('custom-class');
  });

  it('applies custom width styles', () => {
    render(
      <Sidebar width="20rem" collapsedWidth="3rem" testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveStyle({ width: '20rem' });
  });

  it('changes width when collapsed', () => {
    const { rerender } = render(
      <Sidebar isCollapsed={false} width="20rem" collapsedWidth="3rem" testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    const sidebar = screen.getByTestId('test-sidebar');
    expect(sidebar).toHaveStyle({ width: '20rem' });

    rerender(
      <Sidebar isCollapsed={true} width="20rem" collapsedWidth="3rem" testId="test-sidebar">
        <div>Content</div>
      </Sidebar>
    );

    expect(sidebar).toHaveStyle({ width: '3rem' });
  });
});