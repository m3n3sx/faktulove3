/**
 * Visual Regression Testing Setup
 * Configures screenshot testing for all major UI components and theme switching
 */

import React from 'react';
import { render } from '@testing-library/react';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

// Import components for visual testing
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

// Providers
import { DesignSystemProvider } from '../providers/DesignSystemProvider';
import { ThemeProvider } from '../providers/ThemeProvider';

// Extend Jest matchers
expect.extend({ toMatchImageSnapshot });

// Visual testing configuration
const visualTestConfig = {
  threshold: 0.2, // 20% difference threshold
  customDiffConfig: {
    threshold: 0.2,
  },
  failureThreshold: 0.05, // 5% failure threshold
  failureThresholdType: 'percent',
};

// Test wrapper with theme support
const VisualTestWrapper: React.FC<{ 
  children: React.ReactNode; 
  theme?: string;
  viewport?: { width: number; height: number };
}> = ({ children, theme = 'light', viewport }) => {
  React.useEffect(() => {
    if (viewport) {
      // Set viewport size for responsive testing
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: viewport.width,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: viewport.height,
      });
      window.dispatchEvent(new Event('resize'));
    }
  }, [viewport]);

  return (
    <DesignSystemProvider>
      <ThemeProvider theme={theme}>
        <div style={{ padding: '20px', backgroundColor: 'var(--ds-color-background)' }}>
          {children}
        </div>
      </ThemeProvider>
    </DesignSystemProvider>
  );
};

// Helper function to take component screenshots
const takeComponentScreenshot = async (
  component: React.ReactElement,
  testName: string,
  options: {
    theme?: string;
    viewport?: { width: number; height: number };
    states?: string[];
  } = {}
) => {
  const { theme = 'light', viewport, states = ['default'] } = options;

  for (const state of states) {
    const { container } = render(
      <VisualTestWrapper theme={theme} viewport={viewport}>
        {component}
      </VisualTestWrapper>
    );

    // Wait for any animations or async rendering
    await new Promise(resolve => setTimeout(resolve, 100));

    const screenshot = container.firstChild as HTMLElement;
    
    expect(screenshot).toMatchImageSnapshot({
      ...visualTestConfig,
      customSnapshotIdentifier: `${testName}-${theme}-${state}${viewport ? `-${viewport.width}x${viewport.height}` : ''}`,
    });
  }
};

