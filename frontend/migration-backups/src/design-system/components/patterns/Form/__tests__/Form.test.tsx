import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Form, FormField, validateNIP, validateREGON, POLISH_VALIDATION_PATTERNS } from '../Form';
import { Input } from '../../../primitives/Input/Input';

expect.extend(toHaveNoViolations);

// Mock input component for testing
const TestInput: React.FC<any> = ({ value, onChange, onBlur, ...props }) => (
  <input
    type="text"
    value={value || ''}
    onChange={onChange}
    onBlur={onBlur}
    {...props}
  />
);

describe('Form Component', () => {
  const mockSubmit = jest.fn();

  beforeEach(() => {
    mockSubmit.mockClear();
  });

  describe('Basic Form Functionality', () => {
    it('renders form with children', () => {
      render(
        <Form onSubmit={mockSubmit}>
          <FormField name="test" label="Test Field">
            <TestInput />
          </FormField>
        </Form>
      );

      expect(screen.getByRole('form')).toBeInTheDocument();
      expect(screen.getByLabelText('Test Field')).toBeInTheDocument();
    });

    it('handles form submission with valid data', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit}>
          <FormField name="name" label="Name" rules={{ required: true }}>
            <TestInput />
          </FormField>
          <button type="submit">Submit</button>
        </Form>
      );

      const input = screen.getByLabelText('Name *');
      const submitButton = screen.getByRole('button', { name: 'Submit' });

      await user.type(input, 'John Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({ name: 'John Doe' });
      });
    });

    it('prevents submission with invalid data', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit}>
          <FormField name="email" label="Email" rules={{ required: true }}>
            <TestInput />
          </FormField>
          <button type="submit">Submit</button>
        </Form>
      );

      const submitButton = screen.getByRole('button', { name: 'Submit' });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('To pole jest wymagane')).toBeInTheDocument();
      });

      expect(mockSubmit).not.toHaveBeenCalled();
    });

    it('displays initial values', () => {
      render(
        <Form onSubmit={mockSubmit} initialValues={{ name: 'Initial Value' }}>
          <FormField name="name" label="Name">
            <TestInput />
          </FormField>
        </Form>
      );

      expect(screen.getByDisplayValue('Initial Value')).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('validates required fields', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onBlur">
          <FormField name="required" label="Required Field" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Required Field *');
      await user.click(input);
      await user.tab(); // Trigger blur

      await waitFor(() => {
        expect(screen.getByText('To pole jest wymagane')).toBeInTheDocument();
      });
    });

    it('validates minimum length', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onChange">
          <FormField name="minLength" label="Min Length" rules={{ minLength: 5 }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Min Length');
      await user.type(input, 'abc');

      await waitFor(() => {
        expect(screen.getByText('Minimalna długość: 5 znaków')).toBeInTheDocument();
      });
    });

    it('validates maximum length', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onChange">
          <FormField name="maxLength" label="Max Length" rules={{ maxLength: 3 }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Max Length');
      await user.type(input, 'abcdef');

      await waitFor(() => {
        expect(screen.getByText('Maksymalna długość: 3 znaków')).toBeInTheDocument();
      });
    });

    it('validates custom patterns', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onChange">
          <FormField 
            name="pattern" 
            label="Pattern Field" 
            rules={{ pattern: /^\d+$/ }}
          >
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Pattern Field');
      await user.type(input, 'abc123');

      await waitFor(() => {
        expect(screen.getByText('Nieprawidłowy format')).toBeInTheDocument();
      });
    });

    it('validates with custom function', async () => {
      const user = userEvent.setup();
      const customValidator = (value: string) => 
        value === 'forbidden' ? 'Wartość niedozwolona' : null;
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onChange">
          <FormField 
            name="custom" 
            label="Custom Field" 
            rules={{ custom: customValidator }}
          >
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Custom Field');
      await user.type(input, 'forbidden');

      await waitFor(() => {
        expect(screen.getByText('Wartość niedozwolona')).toBeInTheDocument();
      });
    });
  });

  describe('Polish Validation Patterns', () => {
    describe('NIP Validation', () => {
      it('validates correct NIP numbers', () => {
        expect(validateNIP('123-456-78-90')).toBe(false); // Invalid checksum
        expect(validateNIP('123-456-32-18')).toBe(true);  // Valid NIP
        expect(validateNIP('1234563218')).toBe(true);     // Valid NIP without dashes
      });

      it('rejects invalid NIP format', () => {
        expect(validateNIP('123-456-78')).toBe(false);
        expect(validateNIP('abc-def-gh-ij')).toBe(false);
        expect(validateNIP('')).toBe(false);
      });

      it('displays NIP validation error', async () => {
        const user = userEvent.setup();
        
        render(
          <Form onSubmit={mockSubmit} validationMode="onChange">
            <FormField 
              name="nip" 
              label="NIP" 
              rules={{ polishValidator: 'NIP' }}
            >
              <TestInput />
            </FormField>
          </Form>
        );

        const input = screen.getByLabelText('NIP');
        await user.type(input, '123-456-78-90');

        await waitFor(() => {
          expect(screen.getByText('Nieprawidłowy numer NIP')).toBeInTheDocument();
        });
      });
    });

    describe('REGON Validation', () => {
      it('validates REGON format', () => {
        expect(validateREGON('123456785')).toBe(true);   // Valid 9-digit REGON
        expect(validateREGON('12345678512347')).toBe(true); // Valid 14-digit REGON
        expect(validateREGON('12345678')).toBe(false);   // Invalid length
        expect(validateREGON('abcdefghi')).toBe(false);  // Invalid characters
      });

      it('displays REGON validation error', async () => {
        const user = userEvent.setup();
        
        render(
          <Form onSubmit={mockSubmit} validationMode="onChange">
            <FormField 
              name="regon" 
              label="REGON" 
              rules={{ polishValidator: 'REGON' }}
            >
              <TestInput />
            </FormField>
          </Form>
        );

        const input = screen.getByLabelText('REGON');
        await user.type(input, '12345678');

        await waitFor(() => {
          expect(screen.getByText('Nieprawidłowy numer REGON')).toBeInTheDocument();
        });
      });
    });

    describe('Other Polish Validators', () => {
      it('validates postal code', async () => {
        const user = userEvent.setup();
        
        render(
          <Form onSubmit={mockSubmit} validationMode="onChange">
            <FormField 
              name="postal" 
              label="Kod pocztowy" 
              rules={{ polishValidator: 'POSTAL_CODE' }}
            >
              <TestInput />
            </FormField>
          </Form>
        );

        const input = screen.getByLabelText('Kod pocztowy');
        await user.type(input, '12345');

        await waitFor(() => {
          expect(screen.getByText('Nieprawidłowy kod pocztowy (format: 00-000)')).toBeInTheDocument();
        });
      });

      it('validates phone number', async () => {
        const user = userEvent.setup();
        
        render(
          <Form onSubmit={mockSubmit} validationMode="onChange">
            <FormField 
              name="phone" 
              label="Telefon" 
              rules={{ polishValidator: 'PHONE' }}
            >
              <TestInput />
            </FormField>
          </Form>
        );

        const input = screen.getByLabelText('Telefon');
        await user.type(input, '123');

        await waitFor(() => {
          expect(screen.getByText('Nieprawidłowy numer telefonu')).toBeInTheDocument();
        });
      });
    });
  });

  describe('Validation Modes', () => {
    it('validates onChange when mode is onChange', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onChange">
          <FormField name="test" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByRole('textbox');
      await user.type(input, 'a');
      await user.clear(input);

      await waitFor(() => {
        expect(screen.getByText('To pole jest wymagane')).toBeInTheDocument();
      });
    });

    it('validates onBlur when mode is onBlur', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onBlur">
          <FormField name="test" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText('To pole jest wymagane')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', async () => {
      const { container } = render(
        <Form onSubmit={mockSubmit}>
          <FormField name="name" label="Name" rules={{ required: true }}>
            <TestInput />
          </FormField>
          <FormField name="email" label="Email">
            <TestInput />
          </FormField>
        </Form>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('associates labels with inputs', () => {
      render(
        <Form onSubmit={mockSubmit}>
          <FormField name="test" label="Test Label">
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Test Label');
      expect(input).toHaveAttribute('id', 'test');
    });

    it('marks required fields with asterisk', () => {
      render(
        <Form onSubmit={mockSubmit}>
          <FormField name="required" label="Required Field" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      expect(screen.getByLabelText('Required Field *')).toBeInTheDocument();
    });

    it('provides error announcements', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onBlur">
          <FormField name="test" label="Test" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByLabelText('Test *');
      await user.click(input);
      await user.tab();

      await waitFor(() => {
        const errorMessage = screen.getByRole('alert');
        expect(errorMessage).toHaveAttribute('aria-live', 'polite');
        expect(errorMessage).toHaveTextContent('To pole jest wymagane');
      });
    });

    it('sets aria-invalid on fields with errors', async () => {
      const user = userEvent.setup();
      
      render(
        <Form onSubmit={mockSubmit} validationMode="onBlur">
          <FormField name="test" rules={{ required: true }}>
            <TestInput />
          </FormField>
        </Form>
      );

      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.tab();

      await waitFor(() => {
        expect(input).toHaveAttribute('aria-invalid', 'true');
        expect(input).toHaveAttribute('aria-describedby', 'test-error');
      });
    });
  });

  describe('Form State Management', () => {
    it('tracks form submission state', async () => {
      const user = userEvent.setup();
      let submissionPromise: Promise<void>;
      
      const slowSubmit = jest.fn(() => {
        submissionPromise = new Promise(resolve => setTimeout(resolve, 100));
        return submissionPromise;
      });

      render(
        <Form onSubmit={slowSubmit}>
          <FormField name="test" rules={{ required: true }}>
            <TestInput />
          </FormField>
          <button type="submit">Submit</button>
        </Form>
      );

      const input = screen.getByRole('textbox');
      const submitButton = screen.getByRole('button');

      await user.type(input, 'test value');
      await user.click(submitButton);

      // Form should be in submitting state
      expect(slowSubmit).toHaveBeenCalled();
      
      // Wait for submission to complete
      await submissionPromise!;
    });

    it('handles form submission errors gracefully', async () => {
      const user = userEvent.setup();
      const errorSubmit = jest.fn().mockRejectedValue(new Error('Submission failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <Form onSubmit={errorSubmit}>
          <FormField name="test" rules={{ required: true }}>
            <TestInput />
          </FormField>
          <button type="submit">Submit</button>
        </Form>
      );

      const input = screen.getByRole('textbox');
      const submitButton = screen.getByRole('button');

      await user.type(input, 'test value');
      await user.click(submitButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Form submission error:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });
  });
});