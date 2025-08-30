/**
 * Comprehensive Design System Test Suite
 * Tests all components with all variants and states
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';

// Import all components
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Select } from '../components/primitives/Select/Select';
import { Checkbox } from '../components/primitives/Checkbox/Checkbox';
import { Radio } from '../components/primitives/Radio/Radio';
import { Switch } from '../components/primitives/Switch/Switch';
import { Card } from '../components/patterns/Card/Card';
import { Form } from '../components/patterns/Form/Form';
import { Table } from '../components/patterns/Table/Table';
import { Grid } from '../components/layouts/Grid/Grid';
import { Container } from '../components/layouts/Container/Container';
import { Stack } from '../components/layouts/Stack/Stack';
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../components/business/DatePicker/DatePicker';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';

// Import test utilities
import { runA11yTestSuite } from '../utils/testUtils';

describe('Design System - Comprehensive Component Tests', () => {
  describe('Primitive Components', () => {
    describe('Button Component', () => {
      const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
      const sizes = ['xs', 'sm', 'md', 'lg', 'xl'] as const;
      const states = ['default', 'loading', 'disabled'] as const;

      variants.forEach(variant => {
        sizes.forEach(size => {
          states.forEach(state => {
            it(`renders ${variant} ${size} ${state} button correctly`, async () => {
              const props = {
                variant,
                size,
                loading: state === 'loading',
                disabled: state === 'disabled',
                children: `${variant} ${size} ${state}`,
              };

              const { container } = render(<Button {...props} />);
              
              // Test accessibility
              await runA11yTestSuite(container, {
                testKeyboard: true,
                testScreenReader: true,
                testFocus: true,
              });

              // Test visual rendering
              const button = screen.getByRole('button');
              expect(button).toBeInTheDocument();
              expect(button).toHaveTextContent(`${variant} ${size} ${state}`);

              if (state === 'disabled') {
                expect(button).toBeDisabled();
              }

              if (state === 'loading') {
                expect(button).toHaveAttribute('aria-busy', 'true');
              }
            });
          });
        });
      });

      it('handles click events correctly', async () => {
        const handleClick = jest.fn();
        const user = userEvent.setup();

        render(<Button onClick={handleClick}>Click me</Button>);
        
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(handleClick).toHaveBeenCalledTimes(1);
      });

      it('supports keyboard activation', async () => {
        const handleClick = jest.fn();
        const user = userEvent.setup();

        render(<Button onClick={handleClick}>Press me</Button>);
        
        const button = screen.getByRole('button');
        button.focus();
        await user.keyboard('{Enter}');
        
        expect(handleClick).toHaveBeenCalledTimes(1);
      });
    });

    describe('Input Component', () => {
      const types = ['text', 'email', 'password', 'number'] as const;
      const sizes = ['sm', 'md', 'lg'] as const;
      const states = ['default', 'error', 'success'] as const;

      types.forEach(type => {
        sizes.forEach(size => {
          states.forEach(state => {
            it(`renders ${type} ${size} ${state} input correctly`, async () => {
              const props = {
                type,
                size,
                error: state === 'error' ? 'Error message' : undefined,
                success: state === 'success' ? 'Success message' : undefined,
                placeholder: `${type} ${size} ${state}`,
                'aria-label': `${type} input`,
              };

              const { container } = render(<Input {...props} />);
              
              // Test accessibility
              await runA11yTestSuite(container, {
                testKeyboard: true,
                testScreenReader: true,
                testFocus: true,
              });

              // Test visual rendering
              const input = screen.getByRole('textbox');
              expect(input).toBeInTheDocument();
              expect(input).toHaveAttribute('type', type === 'text' ? 'text' : type);
            });
          });
        });
      });

      it('handles value changes correctly', async () => {
        const handleChange = jest.fn();
        const user = userEvent.setup();

        render(<Input onChange={handleChange} aria-label="Test input" />);
        
        const input = screen.getByRole('textbox');
        await user.type(input, 'test value');
        
        expect(handleChange).toHaveBeenCalled();
        expect(input).toHaveValue('test value');
      });
    });

    describe('Select Component', () => {
      const options = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' },
        { value: 'option3', label: 'Option 3' },
      ];

      it('renders select with options correctly', async () => {
        const { container } = render(
          <Select options={options} aria-label="Test select" />
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const select = screen.getByRole('combobox');
        expect(select).toBeInTheDocument();
      });

      it('handles selection changes', async () => {
        const handleChange = jest.fn();
        const user = userEvent.setup();

        render(
          <Select 
            options={options} 
            onChange={handleChange}
            aria-label="Test select"
          />
        );
        
        const select = screen.getByRole('combobox');
        await user.selectOptions(select, 'option2');
        
        expect(handleChange).toHaveBeenCalled();
      });
    });

    describe('Checkbox Component', () => {
      it('renders checkbox correctly', async () => {
        const { container } = render(
          <Checkbox aria-label="Test checkbox">Test checkbox</Checkbox>
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const checkbox = screen.getByRole('checkbox');
        expect(checkbox).toBeInTheDocument();
      });

      it('handles check state changes', async () => {
        const handleChange = jest.fn();
        const user = userEvent.setup();

        render(
          <Checkbox onChange={handleChange} aria-label="Test checkbox">
            Test checkbox
          </Checkbox>
        );
        
        const checkbox = screen.getByRole('checkbox');
        await user.click(checkbox);
        
        expect(handleChange).toHaveBeenCalled();
        expect(checkbox).toBeChecked();
      });
    });

    describe('Radio Component', () => {
      it('renders radio group correctly', async () => {
        const { container } = render(
          <div role="radiogroup" aria-label="Test radio group">
            <Radio name="test" value="option1">Option 1</Radio>
            <Radio name="test" value="option2">Option 2</Radio>
          </div>
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const radios = screen.getAllByRole('radio');
        expect(radios).toHaveLength(2);
      });
    });

    describe('Switch Component', () => {
      it('renders switch correctly', async () => {
        const { container } = render(
          <Switch aria-label="Test switch">Test switch</Switch>
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const switchElement = screen.getByRole('switch');
        expect(switchElement).toBeInTheDocument();
      });

      it('handles toggle state changes', async () => {
        const handleChange = jest.fn();
        const user = userEvent.setup();

        render(
          <Switch onChange={handleChange} aria-label="Test switch">
            Test switch
          </Switch>
        );
        
        const switchElement = screen.getByRole('switch');
        await user.click(switchElement);
        
        expect(handleChange).toHaveBeenCalled();
      });
    });
  });

  describe('Pattern Components', () => {
    describe('Card Component', () => {
      it('renders card with all sections correctly', async () => {
        const { container } = render(
          <Card>
            <Card.Header>Card Header</Card.Header>
            <Card.Body>Card Body Content</Card.Body>
            <Card.Footer>Card Footer</Card.Footer>
          </Card>
        );
        
        // Test accessibility
        await runA11yTestSuite(container);

        expect(screen.getByText('Card Header')).toBeInTheDocument();
        expect(screen.getByText('Card Body Content')).toBeInTheDocument();
        expect(screen.getByText('Card Footer')).toBeInTheDocument();
      });
    });

    describe('Form Component', () => {
      it('renders form with validation correctly', async () => {
        const { container } = render(
          <Form onSubmit={() => {}}>
            <Input aria-label="Name" name="name" required />
            <Button type="submit">Submit</Button>
          </Form>
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const form = container.querySelector('form');
        expect(form).toBeInTheDocument();
      });
    });

    describe('Table Component', () => {
      const data = [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
      ];

      const columns = [
        { key: 'name', header: 'Name' },
        { key: 'email', header: 'Email' },
      ];

      it('renders table with data correctly', async () => {
        const { container } = render(
          <Table data={data} columns={columns} />
        );
        
        // Test accessibility
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
        });

        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      });
    });
  });

  describe('Layout Components', () => {
    describe('Grid Component', () => {
      it('renders grid layout correctly', async () => {
        const { container } = render(
          <Grid cols={2} gap={4}>
            <div>Grid Item 1</div>
            <div>Grid Item 2</div>
          </Grid>
        );
        
        // Test accessibility
        await runA11yTestSuite(container);

        expect(screen.getByText('Grid Item 1')).toBeInTheDocument();
        expect(screen.getByText('Grid Item 2')).toBeInTheDocument();
      });
    });

    describe('Container Component', () => {
      it('renders container with max width correctly', async () => {
        const { container } = render(
          <Container maxWidth="lg">
            <div>Container Content</div>
          </Container>
        );
        
        // Test accessibility
        await runA11yTestSuite(container);

        expect(screen.getByText('Container Content')).toBeInTheDocument();
      });
    });

    describe('Stack Component', () => {
      it('renders vertical stack correctly', async () => {
        const { container } = render(
          <Stack direction="vertical" gap={4}>
            <div>Stack Item 1</div>
            <div>Stack Item 2</div>
          </Stack>
        );
        
        // Test accessibility
        await runA11yTestSuite(container);

        expect(screen.getByText('Stack Item 1')).toBeInTheDocument();
        expect(screen.getByText('Stack Item 2')).toBeInTheDocument();
      });
    });
  });

  describe('Polish Business Components', () => {
    describe('CurrencyInput Component', () => {
      it('renders PLN currency input correctly', async () => {
        const { container } = render(
          <CurrencyInput 
            currency="PLN" 
            aria-label="Amount in PLN"
          />
        );
        
        // Test accessibility with Polish business requirements
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
          testPolishBusiness: true,
        });

        const input = screen.getByRole('textbox');
        expect(input).toBeInTheDocument();
      });

      it('formats PLN currency correctly', async () => {
        const user = userEvent.setup();
        
        render(
          <CurrencyInput 
            currency="PLN" 
            aria-label="Amount in PLN"
          />
        );
        
        const input = screen.getByRole('textbox');
        await user.type(input, '1234.56');
        
        // Should format as Polish currency
        expect(input).toHaveValue('1 234,56 zł');
      });
    });

    describe('DatePicker Component', () => {
      it('renders Polish date picker correctly', async () => {
        const { container } = render(
          <DatePicker 
            format="DD.MM.YYYY"
            aria-label="Select date"
          />
        );
        
        // Test accessibility with Polish business requirements
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
          testPolishBusiness: true,
        });

        const input = screen.getByRole('textbox');
        expect(input).toBeInTheDocument();
      });
    });

    describe('VATRateSelector Component', () => {
      it('renders Polish VAT rates correctly', async () => {
        const { container } = render(
          <VATRateSelector aria-label="Select VAT rate" />
        );
        
        // Test accessibility with Polish business requirements
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
          testPolishBusiness: true,
        });

        const select = screen.getByRole('combobox');
        expect(select).toBeInTheDocument();
        
        // Should include standard Polish VAT rates
        expect(screen.getByText('23%')).toBeInTheDocument();
        expect(screen.getByText('8%')).toBeInTheDocument();
        expect(screen.getByText('5%')).toBeInTheDocument();
        expect(screen.getByText('0%')).toBeInTheDocument();
      });
    });

    describe('NIPValidator Component', () => {
      it('validates Polish NIP numbers correctly', async () => {
        const user = userEvent.setup();
        
        const { container } = render(
          <NIPValidator aria-label="Enter NIP number" />
        );
        
        // Test accessibility with Polish business requirements
        await runA11yTestSuite(container, {
          testKeyboard: true,
          testScreenReader: true,
          testFocus: true,
          testPolishBusiness: true,
        });

        const input = screen.getByRole('textbox');
        
        // Test valid NIP
        await user.type(input, '1234567890');
        expect(input).toHaveValue('123-456-78-90');
        
        // Test invalid NIP
        await user.clear(input);
        await user.type(input, '1234567891');
        expect(screen.getByText(/nieprawidłowy nip/i)).toBeInTheDocument();
      });
    });

    describe('InvoiceStatusBadge Component', () => {
      const statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled'] as const;

      statuses.forEach(status => {
        it(`renders ${status} status badge correctly`, async () => {
          const { container } = render(
            <InvoiceStatusBadge status={status} />
          );
          
          // Test accessibility
          await runA11yTestSuite(container);

          const badge = container.querySelector('[role="status"]');
          expect(badge).toBeInTheDocument();
        });
      });
    });
  });

  describe('Cross-Component Integration Tests', () => {
    it('renders complex form with all component types', async () => {
      const { container } = render(
        <Form onSubmit={() => {}}>
          <Card>
            <Card.Header>Invoice Form</Card.Header>
            <Card.Body>
              <Grid cols={2} gap={4}>
                <Input aria-label="Invoice number" placeholder="Invoice number" />
                <DatePicker aria-label="Invoice date" format="DD.MM.YYYY" />
                <CurrencyInput aria-label="Amount" currency="PLN" />
                <VATRateSelector aria-label="VAT rate" />
                <NIPValidator aria-label="Client NIP" />
                <InvoiceStatusBadge status="draft" />
              </Grid>
            </Card.Body>
            <Card.Footer>
              <Stack direction="horizontal" gap={2}>
                <Button variant="secondary">Cancel</Button>
                <Button variant="primary" type="submit">Save Invoice</Button>
              </Stack>
            </Card.Footer>
          </Card>
        </Form>
      );
      
      // Test comprehensive accessibility
      await runA11yTestSuite(container, {
        testKeyboard: true,
        testScreenReader: true,
        testFocus: true,
        testPolishBusiness: true,
      });

      // Verify all components are rendered
      expect(screen.getByText('Invoice Form')).toBeInTheDocument();
      expect(screen.getByLabelText('Invoice number')).toBeInTheDocument();
      expect(screen.getByLabelText('Invoice date')).toBeInTheDocument();
      expect(screen.getByLabelText('Amount')).toBeInTheDocument();
      expect(screen.getByLabelText('VAT rate')).toBeInTheDocument();
      expect(screen.getByLabelText('Client NIP')).toBeInTheDocument();
      expect(screen.getByText('Save Invoice')).toBeInTheDocument();
    });

    it('maintains focus management across components', async () => {
      const user = userEvent.setup();
      
      render(
        <div>
          <Button>First Button</Button>
          <Input aria-label="Text input" />
          <Select options={[{ value: '1', label: 'Option 1' }]} aria-label="Select" />
          <Checkbox aria-label="Checkbox">Checkbox</Checkbox>
          <Button>Last Button</Button>
        </div>
      );

      // Test tab navigation through all components
      const firstButton = screen.getByText('First Button');
      const input = screen.getByLabelText('Text input');
      const select = screen.getByLabelText('Select');
      const checkbox = screen.getByLabelText('Checkbox');
      const lastButton = screen.getByText('Last Button');

      firstButton.focus();
      expect(firstButton).toHaveFocus();

      await user.tab();
      expect(input).toHaveFocus();

      await user.tab();
      expect(select).toHaveFocus();

      await user.tab();
      expect(checkbox).toHaveFocus();

      await user.tab();
      expect(lastButton).toHaveFocus();
    });
  });
});