describe('Visual Regression Tests', () => {
  // Viewport configurations for responsive testing
  const viewports = {
    mobile: { width: 375, height: 667 },
    tablet: { width: 768, height: 1024 },
    desktop: { width: 1440, height: 900 },
  };

  // Theme configurations
  const themes = ['light', 'dark', 'high-contrast', 'polish-business'];

  describe('Primitive Components Visual Tests', () => {
    describe('Button Component', () => {
      const buttonVariants = ['primary', 'secondary', 'ghost', 'danger'] as const;
      const buttonSizes = ['xs', 'sm', 'md', 'lg', 'xl'] as const;

      buttonVariants.forEach(variant => {
        buttonSizes.forEach(size => {
          it(`renders ${variant} ${size} button correctly`, async () => {
            await takeComponentScreenshot(
              <Button variant={variant} size={size}>
                {variant} {size}
              </Button>,
              `button-${variant}-${size}`,
              { theme: 'light' }
            );
          });
        });
      });

      it('renders button states correctly', async () => {
        const states = [
          <Button key="default">Default Button</Button>,
          <Button key="hover" className="hover">Hover Button</Button>,
          <Button key="focus" className="focus">Focus Button</Button>,
          <Button key="active" className="active">Active Button</Button>,
          <Button key="disabled" disabled>Disabled Button</Button>,
          <Button key="loading" loading>Loading Button</Button>,
        ];

        for (const [index, button] of states.entries()) {
          await takeComponentScreenshot(
            button,
            `button-state-${index}`,
            { theme: 'light' }
          );
        }
      });

      themes.forEach(theme => {
        it(`renders button in ${theme} theme`, async () => {
          await takeComponentScreenshot(
            <Stack gap={4}>
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Danger</Button>
            </Stack>,
            'button-theme-variants',
            { theme }
          );
        });
      });
    });

    describe('Input Component', () => {
      it('renders input variants correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <Input placeholder="Default input" />
            <Input placeholder="Small input" size="sm" />
            <Input placeholder="Large input" size="lg" />
            <Input placeholder="Error input" error="This field has an error" />
            <Input placeholder="Success input" success="This field is valid" />
            <Input placeholder="Disabled input" disabled />
          </Stack>,
          'input-variants',
          { theme: 'light' }
        );
      });

      it('renders input types correctly', async () => {
        await takeComponentScreenshot(
          <Grid cols={2} gap={4}>
            <Input type="text" placeholder="Text input" />
            <Input type="email" placeholder="Email input" />
            <Input type="password" placeholder="Password input" />
            <Input type="number" placeholder="Number input" />
            <Input type="tel" placeholder="Phone input" />
            <Input type="url" placeholder="URL input" />
          </Grid>,
          'input-types',
          { theme: 'light' }
        );
      });
    });

    describe('Select Component', () => {
      const options = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' },
        { value: 'option3', label: 'Option 3' },
      ];

      it('renders select variants correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <Select options={options} placeholder="Default select" />
            <Select options={options} placeholder="Small select" size="sm" />
            <Select options={options} placeholder="Large select" size="lg" />
            <Select options={options} placeholder="Error select" error="Please select an option" />
            <Select options={options} placeholder="Disabled select" disabled />
          </Stack>,
          'select-variants',
          { theme: 'light' }
        );
      });
    });

    describe('Form Controls', () => {
      it('renders form controls correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <Checkbox>Checkbox option</Checkbox>
            <Checkbox checked>Checked checkbox</Checkbox>
            <Checkbox disabled>Disabled checkbox</Checkbox>
            
            <div>
              <Radio name="radio-group" value="option1">Radio option 1</Radio>
              <Radio name="radio-group" value="option2" checked>Radio option 2</Radio>
              <Radio name="radio-group" value="option3" disabled>Radio option 3</Radio>
            </div>
            
            <Switch>Switch option</Switch>
            <Switch checked>Checked switch</Switch>
            <Switch disabled>Disabled switch</Switch>
          </Stack>,
          'form-controls',
          { theme: 'light' }
        );
      });
    });
  });

  describe('Pattern Components Visual Tests', () => {
    describe('Card Component', () => {
      it('renders card variants correctly', async () => {
        await takeComponentScreenshot(
          <Grid cols={2} gap={4}>
            <Card>
              <Card.Header>Default Card</Card.Header>
              <Card.Body>This is a default card with some content.</Card.Body>
              <Card.Footer>
                <Button size="sm">Action</Button>
              </Card.Footer>
            </Card>
            
            <Card variant="outlined">
              <Card.Header>Outlined Card</Card.Header>
              <Card.Body>This is an outlined card variant.</Card.Body>
            </Card>
            
            <Card variant="elevated">
              <Card.Header>Elevated Card</Card.Header>
              <Card.Body>This is an elevated card with shadow.</Card.Body>
            </Card>
            
            <Card variant="ghost">
              <Card.Header>Ghost Card</Card.Header>
              <Card.Body>This is a ghost card variant.</Card.Body>
            </Card>
          </Grid>,
          'card-variants',
          { theme: 'light' }
        );
      });
    });

    describe('Table Component', () => {
      const tableData = [
        { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Inactive' },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Pending' },
      ];

      const columns = [
        { key: 'name', header: 'Name' },
        { key: 'email', header: 'Email' },
        { key: 'status', header: 'Status' },
      ];

      it('renders table correctly', async () => {
        await takeComponentScreenshot(
          <Table data={tableData} columns={columns} />,
          'table-basic',
          { theme: 'light' }
        );
      });

      it('renders table with sorting', async () => {
        await takeComponentScreenshot(
          <Table 
            data={tableData} 
            columns={columns.map(col => ({ ...col, sortable: true }))}
            sortable
          />,
          'table-sortable',
          { theme: 'light' }
        );
      });
    });

    describe('Form Component', () => {
      it('renders complete form correctly', async () => {
        await takeComponentScreenshot(
          <Form onSubmit={() => {}}>
            <Grid cols={2} gap={4}>
              <Input name="firstName" placeholder="First Name" required />
              <Input name="lastName" placeholder="Last Name" required />
              <Input name="email" type="email" placeholder="Email" required />
              <Input name="phone" type="tel" placeholder="Phone" />
              <Select
                name="country"
                options={[
                  { value: 'pl', label: 'Poland' },
                  { value: 'us', label: 'United States' },
                ]}
                placeholder="Select Country"
              />
              <Textarea name="message" placeholder="Message" rows={3} />
            </Grid>
            
            <Stack gap={3} className="mt-6">
              <Checkbox name="newsletter">Subscribe to newsletter</Checkbox>
              <Switch name="notifications">Enable notifications</Switch>
            </Stack>
            
            <Stack direction="horizontal" gap={3} justify="end" className="mt-6">
              <Button variant="secondary" type="button">Cancel</Button>
              <Button variant="primary" type="submit">Submit</Button>
            </Stack>
          </Form>,
          'form-complete',
          { theme: 'light' }
        );
      });
    });
  });

  describe('Layout Components Visual Tests', () => {
    describe('Grid Component', () => {
      it('renders grid layouts correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={6}>
            <div>
              <h3>2 Column Grid</h3>
              <Grid cols={2} gap={4}>
                <Card><Card.Body>Item 1</Card.Body></Card>
                <Card><Card.Body>Item 2</Card.Body></Card>
                <Card><Card.Body>Item 3</Card.Body></Card>
                <Card><Card.Body>Item 4</Card.Body></Card>
              </Grid>
            </div>
            
            <div>
              <h3>3 Column Grid</h3>
              <Grid cols={3} gap={4}>
                <Card><Card.Body>Item 1</Card.Body></Card>
                <Card><Card.Body>Item 2</Card.Body></Card>
                <Card><Card.Body>Item 3</Card.Body></Card>
              </Grid>
            </div>
            
            <div>
              <h3>Responsive Grid</h3>
              <Grid cols={{ base: 1, md: 2, lg: 4 }} gap={4}>
                <Card><Card.Body>Responsive 1</Card.Body></Card>
                <Card><Card.Body>Responsive 2</Card.Body></Card>
                <Card><Card.Body>Responsive 3</Card.Body></Card>
                <Card><Card.Body>Responsive 4</Card.Body></Card>
              </Grid>
            </div>
          </Stack>,
          'grid-layouts',
          { theme: 'light' }
        );
      });
    });

    describe('Container Component', () => {
      it('renders container sizes correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <Container maxWidth="sm">
              <Card><Card.Body>Small Container (sm)</Card.Body></Card>
            </Container>
            <Container maxWidth="md">
              <Card><Card.Body>Medium Container (md)</Card.Body></Card>
            </Container>
            <Container maxWidth="lg">
              <Card><Card.Body>Large Container (lg)</Card.Body></Card>
            </Container>
            <Container maxWidth="xl">
              <Card><Card.Body>Extra Large Container (xl)</Card.Body></Card>
            </Container>
          </Stack>,
          'container-sizes',
          { theme: 'light' }
        );
      });
    });
  });

  describe('Polish Business Components Visual Tests', () => {
    describe('CurrencyInput Component', () => {
      it('renders currency input correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <CurrencyInput currency="PLN" placeholder="Enter amount" />
            <CurrencyInput currency="PLN" value="1234.56" />
            <CurrencyInput currency="PLN" error="Amount is required" />
            <CurrencyInput currency="PLN" disabled placeholder="Disabled" />
          </Stack>,
          'currency-input-variants',
          { theme: 'light' }
        );
      });
    });

    describe('DatePicker Component', () => {
      it('renders date picker correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <DatePicker format="DD.MM.YYYY" placeholder="Select date" />
            <DatePicker format="DD.MM.YYYY" value={new Date(2024, 2, 15)} />
            <DatePicker format="DD.MM.YYYY" error="Date is required" />
            <DatePicker format="DD.MM.YYYY" disabled placeholder="Disabled" />
          </Stack>,
          'date-picker-variants',
          { theme: 'light' }
        );
      });
    });

    describe('VATRateSelector Component', () => {
      it('renders VAT rate selector correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <VATRateSelector placeholder="Select VAT rate" />
            <VATRateSelector value={23} />
            <VATRateSelector error="VAT rate is required" />
            <VATRateSelector disabled />
          </Stack>,
          'vat-rate-selector-variants',
          { theme: 'light' }
        );
      });
    });

    describe('NIPValidator Component', () => {
      it('renders NIP validator correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <NIPValidator placeholder="Enter NIP number" />
            <NIPValidator value="123-456-78-90" />
            <NIPValidator error="Invalid NIP number" />
            <NIPValidator success="Valid NIP number" />
            <NIPValidator disabled placeholder="Disabled" />
          </Stack>,
          'nip-validator-variants',
          { theme: 'light' }
        );
      });
    });

    describe('InvoiceStatusBadge Component', () => {
      it('renders invoice status badges correctly', async () => {
        await takeComponentScreenshot(
          <Stack direction="horizontal" gap={3} wrap>
            <InvoiceStatusBadge status="draft" />
            <InvoiceStatusBadge status="sent" />
            <InvoiceStatusBadge status="paid" />
            <InvoiceStatusBadge status="overdue" />
            <InvoiceStatusBadge status="cancelled" />
            <InvoiceStatusBadge status="partial" />
          </Stack>,
          'invoice-status-badges',
          { theme: 'light' }
        );
      });
    });

    describe('ComplianceIndicator Component', () => {
      it('renders compliance indicators correctly', async () => {
        await takeComponentScreenshot(
          <Stack gap={4}>
            <ComplianceIndicator
              compliant={true}
              requirements={['VAT registration', 'NIP validation', 'Date format']}
            />
            <ComplianceIndicator
              compliant={false}
              failedRequirements={['Missing NIP', 'Invalid date format']}
              suggestions={['Add valid NIP number', 'Use DD.MM.YYYY format']}
            />
          </Stack>,
          'compliance-indicators',
          { theme: 'light' }
        );
      });
    });
  });

  describe('Theme Visual Tests', () => {
    const themeTestComponent = (
      <Card>
        <Card.Header>
          <h3>Theme Test Component</h3>
        </Card.Header>
        <Card.Body>
          <Stack gap={4}>
            <div>
              <Button variant="primary">Primary Button</Button>
              <Button variant="secondary" className="ml-2">Secondary Button</Button>
            </div>
            
            <Input placeholder="Test input" />
            
            <Select
              options={[
                { value: '1', label: 'Option 1' },
                { value: '2', label: 'Option 2' },
              ]}
              placeholder="Select option"
            />
            
            <div>
              <Checkbox>Checkbox option</Checkbox>
              <Switch className="ml-4">Switch option</Switch>
            </div>
            
            <CurrencyInput currency="PLN" placeholder="Amount" />
            
            <Stack direction="horizontal" gap={2}>
              <InvoiceStatusBadge status="paid" />
              <InvoiceStatusBadge status="overdue" />
            </Stack>
          </Stack>
        </Card.Body>
      </Card>
    );

    themes.forEach(theme => {
      it(`renders components in ${theme} theme`, async () => {
        await takeComponentScreenshot(
          themeTestComponent,
          'theme-test',
          { theme }
        );
      });
    });
  });

  describe('Responsive Visual Tests', () => {
    const responsiveTestComponent = (
      <Container maxWidth="xl">
        <Stack gap={6}>
          <h1>Responsive Layout Test</h1>
          
          <Grid cols={{ base: 1, md: 2, lg: 3 }} gap={4}>
            <Card>
              <Card.Header>Card 1</Card.Header>
              <Card.Body>Responsive card content</Card.Body>
            </Card>
            <Card>
              <Card.Header>Card 2</Card.Header>
              <Card.Body>Responsive card content</Card.Body>
            </Card>
            <Card>
              <Card.Header>Card 3</Card.Header>
              <Card.Body>Responsive card content</Card.Body>
            </Card>
          </Grid>
          
          <Form onSubmit={() => {}}>
            <Grid cols={{ base: 1, md: 2 }} gap={4}>
              <Input placeholder="First Name" />
              <Input placeholder="Last Name" />
              <Input type="email" placeholder="Email" />
              <Input type="tel" placeholder="Phone" />
            </Grid>
            
            <Stack direction={{ base: 'vertical', md: 'horizontal' }} gap={3} justify="end" className="mt-6">
              <Button variant="secondary">Cancel</Button>
              <Button variant="primary">Submit</Button>
            </Stack>
          </Form>
        </Stack>
      </Container>
    );

    Object.entries(viewports).forEach(([viewportName, viewport]) => {
      it(`renders responsive layout on ${viewportName}`, async () => {
        await takeComponentScreenshot(
          responsiveTestComponent,
          'responsive-layout',
          { theme: 'light', viewport }
        );
      });
    });
  });

  describe('Complex Integration Visual Tests', () => {
    it('renders complete invoice form', async () => {
      await takeComponentScreenshot(
        <Container maxWidth="lg">
          <Card>
            <Card.Header>
              <h2>Create Invoice</h2>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={() => {}}>
                <Grid cols={2} gap={4}>
                  <Input name="invoiceNumber" placeholder="Invoice Number" required />
                  <DatePicker name="issueDate" format="DD.MM.YYYY" placeholder="Issue Date" required />
                  
                  <NIPValidator name="sellerNIP" placeholder="Seller NIP" required />
                  <NIPValidator name="buyerNIP" placeholder="Buyer NIP" required />
                  
                  <CurrencyInput name="netAmount" currency="PLN" placeholder="Net Amount" required />
                  <VATRateSelector name="vatRate" required />
                  
                  <Textarea name="description" placeholder="Description" rows={3} />
                  <div>
                    <InvoiceStatusBadge status="draft" />
                  </div>
                </Grid>
                
                <Stack direction="horizontal" gap={3} justify="end" className="mt-6">
                  <Button variant="secondary" type="button">Cancel</Button>
                  <Button variant="primary" type="submit">Create Invoice</Button>
                </Stack>
              </Form>
            </Card.Body>
          </Card>
        </Container>,
        'invoice-form-complete',
        { theme: 'light' }
      );
    });

    it('renders dashboard layout', async () => {
      const dashboardData = [
        { metric: 'Total Invoices', value: '150', change: '+12%' },
        { metric: 'Paid Invoices', value: '120', change: '+8%' },
        { metric: 'Overdue Invoices', value: '5', change: '-2%' },
        { metric: 'Total Revenue', value: '€45,230', change: '+15%' },
      ];

      await takeComponentScreenshot(
        <Container maxWidth="xl">
          <Stack gap={6}>
            <h1>Dashboard</h1>
            
            <Grid cols={4} gap={4}>
              {dashboardData.map((item, index) => (
                <Card key={index}>
                  <Card.Body>
                    <Stack gap={2}>
                      <div className="text-sm text-muted">{item.metric}</div>
                      <div className="text-2xl font-bold">{item.value}</div>
                      <div className={`text-sm ${item.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                        {item.change}
                      </div>
                    </Stack>
                  </Card.Body>
                </Card>
              ))}
            </Grid>
            
            <Grid cols={2} gap={6}>
              <Card>
                <Card.Header>Recent Invoices</Card.Header>
                <Card.Body>
                  <Table
                    data={[
                      { invoice: 'INV-001', amount: '€1,200', status: 'paid' },
                      { invoice: 'INV-002', amount: '€850', status: 'sent' },
                      { invoice: 'INV-003', amount: '€2,100', status: 'overdue' },
                    ]}
                    columns={[
                      { key: 'invoice', header: 'Invoice' },
                      { key: 'amount', header: 'Amount' },
                      { 
                        key: 'status', 
                        header: 'Status',
                        render: (value) => <InvoiceStatusBadge status={value as any} />
                      },
                    ]}
                  />
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Header>Quick Actions</Card.Header>
                <Card.Body>
                  <Stack gap={3}>
                    <Button variant="primary" fullWidth>Create New Invoice</Button>
                    <Button variant="secondary" fullWidth>Upload Document</Button>
                    <Button variant="ghost" fullWidth>View Reports</Button>
                  </Stack>
                </Card.Body>
              </Card>
            </Grid>
          </Stack>
        </Container>,
        'dashboard-layout',
        { theme: 'light' }
      );
    });
  });
});