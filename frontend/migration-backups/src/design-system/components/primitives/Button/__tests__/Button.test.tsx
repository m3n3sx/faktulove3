// Button Component Tests
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button, ButtonProps } from '../Button';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock clsx for testing
jest.mock('clsx', () => ({
  clsx: (...args: any[]) => args.filter(Boolean).join(' '),
}));

describe('Button Component', () => {
  const defaultProps: ButtonProps = {
    children: 'Test Button',
  };

  describe('Rendering', () => {
    it('renders button with default props', () => {
      render(<Button {...defaultProps} />);
      const button = screen.getByRole('button', { name: 'Test Button' });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('type', 'button');
    });

    it('renders with custom className', () => {
      render(<Button {...defaultProps} className="custom-class" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });

    it('renders with testId', () => {
      render(<Button {...defaultProps} testId="test-button" />);
      const button = screen.getByTestId('test-button');
      expect(button).toBeInTheDocument();
    });

    it('renders different button types', () => {
      const { rerender } = render(<Button type="submit">Submit</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');

      rerender(<Button type="reset">Reset</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('type', 'reset');
    });
  });

  describe('Variants', () => {
    it('renders primary variant by default', () => {
      render(<Button {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-600');
    });

    it('renders secondary variant', () => {
      render(<Button {...defaultProps} variant="secondary" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'text-primary-600', 'border-primary-600');
    });

    it('renders ghost variant', () => {
      render(<Button {...defaultProps} variant="ghost" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent', 'text-primary-600');
    });

    it('renders danger variant', () => {
      render(<Button {...defaultProps} variant="danger" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-error-600');
    });
  });

  describe('Sizes', () => {
    it('renders medium size by default', () => {
      render(<Button {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base', 'h-10');
    });

    it('renders extra small size', () => {
      render(<Button {...defaultProps} size="xs" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-2', 'py-1', 'text-xs', 'h-6');
    });

    it('renders small size', () => {
      render(<Button {...defaultProps} size="sm" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm', 'h-8');
    });

    it('renders large size', () => {
      render(<Button {...defaultProps} size="lg" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-5', 'py-2.5', 'text-lg', 'h-12');
    });

    it('renders extra large size', () => {
      render(<Button {...defaultProps} size="xl" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6', 'py-3', 'text-xl', 'h-14');
    });
  });

  describe('States', () => {
    it('handles disabled state', () => {
      const handleClick = jest.fn();
      render(<Button {...defaultProps} disabled onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-60');
      
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles loading state', () => {
      const handleClick = jest.fn();
      render(<Button {...defaultProps} loading onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(button).toHaveClass('cursor-wait');
      
      // Should show loading spinner
      const spinner = button.querySelector('svg');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('animate-spin');
      
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles full width', () => {
      render(<Button {...defaultProps} fullWidth />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full');
    });
  });

  describe('Icons', () => {
    const TestIcon = () => <span data-testid="test-icon">🔥</span>;

    it('renders start icon', () => {
      render(<Button {...defaultProps} startIcon={<TestIcon />} />);
      
      const button = screen.getByRole('button');
      const icon = screen.getByTestId('test-icon');
      
      expect(icon).toBeInTheDocument();
      expect(icon.parentElement).toHaveAttribute('aria-hidden', 'true');
      
      // Icon should come before text
      const buttonText = button.textContent;
      expect(buttonText).toBe('🔥Test Button');
    });

    it('renders end icon', () => {
      render(<Button {...defaultProps} endIcon={<TestIcon />} />);
      
      const button = screen.getByRole('button');
      const icon = screen.getByTestId('test-icon');
      
      expect(icon).toBeInTheDocument();
      expect(icon.parentElement).toHaveAttribute('aria-hidden', 'true');
      
      // Icon should come after text
      const buttonText = button.textContent;
      expect(buttonText).toBe('Test Button🔥');
    });

    it('renders both start and end icons', () => {
      const StartIcon = () => <span data-testid="start-icon">⭐</span>;
      const EndIcon = () => <span data-testid="end-icon">🔥</span>;
      
      render(
        <Button 
          {...defaultProps} 
          startIcon={<StartIcon />} 
          endIcon={<EndIcon />} 
        />
      );
      
      expect(screen.getByTestId('start-icon')).toBeInTheDocument();
      expect(screen.getByTestId('end-icon')).toBeInTheDocument();
      
      const button = screen.getByRole('button');
      const buttonText = button.textContent;
      expect(buttonText).toBe('⭐Test Button🔥');
    });

    it('hides end icon when loading', () => {
      render(
        <Button 
          {...defaultProps} 
          loading 
          endIcon={<TestIcon />} 
        />
      );
      
      expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument();
      
      // Should show loading spinner instead
      const button = screen.getByRole('button');
      const spinner = button.querySelector('svg');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('handles click events', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button {...defaultProps} onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
      expect(handleClick).toHaveBeenCalledWith(expect.any(Object));
    });

    it('handles keyboard events (Enter)', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button {...defaultProps} onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('handles keyboard events (Space)', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button {...defaultProps} onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard(' ');
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('prevents interaction when disabled', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button {...defaultProps} disabled onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('prevents interaction when loading', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button {...defaultProps} loading onClick={handleClick} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', async () => {
      const { container } = render(<Button {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('supports ARIA attributes', () => {
      render(
        <Button
          {...defaultProps}
          aria-label="Custom label"
          aria-describedby="description"
          aria-pressed={true}
          aria-expanded={false}
          aria-haspopup="menu"
        />
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Custom label');
      expect(button).toHaveAttribute('aria-describedby', 'description');
      expect(button).toHaveAttribute('aria-pressed', 'true');
      expect(button).toHaveAttribute('aria-expanded', 'false');
      expect(button).toHaveAttribute('aria-haspopup', 'menu');
    });

    it('has proper focus management', async () => {
      const user = userEvent.setup();
      render(<Button {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.tab();
      
      expect(button).toHaveFocus();
      expect(button).toHaveClass('focus-visible');
    });

    it('announces loading state to screen readers', () => {
      render(<Button {...defaultProps} loading />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('properly handles icon accessibility', () => {
      const TestIcon = () => <span>🔥</span>;
      render(<Button {...defaultProps} startIcon={<TestIcon />} />);
      
      const button = screen.getByRole('button');
      const iconContainer = button.querySelector('[aria-hidden="true"]');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner with correct size', () => {
      const { rerender } = render(<Button loading size="xs">Loading</Button>);
      let spinner = screen.getByRole('button').querySelector('svg');
      expect(spinner).toHaveClass('w-3', 'h-3');

      rerender(<Button loading size="sm">Loading</Button>);
      spinner = screen.getByRole('button').querySelector('svg');
      expect(spinner).toHaveClass('w-4', 'h-4');

      rerender(<Button loading size="md">Loading</Button>);
      spinner = screen.getByRole('button').querySelector('svg');
      expect(spinner).toHaveClass('w-5', 'h-5');

      rerender(<Button loading size="lg">Loading</Button>);
      spinner = screen.getByRole('button').querySelector('svg');
      expect(spinner).toHaveClass('w-6', 'h-6');

      rerender(<Button loading size="xl">Loading</Button>);
      spinner = screen.getByRole('button').querySelector('svg');
      expect(spinner).toHaveClass('w-7', 'h-7');
    });

    it('maintains text visibility during loading', () => {
      render(<Button loading>Loading Text</Button>);
      
      const button = screen.getByRole('button');
      const textSpan = button.querySelector('span:not([aria-hidden])');
      expect(textSpan).toBeInTheDocument();
      expect(textSpan).toHaveTextContent('Loading Text');
    });
  });

  describe('Ref Forwarding', () => {
    it('forwards ref to button element', () => {
      const ref = React.createRef<HTMLButtonElement>();
      render(<Button {...defaultProps} ref={ref} />);
      
      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
      expect(ref.current).toBe(screen.getByRole('button'));
    });
  });

  describe('Edge Cases', () => {
    it('handles empty children', () => {
      render(<Button />);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button.textContent).toBe('');
    });

    it('handles complex children', () => {
      render(
        <Button>
          <span>Complex</span>
          <strong>Children</strong>
        </Button>
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('ComplexChildren');
    });

    it('handles rapid state changes', async () => {
      const { rerender } = render(<Button loading>Test</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
      
      rerender(<Button disabled>Test</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
      
      rerender(<Button>Test</Button>);
      expect(screen.getByRole('button')).not.toBeDisabled();
    });
  });

  describe('CSS Classes', () => {
    it('applies correct base classes', () => {
      render(<Button {...defaultProps} />);
      const button = screen.getByRole('button');
      
      expect(button).toHaveClass(
        'ds-button',
        'inline-flex',
        'items-center',
        'justify-center',
        'font-medium',
        'transition-all',
        'duration-200',
        'ease-out',
        'focus-visible',
        'rounded-md'
      );
    });

    it('applies variant-specific classes correctly', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-600', 'text-white');

      rerender(<Button variant="secondary">Secondary</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'text-primary-600', 'border-primary-600');

      rerender(<Button variant="ghost">Ghost</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent', 'text-primary-600');

      rerender(<Button variant="danger">Danger</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-error-600', 'text-white');
    });
  });
});