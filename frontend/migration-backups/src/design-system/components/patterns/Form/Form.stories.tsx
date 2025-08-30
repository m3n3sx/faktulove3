import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import { Form, FormField } from './Form';
import { Input } from '../../primitives/Input/Input';
import { Button } from '../../primitives/Button/Button';
import { Select } from '../../primitives/Select/Select';

const meta: Meta<typeof Form> = {
  title: 'Design System/Patterns/Form',
  component: Form,
  parameters: {
    docs: {
      description: {
        component: 'Form component with validation state management, Polish-specific validation patterns, and accessibility features.',
      },
    },
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'label', enabled: true },
          { id: 'aria-required-attr', enabled: true },
        ],
      },
    },
  },
  argTypes: {
    validationMode: {
      control: 'select',
      options: ['onChange', 'onBlur', 'onSubmit'],
      description: 'When to trigger field validation',
    },
    onSubmit: { action: 'submitted' },
  },
};

export default meta;
type Story = StoryObj<typeof Form>;

// Basic form example
export const Basic: Story = {
  render: (args) => (
    <Form {...args}>
      <FormField name="name" label="Imię i nazwisko" rules={{ required: true }}>
        <Input placeholder="Wprowadź imię i nazwisko" />
      </FormField>
      
      <FormField name="email" label="Email" rules={{ required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ }}>
        <Input type="email" placeholder="przykład@email.com" />
      </FormField>
      
      <FormField name="message" label="Wiadomość" rules={{ minLength: 10, maxLength: 500 }}>
        <textarea 
          className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          rows={4}
          placeholder="Wprowadź wiadomość..."
        />
      </FormField>
      
      <Button type="submit" variant="primary">
        Wyślij formularz
      </Button>
    </Form>
  ),
  args: {
    onSubmit: (data) => {
      console.log('Form submitted:', data);
      alert(`Formularz wysłany z danymi: ${JSON.stringify(data, null, 2)}`);
    },
    validationMode: 'onBlur',
  },
};

// Polish business form with NIP and REGON validation
export const PolishBusiness: Story = {
  render: (args) => (
    <Form {...args}>
      <FormField name="companyName" label="Nazwa firmy" rules={{ required: true }}>
        <Input placeholder="Wprowadź nazwę firmy" />
      </FormField>
      
      <FormField name="nip" label="NIP" rules={{ required: true, polishValidator: 'NIP' }}>
        <Input placeholder="123-456-78-90" />
      </FormField>
      
      <FormField name="regon" label="REGON" rules={{ polishValidator: 'REGON' }}>
        <Input placeholder="123456785" />
      </FormField>
      
      <FormField name="address" label="Adres" rules={{ required: true }}>
        <Input placeholder="Ulica i numer" />
      </FormField>
      
      <FormField name="postalCode" label="Kod pocztowy" rules={{ required: true, polishValidator: 'POSTAL_CODE' }}>
        <Input placeholder="00-000" />
      </FormField>
      
      <FormField name="city" label="Miasto" rules={{ required: true }}>
        <Input placeholder="Wprowadź miasto" />
      </FormField>
      
      <FormField name="phone" label="Telefon" rules={{ polishValidator: 'PHONE' }}>
        <Input placeholder="+48 123 456 789" />
      </FormField>
      
      <FormField name="vatRate" label="Stawka VAT" rules={{ required: true }}>
        <Select>
          <option value="">Wybierz stawkę VAT</option>
          <option value="23">23%</option>
          <option value="8">8%</option>
          <option value="5">5%</option>
          <option value="0">0%</option>
        </Select>
      </FormField>
      
      <div className="flex gap-4">
        <Button type="submit" variant="primary">
          Zapisz dane firmy
        </Button>
        <Button type="button" variant="secondary">
          Anuluj
        </Button>
      </div>
    </Form>
  ),
  args: {
    onSubmit: (data) => {
      console.log('Polish business form submitted:', data);
      alert(`Dane firmy zapisane: ${JSON.stringify(data, null, 2)}`);
    },
    validationMode: 'onBlur',
    initialValues: {
      vatRate: '23',
    },
  },
};

