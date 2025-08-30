/**
 * Visual Regression Testing Suite
 * Tests visual consistency across all component variants
 */

import React from 'react';
import { render } from '@testing-library/react';
import { toMatchImageSnapshot } from 'jest-image-snapshot';

// Extend Jest matchers
expect.extend({ toMatchImageSnapshot });

// Import components for visual testing
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Card } from '../components/patterns/Card/Card';
import { CurrencyInput } from '../components/business/CurrencyInput/CurrencyInput';
import { InvoiceStatusBadge } from '../components/business/InvoiceStatusBadge/InvoiceStatusBadge';

// Mock canvas for visual testing
HTMLCanvasElement.prototype.getContext = jest.fn();

describe('Visual Regression Tests', () => {
  // Helper function to create visual snapshots
  const createVisualSnapshot = async (component: React.ReactElement, testName: string) => {
    const { container } = render(component);
    
    // Wait for any animations or async rendering
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Create snapshot
    expect(container.firstChild).toMatchImageSnapshot({
      customSnapshotIdentifier: testName,
      failureThreshold: 0.01,
      failureThresholdType: 'percent',
    });
  };

  describe('Button Visual Tests', () => {
    const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
    const sizes = ['xs', 'sm', 'md', 'lg', 'xl'] as const;

    variants.forEach(variant => {
      sizes.forEach(size => {
        it(`renders ${variant} ${size} button consistently`, async () => {
          await createVisualSnapshot(
            <Button variant={variant} size={size}>
              {variant} {size}
            </Button>,
            `button-${variant}-${size}`
          );
        });

        it(`renders ${variant} ${size} disabled button consistently`, async () => {
          await createVisualSnapshot(
            <Button variant={variant} size={size} disabled>
              {variant} {size} disabled
            </Button>,
            `button-${variant}-${size}-disabled`
          );
        });

        it(`renders ${variant} ${size} loading button consistently`, async () => {
          await createVisualSnapshot(
            <Button variant={variant} size={size} loading>
              {variant} {size} loading
            </Button>,
            `button-${variant}-${size}-loading`
          );
        });
      });
    });
  });

  describe('Input Visual Tests', () => {
    const sizes = ['sm', 'md', 'lg'] as const;
    const states = ['default', 'error', 'success'] as const;

    sizes.forEach(size => {
      states.forEach(state => {
        it(`renders ${size} ${state} input consistently`, async () => {
          const props = {
            size,
            placeholder: `${size} ${state} input`,
            error: state === 'error' ? 'Error message' : undefined,
            success: state === 'success' ? 'Success message' : undefined,
          };

          await createVisualSnapshot(
            <Input {...props} />,
            `input-${size}-${state}`
          );
        });
      });
    });

    it('renders focused input consistently', async () => {
      const { container } = render(
        <Input placeholder="Focused input" autoFocus />
      );
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(container.firstChild).toMatchImageSnapshot({
        customSnapshotIdentifier: 'input-focused',
        failureThreshold: 0.01,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Card Visual Tests', () => {
    it('renders basic card consistently', async () => {
      await createVisualSnapshot(
        <Card>
          <Card.Header>Card Header</Card.Header>
          <Card.Body>
            This is the card body content with some text to test layout.
          </Card.Body>
          <Card.Footer>Card Footer</Card.Footer>
        </Card>,
        'card-basic'
      );
    });

    it('renders card with actions consistently', async () => {
      await createVisualSnapshot(
        <Card>
          <Card.Header>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>Card with Actions</h3>
              <Button size="sm" variant="ghost">Action</Button>
            </div>
          </Card.Header>
          <Card.Body>
            Card content with header actions.
          </Card.Body>
        </Card>,
        'card-with-actions'
      );
    });
  });

  describe('Polish Business Components Visual Tests', () => {
    it('renders currency input with PLN consistently', async () => {
      await createVisualSnapshot(
        <CurrencyInput 
          currency="PLN" 
          value="1234.56"
          placeholder="Enter amount"
        />,
        'currency-input-pln'
      );
    });

    it('renders currency input with error consistently', async () => {
      await createVisualSnapshot(
        <CurrencyInput 
          currency="PLN" 
          value="invalid"
          error="Invalid amount"
          placeholder="Enter amount"
        />,
        'currency-input-error'
      );
    });

    describe('Invoice Status Badge Visual Tests', () => {
      const statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled'] as const;

      statuses.forEach(status => {
        it(`renders ${status} status badge consistently`, async () => {
          await createVisualSnapshot(
            <InvoiceStatusBadge status={status} />,
            `invoice-status-${status}`
          );
        });
      });
    });
  });

  describe('Theme Visual Tests', () => {
    it('renders components in light theme consistently', async () => {
      await createVisualSnapshot(
        <div data-theme="light" style={{ padding: '16px' }}>
          <Button variant="primary">Primary Button</Button>
          <Input placeholder="Input field" style={{ marginLeft: '8px' }} />
          <Card style={{ marginTop: '16px', maxWidth: '300px' }}>
            <Card.Header>Light Theme Card</Card.Header>
            <Card.Body>Content in light theme</Card.Body>
          </Card>
        </div>,
        'theme-light'
      );
    });

    it('renders components in dark theme consistently', async () => {
      await createVisualSnapshot(
        <div data-theme="dark" style={{ padding: '16px', backgroundColor: '#1a1a1a' }}>
          <Button variant="primary">Primary Button</Button>
          <Input placeholder="Input field" style={{ marginLeft: '8px' }} />
          <Card style={{ marginTop: '16px', maxWidth: '300px' }}>
            <Card.Header>Dark Theme Card</Card.Header>
            <Card.Body>Content in dark theme</Card.Body>
          </Card>
        </div>,
        'theme-dark'
      );
    });

    it('renders components in high contrast theme consistently', async () => {
      await createVisualSnapshot(
        <div data-theme="high-contrast" style={{ padding: '16px' }}>
          <Button variant="primary">Primary Button</Button>
          <Input placeholder="Input field" style={{ marginLeft: '8px' }} />
          <Card style={{ marginTop: '16px', maxWidth: '300px' }}>
            <Card.Header>High Contrast Card</Card.Header>
            <Card.Body>Content in high contrast theme</Card.Body>
          </Card>
        </div>,
        'theme-high-contrast'
      );
    });
  });

  describe('Responsive Visual Tests', () => {
    const breakpoints = [
      { name: 'mobile', width: 375 },
      { name: 'tablet', width: 768 },
      { name: 'desktop', width: 1024 },
      { name: 'wide', width: 1440 },
    ];

    breakpoints.forEach(({ name, width }) => {
      it(`renders responsive layout at ${name} breakpoint consistently`, async () => {
        // Mock viewport size
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width,
        });

        const { container } = render(
          <div style={{ width: `${width}px` }}>
            <Card>
              <Card.Header>Responsive Card</Card.Header>
              <Card.Body>
                <div style={{ display: 'grid', gridTemplateColumns: width < 768 ? '1fr' : '1fr 1fr', gap: '16px' }}>
                  <Input placeholder="First input" />
                  <Input placeholder="Second input" />
                </div>
              </Card.Body>
              <Card.Footer>
                <div style={{ display: 'flex', flexDirection: width < 768 ? 'column' : 'row', gap: '8px' }}>
                  <Button variant="secondary">Cancel</Button>
                  <Button variant="primary">Submit</Button>
                </div>
              </Card.Footer>
            </Card>
          </div>
        );

        await new Promise(resolve => setTimeout(resolve, 100));

        expect(container.firstChild).toMatchImageSnapshot({
          customSnapshotIdentifier: `responsive-${name}`,
          failureThreshold: 0.01,
          failureThresholdType: 'percent',
        });
      });
    });
  });

  describe('Interaction State Visual Tests', () => {
    it('renders hover states consistently', async () => {
      const { container } = render(
        <div>
          <Button className="hover:bg-primary-700">Hover Button</Button>
          <Input className="hover:border-primary-500" placeholder="Hover Input" />
        </div>
      );

      // Simulate hover state with CSS classes
      const button = container.querySelector('button');
      const input = container.querySelector('input');
      
      if (button) button.classList.add('hover:bg-primary-700');
      if (input) input.classList.add('hover:border-primary-500');

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(container).toMatchImageSnapshot({
        customSnapshotIdentifier: 'hover-states',
        failureThreshold: 0.01,
        failureThresholdType: 'percent',
      });
    });

    it('renders focus states consistently', async () => {
      const { container } = render(
        <div>
          <Button autoFocus>Focused Button</Button>
          <Input placeholder="Input field" />
        </div>
      );

      await new Promise(resolve => setTimeout(resolve, 100));

      expect(container).toMatchImageSnapshot({
        customSnapshotIdentifier: 'focus-states',
        failureThreshold: 0.01,
        failureThresholdType: 'percent',
      });
    });
  });

  describe('Complex Layout Visual Tests', () => {
    it('renders complex invoice form layout consistently', async () => {
      await createVisualSnapshot(
        <div style={{ maxWidth: '800px', padding: '16px' }}>
          <Card>
            <Card.Header>
              <h2>Create Invoice</h2>
            </Card.Header>
            <Card.Body>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <Input placeholder="Invoice number" />
                <Input placeholder="Client name" />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <CurrencyInput currency="PLN" placeholder="Amount" />
                <Input placeholder="Due date" />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <InvoiceStatusBadge status="draft" />
              </div>
            </Card.Body>
            <Card.Footer>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <Button variant="secondary">Cancel</Button>
                <Button variant="primary">Save Invoice</Button>
              </div>
            </Card.Footer>
          </Card>
        </div>,
        'complex-invoice-form'
      );
    });
  });
});