import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Card, Container } from './Card';
import { Button } from '../../primitives/Button/Button';

const meta: Meta<typeof Card> = {
  title: 'Design System/Patterns/Card',
  component: Card,
  parameters: {
    docs: {
      description: {
        component: 'Card component for displaying content in a structured container with header, body, and footer sections. Includes responsive Container component for layout management.',
      },
    },
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'landmark-one-main', enabled: false }, // Cards are not main landmarks
        ],
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'outlined', 'elevated', 'flat'],
      description: 'Visual style variant of the card',
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Maximum width constraint for the card',
    },
    padding: {
      control: 'select',
      options: ['none', 'xs', 'sm', 'md', 'lg', 'xl'],
      description: 'Internal padding of the card',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Card>;

// Basic card examples
export const Basic: Story = {
  render: (args) => (
    <Card {...args}>
      <h3 className="text-lg font-semibold mb-2">Podstawowa karta</h3>
      <p className="text-neutral-600">
        To jest przykład podstawowej karty z prostą zawartością. 
        Karty są idealne do grupowania powiązanych informacji.
      </p>
    </Card>
  ),
  args: {
    variant: 'default',
    padding: 'md',
  },
};

// Card variants
export const Variants: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card variant="default">
        <h4 className="font-semibold mb-2">Default</h4>
        <p className="text-sm text-neutral-600">Standardowa karta z subtelnym cieniem</p>
      </Card>
      
      <Card variant="outlined">
        <h4 className="font-semibold mb-2">Outlined</h4>
        <p className="text-sm text-neutral-600">Karta z wyraźną ramką</p>
      </Card>
      
      <Card variant="elevated">
        <h4 className="font-semibold mb-2">Elevated</h4>
        <p className="text-sm text-neutral-600">Karta z mocnym cieniem</p>
      </Card>
      
      <Card variant="flat">
        <h4 className="font-semibold mb-2">Flat</h4>
        <p className="text-sm text-neutral-600">Płaska karta bez cienia</p>
      </Card>
    </div>
  ),
};

// Card with compound components
export const WithSections: Story = {
  render: () => (
    <Card variant="elevated" size="lg">
      <Card.Header actions={
        <div className="flex gap-2">
          <Button variant="secondary" size="sm">Edytuj</Button>
          <Button variant="primary" size="sm">Zapisz</Button>
        </div>
      }>
        <div>
          <h3 className="text-lg font-semibold">Faktura VAT nr FV/2025/001</h3>
          <p className="text-sm text-neutral-600">Data wystawienia: 28 sierpnia 2025</p>
        </div>
      </Card.Header>
      
      <Card.Body>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-neutral-900">Sprzedawca</h4>
              <p className="text-sm text-neutral-600">
                Moja Firma Sp. z o.o.<br />
                ul. Biznesowa 123<br />
                00-001 Warszawa<br />
                NIP: 123-456-78-90
              </p>
            </div>
            <div>
              <h4 className="font-medium text-neutral-900">Nabywca</h4>
              <p className="text-sm text-neutral-600">
                Klient ABC Sp. z o.o.<br />
                ul. Kliencka 456<br />
                00-002 Kraków<br />
                NIP: 987-654-32-10
              </p>
            </div>
          </div>
          
          <div className="border-t pt-4">
            <div className="flex justify-between items-center">
              <span>Kwota netto:</span>
              <span>813,01 PLN</span>
            </div>
            <div className="flex justify-between items-center">
              <span>VAT (23%):</span>
              <span>186,99 PLN</span>
            </div>
            <div className="flex justify-between items-center font-semibold text-lg border-t pt-2 mt-2">
              <span>Kwota brutto:</span>
              <span>1 000,00 PLN</span>
            </div>
          </div>
        </div>
      </Card.Body>
      
      <Card.Footer align="between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-success-500 rounded-full"></div>
          <span className="text-sm text-neutral-600">Status: Opłacona</span>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary">Pobierz PDF</Button>
          <Button variant="primary">Wyślij email</Button>
        </div>
      </Card.Footer>
    </Card>
  ),
};

