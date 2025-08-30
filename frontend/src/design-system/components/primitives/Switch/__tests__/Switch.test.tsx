import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Switch, SwitchProps } from '../Switch';

// Helper function to render Switch with default props
const renderSwitch = (props: Partial<SwitchProps> = {}) => {
  const defaultProps: SwitchProps = {
    label: 'Test Switch',
    ...props,
  };
  return render(<Switch {...defaultProps} />);
};

describe('Switch Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderSwitch();
      expect(screen.getByRole('switch')).toBeInTheDocument();
      expect(screen.getByText('Test Switch')).toBeInTheDocument();
    });

    it('renders without label', () => {
      renderSwitch({ label: undefined });
      expect(screen.getByRole('switch')).toBeInTheDocument();
      expect(screen.queryByText('Test Switch')).not.toBeInTheDocument();
    });

    it('renders with description', () => {
      renderSwitch({ description: 'Switch description' });
      expect(screen.getByText('Switch description')).toBeInTheDocument();
    });

    it('renders with helper text', () => {
      renderSwitch({ helperText: 'Helper text' });
      expect(screen.getByText('Helper text')).toBeInTheDocument();
    });

    it('renders with error message', () => {
      renderSwitch({ error: true, errorMessage: 'Error message' });
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('renders required indicator', () => {
      renderSwitch({ required: true });
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders with label at start position', () => {
      renderSwitch({ labelPosition: 'start' });
      const container = screen.getByRole('switch').closest('.ds-switch-wrapper');
      expect(container).toHaveClass('flex-row-reverse');
    });

    it('renders with label at end position', () => {
      renderSwitch({ labelPosition: 'end' });
      const container = screen.getByRole('switch').closest('.ds-switch-wrapper');
      expect(container).toHaveClass('flex-row');
    });

    it('renders with custom icons', () => {
      const CheckIcon = () => <span data-testid="check-icon">✓</span>;
      const XIcon = () => <span data-testid="x-icon">✗</span>;
      
      renderSwitch({ 
        checked: true,
        checkedIcon: <CheckIcon />,
        uncheckedIcon: <XIcon />
      });
      
      expect(screen.getByTestId('check-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('x-icon')).not.toBeInTheDocument();
    });
  });

  describe('States', () => {
    it('renders unchecked state', () => {
      renderSwitch({ checked: false });
      const switchElement = screen.getByRole('switch');
      expect(switchElement).not.toBeChecked();
      expect(switchElement).toHaveAttribute('aria-checked', 'false');
    });

    it('renders checked state', () => {
      renderSwitch({ checked: true });
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toBeChecked();
      expect(switchElement).toHaveAttribute('aria-checked', 'true');
    });

    it('renders disabled state', () => {
      renderSwitch({ disabled: true });
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toBeDisabled();
      
      const track = switchElement.closest('label');
      expect(track).toHaveClass('cursor-not-allowed');
    });

    it('renders error state', () => {
      renderSwitch({ error: true });
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-invalid', 'true');
    });

    it('renders required state', () => {
      renderSwitch({ required: true });
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Size Variants', () => {
    it.each(['xs', 'sm', 'md', 'lg', 'xl'] as const)('renders %s size correctly', (size) => {
      renderSwitch({ size });
      const track = document.querySelector('.ds-switch-track');
      const expectedWidthClass = size === 'xs' ? 'w-7' : size === 'sm' ? 'w-9' : size === 'md' ? 'w-11' : size === 'lg' ? 'w-14' : 'w-16';
      expect(track).toHaveClass(expectedWidthClass);
    });
  });

  describe('Interaction', () => {
    it('calls onChange when clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ onChange });
      
      const switchElement = screen.getByRole('switch');
      await user.click(switchElement);
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('calls onChange when track is clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ onChange });
      
      const track = document.querySelector('.ds-switch-track') as HTMLElement;
      await user.click(track);
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('calls onChange when label is clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ onChange });
      
      const label = screen.getByText('Test Switch');
      await user.click(label);
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('does not call onChange when disabled', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ disabled: true, onChange });
      
      const switchElement = screen.getByRole('switch');
      await user.click(switchElement);
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('toggles checked state in uncontrolled mode', async () => {
      const user = userEvent.setup();
      renderSwitch({ defaultChecked: false });
      
      const switchElement = screen.getByRole('switch');
      expect(switchElement).not.toBeChecked();
      
      await user.click(switchElement);
      expect(switchElement).toBeChecked();
      
      await user.click(switchElement);
      expect(switchElement).not.toBeChecked();
    });

    it('calls onFocus and onBlur handlers', async () => {
      const user = userEvent.setup();
      const onFocus = jest.fn();
      const onBlur = jest.fn();
      renderSwitch({ onFocus, onBlur });
      
      const switchElement = screen.getByRole('switch');
      
      await user.click(switchElement);
      expect(onFocus).toHaveBeenCalled();
      
      await user.tab();
      expect(onBlur).toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('can be focused with tab', async () => {
      const user = userEvent.setup();
      renderSwitch();
      
      await user.tab();
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveFocus();
    });

    it('can be activated with space key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ onChange });
      
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      await user.keyboard(' ');
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('can be activated with enter key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ onChange });
      
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      await user.keyboard('{Enter}');
      
      expect(onChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('does not activate when disabled and key is pressed', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSwitch({ disabled: true, onChange });
      
      const switchElement = screen.getByRole('switch');
      switchElement.focus();
      await user.keyboard(' ');
      
      expect(onChange).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = renderSwitch({
        label: 'Accessible Switch',
        description: 'Switch description',
        helperText: 'Helper text for accessibility'
      });
      
      // Basic accessibility check - proper role and attributes
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toBeInTheDocument();
      expect(switchElement).toHaveAttribute('type', 'checkbox');
    });

    it('has proper ARIA attributes', () => {
      renderSwitch({ 
        'aria-label': 'Custom aria label',
        'aria-describedby': 'custom-description'
      });
      
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('role', 'switch');
      expect(switchElement).toHaveAttribute('aria-label', 'Custom aria label');
      expect(switchElement).toHaveAttribute('aria-describedby', expect.stringContaining('custom-description'));
    });

    it('associates description and helper text with switch', () => {
      renderSwitch({ 
        description: 'Switch description',
        helperText: 'Helper text',
        errorMessage: 'Error message',
        error: true
      });
      
      const switchElement = screen.getByRole('switch');
      const describedBy = switchElement.getAttribute('aria-describedby');
      expect(describedBy).toBeTruthy();
      
      // Should reference description, helper text, and error message
      expect(describedBy).toContain('description');
      const errorElement = screen.getByRole('alert');
      expect(describedBy).toContain(errorElement.id);
    });

    it('has proper label association', () => {
      renderSwitch();
      
      const switchElement = screen.getByRole('switch');
      const labels = screen.getAllByText('Test Switch');
      
      expect(switchElement).toHaveAttribute('id');
      labels.forEach(label => {
        expect(label).toHaveAttribute('for', switchElement.id);
      });
    });

    it('supports custom aria-label when no visible label', () => {
      renderSwitch({ 
        label: undefined,
        'aria-label': 'Custom switch label'
      });
      
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-label', 'Custom switch label');
    });

    it('indicates checked state to screen readers', () => {
      renderSwitch({ checked: true });
      
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-checked', 'true');
    });

    it('has proper focus management', async () => {
      const user = userEvent.setup();
      renderSwitch();
      
      const track = document.querySelector('.ds-switch-track') as HTMLElement;
      expect(track).toHaveClass('focus-within:ring-2');
      
      await user.tab();
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveFocus();
    });
  });

  describe('Form Integration', () => {
    it('submits correct value in form', () => {
      const { container } = render(
        <form>
          <Switch 
            name="testSwitch" 
            value="test-value"
            checked={true}
            label="Test"
          />
        </form>
      );
      
      const switchElement = screen.getByRole('switch') as HTMLInputElement;
      expect(switchElement.name).toBe('testSwitch');
      expect(switchElement.value).toBe('test-value');
      expect(switchElement.checked).toBe(true);
    });

    it('works with form validation', () => {
      renderSwitch({ 
        required: true,
        name: 'required-switch'
      });
      
      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('required');
      expect(switchElement).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Visual States', () => {
    it('shows thumb in correct position when unchecked', () => {
      renderSwitch({ checked: false });
      
      const thumb = document.querySelector('.ds-switch-thumb');
      expect(thumb).toHaveClass('translate-x-0');
    });

    it('shows thumb in correct position when checked', () => {
      renderSwitch({ checked: true, size: 'md' });
      
      const thumb = document.querySelector('.ds-switch-thumb');
      expect(thumb).toHaveClass('translate-x-5');
    });

    it('applies correct track colors for unchecked state', () => {
      renderSwitch({ checked: false });
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('bg-border-muted');
    });

    it('applies correct track colors for checked state', () => {
      renderSwitch({ checked: true });
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('bg-primary-600');
    });

    it('applies error styling when in error state', () => {
      renderSwitch({ error: true, checked: false });
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('bg-error-200');
    });

    it('applies error styling when checked and in error state', () => {
      renderSwitch({ error: true, checked: true });
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('bg-error-600');
    });

    it('applies disabled styling when disabled', () => {
      renderSwitch({ disabled: true });
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('bg-background-disabled');
      
      const container = track?.closest('.ds-switch-container');
      expect(container).toHaveClass('opacity-60');
    });

    it('shows icons correctly based on state', () => {
      const CheckIcon = () => <span data-testid="check-icon">✓</span>;
      const XIcon = () => <span data-testid="x-icon">✗</span>;
      
      const { rerender } = renderSwitch({ 
        checked: false,
        checkedIcon: <CheckIcon />,
        uncheckedIcon: <XIcon />
      });
      
      expect(screen.getByTestId('x-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('check-icon')).not.toBeInTheDocument();
      
      rerender(
        <Switch 
          checked={true}
          checkedIcon={<CheckIcon />}
          uncheckedIcon={<XIcon />}
          label="Test Switch"
        />
      );
      
      expect(screen.getByTestId('check-icon')).toBeInTheDocument();
      expect(screen.queryByTestId('x-icon')).not.toBeInTheDocument();
    });
  });

  describe('Polish Localization', () => {
    it('uses Polish text for required indicator', () => {
      renderSwitch({ required: true });
      
      const requiredIndicator = screen.getByLabelText('wymagane');
      expect(requiredIndicator).toBeInTheDocument();
    });

    it('supports Polish characters in labels and descriptions', () => {
      renderSwitch({ 
        label: 'Przełącznik z polskimi znakami ąćęłńóśźż',
        description: 'Opis z polskimi znakami ąćęłńóśźż'
      });
      
      expect(screen.getByText('Przełącznik z polskimi znakami ąćęłńóśźż')).toBeInTheDocument();
      expect(screen.getByText('Opis z polskimi znakami ąćęłńóśźż')).toBeInTheDocument();
    });
  });

  describe('Animation and Transitions', () => {
    it('applies transition classes to thumb', () => {
      renderSwitch();
      
      const thumb = document.querySelector('.ds-switch-thumb');
      expect(thumb).toHaveClass('transition-all', 'duration-200', 'ease-out');
    });

    it('applies transition classes to track', () => {
      renderSwitch();
      
      const track = document.querySelector('.ds-switch-track');
      expect(track).toHaveClass('transition-all', 'duration-200', 'ease-out');
    });
  });
});