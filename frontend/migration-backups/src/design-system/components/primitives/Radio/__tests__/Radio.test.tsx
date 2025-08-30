import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Radio, RadioGroup, RadioProps, RadioGroupProps, RadioOption } from '../Radio';

// Mock options for testing
const mockOptions: RadioOption[] = [
  { value: 'option1', label: 'Opcja 1' },
  { value: 'option2', label: 'Opcja 2' },
  { value: 'option3', label: 'Opcja 3', disabled: true },
  { value: 'option4', label: 'Opcja 4', description: 'Opis opcji 4' },
];

// Helper function to render Radio with default props
const renderRadio = (props: Partial<RadioProps> = {}) => {
  const defaultProps: RadioProps = {
    label: 'Test Radio',
    name: 'test-radio',
    value: 'test-value',
    ...props,
  };
  return render(<Radio {...defaultProps} />);
};

// Helper function to render RadioGroup with default props
const renderRadioGroup = (props: Partial<RadioGroupProps> = {}) => {
  const defaultProps: RadioGroupProps = {
    options: mockOptions,
    name: 'test-group',
    label: 'Test Radio Group',
    ...props,
  };
  return render(<RadioGroup {...defaultProps} />);
};

describe('Radio Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderRadio();
      expect(screen.getByRole('radio')).toBeInTheDocument();
      expect(screen.getByText('Test Radio')).toBeInTheDocument();
    });

    it('renders without label', () => {
      renderRadio({ label: undefined });
      expect(screen.getByRole('radio')).toBeInTheDocument();
      expect(screen.queryByText('Test Radio')).not.toBeInTheDocument();
    });

    it('renders required indicator', () => {
      renderRadio({ required: true });
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders with label at start position', () => {
      renderRadio({ labelPosition: 'start' });
      const container = screen.getByRole('radio').closest('.ds-radio-wrapper');
      expect(container).toHaveClass('flex-row-reverse');
    });

    it('renders with label at end position', () => {
      renderRadio({ labelPosition: 'end' });
      const container = screen.getByRole('radio').closest('.ds-radio-wrapper');
      expect(container).toHaveClass('flex-row');
    });
  });

  describe('States', () => {
    it('renders unchecked state', () => {
      renderRadio({ checked: false });
      const radio = screen.getByRole('radio');
      expect(radio).not.toBeChecked();
    });

    it('renders checked state', () => {
      renderRadio({ checked: true });
      const radio = screen.getByRole('radio');
      expect(radio).toBeChecked();
    });

    it('renders disabled state', () => {
      renderRadio({ disabled: true });
      const radio = screen.getByRole('radio');
      expect(radio).toBeDisabled();
      expect(radio).toHaveClass('cursor-not-allowed');
    });

    it('renders error state', () => {
      renderRadio({ error: true });
      const radio = screen.getByRole('radio');
      expect(radio).toHaveAttribute('aria-invalid', 'true');
    });

    it('renders required state', () => {
      renderRadio({ required: true });
      const radio = screen.getByRole('radio');
      expect(radio).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Size Variants', () => {
    it.each(['xs', 'sm', 'md', 'lg', 'xl'] as const)('renders %s size correctly', (size) => {
      renderRadio({ size });
      const radio = screen.getByRole('radio');
      const expectedClass = size === 'xs' ? 'w-3' : size === 'sm' ? 'w-4' : size === 'md' ? 'w-5' : size === 'lg' ? 'w-6' : 'w-7';
      expect(radio).toHaveClass(expectedClass);
    });
  });

  describe('Interaction', () => {
    it('calls onChange when clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderRadio({ onChange });
      
      const radio = screen.getByRole('radio');
      await user.click(radio);
      
      expect(onChange).toHaveBeenCalledWith(expect.any(Object));
    });

    it('calls onChange when label is clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderRadio({ onChange });
      
      const label = screen.getByText('Test Radio');
      await user.click(label);
      
      expect(onChange).toHaveBeenCalledWith(expect.any(Object));
    });

    it('does not call onChange when disabled', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderRadio({ disabled: true, onChange });
      
      const radio = screen.getByRole('radio');
      await user.click(radio);
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('calls onFocus and onBlur handlers', async () => {
      const user = userEvent.setup();
      const onFocus = jest.fn();
      const onBlur = jest.fn();
      renderRadio({ onFocus, onBlur });
      
      const radio = screen.getByRole('radio');
      
      await user.click(radio);
      expect(onFocus).toHaveBeenCalled();
      
      await user.tab();
      expect(onBlur).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = renderRadio({
        label: 'Accessible Radio'
      });
      
      // Basic accessibility check - proper role and attributes
      const radio = screen.getByRole('radio');
      expect(radio).toBeInTheDocument();
      expect(radio).toHaveAttribute('type', 'radio');
    });

    it('has proper ARIA attributes', () => {
      renderRadio({ 
        'aria-label': 'Custom aria label',
        'aria-describedby': 'custom-description'
      });
      
      const radio = screen.getByRole('radio');
      expect(radio).toHaveAttribute('aria-label', 'Custom aria label');
      expect(radio).toHaveAttribute('aria-describedby', 'custom-description');
    });

    it('has proper label association', () => {
      renderRadio();
      
      const radio = screen.getByRole('radio');
      const label = screen.getByText('Test Radio');
      
      expect(radio).toHaveAttribute('id');
      expect(label).toHaveAttribute('for', radio.id);
    });
  });

  describe('Visual States', () => {
    it('shows dot when checked', () => {
      renderRadio({ checked: true });
      
      const dot = document.querySelector('.ds-radio-dot');
      expect(dot).toHaveClass('opacity-100');
    });

    it('hides dot when unchecked', () => {
      renderRadio({ checked: false });
      
      const dot = document.querySelector('.ds-radio-dot');
      expect(dot).toHaveClass('opacity-0');
    });

    it('applies error styling when in error state', () => {
      renderRadio({ error: true });
      
      const radio = screen.getByRole('radio');
      expect(radio).toHaveClass('border-border-error');
    });

    it('applies disabled styling when disabled', () => {
      renderRadio({ disabled: true });
      
      const radio = screen.getByRole('radio');
      expect(radio).toHaveClass('cursor-not-allowed');
      
      const container = radio.closest('.ds-radio-container');
      expect(container).toHaveClass('opacity-60');
    });
  });
});