// Polish business cards
export const PolishBusinessCards: Story = {
  render: () => (
    <div className="space-y-6">
      {/* Company profile card */}
      <Card variant="outlined">
        <Card.Header>
          <h3 className="text-lg font-semibold">Profil firmy</h3>
        </Card.Header>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Nazwa firmy
              </label>
              <p className="text-neutral-900">Przykładowa Firma Sp. z o.o.</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                NIP
              </label>
              <p className="text-neutral-900">123-456-78-90</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                REGON
              </label>
              <p className="text-neutral-900">123456785</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Adres
              </label>
              <p className="text-neutral-900">ul. Przykładowa 1, 00-001 Warszawa</p>
            </div>
          </div>
        </Card.Body>
        <Card.Footer>
          <Button variant="primary">Zapisz zmiany</Button>
        </Card.Footer>
      </Card>

      {/* Invoice summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="flat">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">24</div>
            <div className="text-sm text-neutral-600">Faktury w tym miesiącu</div>
          </div>
        </Card>
        
        <Card variant="flat">
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">45 230,50 PLN</div>
            <div className="text-sm text-neutral-600">Przychody w tym miesiącu</div>
          </div>
        </Card>
        
        <Card variant="flat">
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">3</div>
            <div className="text-sm text-neutral-600">Faktury oczekujące</div>
          </div>
        </Card>
      </div>

      {/* Recent invoices card */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-semibold">Ostatnie faktury</h3>
        </Card.Header>
        <Card.Body>
          <div className="space-y-3">
            {[
              { number: 'FV/2025/001', client: 'ABC Sp. z o.o.', amount: '1 000,00 PLN', status: 'Opłacona' },
              { number: 'FV/2025/002', client: 'XYZ S.A.', amount: '2 500,00 PLN', status: 'Wysłana' },
              { number: 'FV/2025/003', client: 'DEF Sp. j.', amount: '750,00 PLN', status: 'Szkic' },
            ].map((invoice, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-neutral-100 last:border-b-0">
                <div>
                  <div className="font-medium">{invoice.number}</div>
                  <div className="text-sm text-neutral-600">{invoice.client}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{invoice.amount}</div>
                  <div className={`text-sm px-2 py-1 rounded-full inline-block ${
                    invoice.status === 'Opłacona' ? 'bg-success-100 text-success-800' :
                    invoice.status === 'Wysłana' ? 'bg-primary-100 text-primary-800' :
                    'bg-neutral-100 text-neutral-800'
                  }`}>
                    {invoice.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card.Body>
        <Card.Footer>
          <Button variant="secondary">Zobacz wszystkie faktury</Button>
        </Card.Footer>
      </Card>
    </div>
  ),
};

// Card sizes
export const Sizes: Story = {
  render: () => (
    <div className="space-y-4">
      <Card size="xs">
        <h4 className="font-semibold mb-2">Extra Small (xs)</h4>
        <p className="text-sm">Bardzo mała karta</p>
      </Card>
      
      <Card size="sm">
        <h4 className="font-semibold mb-2">Small (sm)</h4>
        <p className="text-sm">Mała karta dla kompaktowych informacji</p>
      </Card>
      
      <Card size="md">
        <h4 className="font-semibold mb-2">Medium (md)</h4>
        <p className="text-sm">Średnia karta dla standardowych treści</p>
      </Card>
      
      <Card size="lg">
        <h4 className="font-semibold mb-2">Large (lg)</h4>
        <p className="text-sm">Duża karta dla rozbudowanych informacji i formularzy</p>
      </Card>
      
      <Card size="xl">
        <h4 className="font-semibold mb-2">Extra Large (xl)</h4>
        <p className="text-sm">Bardzo duża karta dla kompleksowych interfejsów</p>
      </Card>
    </div>
  ),
};

// Container component stories
const ContainerMeta: Meta<typeof Container> = {
  title: 'Design System/Patterns/Container',
  component: Container,
  parameters: {
    docs: {
      description: {
        component: 'Container component for responsive max-width layouts with proper content hierarchy and spacing.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'xl', '2xl', 'full'],
      description: 'Maximum width of the container',
    },
    padding: {
      control: 'boolean',
      description: 'Whether to include responsive horizontal padding',
    },
    center: {
      control: 'boolean',
      description: 'Whether to center the container horizontally',
    },
  },
};

export const ContainerBasic: StoryObj<typeof Container> = {
  render: (args) => (
    <div className="bg-neutral-100 min-h-screen">
      <Container {...args}>
        <div className="bg-white p-8 rounded-lg">
          <h1 className="text-2xl font-bold mb-4">Przykładowa strona</h1>
          <p className="text-neutral-600 mb-6">
            Ten kontener automatycznie dostosowuje swoją szerokość do różnych rozmiarów ekranu,
            zapewniając optymalne doświadczenie użytkownika na wszystkich urządzeniach.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <h3 className="font-semibold mb-2">Karta 1</h3>
              <p className="text-sm text-neutral-600">Zawartość pierwszej karty</p>
            </Card>
            <Card>
              <h3 className="font-semibold mb-2">Karta 2</h3>
              <p className="text-sm text-neutral-600">Zawartość drugiej karty</p>
            </Card>
            <Card>
              <h3 className="font-semibold mb-2">Karta 3</h3>
              <p className="text-sm text-neutral-600">Zawartość trzeciej karty</p>
            </Card>
          </div>
        </div>
      </Container>
    </div>
  ),
  args: {
    size: 'lg',
    padding: true,
    center: true,
  },
};

export const ContainerSizes: StoryObj<typeof Container> = {
  render: () => (
    <div className="space-y-8 bg-neutral-100 p-8">
      {(['sm', 'md', 'lg', 'xl', '2xl', 'full'] as const).map((size) => (
        <Container key={size} size={size}>
          <Card>
            <h3 className="font-semibold mb-2">Container {size}</h3>
            <p className="text-sm text-neutral-600">
              Maksymalna szerokość: {
                size === 'sm' ? '640px' :
                size === 'md' ? '768px' :
                size === 'lg' ? '1024px' :
                size === 'xl' ? '1280px' :
                size === '2xl' ? '1536px' :
                'bez limitu'
              }
            </p>
          </Card>
        </Container>
      ))}
    </div>
  ),
};

// Export container stories
export { ContainerMeta, ContainerBasic, ContainerSizes };