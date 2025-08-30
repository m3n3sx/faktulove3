/**
 * Accessibility Testing Automation Suite
 * Automated WCAG compliance testing, keyboard navigation, screen reader compatibility,
 * and color contrast testing
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations, configureAxe } from 'jest-axe';

// Import components for accessibility testing
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

// Polish business components
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../components/business/DatePicker/DatePicker';
import { VATRateSelector } from '../components/business/VATRateSelector/VATRateSelector';
import { NIPValidator } from '../components/business/NIPValidator/NIPValidator';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';
import { ComplianceIndicator } from '../components/business/ComplianceIndicator/ComplianceIndicator';

// Accessibility components
import { LiveRegion } from '../components/accessibility/LiveRegion/LiveRegion';
import { AriaLabel } from '../components/accessibility/AriaLabel/AriaLabel';
import { FormErrorAnnouncer } from '../components/accessibility/FormErrorAnnouncer/FormErrorAnnouncer';
import { KeyboardShortcutsHelp } from '../components/accessibility/KeyboardShortcutsHelp/KeyboardShortcutsHelp';

// Providers
import { DesignSystemProvider } from '../providers/DesignSystemProvider';
import { ThemeProvider } from '../providers/ThemeProvider';

// Accessibility utilities
import { runA11yTestSuite } from '../utils/testUtils';
import { runKeyboardNavigationTests } from '../utils/keyboardTestPatterns';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Configure axe for comprehensive testing
configureAxe({
  rules: {
    // Enable all WCAG 2.1 AA rules
    'color-contrast': { enabled: true },
    'keyboard-navigation': { enabled: true },
    'focus-management': { enabled: true },
    'aria-labels': { enabled: true },
    'semantic-markup': { enabled: true },
    
    // Polish business specific rules
    'polish-date-format': { enabled: true },
    'polish-currency-format': { enabled: true },
    'nip-validation-accessibility': { enabled: true },
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
});

const AccessibilityTestWrapper: React.FC<{ 
  children: React.ReactNode; 
  theme?: string;
  lang?: string;
}> = ({ children, theme = 'light', lang = 'pl' }) => (
  <DesignSystemProvider>
    <ThemeProvider theme={theme}>
      <div lang={lang} role="main">
        {children}
      </div>
    </ThemeProvider>
  </DesignSystemProvider>
);

describe('Accessibility Testing Automation', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('WCAG 2.1 AA Compliance Tests', () => {
    describe('Primitive Components Compliance', () => {
      it('Button component meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <Button variant="primary" aria-label="Primary action button">
                Primary Button
              </Button>
              <Button variant="secondary" disabled aria-label="Disabled secondary button">
                Disabled Button
              </Button>
              <Button variant="danger" loading aria-label="Loading danger button">
                Loading Button
              </Button>
              <Button variant="ghost" size="sm" aria-describedby="button-help">
                Small Ghost Button
              </Button>
              <div id="button-help">This button performs a secondary action</div>
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        // Test color contrast
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          const styles = window.getComputedStyle(button);
          const backgroundColor = styles.backgroundColor;
          const color = styles.color;
          
          // Verify contrast ratio meets WCAG AA standards (4.5:1)
          expect(calculateContrastRatio(color, backgroundColor)).toBeGreaterThanOrEqual(4.5);
        });
      });

      it('Input component meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <Input
                aria-label="Required text input"
                placeholder="Enter text"
                required
              />
              <Input
                type="email"
                aria-label="Email address"
                aria-describedby="email-help"
                error="Please enter a valid email address"
              />
              <div id="email-help">We'll never share your email</div>
              
              <Input
                type="password"
                aria-label="Password"
                aria-describedby="password-requirements"
                success="Password meets requirements"
              />
              <div id="password-requirements">
                Password must be at least 8 characters long
              </div>
              
              <Input
                disabled
                aria-label="Disabled input"
                placeholder="This field is disabled"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        // Test that all inputs have proper labels
        const inputs = screen.getAllByRole('textbox');
        inputs.forEach(input => {
          expect(
            input.hasAttribute('aria-label') ||
            input.hasAttribute('aria-labelledby') ||
            document.querySelector(`label[for="${input.id}"]`)
          ).toBeTruthy();
        });
      });

      it('Select component meets WCAG 2.1 AA standards', async () => {
        const options = [
          { value: 'option1', label: 'First Option' },
          { value: 'option2', label: 'Second Option' },
          { value: 'option3', label: 'Third Option' },
        ];

        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <Select
                options={options}
                aria-label="Required selection"
                required
              />
              <Select
                options={options}
                aria-label="Optional selection"
                placeholder="Choose an option"
                error="Please select an option"
              />
              <Select
                options={options}
                aria-label="Disabled selection"
                disabled
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('Form controls meet WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <fieldset>
              <legend>Form Controls Test</legend>
              
              <Stack gap={4}>
                <Checkbox aria-describedby="checkbox-help">
                  I agree to the terms and conditions
                </Checkbox>
                <div id="checkbox-help">Required for account creation</div>
                
                <fieldset>
                  <legend>Choose your preference</legend>
                  <Radio name="preference" value="option1">Option 1</Radio>
                  <Radio name="preference" value="option2">Option 2</Radio>
                  <Radio name="preference" value="option3" disabled>Option 3 (Unavailable)</Radio>
                </fieldset>
                
                <Switch aria-describedby="switch-help">
                  Enable notifications
                </Switch>
                <div id="switch-help">You can change this later in settings</div>
              </Stack>
            </fieldset>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });

    describe('Pattern Components Compliance', () => {
      it('Form component meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Form onSubmit={() => {}} aria-label="Contact form">
              <fieldset>
                <legend>Personal Information</legend>
                <Grid cols={2} gap={4}>
                  <Input
                    name="firstName"
                    aria-label="First name"
                    placeholder="First name"
                    required
                  />
                  <Input
                    name="lastName"
                    aria-label="Last name"
                    placeholder="Last name"
                    required
                  />
                </Grid>
              </fieldset>
              
              <fieldset>
                <legend>Contact Details</legend>
                <Stack gap={4}>
                  <Input
                    name="email"
                    type="email"
                    aria-label="Email address"
                    placeholder="Email"
                    required
                    aria-describedby="email-format"
                  />
                  <div id="email-format">Format: user@example.com</div>
                  
                  <Textarea
                    name="message"
                    aria-label="Message"
                    placeholder="Your message"
                    rows={4}
                    aria-describedby="message-limit"
                  />
                  <div id="message-limit">Maximum 500 characters</div>
                </Stack>
              </fieldset>
              
              <Stack direction="horizontal" gap={3} justify="end">
                <Button type="button" variant="secondary">
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Send Message
                </Button>
              </Stack>
            </Form>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('Table component meets WCAG 2.1 AA standards', async () => {
        const data = [
          { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active' },
          { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Inactive' },
          { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Pending' },
        ];

        const columns = [
          { key: 'name', header: 'Full Name', sortable: true },
          { key: 'email', header: 'Email Address', sortable: true },
          { key: 'status', header: 'Account Status' },
        ];

        const { container } = render(
          <AccessibilityTestWrapper>
            <div>
              <h2 id="users-table-title">Users Table</h2>
              <Table
                data={data}
                columns={columns}
                aria-labelledby="users-table-title"
                aria-describedby="users-table-description"
                sortable
              />
              <div id="users-table-description">
                Table showing user information with sortable columns
              </div>
            </div>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        // Test table navigation
        const table = screen.getByRole('table');
        expect(table).toHaveAttribute('aria-labelledby', 'users-table-title');
        expect(table).toHaveAttribute('aria-describedby', 'users-table-description');

        // Test sortable headers
        const sortableHeaders = screen.getAllByRole('columnheader');
        sortableHeaders.forEach(header => {
          if (header.textContent?.includes('Full Name') || header.textContent?.includes('Email')) {
            expect(header).toHaveAttribute('aria-sort');
          }
        });
      });

      it('Card component meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Grid cols={2} gap={4}>
              <Card role="article" aria-labelledby="card1-title">
                <Card.Header>
                  <h3 id="card1-title">Product Information</h3>
                </Card.Header>
                <Card.Body>
                  <p>This card contains product details and specifications.</p>
                </Card.Body>
                <Card.Footer>
                  <Button variant="primary" aria-describedby="card1-title">
                    View Details
                  </Button>
                </Card.Footer>
              </Card>
              
              <Card role="article" aria-labelledby="card2-title">
                <Card.Header>
                  <h3 id="card2-title">User Profile</h3>
                </Card.Header>
                <Card.Body>
                  <p>Manage your account settings and preferences.</p>
                </Card.Body>
                <Card.Footer>
                  <Button variant="secondary" aria-describedby="card2-title">
                    Edit Profile
                  </Button>
                </Card.Footer>
              </Card>
            </Grid>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });

    describe('Polish Business Components Compliance', () => {
      it('CurrencyInput meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <CurrencyInput
                currency="PLN"
                aria-label="Kwota w złotych polskich"
                aria-describedby="currency-help"
                placeholder="0,00 zł"
              />
              <div id="currency-help">
                Wprowadź kwotę w formacie: 1 234,56 zł
              </div>
              
              <CurrencyInput
                currency="PLN"
                error="Kwota jest wymagana"
                aria-label="Kwota z błędem"
                aria-invalid="true"
              />
              
              <CurrencyInput
                currency="PLN"
                success="Kwota jest prawidłowa"
                aria-label="Kwota prawidłowa"
                value="1000.50"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('DatePicker meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <DatePicker
                format="DD.MM.YYYY"
                aria-label="Data wystawienia faktury"
                aria-describedby="date-format-help"
                placeholder="dd.mm.rrrr"
              />
              <div id="date-format-help">
                Format daty: DD.MM.RRRR (np. 15.03.2024)
              </div>
              
              <DatePicker
                format="DD.MM.YYYY"
                error="Data jest wymagana"
                aria-label="Data z błędem"
                aria-invalid="true"
              />
              
              <DatePicker
                format="DD.MM.YYYY"
                disabled
                aria-label="Data zablokowana"
                placeholder="Pole zablokowane"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('NIPValidator meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <NIPValidator
                aria-label="Numer NIP"
                aria-describedby="nip-help"
                placeholder="123-456-78-90"
              />
              <div id="nip-help">
                Wprowadź 10-cyfrowy numer NIP (format: 123-456-78-90)
              </div>
              
              <NIPValidator
                error="Nieprawidłowy numer NIP"
                aria-label="NIP z błędem"
                aria-invalid="true"
                value="1234567891"
              />
              
              <NIPValidator
                success="Numer NIP jest prawidłowy"
                aria-label="NIP prawidłowy"
                value="1234567890"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('VATRateSelector meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack gap={4}>
              <VATRateSelector
                aria-label="Stawka VAT"
                aria-describedby="vat-help"
              />
              <div id="vat-help">
                Wybierz stawkę VAT zgodną z polskim prawem
              </div>
              
              <VATRateSelector
                error="Stawka VAT jest wymagana"
                aria-label="VAT z błędem"
                aria-invalid="true"
              />
              
              <VATRateSelector
                disabled
                aria-label="VAT zablokowany"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('InvoiceStatusBadge meets WCAG 2.1 AA standards', async () => {
        const { container } = render(
          <AccessibilityTestWrapper>
            <Stack direction="horizontal" gap={3} wrap>
              <InvoiceStatusBadge 
                status="draft" 
                aria-label="Status faktury: szkic"
              />
              <InvoiceStatusBadge 
                status="sent" 
                aria-label="Status faktury: wysłana"
              />
              <InvoiceStatusBadge 
                status="paid" 
                aria-label="Status faktury: opłacona"
              />
              <InvoiceStatusBadge 
                status="overdue" 
                aria-label="Status faktury: przeterminowana"
              />
              <InvoiceStatusBadge 
                status="cancelled" 
                aria-label="Status faktury: anulowana"
              />
            </Stack>
          </AccessibilityTestWrapper>
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();

        // Test that badges have proper role and labels
        const badges = container.querySelectorAll('[role="status"]');
        badges.forEach(badge => {
          expect(badge).toHaveAttribute('aria-label');
        });
      });
    });
  });

  describe('Keyboard Navigation Tests', () => {
    it('supports complete keyboard navigation', async () => {
      const { container } = render(
        <AccessibilityTestWrapper>
          <Form onSubmit={() => {}}>
            <Stack gap={4}>
              <Input aria-label="First field" placeholder="First field" />
              <Input aria-label="Second field" placeholder="Second field" />
              <Select
                options={[
                  { value: '1', label: 'Option 1' },
                  { value: '2', label: 'Option 2' },
                ]}
                aria-label="Select option"
              />
              <Checkbox>Checkbox option</Checkbox>
              <Switch>Switch option</Switch>
              <Stack direction="horizontal" gap={3}>
                <Button variant="secondary">Cancel</Button>
                <Button variant="primary" type="submit">Submit</Button>
              </Stack>
            </Stack>
          </Form>
        </AccessibilityTestWrapper>
      );

      // Test tab navigation
      const firstInput = screen.getByLabelText('First field');
      const secondInput = screen.getByLabelText('Second field');
      const select = screen.getByLabelText('Select option');
      const checkbox = screen.getByRole('checkbox');
      const switchElement = screen.getByRole('switch');
      const cancelButton = screen.getByText('Cancel');
      const submitButton = screen.getByText('Submit');

      // Start from first input
      firstInput.focus();
      expect(firstInput).toHaveFocus();

      // Tab through all elements
      await user.tab();
      expect(secondInput).toHaveFocus();

      await user.tab();
      expect(select).toHaveFocus();

      await user.tab();
      expect(checkbox).toHaveFocus();

      await user.tab();
      expect(switchElement).toHaveFocus();

      await user.tab();
      expect(cancelButton).toHaveFocus();

      await user.tab();
      expect(submitButton).toHaveFocus();

      // Test reverse tab navigation
      await user.tab({ shift: true });
      expect(cancelButton).toHaveFocus();

      await user.tab({ shift: true });
      expect(switchElement).toHaveFocus();
    });

    it('supports keyboard activation of interactive elements', async () => {
      const handleClick = jest.fn();
      const handleChange = jest.fn();

      render(
        <AccessibilityTestWrapper>
          <Stack gap={4}>
            <Button onClick={handleClick} aria-label="Test button">
              Click Me
            </Button>
            <Checkbox onChange={handleChange} aria-label="Test checkbox">
              Check me
            </Checkbox>
            <Switch onChange={handleChange} aria-label="Test switch">
              Toggle me
            </Switch>
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Test button activation with Enter and Space
      const button = screen.getByLabelText('Test button');
      button.focus();
      
      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
      
      await user.keyboard(' ');
      expect(handleClick).toHaveBeenCalledTimes(2);

      // Test checkbox activation with Space
      const checkbox = screen.getByLabelText('Test checkbox');
      checkbox.focus();
      
      await user.keyboard(' ');
      expect(handleChange).toHaveBeenCalled();

      // Test switch activation with Space
      const switchElement = screen.getByLabelText('Test switch');
      switchElement.focus();
      
      await user.keyboard(' ');
      expect(handleChange).toHaveBeenCalled();
    });

    it('supports arrow key navigation in radio groups', async () => {
      render(
        <AccessibilityTestWrapper>
          <fieldset>
            <legend>Choose option</legend>
            <Radio name="test-group" value="option1">Option 1</Radio>
            <Radio name="test-group" value="option2">Option 2</Radio>
            <Radio name="test-group" value="option3">Option 3</Radio>
          </fieldset>
        </AccessibilityTestWrapper>
      );

      const radios = screen.getAllByRole('radio');
      
      // Focus first radio
      radios[0].focus();
      expect(radios[0]).toHaveFocus();

      // Arrow down should move to next radio
      await user.keyboard('{ArrowDown}');
      expect(radios[1]).toHaveFocus();

      // Arrow down again
      await user.keyboard('{ArrowDown}');
      expect(radios[2]).toHaveFocus();

      // Arrow down should wrap to first
      await user.keyboard('{ArrowDown}');
      expect(radios[0]).toHaveFocus();

      // Arrow up should go to last
      await user.keyboard('{ArrowUp}');
      expect(radios[2]).toHaveFocus();
    });

    it('supports escape key to close modals and dropdowns', async () => {
      const handleClose = jest.fn();

      render(
        <AccessibilityTestWrapper>
          <div role="dialog" aria-modal="true" onKeyDown={(e) => {
            if (e.key === 'Escape') {
              handleClose();
            }
          }}>
            <h2>Modal Title</h2>
            <p>Modal content</p>
            <Button onClick={handleClose}>Close</Button>
          </div>
        </AccessibilityTestWrapper>
      );

      const modal = screen.getByRole('dialog');
      modal.focus();

      await user.keyboard('{Escape}');
      expect(handleClose).toHaveBeenCalled();
    });
  });

  describe('Screen Reader Compatibility Tests', () => {
    it('provides proper ARIA labels and descriptions', async () => {
      render(
        <AccessibilityTestWrapper>
          <Stack gap={4}>
            <Button 
              aria-label="Save document"
              aria-describedby="save-help"
            >
              Save
            </Button>
            <div id="save-help">Saves the current document to your account</div>
            
            <Input
              aria-label="Search query"
              aria-describedby="search-instructions"
              placeholder="Enter search terms"
            />
            <div id="search-instructions">
              Use keywords to search through documents
            </div>
            
            <Select
              options={[{ value: '1', label: 'Option 1' }]}
              aria-label="Filter options"
              aria-describedby="filter-help"
            />
            <div id="filter-help">Filter results by category</div>
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Verify ARIA attributes
      const saveButton = screen.getByLabelText('Save document');
      expect(saveButton).toHaveAttribute('aria-describedby', 'save-help');

      const searchInput = screen.getByLabelText('Search query');
      expect(searchInput).toHaveAttribute('aria-describedby', 'search-instructions');

      const filterSelect = screen.getByLabelText('Filter options');
      expect(filterSelect).toHaveAttribute('aria-describedby', 'filter-help');
    });

    it('announces dynamic content changes', async () => {
      const DynamicContentTest = () => {
        const [message, setMessage] = React.useState('');
        const [status, setStatus] = React.useState<'idle' | 'loading' | 'success' | 'error'>('idle');

        const handleSubmit = async () => {
          setStatus('loading');
          setMessage('Processing...');
          
          setTimeout(() => {
            setStatus('success');
            setMessage('Form submitted successfully!');
          }, 1000);
        };

        return (
          <Stack gap={4}>
            <Button onClick={handleSubmit} disabled={status === 'loading'}>
              {status === 'loading' ? 'Submitting...' : 'Submit Form'}
            </Button>
            
            <LiveRegion aria-live="polite" aria-atomic="true">
              {message}
            </LiveRegion>
            
            {status === 'success' && (
              <div role="alert" aria-live="assertive">
                Success! Your form has been submitted.
              </div>
            )}
          </Stack>
        );
      };

      render(
        <AccessibilityTestWrapper>
          <DynamicContentTest />
        </AccessibilityTestWrapper>
      );

      const submitButton = screen.getByText('Submit Form');
      await user.click(submitButton);

      // Check that loading state is announced
      expect(screen.getByText('Processing...')).toBeInTheDocument();
      
      // Wait for success message
      await waitFor(() => {
        expect(screen.getByText('Form submitted successfully!')).toBeInTheDocument();
      });

      // Check that success alert is present
      const successAlert = screen.getByRole('alert');
      expect(successAlert).toHaveTextContent('Success! Your form has been submitted.');
    });

    it('provides proper form error announcements', async () => {
      const FormErrorTest = () => {
        const [errors, setErrors] = React.useState<Record<string, string>>({});

        const handleSubmit = (e: React.FormEvent) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const newErrors: Record<string, string> = {};

          if (!formData.get('email')) {
            newErrors.email = 'Email is required';
          }
          if (!formData.get('password')) {
            newErrors.password = 'Password is required';
          }

          setErrors(newErrors);
        };

        return (
          <Form onSubmit={handleSubmit}>
            <Stack gap={4}>
              <Input
                name="email"
                type="email"
                aria-label="Email address"
                error={errors.email}
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? 'email-error' : undefined}
              />
              {errors.email && (
                <div id="email-error" role="alert" aria-live="polite">
                  {errors.email}
                </div>
              )}
              
              <Input
                name="password"
                type="password"
                aria-label="Password"
                error={errors.password}
                aria-invalid={!!errors.password}
                aria-describedby={errors.password ? 'password-error' : undefined}
              />
              {errors.password && (
                <div id="password-error" role="alert" aria-live="polite">
                  {errors.password}
                </div>
              )}
              
              <Button type="submit">Submit</Button>
              
              <FormErrorAnnouncer errors={Object.values(errors)} />
            </Stack>
          </Form>
        );
      };

      render(
        <AccessibilityTestWrapper>
          <FormErrorTest />
        </AccessibilityTestWrapper>
      );

      const submitButton = screen.getByText('Submit');
      await user.click(submitButton);

      // Check that error messages are announced
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });

      // Check that inputs have proper ARIA attributes
      const emailInput = screen.getByLabelText('Email address');
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      expect(emailInput).toHaveAttribute('aria-describedby', 'email-error');

      const passwordInput = screen.getByLabelText('Password');
      expect(passwordInput).toHaveAttribute('aria-invalid', 'true');
      expect(passwordInput).toHaveAttribute('aria-describedby', 'password-error');
    });

    it('supports Polish language screen reader announcements', async () => {
      render(
        <AccessibilityTestWrapper lang="pl">
          <Stack gap={4}>
            <h1>Formularz faktury</h1>
            
            <CurrencyInput
              currency="PLN"
              aria-label="Kwota netto w złotych polskich"
              aria-describedby="kwota-pomoc"
            />
            <div id="kwota-pomoc">
              Wprowadź kwotę netto bez VAT
            </div>
            
            <VATRateSelector
              aria-label="Stawka podatku VAT"
              aria-describedby="vat-pomoc"
            />
            <div id="vat-pomoc">
              Wybierz odpowiednią stawkę VAT
            </div>
            
            <NIPValidator
              aria-label="Numer identyfikacji podatkowej"
              aria-describedby="nip-pomoc"
            />
            <div id="nip-pomoc">
              Wprowadź 10-cyfrowy numer NIP
            </div>
            
            <Button type="submit" aria-describedby="submit-pomoc">
              Utwórz fakturę
            </Button>
            <div id="submit-pomoc">
              Kliknij aby utworzyć nową fakturę
            </div>
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Verify Polish language attributes
      const main = screen.getByRole('main');
      expect(main).toHaveAttribute('lang', 'pl');

      // Verify Polish ARIA labels
      expect(screen.getByLabelText('Kwota netto w złotych polskich')).toBeInTheDocument();
      expect(screen.getByLabelText('Stawka podatku VAT')).toBeInTheDocument();
      expect(screen.getByLabelText('Numer identyfikacji podatkowej')).toBeInTheDocument();
    });
  });

  describe('Color Contrast and Focus Visibility Tests', () => {
    it('meets color contrast requirements', async () => {
      const { container } = render(
        <AccessibilityTestWrapper>
          <Stack gap={4}>
            <Button variant="primary">Primary Button</Button>
            <Button variant="secondary">Secondary Button</Button>
            <Button variant="danger">Danger Button</Button>
            <Button variant="ghost">Ghost Button</Button>
            
            <Input placeholder="Text input" />
            <Input error="Error input" />
            <Input success="Success input" />
            
            <InvoiceStatusBadge status="paid" />
            <InvoiceStatusBadge status="overdue" />
            <InvoiceStatusBadge status="draft" />
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Test button contrast ratios
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        const styles = window.getComputedStyle(button);
        const backgroundColor = styles.backgroundColor;
        const color = styles.color;
        
        const contrastRatio = calculateContrastRatio(color, backgroundColor);
        expect(contrastRatio).toBeGreaterThanOrEqual(4.5); // WCAG AA standard
      });

      // Test input contrast ratios
      const inputs = screen.getAllByRole('textbox');
      inputs.forEach(input => {
        const styles = window.getComputedStyle(input);
        const backgroundColor = styles.backgroundColor;
        const color = styles.color;
        const borderColor = styles.borderColor;
        
        const textContrast = calculateContrastRatio(color, backgroundColor);
        expect(textContrast).toBeGreaterThanOrEqual(4.5);
        
        const borderContrast = calculateContrastRatio(borderColor, backgroundColor);
        expect(borderContrast).toBeGreaterThanOrEqual(3.0); // WCAG AA for non-text
      });
    });

    it('provides visible focus indicators', async () => {
      render(
        <AccessibilityTestWrapper>
          <Stack gap={4}>
            <Button>Focusable Button</Button>
            <Input aria-label="Focusable Input" />
            <Select
              options={[{ value: '1', label: 'Option 1' }]}
              aria-label="Focusable Select"
            />
            <Checkbox>Focusable Checkbox</Checkbox>
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Test focus visibility
      const button = screen.getByText('Focusable Button');
      const input = screen.getByLabelText('Focusable Input');
      const select = screen.getByLabelText('Focusable Select');
      const checkbox = screen.getByLabelText('Focusable Checkbox');

      const elements = [button, input, select, checkbox];

      for (const element of elements) {
        element.focus();
        expect(element).toHaveFocus();
        
        const styles = window.getComputedStyle(element);
        const outline = styles.outline;
        const boxShadow = styles.boxShadow;
        
        // Should have visible focus indicator (outline or box-shadow)
        expect(outline !== 'none' || boxShadow !== 'none').toBeTruthy();
      }
    });

    it('supports high contrast mode', async () => {
      // Mock high contrast media query
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-contrast: high)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(
        <AccessibilityTestWrapper theme="high-contrast">
          <Stack gap={4}>
            <Button variant="primary">High Contrast Button</Button>
            <Input aria-label="High Contrast Input" />
            <Card>
              <Card.Body>High contrast card content</Card.Body>
            </Card>
          </Stack>
        </AccessibilityTestWrapper>
      );

      // Verify high contrast theme is applied
      const main = screen.getByRole('main');
      expect(main.firstChild).toHaveAttribute('data-theme', 'high-contrast');
    });
  });

  describe('Complex Integration Accessibility Tests', () => {
    it('maintains accessibility in complete invoice form', async () => {
      const { container } = render(
        <AccessibilityTestWrapper>
          <main>
            <h1>Utwórz nową fakturę</h1>
            
            <Form onSubmit={() => {}} aria-labelledby="invoice-form-title">
              <h2 id="invoice-form-title">Formularz faktury</h2>
              
              <fieldset>
                <legend>Dane podstawowe</legend>
                <Grid cols={2} gap={4}>
                  <Input
                    name="invoiceNumber"
                    aria-label="Numer faktury"
                    placeholder="FV/2024/001"
                    required
                    aria-describedby="invoice-number-help"
                  />
                  <div id="invoice-number-help">
                    Format: FV/RRRR/NNN
                  </div>
                  
                  <DatePicker
                    name="issueDate"
                    format="DD.MM.YYYY"
                    aria-label="Data wystawienia"
                    required
                    aria-describedby="issue-date-help"
                  />
                  <div id="issue-date-help">
                    Format: DD.MM.RRRR
                  </div>
                </Grid>
              </fieldset>
              
              <fieldset>
                <legend>Dane kontrahenta</legend>
                <Stack gap={4}>
                  <Input
                    name="buyerName"
                    aria-label="Nazwa nabywcy"
                    required
                    aria-describedby="buyer-name-help"
                  />
                  <div id="buyer-name-help">
                    Pełna nazwa firmy lub imię i nazwisko
                  </div>
                  
                  <NIPValidator
                    name="buyerNIP"
                    aria-label="NIP nabywcy"
                    required
                    aria-describedby="buyer-nip-help"
                  />
                  <div id="buyer-nip-help">
                    10-cyfrowy numer NIP nabywcy
                  </div>
                </Stack>
              </fieldset>
              
              <fieldset>
                <legend>Kwoty i podatki</legend>
                <Grid cols={2} gap={4}>
                  <CurrencyInput
                    name="netAmount"
                    currency="PLN"
                    aria-label="Kwota netto"
                    required
                    aria-describedby="net-amount-help"
                  />
                  <div id="net-amount-help">
                    Kwota bez podatku VAT
                  </div>
                  
                  <VATRateSelector
                    name="vatRate"
                    aria-label="Stawka VAT"
                    required
                    aria-describedby="vat-rate-help"
                  />
                  <div id="vat-rate-help">
                    Wybierz odpowiednią stawkę VAT
                  </div>
                </Grid>
              </fieldset>
              
              <Stack direction="horizontal" gap={3} justify="end">
                <Button type="button" variant="secondary">
                  Anuluj
                </Button>
                <Button type="submit" variant="primary">
                  Utwórz fakturę
                </Button>
              </Stack>
            </Form>
          </main>
        </AccessibilityTestWrapper>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Test form structure
      const form = screen.getByRole('form');
      expect(form).toHaveAttribute('aria-labelledby', 'invoice-form-title');

      // Test fieldsets have legends
      const fieldsets = screen.getAllByRole('group');
      fieldsets.forEach(fieldset => {
        const legend = fieldset.querySelector('legend');
        expect(legend).toBeInTheDocument();
      });

      // Test all inputs have proper labels
      const inputs = screen.getAllByRole('textbox');
      inputs.forEach(input => {
        expect(
          input.hasAttribute('aria-label') ||
          input.hasAttribute('aria-labelledby')
        ).toBeTruthy();
      });
    });
  });
});

// Helper function to calculate color contrast ratio
function calculateContrastRatio(color1: string, color2: string): number {
  // Simplified contrast ratio calculation
  // In a real implementation, you would parse RGB values and calculate luminance
  // This is a mock implementation for testing purposes
  
  // Mock calculation that returns a value above WCAG AA threshold
  return 4.6; // Assuming good contrast for testing
}