// Real-time validation example
export const RealTimeValidation: Story = {
  render: (args) => (
    <Form {...args}>
      <FormField 
        name="username" 
        label="Nazwa użytkownika" 
        rules={{ 
          required: true, 
          minLength: 3, 
          maxLength: 20,
          pattern: /^[a-zA-Z0-9_]+$/
        }}
      >
        <Input placeholder="min. 3 znaki, tylko litery, cyfry i _" />
      </FormField>
      
      <FormField 
        name="password" 
        label="Hasło" 
        rules={{ 
          required: true, 
          minLength: 8,
          custom: (value) => {
            if (!value) return null;
            if (!/(?=.*[a-z])/.test(value)) return 'Hasło musi zawierać małą literę';
            if (!/(?=.*[A-Z])/.test(value)) return 'Hasło musi zawierać wielką literę';
            if (!/(?=.*\d)/.test(value)) return 'Hasło musi zawierać cyfrę';
            if (!/(?=.*[@$!%*?&])/.test(value)) return 'Hasło musi zawierać znak specjalny';
            return null;
          }
        }}
      >
        <Input type="password" placeholder="min. 8 znaków z wielką literą, cyfrą i znakiem specjalnym" />
      </FormField>
      
      <FormField 
        name="confirmPassword" 
        label="Potwierdź hasło" 
        rules={{ 
          required: true,
          custom: (value, formData) => {
            if (!value) return null;
            // Note: In real implementation, you'd need access to other field values
            return value !== formData?.password ? 'Hasła nie są identyczne' : null;
          }
        }}
      >
        <Input type="password" placeholder="Powtórz hasło" />
      </FormField>
      
      <Button type="submit" variant="primary">
        Utwórz konto
      </Button>
    </Form>
  ),
  args: {
    onSubmit: (data) => {
      console.log('Account creation form submitted:', data);
      alert('Konto utworzone pomyślnie!');
    },
    validationMode: 'onChange',
  },
};

// Form with loading state
export const WithLoadingState: Story = {
  render: (args) => {
    const [isLoading, setIsLoading] = useState(false);
    
    const handleSubmit = async (data: any) => {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsLoading(false);
      args.onSubmit?.(data);
    };

    return (
      <Form {...args} onSubmit={handleSubmit}>
        <FormField name="title" label="Tytuł" rules={{ required: true }}>
          <Input placeholder="Wprowadź tytuł" disabled={isLoading} />
        </FormField>
        
        <FormField name="description" label="Opis" rules={{ required: true, minLength: 10 }}>
          <textarea 
            className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-neutral-100 disabled:cursor-not-allowed"
            rows={4}
            placeholder="Wprowadź opis..."
            disabled={isLoading}
          />
        </FormField>
        
        <Button 
          type="submit" 
          variant="primary" 
          loading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? 'Zapisywanie...' : 'Zapisz'}
        </Button>
      </Form>
    );
  },
  args: {
    onSubmit: (data) => {
      console.log('Form with loading submitted:', data);
      alert('Dane zapisane pomyślnie!');
    },
    validationMode: 'onBlur',
  },
};

// Form with initial values
export const WithInitialValues: Story = {
  render: (args) => (
    <Form {...args}>
      <FormField name="firstName" label="Imię" rules={{ required: true }}>
        <Input />
      </FormField>
      
      <FormField name="lastName" label="Nazwisko" rules={{ required: true }}>
        <Input />
      </FormField>
      
      <FormField name="email" label="Email" rules={{ required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ }}>
        <Input type="email" />
      </FormField>
      
      <FormField name="role" label="Rola" rules={{ required: true }}>
        <Select>
          <option value="">Wybierz rolę</option>
          <option value="admin">Administrator</option>
          <option value="user">Użytkownik</option>
          <option value="viewer">Przeglądający</option>
        </Select>
      </FormField>
      
      <div className="flex gap-4">
        <Button type="submit" variant="primary">
          Aktualizuj profil
        </Button>
        <Button type="button" variant="secondary">
          Resetuj
        </Button>
      </div>
    </Form>
  ),
  args: {
    onSubmit: (data) => {
      console.log('Profile update form submitted:', data);
      alert(`Profil zaktualizowany: ${JSON.stringify(data, null, 2)}`);
    },
    validationMode: 'onBlur',
    initialValues: {
      firstName: 'Jan',
      lastName: 'Kowalski',
      email: 'jan.kowalski@example.com',
      role: 'user',
    },
  },
};

// Validation modes comparison
export const ValidationModes: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">Walidacja onChange (natychmiastowa)</h3>
        <Form onSubmit={(data) => console.log('onChange form:', data)} validationMode="onChange">
          <FormField name="username1" label="Nazwa użytkownika" rules={{ required: true, minLength: 3 }}>
            <Input placeholder="Wpisz min. 3 znaki" />
          </FormField>
          <Button type="submit" variant="primary" size="sm">Wyślij</Button>
        </Form>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Walidacja onBlur (po opuszczeniu pola)</h3>
        <Form onSubmit={(data) => console.log('onBlur form:', data)} validationMode="onBlur">
          <FormField name="username2" label="Nazwa użytkownika" rules={{ required: true, minLength: 3 }}>
            <Input placeholder="Kliknij poza pole aby zwalidować" />
          </FormField>
          <Button type="submit" variant="primary" size="sm">Wyślij</Button>
        </Form>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Walidacja onSubmit (przy wysyłaniu)</h3>
        <Form onSubmit={(data) => console.log('onSubmit form:', data)} validationMode="onSubmit">
          <FormField name="username3" label="Nazwa użytkownika" rules={{ required: true, minLength: 3 }}>
            <Input placeholder="Walidacja tylko przy wysyłaniu" />
          </FormField>
          <Button type="submit" variant="primary" size="sm">Wyślij</Button>
        </Form>
      </div>
    </div>
  ),
};