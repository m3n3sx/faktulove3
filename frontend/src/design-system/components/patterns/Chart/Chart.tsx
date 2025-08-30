import React from 'react';
import { cn } from '../../../utils/cn';
import { BaseComponentProps } from '../../../types';
import { Typography } from '../../primitives/Typography/Typography';
import { Card } from '../Card/Card';
import { Stack } from '../../layouts/Stack/Stack';
import { Flex } from '../../layouts/Flex/Flex';
import { Grid } from '../../layouts/Grid/Grid';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  percentage?: number;
  metadata?: Record<string, any>;
}

export interface ChartProps extends BaseComponentProps {
  data: ChartDataPoint[];
  type: 'bar' | 'pie' | 'line' | 'distribution' | 'trend';
  title?: string;
  height?: number;
  showLegend?: boolean;
  showValues?: boolean;
  showPercentages?: boolean;
  responsive?: boolean;
  polishFormatting?: boolean;
  accessibilityLabel?: string;
}

// Color palette for charts using design system colors
const chartColors = [
  'rgb(59, 130, 246)',   // blue-500
  'rgb(16, 185, 129)',   // emerald-500
  'rgb(245, 158, 11)',   // amber-500
  'rgb(239, 68, 68)',    // red-500
  'rgb(139, 92, 246)',   // violet-500
  'rgb(236, 72, 153)',   // pink-500
  'rgb(20, 184, 166)',   // teal-500
  'rgb(251, 146, 60)',   // orange-500
];

// Polish number formatting utility
const formatPolishNumber = (value: number): string => {
  return new Intl.NumberFormat('pl-PL').format(value);
};

const formatPolishPercentage = (value: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100);
};

// Simple Bar Chart Component
const BarChart: React.FC<{ data: ChartDataPoint[]; height: number; showValues: boolean; polishFormatting: boolean }> = ({
  data,
  height,
  showValues,
  polishFormatting
}) => {
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="space-y-2" style={{ height }}>
      {data.map((item, index) => {
        const barHeight = (item.value / maxValue) * (height - 40);
        const color = item.color || chartColors[index % chartColors.length];
        
        return (
          <Flex key={item.label} align="center" gap="sm" className="mb-2">
            <div className="w-20 text-right">
              <Typography variant="bodySmall" color="secondary" className="truncate">
                {item.label}
              </Typography>
            </div>
            <div className="flex-1 relative">
              <div 
                className="rounded-sm transition-all duration-300 hover:opacity-80"
                style={{ 
                  backgroundColor: color,
                  height: '20px',
                  width: `${(item.value / maxValue) * 100}%`,
                  minWidth: '2px'
                }}
              />
              {showValues && (
                <Typography 
                  variant="caption" 
                  className="absolute right-2 top-0 leading-5"
                  color="primary"
                >
                  {polishFormatting ? formatPolishNumber(item.value) : item.value}
                </Typography>
              )}
            </div>
          </Flex>
        );
      })}
    </div>
  );
};

// Simple Pie Chart Component (using CSS for visual representation)
const PieChart: React.FC<{ data: ChartDataPoint[]; height: number; showPercentages: boolean; polishFormatting: boolean }> = ({
  data,
  height,
  showPercentages,
  polishFormatting
}) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  return (
    <div className="space-y-3">
      <div className="flex justify-center">
        <div 
          className="relative rounded-full border-8 border-neutral-200"
          style={{ width: height * 0.6, height: height * 0.6 }}
        >
          {/* This is a simplified representation - in a real implementation, you'd use SVG or Canvas */}
          <div className="absolute inset-0 flex items-center justify-center">
            <Typography variant="h4" color="primary">
              {polishFormatting ? formatPolishNumber(total) : total}
            </Typography>
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        {data.map((item, index) => {
          const percentage = (item.value / total) * 100;
          const color = item.color || chartColors[index % chartColors.length];
          
          return (
            <Flex key={item.label} align="center" justify="between">
              <Flex align="center" gap="sm">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <Typography variant="bodySmall">{item.label}</Typography>
              </Flex>
              <Flex align="center" gap="sm">
                <Typography variant="bodySmall" color="secondary">
                  {polishFormatting ? formatPolishNumber(item.value) : item.value}
                </Typography>
                {showPercentages && (
                  <Typography variant="bodySmall" color="primary">
                    {polishFormatting ? formatPolishPercentage(percentage) : `${percentage.toFixed(1)}%`}
                  </Typography>
                )}
              </Flex>
            </Flex>
          );
        })}
      </div>
    </div>
  );
};

