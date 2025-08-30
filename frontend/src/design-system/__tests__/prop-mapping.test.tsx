/**
 * Prop Mapping and Compatibility Layer Test Suite
 * Tests component prop mapping, migration utilities, and backward compatibility
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Import compatibility utilities
import { ComponentWrapper } from '../compatibility/ComponentWrapper';
import { MigrationTester } from '../compatibility/MigrationTester';
import { MigrationValidator } from '../compatibility/MigrationValidator';
import { MigrationUtils } from '../compatibility/MigrationUtils';
import { ComponentUsageAnalyzer } from '../compatibility/ComponentUsageAnalyzer';

// Import design system components
import { Button } from '../components/primitives/Button/Button';
import { Input } from '../components/primitives/Input/Input';
import { Select } from '../components/primitives/Select/Select';

// Import providers
import { DesignSystemProvider } from '../providers/DesignSystemProvider';

// Mock legacy components for testing
const LegacyButton = ({ children, className, onClick, disabled, ...props }: any) => (
  <button 
    className={`legacy-btn ${className || ''}`}
    onClick={onClick}
    disabled={disabled}
    {...props}
  >
    {children}
  </button>
);

const LegacyInput = ({ className, type = 'text', onChange, ...props }: any) => (
  <input
    className={`legacy-input ${className || ''}`}
    type={type}
    onChange={onChange}
    {...props}
  />
);

const LegacySelect = ({ children, className, onChange, ...props }: any) => (
  <select
    className={`legacy-select ${className || ''}`}
    onChange={onChange}
    {...props}
  >
    {children}
  </select>
);

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <DesignSystemProvider>
    {children}
  </DesignSystemProvider>
);

describe('Prop Mapping and Compatibility Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('ComponentWrapper', () => {
    describe('Button Prop Mapping', () => {
      it('maps legacy button props to design system props', () => {
        const handleClick = jest.fn();
        
        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyButton}
              newComponent={Button}
              propMapping={{
                className: (value: string) => {
                  const variantMap: Record<string, string> = {
                    'btn-primary': 'primary',
                    'btn-secondary': 'secondary',
                    'btn-danger': 'danger',
                  };
                  return { variant: variantMap[value] || 'primary' };
                },
                size: (value: string) => {
                  const sizeMap: Record<string, string> = {
                    'btn-sm': 'sm',
                    'btn-lg': 'lg',
                  };
                  return { size: sizeMap[value] || 'md' };
                },
              }}
              className="btn-primary"
              onClick={handleClick}
            >
              Mapped Button
            </ComponentWrapper>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        expect(button).toHaveTextContent('Mapped Button');
        expect(button).toHaveClass('ds-button--primary');
      });

      it('handles complex prop transformations', () => {
        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyButton}
              newComponent={Button}
              propMapping={{
                className: (value: string) => {
                  const classes = value.split(' ');
                  const props: any = {};
                  
                  if (classes.includes('btn-primary')) props.variant = 'primary';
                  if (classes.includes('btn-large')) props.size = 'lg';
                  if (classes.includes('btn-full')) props.fullWidth = true;
                  if (classes.includes('btn-loading')) props.loading = true;
                  
                  return props;
                },
              }}
              className="btn-primary btn-large btn-full"
            >
              Complex Mapped Button
            </ComponentWrapper>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        expect(button).toHaveClass('ds-button--primary');
        expect(button).toHaveClass('ds-button--lg');
        expect(button).toHaveClass('ds-button--full-width');
      });

      it('preserves event handlers during mapping', async () => {
        const handleClick = jest.fn();
        const handleMouseEnter = jest.fn();
        
        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyButton}
              newComponent={Button}
              propMapping={{
                className: (value: string) => ({ variant: 'primary' }),
              }}
              className="btn-primary"
              onClick={handleClick}
              onMouseEnter={handleMouseEnter}
            >
              Event Button
            </ComponentWrapper>
          </TestWrapper>
        );

        const button = screen.getByRole('button');
        
        await user.click(button);
        expect(handleClick).toHaveBeenCalledTimes(1);
        
        fireEvent.mouseEnter(button);
        expect(handleMouseEnter).toHaveBeenCalledTimes(1);
      });
    });

    describe('Input Prop Mapping', () => {
      it('maps legacy input props to design system props', () => {
        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyInput}
              newComponent={Input}
              propMapping={{
                className: (value: string) => {
                  const sizeMap: Record<string, string> = {
                    'input-sm': 'sm',
                    'input-lg': 'lg',
                  };
                  return { size: sizeMap[value] || 'md' };
                },
                errorClass: (value: string) => ({
                  error: value ? 'This field has an error' : undefined,
                }),
              }}
              className="input-lg"
              placeholder="Mapped input"
              errorClass="has-error"
            />
          </TestWrapper>
        );

        const input = screen.getByRole('textbox');
        expect(input).toHaveClass('ds-input--lg');
        expect(screen.getByText(/this field has an error/i)).toBeInTheDocument();
      });

      it('handles input validation prop mapping', () => {
        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacyInput}
              newComponent={Input}
              propMapping={{
                'data-required': (value: boolean) => ({ required: value }),
                'data-pattern': (value: string) => ({ pattern: value }),
                'data-min-length': (value: number) => ({ minLength: value }),
              }}
              data-required={true}
              data-pattern="[A-Za-z]+"
              data-min-length={3}
              placeholder="Validation input"
            />
          </TestWrapper>
        );

        const input = screen.getByRole('textbox');
        expect(input).toHaveAttribute('required');
        expect(input).toHaveAttribute('pattern', '[A-Za-z]+');
        expect(input).toHaveAttribute('minlength', '3');
      });
    });

    describe('Select Prop Mapping', () => {
      it('maps legacy select props to design system props', () => {
        const options = [
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' },
        ];

        render(
          <TestWrapper>
            <ComponentWrapper
              legacyComponent={LegacySelect}
              newComponent={Select}
              propMapping={{
                className: (value: string) => {
                  return { size: value.includes('select-lg') ? 'lg' : 'md' };
                },
                'data-options': (value: any[]) => ({ options: value }),
              }}
              className="select-lg"
              data-options={options}
            />
          </TestWrapper>
        );

        const select = screen.getByRole('combobox');
        expect(select).toHaveClass('ds-select--lg');
      });
    });
  });

  describe('MigrationTester', () => {
    it('tests button migration compatibility', () => {
      const migrationConfig = {
        component: 'Button',
        legacyComponent: LegacyButton,
        newComponent: Button,
        testCases: [
          {
            name: 'Primary button',
            legacyProps: { className: 'btn-primary', children: 'Primary' },
            newProps: { variant: 'primary', children: 'Primary' },
            propMapping: {
              className: (value: string) => ({ variant: 'primary' }),
            },
          },
          {
            name: 'Secondary button',
            legacyProps: { className: 'btn-secondary', children: 'Secondary' },
            newProps: { variant: 'secondary', children: 'Secondary' },
            propMapping: {
              className: (value: string) => ({ variant: 'secondary' }),
            },
          },
        ],
      };

      render(
        <TestWrapper>
          <MigrationTester config={migrationConfig} />
        </TestWrapper>
      );

      // Should render both legacy and new versions for comparison
      expect(screen.getByText(/migration test/i)).toBeInTheDocument();
      expect(screen.getAllByText('Primary')).toHaveLength(2); // Legacy and new
      expect(screen.getAllByText('Secondary')).toHaveLength(2);
    });

    it('detects visual differences in migration', () => {
      const migrationConfig = {
        component: 'Input',
        legacyComponent: LegacyInput,
        newComponent: Input,
        testCases: [
          {
            name: 'Text input',
            legacyProps: { type: 'text', placeholder: 'Enter text' },
            newProps: { type: 'text', placeholder: 'Enter text' },
            propMapping: {},
          },
        ],
        visualComparison: true,
      };

      render(
        <TestWrapper>
          <MigrationTester config={migrationConfig} />
        </TestWrapper>
      );

      // Should include visual comparison indicators
      expect(screen.getByText(/visual comparison/i)).toBeInTheDocument();
    });
  });

  describe('MigrationValidator', () => {
    it('validates migration completeness', () => {
      const migrationStatus = {
        totalComponents: 50,
        migratedComponents: 45,
        testCoverage: 85,
        accessibilityScore: 90,
        performanceScore: 88,
      };

      const results = MigrationValidator.validate(migrationStatus);

      expect(results.isComplete).toBe(false);
      expect(results.completionPercentage).toBe(90);
      expect(results.issues).toContain('Migration not complete: 5 components remaining');
      expect(results.warnings).toContain('Test coverage below 90%: 85%');
    });

    it('validates prop mapping accuracy', () => {
      const propMappings = [
        {
          component: 'Button',
          legacyProp: 'className',
          newProp: 'variant',
          mapping: (value: string) => ({ variant: value.replace('btn-', '') }),
          testCases: [
            { input: 'btn-primary', expected: { variant: 'primary' } },
            { input: 'btn-secondary', expected: { variant: 'secondary' } },
          ],
        },
      ];

      const results = MigrationValidator.validatePropMappings(propMappings);

      expect(results.isValid).toBe(true);
      expect(results.errors).toHaveLength(0);
    });

    it('detects breaking changes in prop mapping', () => {
      const propMappings = [
        {
          component: 'Button',
          legacyProp: 'className',
          newProp: 'variant',
          mapping: (value: string) => ({ variant: 'always-primary' }), // Incorrect mapping
          testCases: [
            { input: 'btn-secondary', expected: { variant: 'secondary' } },
          ],
        },
      ];

      const results = MigrationValidator.validatePropMappings(propMappings);

      expect(results.isValid).toBe(false);
      expect(results.errors).toContain('Prop mapping failed for Button.className');
    });
  });

  describe('MigrationUtils', () => {
    it('analyzes component usage patterns', () => {
      const codebase = `
        import React from 'react';
        
        function App() {
          return (
            <div>
              <button className="btn-primary">Primary</button>
              <button className="btn-secondary">Secondary</button>
              <input className="input-lg" type="text" />
              <select className="select-sm">
                <option>Option 1</option>
              </select>
            </div>
          );
        }
      `;

      const analysis = MigrationUtils.analyzeComponentUsage(codebase);

      expect(analysis.components).toEqual({
        button: 2,
        input: 1,
        select: 1,
      });

      expect(analysis.classNames).toEqual({
        'btn-primary': 1,
        'btn-secondary': 1,
        'input-lg': 1,
        'select-sm': 1,
      });
    });

    it('generates migration suggestions', () => {
      const componentUsage = {
        button: { count: 15, classes: ['btn-primary', 'btn-secondary', 'btn-danger'] },
        input: { count: 8, classes: ['input-sm', 'input-lg'] },
      };

      const suggestions = MigrationUtils.generateMigrationSuggestions(componentUsage);

      expect(suggestions).toContainEqual({
        component: 'button',
        priority: 'high',
        reason: 'High usage count (15 instances)',
        propMappings: expect.any(Object),
      });

      expect(suggestions).toContainEqual({
        component: 'input',
        priority: 'medium',
        reason: 'Medium usage count (8 instances)',
        propMappings: expect.any(Object),
      });
    });

    it('creates automated migration scripts', () => {
      const migrationConfig = {
        component: 'Button',
        propMappings: {
          className: {
            'btn-primary': { variant: 'primary' },
            'btn-secondary': { variant: 'secondary' },
          },
        },
      };

      const script = MigrationUtils.createMigrationScript(migrationConfig);

      expect(script).toContain('// Automated migration for Button component');
      expect(script).toContain('className="btn-primary"');
      expect(script).toContain('variant="primary"');
    });
  });

  describe('ComponentUsageAnalyzer', () => {
    it('analyzes component usage in codebase', () => {
      const files = [
        {
          path: 'src/components/Header.tsx',
          content: `
            import React from 'react';
            
            export const Header = () => (
              <header>
                <button className="btn-primary">Login</button>
                <button className="btn-secondary">Register</button>
              </header>
            );
          `,
        },
        {
          path: 'src/components/Form.tsx',
          content: `
            import React from 'react';
            
            export const Form = () => (
              <form>
                <input className="input-lg" type="email" />
                <input className="input-sm" type="password" />
                <button className="btn-primary" type="submit">Submit</button>
              </form>
            );
          `,
        },
      ];

      const analyzer = new ComponentUsageAnalyzer();
      const results = analyzer.analyze(files);

      expect(results.totalFiles).toBe(2);
      expect(results.componentsFound).toEqual({
        button: 3,
        input: 2,
      });

      expect(results.classUsage).toEqual({
        'btn-primary': 2,
        'btn-secondary': 1,
        'input-lg': 1,
        'input-sm': 1,
      });

      expect(results.migrationComplexity).toBe('medium');
    });

    it('identifies migration priorities', () => {
      const analyzer = new ComponentUsageAnalyzer();
      const usageData = {
        button: { count: 25, complexity: 'low' },
        input: { count: 15, complexity: 'medium' },
        select: { count: 5, complexity: 'high' },
      };

      const priorities = analyzer.calculateMigrationPriorities(usageData);

      expect(priorities[0]).toEqual({
        component: 'button',
        priority: 'high',
        score: expect.any(Number),
        reason: 'High usage, low complexity',
      });

      expect(priorities[1]).toEqual({
        component: 'input',
        priority: 'medium',
        score: expect.any(Number),
        reason: 'Medium usage, medium complexity',
      });
    });
  });

  describe('Polish Business Component Prop Mapping', () => {
    it('maps legacy currency input props', () => {
      const LegacyCurrencyInput = ({ value, currency = 'PLN', ...props }: any) => (
        <input
          type="text"
          value={value ? `${value} ${currency}` : ''}
          {...props}
        />
      );

      render(
        <TestWrapper>
          <ComponentWrapper
            legacyComponent={LegacyCurrencyInput}
            newComponent={Input} // Simplified for testing
            propMapping={{
              currency: (value: string) => ({ 
                'data-currency': value,
                placeholder: `Amount in ${value}`,
              }),
              value: (value: string) => ({
                defaultValue: value,
              }),
            }}
            currency="PLN"
            value="1000"
          />
        </TestWrapper>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('data-currency', 'PLN');
      expect(input).toHaveAttribute('placeholder', 'Amount in PLN');
    });

    it('maps legacy NIP validator props', () => {
      const LegacyNIPInput = ({ validateNIP, ...props }: any) => (
        <input
          type="text"
          pattern={validateNIP ? '[0-9]{10}' : undefined}
          {...props}
        />
      );

      render(
        <TestWrapper>
          <ComponentWrapper
            legacyComponent={LegacyNIPInput}
            newComponent={Input}
            propMapping={{
              validateNIP: (value: boolean) => ({
                pattern: value ? '[0-9]{10}' : undefined,
                'data-validate-nip': value,
              }),
            }}
            validateNIP={true}
            placeholder="Enter NIP"
          />
        </TestWrapper>
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('pattern', '[0-9]{10}');
      expect(input).toHaveAttribute('data-validate-nip', 'true');
    });

    it('maps legacy VAT rate selector props', () => {
      const LegacyVATSelect = ({ rates = [0, 5, 8, 23], ...props }: any) => (
        <select {...props}>
          {rates.map((rate: number) => (
            <option key={rate} value={rate}>
              {rate}%
            </option>
          ))}
        </select>
      );

      render(
        <TestWrapper>
          <ComponentWrapper
            legacyComponent={LegacyVATSelect}
            newComponent={Select}
            propMapping={{
              rates: (rates: number[]) => ({
                options: rates.map(rate => ({
                  value: rate.toString(),
                  label: `${rate}%`,
                })),
              }),
            }}
            rates={[0, 5, 8, 23]}
          />
        </TestWrapper>
      );

      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
      expect(screen.getByText('23%')).toBeInTheDocument();
      expect(screen.getByText('8%')).toBeInTheDocument();
    });
  });

  describe('Error Handling in Prop Mapping', () => {
    it('handles invalid prop mappings gracefully', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <ComponentWrapper
            legacyComponent={LegacyButton}
            newComponent={Button}
            propMapping={{
              invalidProp: () => {
                throw new Error('Mapping error');
              },
            }}
            invalidProp="test"
          >
            Error Test Button
          </ComponentWrapper>
        </TestWrapper>
      );

      // Should still render the button with fallback behavior
      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Prop mapping error')
      );

      consoleSpy.mockRestore();
    });

    it('provides fallback for missing prop mappings', () => {
      render(
        <TestWrapper>
          <ComponentWrapper
            legacyComponent={LegacyButton}
            newComponent={Button}
            propMapping={{}}
            className="unmapped-class"
            customProp="unmapped-value"
          >
            Fallback Button
          </ComponentWrapper>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Fallback Button');
      // Should use default variant when no mapping is provided
      expect(button).toHaveClass('ds-button');
    });
  });
});