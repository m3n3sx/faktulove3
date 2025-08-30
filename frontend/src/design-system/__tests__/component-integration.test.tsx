/**
 * Component Integration Test Suite
 * Tests all migrated components, prop mapping, compatibility layers, and Polish business logic
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

// Import design system components
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Select } from '../components/primitives/Select/Select';
import { Checkbox } from '../components/primitives/Checkbox/Checkbox';
import { Radio } from '../components/primitives/Radio/Radio';
import { Switch } from '../components/primitives/Switch/Switch';
import { Textarea } from '../components/primitives/Textarea/Textarea';
import { Card } from '../components/patterns/Card/Card';
import { Form } from '../components/patterns/Form/Form';
import { Table } from '../components/patterns/Table/Table';
import { FileUpload } from '../components/patterns/FileUpload/FileUpload';
import { Grid } from '../components/layouts/Grid/Grid';
import { Container } from '../components/layouts/Container/Container';
import { Stack } from '../components/layouts/Stack/Stack';

// Import Polish business components
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../components/business/DatePicker/DatePicker';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';
import { ComplianceIndicator } from '../components/business/ComplianceIndicator/ComplianceIndicator';

// Import compatibility and migration utilities
import { ComponentWrapper } from '../compatibility/ComponentWrapper';
import { MigrationTester } from '../compatibility/MigrationTester';
import { MigrationValidator } from '../compatibility/MigrationValidator';

// Import providers and context
import { DesignSystemProvider } from '../providers/DesignSystemProvider';
import { ThemeProvider } from '../providers/ThemeProvider';

// Import test utilities
import { runA11yTestSuite } from '../utils/testUtils';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Test wrapper with providers
const TestWrapper: React.FC<{ children: React.ReactNode; theme?: string }> = ({ 
  children, 
  theme = 'light' 
}) => (
  <DesignSystemProvider>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </DesignSystemProvider>
);

describe('Design System Component Integration Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('Primitive Component Integration', () => {
    describe('Button Integration', () => {
      it('integrates with form submission correctly', async () => {
        const handleSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <form onSubmit={handleSubmit}>
              <Button type="submit" variant="primary">
                Submit Form
              </Button>
            </form>
          </TestWrapper>
        );

        const button = screen.getByRole('button', { name: /submit form/i });
        await user.click(button);

        expect(handleSubmit).toHaveBeenCalled();
      });

      it('maintains accessibility with loading state', async () => {
        const { container } = render(
          <TestWrapper>
            <Button loading variant="primary">
              Loading Button
            </Button>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-busy', 'true');
        expect(button).toBeDisabled();

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('works with keyboard navigation', async () => {
        const handleClick = jest.fn();
        
        render(
          <TestWrapper>
            <Button onClick={handleClick}>Keyboard Button</Button>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        button.focus();
        expect(button).toHaveFocus();

        await user.keyboard('{Enter}');
        expect(handleClick).toHaveBeenCalledTimes(1);

        await user.keyboard(' ');
        expect(handleClick).toHaveBeenCalledTimes(2);
      });
    });

    describe('Input Integration', () => {
      it('integrates with form validation', async () => {
        const handleSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <form onSubmit={handleSubmit}>
              <Input
                name="email"
                type="email"
                required
                aria-label="Email address"
                error="Please enter a valid email"
              />
              <Button type="submit">Submit</Button>
            </form>
          </TestWrapper>
        );

        const input = screen.getByLabelText(/email address/i);
        const submitButton = screen.getByRole('button', { name: /submit/i });

        // Test invalid input
        await user.type(input, 'invalid-email');
        await user.click(submitButton);

        expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
        expect(input).toHaveAttribute('aria-invalid', 'true');
      });

      it('handles controlled and uncontrolled states', async () => {
        const ControlledInput = () => {
          const [value, setValue] = React.useState('');
          return (
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              aria-label="Controlled input"
            />
          );
        };

        render(
          <TestWrapper>
            <ControlledInput />
            <Input defaultValue="uncontrolled" aria-label="Uncontrolled input" />
          </TestWrapper>
        );

        const controlledInput = screen.getByLabelText(/controlled input/i);
        const uncontrolledInput = screen.getByLabelText(/uncontrolled input/i);

        await user.type(controlledInput, 'controlled value');
        expect(controlledInput).toHaveValue('controlled value');

        await user.clear(uncontrolledInput);
        await user.type(uncontrolledInput, 'new uncontrolled value');
        expect(uncontrolledInput).toHaveValue('new uncontrolled value');
      });
    });

    describe('Select Integration', () => {
      const options = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' },
        { value: 'option3', label: 'Option 3' },
      ];

      it('integrates with form data collection', async () => {
        const handleSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              handleSubmit(Object.fromEntries(formData));
            }}>
              <Select
                name="selection"
                options={options}
                aria-label="Test selection"
              />
              <Button type="submit">Submit</Button>
            </form>
          </TestWrapper>
        );

        const select = screen.getByLabelText(/test selection/i);
        await user.selectOptions(select, 'option2');
        
        const submitButton = screen.getByRole('button', { name: /submit/i });
        await user.click(submitButton);

        expect(handleSubmit).toHaveBeenCalledWith({ selection: 'option2' });
      });
    });
  });

  describe('Pattern Component Integration', () => {
    describe('Form Integration', () => {
      it('handles complex form with validation', async () => {
        const handleSubmit = jest.fn();
        const handleValidation = jest.fn();
        
        render(
          <TestWrapper>
            <Form onSubmit={handleSubmit} onValidate={handleValidation}>
              <Input
                name="name"
                required
                aria-label="Full name"
                placeholder="Enter your full name"
              />
              <Input
                name="email"
                type="email"
                required
                aria-label="Email address"
                placeholder="Enter your email"
              />
              <Select
                name="country"
                options={[
                  { value: 'pl', label: 'Poland' },
                  { value: 'us', label: 'United States' },
                ]}
                required
                aria-label="Country"
              />
              <Checkbox name="terms" required>
                I agree to the terms and conditions
              </Checkbox>
              <Button type="submit" variant="primary">
                Submit Form
              </Button>
            </Form>
          </TestWrapper>
        );

        // Fill out form
        await user.type(screen.getByLabelText(/full name/i), 'John Doe');
        await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
        await user.selectOptions(screen.getByLabelText(/country/i), 'pl');
        await user.click(screen.getByRole('checkbox'));

        // Submit form
        await user.click(screen.getByRole('button', { name: /submit form/i }));

        expect(handleSubmit).toHaveBeenCalled();
      });
    });

    describe('Table Integration', () => {
      const tableData = [
        { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive' },
      ];

      const columns = [
        { key: 'name', header: 'Name', sortable: true },
        { key: 'email', header: 'Email' },
        { 
          key: 'status', 
          header: 'Status',
          render: (value: string) => (
            <InvoiceStatusBadge status={value as any} />
          )
        },
      ];

      it('integrates with sorting and filtering', async () => {
        const handleSort = jest.fn();
        
        render(
          <TestWrapper>
            <Table
              data={tableData}
              columns={columns}
              onSort={handleSort}
              sortable
            />
          </TestWrapper>
        );

        const nameHeader = screen.getByRole('columnheader', { name: /name/i });
        await user.click(nameHeader);

        expect(handleSort).toHaveBeenCalledWith('name', 'asc');
      });

      it('maintains accessibility with complex content', async () => {
        const { container } = render(
          <TestWrapper>
            <Table data={tableData} columns={columns} />
          </TestWrapper>
        );

        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();

        // Check that status badges are rendered
        expect(screen.getByText('active')).toBeInTheDocument();
        expect(screen.getByText('inactive')).toBeInTheDocument();

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });

    describe('FileUpload Integration', () => {
      it('handles file upload with validation', async () => {
        const handleUpload = jest.fn();
        
        render(
          <TestWrapper>
            <FileUpload
              onUpload={handleUpload}
              acceptedTypes={['image/jpeg', 'image/png', 'application/pdf']}
              maxSize={5 * 1024 * 1024} // 5MB
              multiple
            />
          </TestWrapper>
        );

        const fileInput = screen.getByLabelText(/choose files/i);
        
        // Create mock files
        const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
        const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });

        await user.upload(fileInput, [validFile, invalidFile]);

        expect(handleUpload).toHaveBeenCalledWith([validFile]);
        expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
      });
    });
  });

  describe('Layout Component Integration', () => {
    describe('Grid Integration', () => {
      it('handles responsive grid layouts', () => {
        render(
          <TestWrapper>
            <Grid cols={{ base: 1, md: 2, lg: 3 }} gap={4}>
              <Card>Card 1</Card>
              <Card>Card 2</Card>
              <Card>Card 3</Card>
            </Grid>
          </TestWrapper>
        );

        const grid = screen.getByRole('generic');
        expect(grid).toHaveClass('grid');
        
        // Check that cards are rendered
        expect(screen.getByText('Card 1')).toBeInTheDocument();
        expect(screen.getByText('Card 2')).toBeInTheDocument();
        expect(screen.getByText('Card 3')).toBeInTheDocument();
      });
    });

    describe('Stack Integration', () => {
      it('handles different stack directions and gaps', () => {
        render(
          <TestWrapper>
            <Stack direction="vertical" gap={4}>
              <Button>Button 1</Button>
              <Button>Button 2</Button>
            </Stack>
            <Stack direction="horizontal" gap={2}>
              <Button>Button 3</Button>
              <Button>Button 4</Button>
            </Stack>
          </TestWrapper>
        );

        expect(screen.getByText('Button 1')).toBeInTheDocument();
        expect(screen.getByText('Button 2')).toBeInTheDocument();
        expect(screen.getByText('Button 3')).toBeInTheDocument();
        expect(screen.getByText('Button 4')).toBeInTheDocument();
      });
    });
  });

  describe('Polish Business Component Integration', () => {
    describe('CurrencyInput Integration', () => {
      it('formats Polish currency correctly', async () => {
        const handleChange = jest.fn();
        
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              onChange={handleChange}
              aria-label="Amount in PLN"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/amount in pln/i);
        await user.type(input, '1234.56');

        expect(input).toHaveValue('1 234,56 zł');
        expect(handleChange).toHaveBeenCalledWith(1234.56);
      });

      it('validates currency input ranges', async () => {
        render(
          <TestWrapper>
            <CurrencyInput
              currency="PLN"
              min={0}
              max={10000}
              aria-label="Amount with validation"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/amount with validation/i);
        
        // Test invalid amount (too high)
        await user.type(input, '15000');
        expect(screen.getByText(/amount cannot exceed/i)).toBeInTheDocument();
      });
    });

    describe('DatePicker Integration', () => {
      it('handles Polish date formats', async () => {
        const handleChange = jest.fn();
        
        render(
          <TestWrapper>
            <DatePicker
              format="DD.MM.YYYY"
              onChange={handleChange}
              aria-label="Select date"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/select date/i);
        await user.type(input, '15.03.2024');

        expect(input).toHaveValue('15.03.2024');
        expect(handleChange).toHaveBeenCalledWith(new Date(2024, 2, 15));
      });
    });

    describe('VATRateSelector Integration', () => {
      it('provides Polish VAT rates', () => {
        render(
          <TestWrapper>
            <VATRateSelector aria-label="Select VAT rate" />
          </TestWrapper>
        );

        const select = screen.getByLabelText(/select vat rate/i);
        
        // Check Polish VAT rates are available
        expect(screen.getByText('23%')).toBeInTheDocument();
        expect(screen.getByText('8%')).toBeInTheDocument();
        expect(screen.getByText('5%')).toBeInTheDocument();
        expect(screen.getByText('0%')).toBeInTheDocument();
      });
    });

    describe('NIPValidator Integration', () => {
      it('validates Polish NIP numbers', async () => {
        const handleValidation = jest.fn();
        
        render(
          <TestWrapper>
            <NIPValidator
              onValidation={handleValidation}
              aria-label="Enter NIP number"
            />
          </TestWrapper>
        );

        const input = screen.getByLabelText(/enter nip number/i);
        
        // Test valid NIP
        await user.type(input, '1234567890');
        expect(input).toHaveValue('123-456-78-90');
        expect(handleValidation).toHaveBeenCalledWith(true, '1234567890');

        // Test invalid NIP
        await user.clear(input);
        await user.type(input, '1234567891');
        expect(screen.getByText(/nieprawidłowy nip/i)).toBeInTheDocument();
        expect(handleValidation).toHaveBeenCalledWith(false, '1234567891');
      });
    });

    describe('InvoiceStatusBadge Integration', () => {
      const statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled'] as const;

      statuses.forEach(status => {
        it(`renders ${status} status with correct styling`, () => {
          render(
            <TestWrapper>
              <InvoiceStatusBadge status={status} />
            </TestWrapper>
          );

          const badge = screen.getByRole('status');
          expect(badge).toHaveClass(`status-${status}`);
        });
      });
    });

    describe('ComplianceIndicator Integration', () => {
      it('shows compliance status correctly', () => {
        render(
          <TestWrapper>
            <ComplianceIndicator
              compliant={true}
              requirements={['VAT', 'NIP', 'Date format']}
            />
          </TestWrapper>
        );

        expect(screen.getByText(/compliant/i)).toBeInTheDocument();
        expect(screen.getByText('VAT')).toBeInTheDocument();
        expect(screen.getByText('NIP')).toBeInTheDocument();
        expect(screen.getByText('Date format')).toBeInTheDocument();
      });
    });
  });

  describe('Compatibility Layer Integration', () => {
    describe('ComponentWrapper', () => {
      it('wraps legacy components correctly', () => {
        const LegacyButton = ({ children, ...props }: any) => (
          <button className="legacy-button" {...props}>
            {children}
          </button>
        );

        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyButton}
              newComponent={Button}
              propMapping={{
                className: 'variant',
                onClick: 'onClick',
              }}
              className="primary"
              onClick={() => {}}
            >
              Wrapped Button
            </ComponentWrapper>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        expect(button).toHaveTextContent('Wrapped Button');
      });
    });

    describe('MigrationTester', () => {
      it('tests component migration compatibility', async () => {
        const migrationConfig = {
          component: 'Button',
          oldProps: { className: 'btn-primary', onClick: jest.fn() },
          newProps: { variant: 'primary', onClick: jest.fn() },
          propMapping: { className: 'variant' },
        };

        render(
          <TestWrapper>
            <MigrationTester config={migrationConfig} />
          </TestWrapper>
        );

        // Migration tester should render both old and new versions
        expect(screen.getByText(/migration test/i)).toBeInTheDocument();
      });
    });

    describe('MigrationValidator', () => {
      it('validates migration completeness', () => {
        const validationResults = MigrationValidator.validate({
          totalComponents: 50,
          migratedComponents: 45,
          testCoverage: 85,
          accessibilityScore: 90,
        });

        expect(validationResults.isComplete).toBe(false);
        expect(validationResults.completionPercentage).toBe(90);
        expect(validationResults.issues).toContain('Migration not complete');
      });
    });
  });

  describe('Theme Integration', () => {
    it('applies themes correctly across components', () => {
      render(
        <TestWrapper theme="dark">
          <Card>
            <Button variant="primary">Dark Theme Button</Button>
            <Input placeholder="Dark theme input" />
          </Card>
        </TestWrapper>
      );

      const card = screen.getByRole('generic');
      expect(card).toHaveAttribute('data-theme', 'dark');
    });

    it('handles theme switching', async () => {
      const ThemeTest = () => {
        const [theme, setTheme] = React.useState('light');
        
        return (
          <TestWrapper theme={theme}>
            <Button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
              Switch to {theme === 'light' ? 'dark' : 'light'} theme
            </Button>
          </TestWrapper>
        );
      };

      render(<ThemeTest />);

      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Switch to dark theme');

      await user.click(button);
      expect(button).toHaveTextContent('Switch to light theme');
    });
  });

  describe('Cross-Component Integration', () => {
    it('handles complex invoice form integration', async () => {
      const handleSubmit = jest.fn();
      
      render(
        <TestWrapper>
          <Form onSubmit={handleSubmit}>
            <Card>
              <Card.Header>
                <h2>Create Invoice</h2>
              </Card.Header>
              <Card.Body>
                <Grid cols={2} gap={4}>
                  <Input
                    name="invoiceNumber"
                    label="Invoice Number"
                    required
                    placeholder="INV-001"
                  />
                  <DatePicker
                    name="issueDate"
                    label="Issue Date"
                    format="DD.MM.YYYY"
                    required
                  />
                  <NIPValidator
                    name="clientNIP"
                    label="Client NIP"
                    required
                  />
                  <CurrencyInput
                    name="amount"
                    label="Amount"
                    currency="PLN"
                    required
                  />
                  <VATRateSelector
                    name="vatRate"
                    label="VAT Rate"
                    required
                  />
                  <InvoiceStatusBadge status="draft" />
                </Grid>
              </Card.Body>
              <Card.Footer>
                <Stack direction="horizontal" gap={2} justify="end">
                  <Button variant="secondary" type="button">
                    Cancel
                  </Button>
                  <Button variant="primary" type="submit">
                    Create Invoice
                  </Button>
                </Stack>
              </Card.Footer>
            </Card>
          </Form>
        </TestWrapper>
      );

      // Fill out the form
      await user.type(screen.getByLabelText(/invoice number/i), 'INV-001');
      await user.type(screen.getByLabelText(/issue date/i), '15.03.2024');
      await user.type(screen.getByLabelText(/client nip/i), '1234567890');
      await user.type(screen.getByLabelText(/amount/i), '1000');
      await user.selectOptions(screen.getByLabelText(/vat rate/i), '23');

      // Submit the form
      await user.click(screen.getByRole('button', { name: /create invoice/i }));

      expect(handleSubmit).toHaveBeenCalled();
    });

    it('maintains accessibility across complex layouts', async () => {
      const { container } = render(
        <TestWrapper>
          <Container maxWidth="lg">
            <Grid cols={3} gap={6}>
              <Card>
                <Card.Header>Statistics</Card.Header>
                <Card.Body>
                  <Table
                    data={[
                      { metric: 'Total Invoices', value: '150' },
                      { metric: 'Paid Invoices', value: '120' },
                    ]}
                    columns={[
                      { key: 'metric', header: 'Metric' },
                      { key: 'value', header: 'Value' },
                    ]}
                  />
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Header>Quick Actions</Card.Header>
                <Card.Body>
                  <Stack gap={3}>
                    <Button variant="primary" fullWidth>
                      Create Invoice
                    </Button>
                    <Button variant="secondary" fullWidth>
                      Upload Document
                    </Button>
                  </Stack>
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Header>Recent Activity</Card.Header>
                <Card.Body>
                  <Stack gap={2}>
                    <div>Invoice INV-001 created</div>
                    <div>Document uploaded</div>
                  </Stack>
                </Card.Body>
              </Card>
            </Grid>
          </Container>
        </TestWrapper>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});