// Distribution Chart Component
const DistributionChart: React.FC<{ data: ChartDataPoint[]; showValues: boolean; polishFormatting: boolean }> = ({
  data,
  showValues,
  polishFormatting
}) => {
  return (
    <Grid cols={data.length > 4 ? 4 : data.length} gap="md">
      {data.map((item, index) => {
        const color = item.color || chartColors[index % chartColors.length];
        
        return (
          <Card key={item.label} variant="flat" padding="sm" className="text-center">
            <Stack gap="xs">
              <div 
                className="w-4 h-4 rounded-full mx-auto"
                style={{ backgroundColor: color }}
              />
              <Typography variant="h4" color="primary">
                {polishFormatting ? formatPolishNumber(item.value) : item.value}
              </Typography>
              <Typography variant="caption" color="secondary">
                {item.label}
              </Typography>
              {showValues && item.percentage && (
                <Typography variant="caption" color="muted">
                  {polishFormatting ? formatPolishPercentage(item.percentage) : `${item.percentage.toFixed(1)}%`}
                </Typography>
              )}
            </Stack>
          </Card>
        );
      })}
    </Grid>
  );
};

// Trend Chart Component
const TrendChart: React.FC<{ data: ChartDataPoint[]; height: number; polishFormatting: boolean }> = ({
  data,
  height,
  polishFormatting
}) => {
  return (
    <Grid cols={data.length > 6 ? 6 : data.length} gap="sm">
      {data.map((item, index) => (
        <div key={item.label} className="text-center">
          <Typography variant="h5" color="primary">
            {polishFormatting ? formatPolishNumber(item.value) : item.value}
          </Typography>
          <Typography variant="caption" color="secondary">
            {item.label}
          </Typography>
          {item.metadata?.successRate && (
            <Typography variant="caption" color="success">
              {polishFormatting ? formatPolishPercentage(item.metadata.successRate) : `${item.metadata.successRate.toFixed(1)}%`} success
            </Typography>
          )}
        </div>
      ))}
    </Grid>
  );
};

export const Chart: React.FC<ChartProps> = ({
  data,
  type,
  title,
  height = 300,
  showLegend = true,
  showValues = true,
  showPercentages = false,
  responsive = true,
  polishFormatting = true,
  accessibilityLabel,
  className,
  testId = 'chart',
  ...props
}) => {
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <BarChart 
            data={data} 
            height={height} 
            showValues={showValues}
            polishFormatting={polishFormatting}
          />
        );
      case 'pie':
        return (
          <PieChart 
            data={data} 
            height={height} 
            showPercentages={showPercentages}
            polishFormatting={polishFormatting}
          />
        );
      case 'distribution':
        return (
          <DistributionChart 
            data={data} 
            showValues={showValues}
            polishFormatting={polishFormatting}
          />
        );
      case 'trend':
        return (
          <TrendChart 
            data={data} 
            height={height}
            polishFormatting={polishFormatting}
          />
        );
      case 'line':
      default:
        // For now, fall back to bar chart for line charts
        return (
          <BarChart 
            data={data} 
            height={height} 
            showValues={showValues}
            polishFormatting={polishFormatting}
          />
        );
    }
  };

  return (
    <div
      className={cn(
        'chart-container',
        responsive && 'w-full',
        className
      )}
      data-testid={testId}
      role="img"
      aria-label={accessibilityLabel || `${type} chart showing ${title || 'data'}`}
      {...props}
    >
      {title && (
        <div className="mb-4">
          <Typography variant="h4">{title}</Typography>
        </div>
      )}
      
      <div className="chart-content">
        {renderChart()}
      </div>
    </div>
  );
};

// Chart Card wrapper component for consistent styling
export interface ChartCardProps extends ChartProps {
  cardVariant?: 'default' | 'outlined' | 'elevated' | 'flat';
  cardPadding?: 'sm' | 'md' | 'lg';
}

export const ChartCard: React.FC<ChartCardProps> = ({
  cardVariant = 'elevated',
  cardPadding = 'md',
  ...chartProps
}) => {
  return (
    <Card variant={cardVariant} padding={cardPadding}>
      <Chart {...chartProps} />
    </Card>
  );
};

Chart.displayName = 'Chart';
ChartCard.displayName = 'ChartCard';