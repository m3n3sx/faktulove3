import React from 'react';
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Card, CardHeader, CardBody, CardFooter, Container } from '../Card';
import { Button } from '../../../primitives/Button/Button';
import { Grid } from '../../layouts/Grid/Grid';

expect.extend(toHaveNoViolations);

describe('Card Component', () => {
  describe('Basic Card Functionality', () => {
    it('renders card with children', () => {
      render(
        <Card>
          <div>Card content</div>
        </Card>
      );

      expect(screen.getByRole('article')).toBeInTheDocument();
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('applies default variant styles', () => {
      render(<Card testId="test-card">Content</Card>);
      
      const card = screen.getByTestId('test-card');
      expect(card).toHaveClass('bg-white', 'border', 'border-neutral-200', 'shadow-sm-sm');
    });

    it('applies custom className', () => {
      render(<Card className="custom-class">Content</Card>);
      
      const card = screen.getByRole('article');
      expect(card).toHaveClass('custom-class');
    });
  });

  describe('Card Variants', () => {
    it('applies outlined variant styles', () => {
      render(<Card variant="outlined" testId="outlined-card">Content</Card>);
      
      const card = screen.getByTestId('outlined-card');
      expect(card).toHaveClass('bg-white', 'border-2', 'border-neutral-300');
    });

    it('applies elevated variant styles', () => {
      render(<Card variant="elevated" testId="elevated-card">Content</Card>);
      
      const card = screen.getByTestId('elevated-card');
      expect(card).toHaveClass('bg-white', 'border', 'border-neutral-200', 'shadow-sm-lg');
    });

    it('applies flat variant styles', () => {
      render(<Card variant="flat" testId="flat-card">Content</Card>);
      
      const card = screen.getByTestId('flat-card');
      expect(card).toHaveClass('bg-neutral-50', 'border-0');
    });
  });

  describe('Card Sizes', () => {
    it('applies size constraints', () => {
      render(<Card size="sm" testId="small-card">Content</Card>);
      
      const card = screen.getByTestId('small-card');
      expect(card).toHaveClass('max-w-sm');
    });

    it('applies large size', () => {
      render(<Card size="lg" testId="large-card">Content</Card>);
      
      const card = screen.getByTestId('large-card');
      expect(card).toHaveClass('max-w-lg');
    });
  });

  describe('Card Padding', () => {
    it('applies default medium padding', () => {
      render(<Card testId="default-padding">Content</Card>);
      
      const card = screen.getByTestId('default-padding');
      expect(card).toHaveClass('p-6');
    });

    it('applies no padding when specified', () => {
      render(<Card padding="none" testId="no-padding">Content</Card>);
      
      const card = screen.getByTestId('no-padding');
      expect(card).toHaveClass('p-0');
    });

    it('applies small padding', () => {
      render(<Card padding="sm" testId="small-padding">Content</Card>);
      
      const card = screen.getByTestId('small-padding');
      expect(card).toHaveClass('p-4');
    });
  });
});

describe('CardHeader Component', () => {
  it('renders header with children', () => {
    render(
      <CardHeader>
        <h2>Card Title</h2>
      </CardHeader>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
  });

  it('renders header with actions', () => {
    render(
      <CardHeader actions={<Button size="sm">Action</Button>}>
        <h2>Card Title</h2>
      </CardHeader>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });

  it('applies proper header styling', () => {
    render(<CardHeader testId="card-header">Title</CardHeader>);
    
    const header = screen.getByTestId('card-header');
    expect(header).toHaveClass('flex', 'items-center', 'justify-between', 'p-6', 'border-b', 'border-neutral-200');
  });
});

describe('CardBody Component', () => {
  it('renders body with children', () => {
    render(
      <CardBody>
        <p>Card body content</p>
      </CardBody>
    );

    expect(screen.getByText('Card body content')).toBeInTheDocument();
  });

  it('applies proper body styling', () => {
    render(<CardBody testId="card-body">Content</CardBody>);
    
    const body = screen.getByTestId('card-body');
    expect(body).toHaveClass('p-6');
  });
});

describe('CardFooter Component', () => {
  it('renders footer with children', () => {
    render(
      <CardFooter>
        <Button>Save</Button>
      </CardFooter>
    );

    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
  });

  it('applies default right alignment', () => {
    render(<CardFooter testId="card-footer">Content</CardFooter>);
    
    const footer = screen.getByTestId('card-footer');
    expect(footer).toHaveClass('justify-end');
  });

  it('applies left alignment', () => {
    render(<CardFooter align="left" testId="left-footer">Content</CardFooter>);
    
    const footer = screen.getByTestId('left-footer');
    expect(footer).toHaveClass('justify-start');
  });

  it('applies center alignment', () => {
    render(<CardFooter align="center" testId="center-footer">Content</CardFooter>);
    
    const footer = screen.getByTestId('center-footer');
    expect(footer).toHaveClass('justify-center');
  });

  it('applies between alignment', () => {
    render(<CardFooter align="between" testId="between-footer">Content</CardFooter>);
    
    const footer = screen.getByTestId('between-footer');
    expect(footer).toHaveClass('justify-between');
  });

  it('applies proper footer styling', () => {
    render(<CardFooter testId="card-footer">Content</CardFooter>);
    
    const footer = screen.getByTestId('card-footer');
    expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'border-t', 'border-neutral-200', 'bg-neutral-50');
  });
});

describe('Compound Card Usage', () => {
  it('renders complete card with all sections', () => {
    render(
      <Card>
        <Card.Header actions={<Button size="sm">Edit</Button>}>
          <h2>Invoice #001</h2>
        </Card.Header>
        <Card.Body>
          <p>Invoice details go here</p>
        </Card.Body>
        <Card.Footer align="between">
          <span>Total: 1000 PLN</span>
          <Button variant="primary">Pay Now</Button>
        </Card.Footer>
      </Card>
    );

    expect(screen.getByText('Invoice #001')).toBeInTheDocument();
    expect(screen.getByText('Invoice details go here')).toBeInTheDocument();
    expect(screen.getByText('Total: 1000 PLN')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pay Now' })).toBeInTheDocument();
  });

  it('works with padding="none" and individual section padding', () => {
    render(
      <Card padding="none">
        <Card.Header>
          <h2>No Card Padding</h2>
        </Card.Header>
        <Card.Body>
          <p>Only sections have padding</p>
        </Card.Body>
      </Card>
    );

    const card = screen.getByRole('article');
    expect(card).toHaveClass('p-0');
    
    // Header and body should still have their own padding
    expect(screen.getByTestId('card-header')).toHaveClass('p-6');
    expect(screen.getByTestId('card-body')).toHaveClass('p-6');
  });
});

describe('Container Component', () => {
  it('renders container with children', () => {
    render(
      <Container>
        <div>Container content</div>
      </Container>
    );

    expect(screen.getByText('Container content')).toBeInTheDocument();
  });

  it('applies default size and styling', () => {
    render(<Container testId="default-container">Content</Container>);
    
    const container = screen.getByTestId('default-container');
    expect(container).toHaveClass('max-w-screen-lg', 'px-4', 'sm:px-6', 'lg:px-8', 'mx-auto');
  });

  it('applies different sizes', () => {
    render(<Container size="sm" testId="small-container">Content</Container>);
    
    const container = screen.getByTestId('small-container');
    expect(container).toHaveClass('max-w-screen-sm');
  });

  it('applies full width', () => {
    render(<Container size="full" testId="full-container">Content</Container>);
    
    const container = screen.getByTestId('full-container');
    expect(container).toHaveClass('max-w-full');
  });

  it('removes padding when disabled', () => {
    render(<Container padding={false} testId="no-padding-container">Content</Container>);
    
    const container = screen.getByTestId('no-padding-container');
    expect(container).not.toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
  });

  it('removes centering when disabled', () => {
    render(<Container center={false} testId="no-center-container">Content</Container>);
    
    const container = screen.getByTestId('no-center-container');
    expect(container).not.toHaveClass('mx-auto');
  });

  it('applies custom className', () => {
    render(<Container className="custom-container">Content</Container>);
    
    const container = screen.getByTestId('container');
    expect(container).toHaveClass('custom-container');
  });
});

describe('Accessibility', () => {
  it('Card meets accessibility standards', async () => {
    const { container } = render(
      <Card>
        <Card.Header>
          <h2>Accessible Card</h2>
        </Card.Header>
        <Card.Body>
          <p>This card is accessible</p>
        </Card.Body>
        <Card.Footer>
          <Button>Action</Button>
        </Card.Footer>
      </Card>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Container meets accessibility standards', async () => {
    const { container } = render(
      <Container>
        <h1>Page Title</h1>
        <p>Page content</p>
      </Container>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Card has proper semantic role', () => {
    render(<Card>Content</Card>);
    
    const card = screen.getByRole('article');
    expect(card).toBeInTheDocument();
  });
});

describe('Polish Business Context', () => {
  it('renders invoice card with Polish content', () => {
    render(
      <Card variant="elevated">
        <Card.Header actions={<Button size="sm">Edytuj</Button>}>
          <div>
            <h3 className="text-lg font-semibold">Faktura VAT nr FV/2025/001</h3>
            <p className="text-sm text-neutral-600">Data wystawienia: 28.08.2025</p>
          </div>
        </Card.Header>
        <Card.Body>
          <div className="space-y-2">
            <p><strong>Nabywca:</strong> Firma ABC Sp. z o.o.</p>
            <p><strong>NIP:</strong> 123-456-78-90</p>
            <p><strong>Kwota netto:</strong> 813,01 PLN</p>
            <p><strong>VAT (23%):</strong> 186,99 PLN</p>
            <p><strong>Kwota brutto:</strong> 1 000,00 PLN</p>
          </div>
        </Card.Body>
        <Card.Footer align="between">
          <span className="text-sm text-neutral-600">Status: Opłacona</span>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm">Pobierz PDF</Button>
            <Button variant="primary" size="sm">Wyślij email</Button>
          </div>
        </Card.Footer>
      </Card>
    );

    expect(screen.getByText('Faktura VAT nr FV/2025/001')).toBeInTheDocument();
    expect(screen.getByText('Data wystawienia: 28.08.2025')).toBeInTheDocument();
    expect(screen.getByText('Kwota brutto: 1 000,00 PLN')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Edytuj' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pobierz PDF' })).toBeInTheDocument();
  });

  it('renders company profile card', () => {
    render(
      <Container size="md">
        <Card>
          <Card.Header>
            <h2>Profil firmy</h2>
          </Card.Header>
          <Card.Body>
            <div cols={2}>
              <div>
                <label className="block text-sm font-medium text-neutral-700">Nazwa firmy</label>
                <p className="mt-1">Przykładowa Firma Sp. z o.o.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700">NIP</label>
                <p className="mt-1">123-456-78-90</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700">REGON</label>
                <p className="mt-1">123456785</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700">Adres</label>
                <p className="mt-1">ul. Przykładowa 1, 00-001 Warszawa</p>
              </div>
            </div>
          </Card.Body>
          <Card.Footer>
            <Button variant="primary">Zapisz zmiany</Button>
          </Card.Footer>
        </Card>
      </Container>
    );

    expect(screen.getByText('Profil firmy')).toBeInTheDocument();
    expect(screen.getByText('Przykładowa Firma Sp. z o.o.')).toBeInTheDocument();
    expect(screen.getByText('123-456-78-90')).toBeInTheDocument();
  });
});