import React from 'react';
import { useQuery } from 'react-query';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  FileText,
  DollarSign,
  Users,
  Calendar,
  Zap
} from 'lucide-react';
import axios from 'axios';
import { 
  Grid, 
  Card, 
  Typography, 
  Container, 
  Stack, 
  Flex,
  ChartCard
} from '../design-system';

const StatisticsPage = () => {
  // Fetch detailed statistics
  const { data: stats, isLoading } = useQuery(
    ['detailed-statistics'],
    async () => {
      const response = await axios.get('/api/ocr/statistics/detailed/');
      return response.data;
    },
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Mock data for development
  const mockStats = {
    overview: {
      total_documents: 1247,
      processed_documents: 1189,
      processing_documents: 23,
      failed_documents: 35,
      success_rate: 95.3,
      average_confidence: 94.2,
      average_processing_time: 2.8,
      total_invoices_created: 892,
      manual_review_required: 297,
      time_saved_hours: 2972
    },
    daily_stats: [
      { date: '2024-01-15', documents: 45, success_rate: 96.2, avg_confidence: 94.5 },
      { date: '2024-01-16', documents: 52, success_rate: 94.8, avg_confidence: 93.8 },
      { date: '2024-01-17', documents: 38, success_rate: 97.1, avg_confidence: 95.2 },
      { date: '2024-01-18', documents: 61, success_rate: 95.9, avg_confidence: 94.1 },
      { date: '2024-01-19', documents: 47, success_rate: 96.7, avg_confidence: 94.8 },
      { date: '2024-01-20', documents: 29, success_rate: 93.1, avg_confidence: 92.5 },
      { date: '2024-01-21', documents: 33, success_rate: 95.8, avg_confidence: 94.3 }
    ],
    file_type_distribution: [
      { type: 'PDF', count: 892, percentage: 71.5 },
      { type: 'JPEG', count: 234, percentage: 18.8 },
      { type: 'PNG', count: 89, percentage: 7.1 },
      { type: 'TIFF', count: 32, percentage: 2.6 }
    ],
    confidence_distribution: [
      { range: '95-100%', count: 567, percentage: 45.5 },
      { range: '90-95%', count: 423, percentage: 33.9 },
      { range: '80-90%', count: 189, percentage: 15.2 },
      { range: '70-80%', count: 45, percentage: 3.6 },
      { range: '<70%', count: 23, percentage: 1.8 }
    ],
    processing_time_distribution: [
      { range: '<2s', count: 234, percentage: 18.8 },
      { range: '2-3s', count: 567, percentage: 45.5 },
      { range: '3-5s', count: 345, percentage: 27.7 },
      { range: '5-10s', count: 89, percentage: 7.1 },
      { range: '>10s', count: 12, percentage: 1.0 }
    ],
    top_suppliers: [
      { name: 'ACME Corp Sp. z o.o.', count: 156, avg_confidence: 96.2 },
      { name: 'Tech Solutions S.A.', count: 134, avg_confidence: 94.8 },
      { name: 'Digital Services Ltd.', count: 98, avg_confidence: 93.5 },
      { name: 'Innovation Systems', count: 87, avg_confidence: 95.1 },
      { name: 'Future Technologies', count: 76, avg_confidence: 92.8 }
    ],
    monthly_trends: [
      { month: 'Jul 2023', documents: 234, success_rate: 92.1 },
      { month: 'Aug 2023', documents: 267, success_rate: 93.5 },
      { month: 'Sep 2023', documents: 298, success_rate: 94.2 },
      { month: 'Oct 2023', documents: 312, success_rate: 94.8 },
      { month: 'Nov 2023', documents: 345, success_rate: 95.1 },
      { month: 'Dec 2023', documents: 378, success_rate: 95.5 },
      { month: 'Jan 2024', documents: 401, success_rate: 95.3 }
    ]
  };

  const data = stats || mockStats;

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatPercentage = (num) => {
    return `${num.toFixed(1)}%`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 95) return 'text-success-600';
    if (confidence >= 90) return 'text-warning-600';
    if (confidence >= 80) return 'text-orange-600';
    return 'text-error-600';
  };

  return (
    <Container size="xl" className="py-6">
      <Stack gap="lg">
        {/* Header */}
        <Stack gap="sm">
          <Typography variant="h1">Statistics & Analytics</Typography>
          <Typography variant="body" color="secondary">
            Detailed insights into OCR processing performance and system usage.
          </Typography>
        </Stack>

        {/* Key Metrics Overview */}
        <Grid cols={4} gap="lg">
          <Card variant="elevated" padding="md">
            <Flex align="center" gap="md">
              <div className="p-2 bg-primary-100 rounded-lg">
                <FileText className="h-6 w-6 text-primary-600" />
              </div>
              <Stack gap="xs">
                <Typography variant="label" color="muted">Total Documents</Typography>
                <Typography variant="h3">{formatNumber(data.overview.total_documents)}</Typography>
              </Stack>
            </Flex>
          </Card>

          <Card variant="elevated" padding="md">
            <Flex align="center" gap="md">
              <div className="p-2 bg-success-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-success-600" />
              </div>
              <Stack gap="xs">
                <Typography variant="label" color="muted">Success Rate</Typography>
                <Typography variant="h3">{formatPercentage(data.overview.success_rate)}</Typography>
              </Stack>
            </Flex>
          </Card>

          <Card variant="elevated" padding="md">
            <Flex align="center" gap="md">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
              <Stack gap="xs">
                <Typography variant="label" color="muted">Avg Confidence</Typography>
                <Typography variant="h3">{formatPercentage(data.overview.average_confidence)}</Typography>
              </Stack>
            </Flex>
          </Card>

          <Card variant="elevated" padding="md">
            <Flex align="center" gap="md">
              <div className="p-2 bg-warning-100 rounded-lg">
                <Clock className="h-6 w-6 text-warning-600" />
              </div>
              <Stack gap="xs">
                <Typography variant="label" color="muted">Avg Processing Time</Typography>
                <Typography variant="h3">{data.overview.average_processing_time}s</Typography>
              </Stack>
            </Flex>
          </Card>
        </Grid>

        {/* Detailed Analytics */}
        <Grid cols={2} gap="lg">
          {/* File Type Distribution */}
          <ChartCard
            data={data.file_type_distribution.map(item => ({
              label: item.type,
              value: item.count,
              percentage: item.percentage
            }))}
            type="pie"
            title="File Type Distribution"
            showPercentages={true}
            polishFormatting={true}
            accessibilityLabel="Pie chart showing file type distribution across PDF, JPEG, PNG, and TIFF formats"
          />

          {/* Confidence Distribution */}
          <ChartCard
            data={data.confidence_distribution.map(item => ({
              label: item.range,
              value: item.count,
              percentage: item.percentage
            }))}
            type="bar"
            title="Confidence Distribution"
            showValues={true}
            polishFormatting={true}
            accessibilityLabel="Bar chart showing OCR confidence score distribution across different confidence ranges"
          />
        </Grid>

        {/* Processing Time Analysis */}
        <ChartCard
          data={data.processing_time_distribution.map(item => ({
            label: item.range,
            value: item.count,
            percentage: item.percentage
          }))}
          type="distribution"
          title="Processing Time Distribution"
          showValues={true}
          polishFormatting={true}
          accessibilityLabel="Distribution chart showing processing time ranges and document counts for each range"
        />

        {/* Top Suppliers */}
        <Card variant="elevated" padding="md">
          <Stack gap="md">
            <Typography variant="h4">Top Suppliers by Volume</Typography>
            <Stack gap="sm">
              {data.top_suppliers.map((supplier, index) => (
                <Card key={supplier.name} variant="flat" padding="sm">
                  <Flex justify="between" align="center">
                    <Flex align="center" gap="sm">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <Typography variant="bodySmall" color="primary">{index + 1}</Typography>
                      </div>
                      <Stack gap="xs">
                        <Typography variant="bodySmall">{supplier.name}</Typography>
                        <Typography variant="caption" color="muted">
                          {formatNumber(supplier.count)} documents
                        </Typography>
                      </Stack>
                    </Flex>
                    <Typography 
                      variant="bodySmall" 
                      color={supplier.avg_confidence >= 95 ? 'success' : supplier.avg_confidence >= 90 ? 'warning' : 'error'}
                    >
                      {formatPercentage(supplier.avg_confidence)} avg confidence
                    </Typography>
                  </Flex>
                </Card>
              ))}
            </Stack>
          </Stack>
        </Card>

        {/* Monthly Trends */}
        <ChartCard
          data={data.monthly_trends.map(month => ({
            label: month.month,
            value: month.documents,
            metadata: { successRate: month.success_rate }
          }))}
          type="trend"
          title="Monthly Trends"
          polishFormatting={true}
          accessibilityLabel="Trend chart showing monthly document processing volumes and success rates over time"
        />

        {/* Business Impact */}
        <Grid cols={3} gap="lg">
          <Card variant="elevated" padding="md">
            <Flex align="center" gap="sm">
              <DollarSign className="h-8 w-8 text-success-600" />
              <Stack gap="xs">
                <Typography variant="label" color="muted">Invoices Created</Typography>
                <Typography variant="h3">{formatNumber(data.overview.total_invoices_created)}</Typography>
              </Stack>
            </Flex>
          </Card>

          <Card variant="elevated" padding="md">
            <Flex align="center" gap="sm">
              <Users className="h-8 w-8 text-blue-600" />
              <Stack gap="xs">
                <Typography variant="label" color="muted">Manual Review Required</Typography>
                <Typography variant="h3">{formatNumber(data.overview.manual_review_required)}</Typography>
              </Stack>
            </Flex>
          </Card>

          <Card variant="elevated" padding="md">
            <Flex align="center" gap="sm">
              <Zap className="h-8 w-8 text-warning-600" />
              <Stack gap="xs">
                <Typography variant="label" color="muted">Time Saved</Typography>
                <Typography variant="h3">{formatNumber(data.overview.time_saved_hours)}h</Typography>
              </Stack>
            </Flex>
          </Card>
        </Grid>

        {/* Daily Performance Chart */}
        <ChartCard
          data={data.daily_stats.map(day => ({
            label: new Date(day.date).toLocaleDateString('pl-PL', { month: 'short', day: 'numeric' }),
            value: day.documents,
            metadata: { 
              successRate: day.success_rate,
              avgConfidence: day.avg_confidence 
            }
          }))}
          type="trend"
          title="Daily Performance (Last 7 Days)"
          polishFormatting={true}
          accessibilityLabel="Daily performance chart showing document processing volumes, success rates, and confidence scores for the last 7 days"
        />
      </Stack>
    </Container>
  );
};

export default StatisticsPage;
