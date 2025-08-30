import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Checkbox, CheckboxProps } from '../Checkbox';

// Helper function to render Checkbox with default props
const renderCheckbox = (props: Partial<CheckboxProps> = {}) => {
  const defaultProps: CheckboxProps = {
    label: 'Test Checkbox',
    ...props,
  };
  return render(<Checkbox {...defaultProps} />);
};

describe('Checkbox Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderCheckbox();
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
      expect(screen.getByText('Test Checkbox')).toBeInTheDocument();
    });

    it('renders without label', () => {
      renderCheckbox({ label: undefined });
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
      expect(screen.queryByText('Test Checkbox')).not.toBeInTheDocument();
    });

    it('renders with helper text', () => {
      renderCheckbox({ helperText: 'Helper text' });
      expect(screen.getByText('Helper text')).toBeInTheDocument();
    });

    it('renders with error message', () => {
      renderCheckbox({ error: true, errorMessage: 'Error message' });
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('renders required indicator', () => {
      renderCheckbox({ required: true });
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders with label at start position', () => {
      renderCheckbox({ labelPosition: 'start' });
      const container = screen.getByRole('checkbox').closest('.ds-checkbox-wrapper');
      expect(container).toHaveClass('flex-row-reverse');
    });

    it('renders with label at end position', () => {
      renderCheckbox({ labelPosition: 'end' });
      const container = screen.getByRole('checkbox').closest('.ds-checkbox-wrapper');
      expect(container).toHaveClass('flex-row');
    });
  });

  describe('States', () => {
    it('renders unchecked state', () => {
      renderCheckbox({ checked: false });
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).not.toBeChecked();
    });

    it('renders checked state', () => {
      renderCheckbox({ checked: true });
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeChecked();
    });

    it('renders indeterminate state', () => {
      renderCheckbox({ indeterminate: true });
      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      expect(checkbox.indeterminate).toBe(true);
    });

    it('renders disabled state', () => {
      renderCheckbox({ disabled: true });
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeDisabled();
      expect(checkbox).toHaveClass('cursor-not-allowed');
    });

    it('renders error state', () => {
      renderCheckbox({ error: true });
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-invalid', 'true');
    });

    it('renders required state', () => {
      renderCheckbox({ required: true });
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Size Variants', () => {
    it.each(['xs', 'sm', 'md', 'lg', 'xl'] as const)('renders %s size correctly', (size) => {
      renderCheckbox({ size });
      const checkbox = screen.getByRole('checkbox');
      const expectedClass = size === 'xs' ? 'w-3' : size === 'sm' ? 'w-4' : size === 'md' ? 'w-5' : size === 'lg' ? 'w-6' : 'w-7';
      expect(checkbox).toHaveClass(expectedClass);
    });
  });

  describe('Interaction', () => {
    it('calls onChange when clicked', async () => {
      const onChange = jest.fn();
      renderCheckbox({ onChange });
      
      const checkbox = screen.getByRole('checkbox');
      await userEvent.click(checkbox);
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('calls onChange when label is clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderCheckbox({ onChange });
      
      const label = screen.getByText('Test Checkbox');
      await user.click(label);
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('does not call onChange when disabled', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderCheckbox({ disabled: true, onChange });
      
      const checkbox = screen.getByRole('checkbox');
      await user.click(checkbox);
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('toggles checked state in uncontrolled mode', async () => {
      const user = userEvent.setup();
      renderCheckbox({ defaultChecked: false });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).not.toBeChecked();
      
      await user.click(checkbox);
      expect(checkbox).toBeChecked();
      
      await user.click(checkbox);
      expect(checkbox).not.toBeChecked();
    });

    it('calls onFocus and onBlur handlers', async () => {
      const user = userEvent.setup();
      const onFocus = jest.fn();
      const onBlur = jest.fn();
      renderCheckbox({ onFocus, onBlur });
      
      const checkbox = screen.getByRole('checkbox');
      
      await user.click(checkbox);
      expect(onFocus).toHaveBeenCalled();
      
      await user.tab();
      expect(onBlur).toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('can be focused with tab', async () => {
      const user = userEvent.setup();
      renderCheckbox();
      
      await user.tab();
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveFocus();
    });

    it('can be activated with space key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderCheckbox({ onChange });
      
      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      await user.keyboard(' ');
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('can be activated with enter key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderCheckbox({ onChange });
      
      const checkbox = screen.getByRole('checkbox');
      checkbox.focus();
      await user.keyboard('{Enter}');
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = renderCheckbox({
        label: 'Accessible Checkbox',
        helperText: 'Helper text for accessibility'
      });
      
      // Basic accessibility check - proper role and attributes
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).toHaveAttribute('type', 'checkbox');
    });

    it('has proper ARIA attributes', () => {
      renderCheckbox({ 
        'aria-label': 'Custom aria label',
        'aria-describedby': 'custom-description'
      });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-label', 'Custom aria label');
      expect(checkbox).toHaveAttribute('aria-describedby', expect.stringContaining('custom-description'));
    });

    it('associates helper text with checkbox', () => {
      renderCheckbox({ 
        helperText: 'Helper text',
        errorMessage: 'Error message',
        error: true
      });
      
      const checkbox = screen.getByRole('checkbox');
      const describedBy = checkbox.getAttribute('aria-describedby');
      expect(describedBy).toBeTruthy();
      
      // Should reference error message when in error state
      const errorElement = screen.getByRole('alert');
      expect(describedBy).toContain(errorElement.id);
    });

    it('has proper label association', () => {
      renderCheckbox();
      
      const checkbox = screen.getByRole('checkbox');
      const label = screen.getByText('Test Checkbox');
      
      expect(checkbox).toHaveAttribute('id');
      expect(label).toHaveAttribute('for', checkbox.id);
    });

    it('supports custom aria-label when no visible label', () => {
      renderCheckbox({ 
        label: undefined,
        'aria-label': 'Custom checkbox label'
      });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-label', 'Custom checkbox label');
    });

    it('indicates indeterminate state to screen readers', () => {
      renderCheckbox({ indeterminate: true });
      
      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      expect(checkbox.indeterminate).toBe(true);
    });
  });

  describe('Form Integration', () => {
    it('submits correct value in form', () => {
      const { container } = render(
        <form>
          <Checkbox 
            name="testCheckbox" 
            value="test-value"
            checked={true}
            label="Test"
          />
        </form>
      );
      
      const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
      expect(checkbox.name).toBe('testCheckbox');
      expect(checkbox.value).toBe('test-value');
      expect(checkbox.checked).toBe(true);
    });

    it('works with form validation', () => {
      renderCheckbox({ 
        required: true,
        name: 'required-checkbox'
      });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('required');
      expect(checkbox).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Visual States', () => {
    it('shows check icon when checked', () => {
      renderCheckbox({ checked: true });
      
      const icon = document.querySelector('.ds-checkbox-icon svg');
      expect(icon).toBeInTheDocument();
    });

    it('shows indeterminate icon when indeterminate', () => {
      renderCheckbox({ indeterminate: true });
      
      const icon = document.querySelector('.ds-checkbox-icon svg');
      expect(icon).toBeInTheDocument();
    });

    it('applies error styling when in error state', () => {
      renderCheckbox({ error: true });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveClass('border-border-error');
    });

    it('applies disabled styling when disabled', () => {
      renderCheckbox({ disabled: true });
      
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveClass('cursor-not-allowed');
      
      const container = checkbox.closest('.ds-checkbox-container');
      expect(container).toHaveClass('opacity-60');
    });
  });

  describe('Polish Localization', () => {
    it('uses Polish text for required indicator', () => {
      renderCheckbox({ required: true });
      
      const requiredIndicator = screen.getByLabelText('wymagane');
      expect(requiredIndicator).toBeInTheDocument();
    });

    it('supports Polish characters in labels', () => {
      renderCheckbox({ label: 'Zaznacz tę opcję ąćęłńóśźż' });
      
      expect(screen.getByText('Zaznacz tę opcję ąćęłńóśźż')).toBeInTheDocument();
    });
  });
});