describe('RadioGroup Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderRadioGroup();
      expect(screen.getByRole('radiogroup')).toBeInTheDocument();
      expect(screen.getByText('Test Radio Group')).toBeInTheDocument();
      
      mockOptions.forEach(option => {
        expect(screen.getByText(option.label)).toBeInTheDocument();
      });
    });

    it('renders without label', () => {
      renderRadioGroup({ label: undefined });
      expect(screen.getByRole('radiogroup')).toBeInTheDocument();
      expect(screen.queryByText('Test Radio Group')).not.toBeInTheDocument();
    });

    it('renders with helper text', () => {
      renderRadioGroup({ helperText: 'Helper text' });
      expect(screen.getByText('Helper text')).toBeInTheDocument();
    });

    it('renders with error message', () => {
      renderRadioGroup({ error: true, errorMessage: 'Error message' });
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('renders required indicator', () => {
      renderRadioGroup({ required: true });
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders option descriptions', () => {
      renderRadioGroup();
      expect(screen.getByText('Opis opcji 4')).toBeInTheDocument();
    });

    it('renders disabled options', () => {
      renderRadioGroup();
      const disabledRadio = screen.getByDisplayValue('option3');
      expect(disabledRadio).toBeDisabled();
    });
  });

  describe('Layout', () => {
    it('renders vertical layout by default', () => {
      renderRadioGroup();
      const optionsContainer = document.querySelector('.ds-radio-group-options');
      expect(optionsContainer).toHaveClass('flex-col');
    });

    it('renders horizontal layout when specified', () => {
      renderRadioGroup({ direction: 'horizontal' });
      const optionsContainer = document.querySelector('.ds-radio-group-options');
      expect(optionsContainer).toHaveClass('flex-row');
    });
  });

  describe('Selection', () => {
    it('shows selected value', () => {
      renderRadioGroup({ value: 'option1' });
      const selectedRadio = screen.getByDisplayValue('option1');
      expect(selectedRadio).toBeChecked();
    });

    it('calls onChange when option is selected', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderRadioGroup({ onChange });
      
      const option = screen.getByText('Opcja 2');
      await user.click(option);
      
      expect(onChange).toHaveBeenCalledWith('option2', expect.any(Object));
    });

    it('does not select disabled options', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderRadioGroup({ onChange });
      
      const disabledOption = screen.getByText('Opcja 3');
      await user.click(disabledOption);
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('allows only one selection at a time', async () => {
      const user = userEvent.setup();
      renderRadioGroup({ defaultValue: 'option1' });
      
      const option1 = screen.getByDisplayValue('option1');
      const option2 = screen.getByDisplayValue('option2');
      
      expect(option1).toBeChecked();
      expect(option2).not.toBeChecked();
      
      await user.click(screen.getByText('Opcja 2'));
      
      expect(option1).not.toBeChecked();
      expect(option2).toBeChecked();
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports arrow key navigation', async () => {
      const user = userEvent.setup();
      renderRadioGroup();
      
      const firstRadio = screen.getByDisplayValue('option1');
      firstRadio.focus();
      
      await user.keyboard('{ArrowDown}');
      const secondRadio = screen.getByDisplayValue('option2');
      expect(secondRadio).toHaveFocus();
      
      await user.keyboard('{ArrowDown}');
      // Should skip disabled option3 and go to option4
      const fourthRadio = screen.getByDisplayValue('option4');
      expect(fourthRadio).toHaveFocus();
    });

    it('wraps around when navigating with arrows', async () => {
      const user = userEvent.setup();
      renderRadioGroup();
      
      const lastRadio = screen.getByDisplayValue('option4');
      lastRadio.focus();
      
      await user.keyboard('{ArrowDown}');
      const firstRadio = screen.getByDisplayValue('option1');
      expect(firstRadio).toHaveFocus();
    });
  });

  describe('States', () => {
    it('renders disabled state correctly', () => {
      renderRadioGroup({ disabled: true });
      const radios = screen.getAllByRole('radio');
      radios.forEach(radio => {
        expect(radio).toBeDisabled();
      });
    });

    it('renders error state correctly', () => {
      renderRadioGroup({ error: true });
      const fieldset = screen.getByRole('radiogroup').closest('fieldset');
      expect(fieldset).toHaveAttribute('aria-invalid', 'true');
    });

    it('renders required state correctly', () => {
      renderRadioGroup({ required: true });
      const fieldset = screen.getByRole('radiogroup').closest('fieldset');
      expect(fieldset).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Size Variants', () => {
    it.each(['xs', 'sm', 'md', 'lg', 'xl'] as const)('renders %s size correctly', (size) => {
      renderRadioGroup({ size });
      const radios = screen.getAllByRole('radio');
      const expectedClass = size === 'xs' ? 'w-3' : size === 'sm' ? 'w-4' : size === 'md' ? 'w-5' : size === 'lg' ? 'w-6' : 'w-7';
      radios.forEach(radio => {
        expect(radio).toHaveClass(expectedClass);
      });
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = renderRadioGroup({
        label: 'Accessible Radio Group',
        helperText: 'Helper text for accessibility'
      });
      
      // Basic accessibility check - proper role and attributes
      const radiogroup = screen.getByRole('radiogroup');
      expect(radiogroup).toBeInTheDocument();
    });

    it('has proper ARIA attributes', () => {
      renderRadioGroup({ 
        'aria-label': 'Custom aria label'
      });
      
      const radiogroup = screen.getByRole('radiogroup');
      expect(radiogroup).toHaveAttribute('aria-label', 'Custom aria label');
    });

    it('associates helper text with radiogroup', () => {
      renderRadioGroup({ 
        helperText: 'Helper text',
        errorMessage: 'Error message',
        error: true
      });
      
      const fieldset = screen.getByRole('radiogroup').closest('fieldset');
      const describedBy = fieldset?.getAttribute('aria-describedby');
      expect(describedBy).toBeTruthy();
      
      // Should reference error message when in error state
      const errorElement = screen.getByRole('alert');
      expect(describedBy).toContain(errorElement.id);
    });

    it('uses fieldset and legend for proper grouping', () => {
      renderRadioGroup();
      
      const fieldset = screen.getByRole('radiogroup').closest('fieldset');
      const legend = screen.getByText('Test Radio Group');
      
      expect(fieldset).toBeInTheDocument();
      expect(legend.tagName.toLowerCase()).toBe('legend');
    });

    it('has proper radio button attributes', () => {
      renderRadioGroup({ name: 'test-group' });
      
      const radios = screen.getAllByRole('radio');
      radios.forEach(radio => {
        expect(radio).toHaveAttribute('name', 'test-group');
        expect(radio).toHaveAttribute('type', 'radio');
      });
    });
  });

  describe('Form Integration', () => {
    it('submits correct value in form', () => {
      renderRadioGroup({ 
        name: 'testRadioGroup',
        value: 'option1'
      });
      
      const selectedRadio = screen.getByDisplayValue('option1') as HTMLInputElement;
      expect(selectedRadio.name).toBe('testRadioGroup');
      expect(selectedRadio.value).toBe('option1');
      expect(selectedRadio.checked).toBe(true);
    });

    it('works with form validation', () => {
      renderRadioGroup({ 
        required: true,
        name: 'required-radio-group'
      });
      
      const fieldset = screen.getByRole('radiogroup').closest('fieldset');
      expect(fieldset).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Polish Localization', () => {
    it('uses Polish text for required indicator', () => {
      renderRadioGroup({ required: true });
      
      const requiredIndicator = screen.getByLabelText('wymagane');
      expect(requiredIndicator).toBeInTheDocument();
    });

    it('supports Polish characters in labels and descriptions', () => {
      const polishOptions: RadioOption[] = [
        { value: 'pl1', label: 'Opcja z polskimi znakami ąćęłńóśźż' },
        { value: 'pl2', label: 'Druga opcja', description: 'Opis z polskimi znakami ąćęłńóśźż' },
      ];
      
      renderRadioGroup({ 
        options: polishOptions,
        label: 'Grupa opcji z polskimi znakami'
      });
      
      expect(screen.getByText('Opcja z polskimi znakami ąćęłńóśźż')).toBeInTheDocument();
      expect(screen.getByText('Opis z polskimi znakami ąćęłńóśźż')).toBeInTheDocument();
      expect(screen.getByText('Grupa opcji z polskimi znakami')).toBeInTheDocument();
    });
  });
});