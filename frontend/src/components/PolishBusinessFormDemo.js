import React from 'react';
import { Form, FormField, Input, Button, Grid, Stack } from '../design-system';

const PolishBusinessFormDemo = () => {
  const handleSubmit = (formData) => {
    console.log('Form submitted with data:', formData);
    alert('Formularz został pomyślnie wysłany!');
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-sm">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Demo formularza biznesowego
      </h2>
      
      <Form
        onSubmit={handleSubmit}
        validationMode="onBlur"
        initialValues={{
          companyName: '',
          nip: '',
          regon: '',
          postalCode: '',
          phone: '',
          email: ''
        }}
      >
        <Stack spacing={6}>
          <FormField
            name="companyName"
            label="Nazwa firmy"
            rules={{
              required: true,
              minLength: 2,
              maxLength: 100
            }}
          >
            <Input placeholder="Wprowadź nazwę firmy" />
          </FormField>

          <Grid cols={2} gap="md">
            <FormField
              name="nip"
              label="NIP"
              rules={{
                required: true,
                polishValidator: 'NIP'
              }}
            >
              <Input placeholder="123-456-78-90" />
            </FormField>

            <FormField
              name="regon"
              label="REGON"
              rules={{
                polishValidator: 'REGON'
              }}
            >
              <Input placeholder="123456789" />
            </FormField>
          </Grid>

          <Grid cols={2} gap="md">
            <FormField
              name="postalCode"
              label="Kod pocztowy"
              rules={{
                required: true,
                polishValidator: 'POSTAL_CODE'
              }}
            >
              <Input placeholder="00-000" />
            </FormField>

            <FormField
              name="phone"
              label="Telefon"
              rules={{
                polishValidator: 'PHONE'
              }}
            >
              <Input placeholder="+48 123 456 789" />
            </FormField>
          </Grid>

          <FormField
            name="email"
            label="E-mail"
            rules={{
              required: true,
              pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            }}
          >
            <Input type="email" placeholder="firma@example.com" />
          </FormField>

          <div className="flex justify-end">
            <Button type="submit" variant="primary">
              Zapisz dane firmy
            </Button>
          </div>
        </Stack>
      </Form>
    </div>
  );
};

export default PolishBusinessFormDemo;