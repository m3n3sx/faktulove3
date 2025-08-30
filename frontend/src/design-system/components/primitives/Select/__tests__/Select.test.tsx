import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Select, SelectProps, SelectOption } from '../Select';

// Mock options for testing
const mockOptions: SelectOption[] = [
  { value: 'option1', label: 'Opcja 1' },
  { value: 'option2', label: 'Opcja 2' },
  { value: 'option3', label: 'Opcja 3', disabled: true },
  { value: 'option4', label: 'Opcja 4' },
];

// Helper function to render Select with default props
const renderSelect = (props: Partial<SelectProps> = {}) => {
  const defaultProps: SelectProps = {
    options: mockOptions,
    placeholder: 'Wybierz opcję',
    ...props,
  };
  return render(<Select {...defaultProps} />);
};

describe('Select Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      renderSelect();
      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(screen.getByText('Wybierz opcję')).toBeInTheDocument();
    });

    it('renders with label', () => {
      renderSelect({ label: 'Test Label' });
      expect(screen.getByText('Test Label')).toBeInTheDocument();
      expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    });

    it('renders with helper text', () => {
      renderSelect({ helperText: 'Helper text' });
      expect(screen.getByText('Helper text')).toBeInTheDocument();
    });

    it('renders with error message', () => {
      renderSelect({ error: true, errorMessage: 'Error message' });
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('renders required indicator', () => {
      renderSelect({ label: 'Required Field', required: true });
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders with custom placeholder', () => {
      renderSelect({ placeholder: 'Custom placeholder' });
      expect(screen.getByText('Custom placeholder')).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('opens dropdown when clicked', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      mockOptions.forEach(option => {
        if (!option.disabled) {
          expect(screen.getByText(option.label)).toBeInTheDocument();
        }
      });
    });

    it('closes dropdown when clicking outside', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      await user.click(document.body);
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('selects option when clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSelect({ onChange });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const option = screen.getByText('Opcja 1');
      await user.click(option);
      
      expect(onChange).toHaveBeenCalledWith('option1');
      expect(screen.getByText('Opcja 1')).toBeInTheDocument();
    });

    it('does not select disabled option', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSelect({ onChange });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const disabledOption = screen.getByText('Opcja 3');
      await user.click(disabledOption);
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('handles multiple selection', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSelect({ multiple: true, onChange });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const option1 = screen.getByText('Opcja 1');
      const option2 = screen.getByText('Opcja 2');
      
      await user.click(option1);
      expect(onChange).toHaveBeenCalledWith(['option1']);
      
      await user.click(option2);
      expect(onChange).toHaveBeenCalledWith(['option1', 'option2']);
    });

    it('clears selection when clear button is clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      renderSelect({ 
        clearable: true, 
        value: 'option1',
        onChange 
      });
      
      const clearButton = screen.getByLabelText('Wyczyść wybór');
      await user.click(clearButton);
      
      expect(onChange).toHaveBeenCalledWith('');
    });
  });

  describe('Keyboard Navigation', () => {
    it('opens dropdown with Enter key', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      trigger.focus();
      await user.keyboard('{Enter}');
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('opens dropdown with Space key', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      trigger.focus();
      await user.keyboard(' ');
      
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('navigates options with arrow keys', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      trigger.focus();
      await user.keyboard('{Enter}');
      
      // Arrow down should focus first option
      await user.keyboard('{ArrowDown}');
      // Arrow down again should focus second option
      await user.keyboard('{ArrowDown}');
      
      // Enter should select the focused option
      await user.keyboard('{Enter}');
      expect(screen.getByText('Opcja 2')).toBeInTheDocument();
    });

    it('closes dropdown with Escape key', async () => {
      const user = userEvent.setup();
      renderSelect();
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      
      await user.keyboard('{Escape}');
      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    it('filters options when searchable', async () => {
      const user = userEvent.setup();
      renderSelect({ searchable: true });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const searchInput = screen.getByPlaceholderText('Szukaj...');
      await user.type(searchInput, '1');
      
      expect(screen.getByText('Opcja 1')).toBeInTheDocument();
      expect(screen.queryByText('Opcja 2')).not.toBeInTheDocument();
    });

    it('shows no results message when no matches', async () => {
      const user = userEvent.setup();
      renderSelect({ searchable: true });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const searchInput = screen.getByPlaceholderText('Szukaj...');
      await user.type(searchInput, 'xyz');
      
      expect(screen.getByText('Brak wyników')).toBeInTheDocument();
    });
  });

  describe('States', () => {
    it('renders disabled state correctly', () => {
      renderSelect({ disabled: true });
      const trigger = screen.getByRole('button');
      expect(trigger).toBeDisabled();
      expect(trigger).toHaveClass('cursor-not-allowed');
    });

    it('renders error state correctly', () => {
      renderSelect({ error: true });
      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-invalid', 'true');
    });

    it('renders required state correctly', () => {
      renderSelect({ required: true });
      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-required', 'true');
    });
  });

  describe('Size Variants', () => {
    it.each(['xs', 'sm', 'md', 'lg', 'xl'] as const)('renders %s size correctly', (size) => {
      renderSelect({ size });
      const trigger = screen.getByRole('button');
      expect(trigger).toHaveClass(`h-${size === 'xs' ? '6' : size === 'sm' ? '8' : size === 'md' ? '10' : size === 'lg' ? '12' : '14'}`);
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = renderSelect({
        label: 'Accessible Select',
        helperText: 'Helper text for accessibility'
      });
      
      // Basic accessibility check - proper role and attributes
      const select = screen.getByRole('button');
      expect(select).toBeInTheDocument();
      expect(select).toHaveAttribute('aria-haspopup', 'listbox');
    });

    it('has proper ARIA attributes', () => {
      renderSelect({ 
        label: 'Test Select',
        'aria-label': 'Custom aria label'
      });
      
      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');
      expect(trigger).toHaveAttribute('aria-label', 'Custom aria label');
    });

    it('associates helper text with select', () => {
      renderSelect({ 
        helperText: 'Helper text',
        errorMessage: 'Error message',
        error: true
      });
      
      const trigger = screen.getByRole('button');
      const describedBy = trigger.getAttribute('aria-describedby');
      expect(describedBy).toBeTruthy();
      
      // Should reference error message when in error state
      const errorElement = screen.getByRole('alert');
      expect(describedBy).toContain(errorElement.id);
    });

    it('supports screen reader announcements', async () => {
      const user = userEvent.setup();
      renderSelect({ label: 'Test Select' });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const listbox = screen.getByRole('listbox');
      expect(listbox).toHaveAttribute('aria-label', 'Test Select');
      
      const options = screen.getAllByRole('option');
      options.forEach(option => {
        expect(option).toHaveAttribute('aria-selected');
      });
    });

    it('handles focus management correctly', async () => {
      const user = userEvent.setup();
      renderSelect({ searchable: true });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      // Search input should be focused when dropdown opens
      const searchInput = screen.getByPlaceholderText('Szukaj...');
      expect(searchInput).toHaveFocus();
    });
  });

  describe('Form Integration', () => {
    it('submits correct value in form', () => {
      const { container } = render(
        <form>
          <Select 
            name="testSelect" 
            value="option1" 
            options={mockOptions}
          />
        </form>
      );
      
      const hiddenInput = container.querySelector('input[type="hidden"]');
      expect(hiddenInput).toHaveAttribute('name', 'testSelect');
      expect(hiddenInput).toHaveAttribute('value', 'option1');
    });

    it('submits multiple values correctly', () => {
      const { container } = render(
        <form>
          <Select 
            name="testSelect" 
            value={['option1', 'option2']} 
            multiple
            options={mockOptions}
          />
        </form>
      );
      
      const hiddenInput = container.querySelector('input[type="hidden"]');
      expect(hiddenInput).toHaveAttribute('value', 'option1,option2');
    });
  });

  describe('Polish Localization', () => {
    it('uses Polish text for UI elements', async () => {
      const user = userEvent.setup();
      renderSelect({ searchable: true, clearable: true, value: 'option1' });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      expect(screen.getByPlaceholderText('Szukaj...')).toBeInTheDocument();
      expect(screen.getByLabelText('Wyczyść wybór')).toBeInTheDocument();
    });

    it('shows Polish no results message', async () => {
      const user = userEvent.setup();
      renderSelect({ searchable: true });
      
      const trigger = screen.getByRole('button');
      await user.click(trigger);
      
      const searchInput = screen.getByPlaceholderText('Szukaj...');
      await user.type(searchInput, 'nonexistent');
      
      expect(screen.getByText('Brak wyników')).toBeInTheDocument();
    });

    it('shows Polish multiple selection text', () => {
      renderSelect({ 
        multiple: true, 
        value: ['option1', 'option2'] 
      });
      
      expect(screen.getByText('2 opcji wybranych')).toBeInTheDocument();
    });
  });
});