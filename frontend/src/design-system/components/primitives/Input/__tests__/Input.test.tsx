// Input Component Tests
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Input, InputProps } from '../Input';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('Input Component', () => {
  const defaultProps: InputProps = {
    label: 'Test Input',
    placeholder: 'Enter text',
  };

  describe('Rendering', () => {
    it('renders input with default props', () => {
      render(<Input {...defaultProps} />);
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
      expect(input).toHaveAttribute('placeholder', 'Enter text');
    });

    it('renders with custom className', () => {
      render(<Input {...defaultProps} className="custom-class" />);
      
      const container = screen.getByLabelText('Test Input').closest('.ds-input-container');
      expect(container).toHaveClass('custom-class');
    });

    it('renders with testId', () => {
      render(<Input {...defaultProps} testId="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toBeInTheDocument();
    });

    it('renders different input types', () => {
      const { rerender } = render(<Input label="Email" type="email" />);
      expect(screen.getByLabelText('Email')).toHaveAttribute('type', 'email');

      rerender(<Input label="Password" type="password" />);
      expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password');

      rerender(<Input label="Number" type="number" />);
      expect(screen.getByLabelText('Number')).toHaveAttribute('type', 'number');
    });
  });

  describe('Label and Required', () => {
    it('renders label correctly', () => {
      render(<Input label="Username" />);
      
      const label = screen.getByText('Username');
      expect(label).toBeInTheDocument();
      expect(label.tagName).toBe('LABEL');
    });

    it('renders required indicator', () => {
      render(<Input label="Required Field" required />);
      
      const requiredIndicator = screen.getByText('*');
      expect(requiredIndicator).toBeInTheDocument();
      expect(requiredIndicator).toHaveClass('text-error-600');
      expect(requiredIndicator).toHaveAttribute('aria-label', 'wymagane');
    });

    it('associates label with input', () => {
      render(<Input label="Associated Field" />);
      
      const input = screen.getByLabelText('Associated Field');
      const label = screen.getByText('Associated Field');
      
      expect(input).toHaveAttribute('id');
      expect(label).toHaveAttribute('for', input.getAttribute('id'));
    });

    it('works without label', () => {
      render(<Input placeholder="No label" />);
      
      const input = screen.getByPlaceholderText('No label');
      expect(input).toBeInTheDocument();
      expect(screen.queryByRole('label')).not.toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('renders medium size by default', () => {
      render(<Input {...defaultProps} />);
      
      const wrapper = screen.getByLabelText('Test Input').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-10');
    });

    it('renders all size variants correctly', () => {
      const { rerender } = render(<Input label="Size Test" size="xs" />);
      let wrapper = screen.getByLabelText('Size Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-6');

      rerender(<Input label="Size Test" size="sm" />);
      wrapper = screen.getByLabelText('Size Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-8');

      rerender(<Input label="Size Test" size="md" />);
      wrapper = screen.getByLabelText('Size Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-10');

      rerender(<Input label="Size Test" size="lg" />);
      wrapper = screen.getByLabelText('Size Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-12');

      rerender(<Input label="Size Test" size="xl" />);
      wrapper = screen.getByLabelText('Size Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('h-14');
    });
  });

  describe('States', () => {
    it('handles disabled state', () => {
      const handleChange = jest.fn();
      render(<Input {...defaultProps} disabled onChange={handleChange} />);
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toBeDisabled();
      
      const wrapper = input.closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-muted', 'bg-background-disabled', 'cursor-not-allowed');
      
      fireEvent.change(input, { target: { value: 'test' } });
      expect(handleChange).not.toHaveBeenCalled();
    });

    it('handles readonly state', () => {
      render(<Input {...defaultProps} readOnly />);
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveAttribute('readonly');
      
      const wrapper = input.closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('bg-background-secondary');
    });

    it('handles error state', () => {
      render(<Input {...defaultProps} error errorMessage="This field is required" />);
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveAttribute('aria-invalid', 'true');
      
      const wrapper = input.closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-error', 'bg-error-50');
      
      const errorMessage = screen.getByText('This field is required');
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveAttribute('role', 'alert');
      expect(errorMessage).toHaveAttribute('aria-live', 'polite');
    });

    it('handles focus state', async () => {
      const user = userEvent.setup();
      render(<Input {...defaultProps} />);
      
      const input = screen.getByLabelText('Test Input');
      await user.click(input);
      
      const wrapper = input.closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-focus', 'ring-2', 'ring-primary-600/20');
    });
  });

  describe('Helper Text', () => {
    it('renders helper text', () => {
      render(<Input {...defaultProps} helperText="This is helper text" />);
      
      const helperText = screen.getByText('This is helper text');
      expect(helperText).toBeInTheDocument();
      expect(helperText).toHaveClass('typography-form-helper', 'text-text-muted');
    });

    it('prioritizes error message over helper text', () => {
      render(
        <Input 
          {...defaultProps} 
          error 
          errorMessage="Error message" 
          helperText="Helper text" 
        />
      );
      
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.queryByText('Helper text')).not.toBeInTheDocument();
    });

    it('associates helper text with input via aria-describedby', () => {
      render(<Input {...defaultProps} helperText="Helper text" />);
      
      const input = screen.getByLabelText('Test Input');
      const helperText = screen.getByText('Helper text');
      
      expect(input).toHaveAttribute('aria-describedby');
      expect(input.getAttribute('aria-describedby')).toContain(helperText.getAttribute('id'));
    });
  });

  describe('Icons', () => {
    const TestIcon = () => <span data-testid="test-icon">🔍</span>;

    it('renders start icon', () => {
      render(<Input {...defaultProps} icon={<TestIcon />} iconPosition="start" />);
      
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
      
      const iconContainer = icon.closest('.ds-input-icon');
      expect(iconContainer).toHaveClass('left-0');
      expect(iconContainer).toHaveAttribute('aria-hidden', 'true');
    });

    it('renders end icon', () => {
      render(<Input {...defaultProps} icon={<TestIcon />} iconPosition="end" />);
      
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
      
      const iconContainer = icon.closest('.ds-input-icon');
      expect(iconContainer).toHaveClass('right-0');
    });

    it('adjusts input padding for icons', () => {
      const { rerender } = render(<Input label="Icon Test" icon={<TestIcon />} iconPosition="start" size="md" />);
      let input = screen.getByLabelText('Icon Test');
      expect(input).toHaveClass('pl-10');

      rerender(<Input label="Icon Test" icon={<TestIcon />} iconPosition="end" size="md" />);
      input = screen.getByLabelText('Icon Test');
      expect(input).toHaveClass('pr-10');
    });

    it('scales icon size with input size', () => {
      const { rerender } = render(<Input label="Icon Test" icon={<TestIcon />} size="xs" />);
      let iconContainer = screen.getByTestId('test-icon').closest('.ds-input-icon');
      expect(iconContainer).toHaveClass('w-6', 'h-6');

      rerender(<Input label="Icon Test" icon={<TestIcon />} size="xl" />);
      iconContainer = screen.getByTestId('test-icon').closest('.ds-input-icon');
      expect(iconContainer).toHaveClass('w-14', 'h-14');
    });
  });

  describe('Interactions', () => {
    it('handles change events', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      render(<Input {...defaultProps} onChange={handleChange} />);
      
      const input = screen.getByLabelText('Test Input');
      await user.type(input, 'test value');
      
      expect(handleChange).toHaveBeenCalled();
      expect(input).toHaveValue('test value');
    });

    it('handles focus and blur events', async () => {
      const handleFocus = jest.fn();
      const handleBlur = jest.fn();
      const user = userEvent.setup();
      
      render(<Input {...defaultProps} onFocus={handleFocus} onBlur={handleBlur} />);
      
      const input = screen.getByLabelText('Test Input');
      
      await user.click(input);
      expect(handleFocus).toHaveBeenCalled();
      
      await user.tab();
      expect(handleBlur).toHaveBeenCalled();
    });

    it('handles controlled input', async () => {
      const handleChange = jest.fn();
      const user = userEvent.setup();
      
      const { rerender } = render(
        <Input {...defaultProps} value="initial" onChange={handleChange} />
      );
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveValue('initial');
      
      await user.clear(input);
      await user.type(input, 'new value');
      
      // Simulate parent component updating value
      rerender(<Input {...defaultProps} value="new value" onChange={handleChange} />);
      expect(input).toHaveValue('new value');
    });

    it('handles uncontrolled input with defaultValue', () => {
      render(<Input {...defaultProps} defaultValue="default value" />);
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveValue('default value');
    });
  });

  describe('Validation Attributes', () => {
    it('applies validation attributes correctly', () => {
      render(
        <Input
          {...defaultProps}
          required
          maxLength={10}
          minLength={3}
          pattern="[A-Za-z]+"
          autoComplete="username"
          name="test-input"
        />
      );
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveAttribute('required');
      expect(input).toHaveAttribute('maxlength', '10');
      expect(input).toHaveAttribute('minlength', '3');
      expect(input).toHaveAttribute('pattern', '[A-Za-z]+');
      expect(input).toHaveAttribute('autocomplete', 'username');
      expect(input).toHaveAttribute('name', 'test-input');
      expect(input).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', async () => {
      const { container } = render(<Input {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('supports ARIA attributes', () => {
      render(
        <Input
          {...defaultProps}
          aria-label="Custom label"
          aria-describedby="custom-description"
          aria-invalid={true}
        />
      );
      
      const input = screen.getByLabelText('Custom label');
      expect(input).toHaveAttribute('aria-label', 'Custom label');
      expect(input).toHaveAttribute('aria-describedby');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    it('combines multiple describedby IDs', () => {
      render(
        <Input
          {...defaultProps}
          helperText="Helper text"
          errorMessage="Error message"
          error
          aria-describedby="custom-id"
        />
      );
      
      const input = screen.getByLabelText('Test Input');
      const describedBy = input.getAttribute('aria-describedby');
      
      expect(describedBy).toContain('custom-id');
      expect(describedBy?.split(' ').length).toBeGreaterThan(1);
    });

    it('has proper focus management', async () => {
      const user = userEvent.setup();
      render(<Input {...defaultProps} />);
      
      const input = screen.getByLabelText('Test Input');
      await user.tab();
      
      expect(input).toHaveFocus();
    });

    it('announces errors to screen readers', () => {
      render(<Input {...defaultProps} error errorMessage="Required field" />);
      
      const errorMessage = screen.getByText('Required field');
      expect(errorMessage).toHaveAttribute('role', 'alert');
      expect(errorMessage).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Ref Forwarding', () => {
    it('forwards ref to input element', () => {
      const ref = React.createRef<HTMLInputElement>();
      render(<Input {...defaultProps} ref={ref} />);
      
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
      expect(ref.current).toBe(screen.getByLabelText('Test Input'));
    });
  });

  describe('Edge Cases', () => {
    it('handles empty label gracefully', () => {
      render(<Input label="" placeholder="No label" />);
      
      const input = screen.getByPlaceholderText('No label');
      expect(input).toBeInTheDocument();
    });

    it('handles long error messages', () => {
      const longError = 'This is a very long error message that should wrap properly and not break the layout of the form component';
      
      render(<Input {...defaultProps} error errorMessage={longError} />);
      
      const errorMessage = screen.getByText(longError);
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveClass('typography-form-helper');
    });

    it('handles rapid state changes', () => {
      const { rerender } = render(<Input {...defaultProps} error />);
      expect(screen.getByLabelText('Test Input')).toHaveAttribute('aria-invalid', 'true');
      
      rerender(<Input {...defaultProps} error={false} />);
      expect(screen.getByLabelText('Test Input')).toHaveAttribute('aria-invalid', 'false');
      
      rerender(<Input {...defaultProps} disabled />);
      expect(screen.getByLabelText('Test Input')).toBeDisabled();
    });
  });

  describe('CSS Classes', () => {
    it('applies correct base classes', () => {
      render(<Input {...defaultProps} />);
      
      const container = screen.getByLabelText('Test Input').closest('.ds-input-container');
      expect(container).toHaveClass('ds-input-container', 'relative', 'w-full');
      
      const wrapper = screen.getByLabelText('Test Input').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass(
        'ds-input-wrapper',
        'relative',
        'flex',
        'items-center',
        'border',
        'rounded-md-md',
        'transition-all',
        'duration-200'
      );
      
      const input = screen.getByLabelText('Test Input');
      expect(input).toHaveClass(
        'ds-input',
        'flex-1',
        'bg-transparent',
        'border-0',
        'outline-none'
      );
    });

    it('applies state-specific classes correctly', () => {
      const { rerender } = render(<Input label="State Test" />);
      let wrapper = screen.getByLabelText('State Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-default', 'bg-white');

      rerender(<Input label="State Test" error />);
      wrapper = screen.getByLabelText('State Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-error', 'bg-error-50');

      rerender(<Input label="State Test" disabled />);
      wrapper = screen.getByLabelText('State Test').closest('.ds-input-wrapper');
      expect(wrapper).toHaveClass('border-border-muted', 'bg-background-disabled');
    });
  });
});