import React from 'react';
import { useQuery } from 'react-query';
import { 
  FileText, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  TrendingUp, 
  Zap,
  BarChart3,
  Calendar,
  DollarSign,
  Users,
  Upload,
  Settings
} from 'lucide-react';
import axios from 'axios';
import { 
  Button, 
  Grid, 
  Card, 
  Typography, 
  Badge, 
  Container,
  Stack,
  Flex
} from '../design-system';

const Dashboard = () => {
  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading } = useQuery(
    ['dashboard-stats'],
    async () => {
      const response = await axios.get('/api/ocr/statistics/');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Fetch recent documents
  const { data: recentDocs, isLoading: docsLoading } = useQuery(
    ['recent-documents'],
    async () => {
      const response = await axios.get('/api/ocr/documents/?limit=5');
      return response.data;
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  );

  // Mock data for development
  const mockStats = {
    total_documents: 1247,
    processed_documents: 1189,
    processing_documents: 23,
    failed_documents: 35,
    average_confidence: 94.2,
    average_processing_time: 2.8,
    total_invoices_created: 892,
    manual_review_required: 297,
    success_rate: 95.3,
    documents_today: 45,
    documents_this_week: 234,
    documents_this_month: 892
  };

  const mockRecentDocs = [
    {
      id: 1,
      original_filename: 'invoice_2024_001.pdf',
      status: 'completed',
      confidence_score: 96.5,
      processing_time: 2.3,
      upload_timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      ocr_result: {
        invoice_number: 'FV/2024/001',
        total_amount: '1230.00',
        supplier_name: 'ACME Corp Sp. z o.o.',
        invoice_date: '2024-01-15'
      }
    },
    {
      id: 2,
      original_filename: 'receipt_restaurant.jpg',
      status: 'processing',
      confidence_score: null,
      processing_time: null,
      upload_timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      ocr_result: null
    },
    {
      id: 3,
      original_filename: 'invoice_2024_002.pdf',
      status: 'completed',
      confidence_score: 89.2,
      processing_time: 3.1,
      upload_timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      ocr_result: {
        invoice_number: 'FV/2024/002',
        total_amount: '567.89',
        supplier_name: 'Tech Solutions S.A.',
        invoice_date: '2024-01-14'
      }
    }
  ];

  const data = stats || mockStats;
  const recentData = recentDocs?.results || mockRecentDocs;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-success-600';
      case 'processing':
        return 'text-warning-600';
      case 'failed':
        return 'text-error-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <Container size="xl" className="py-6">
      <Stack gap="lg">
        {/* Header */}
        <Stack gap="sm">
          <Typography variant="h1">Dashboard</Typography>
          <Typography variant="body" color="secondary">
            Overview of your OCR processing activity and system performance.
          </Typography>
        </Stack>

        {/* Key Metrics */}
        <Grid cols={4} gap="lg">
          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Flex align="center" gap="md">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <FileText className="h-6 w-6 text-primary-600" />
                </div>
                <Stack gap="xs">
                  <Typography variant="label" color="muted">Total Documents</Typography>
                  <Typography variant="h3">{data.total_documents?.toLocaleString()}</Typography>
                </Stack>
              </Flex>
              <Flex align="center" gap="xs">
                <TrendingUp className="h-4 w-4 text-success-500" />
                <Typography variant="bodySmall" color="success">+12% from last month</Typography>
              </Flex>
            </Stack>
          </Card>

          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Flex align="center" gap="md">
                <div className="p-2 bg-success-100 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-success-600" />
                </div>
                <Stack gap="xs">
                  <Typography variant="label" color="muted">Success Rate</Typography>
                  <Typography variant="h3">{data.success_rate}%</Typography>
                </Stack>
              </Flex>
              <Flex align="center" gap="xs">
                <Zap className="h-4 w-4 text-success-500" />
                <Typography variant="bodySmall" color="success">+2.3% improvement</Typography>
              </Flex>
            </Stack>
          </Card>

          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Flex align="center" gap="md">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <Clock className="h-6 w-6 text-warning-600" />
                </div>
                <Stack gap="xs">
                  <Typography variant="label" color="muted">Avg Processing Time</Typography>
                  <Typography variant="h3">{data.average_processing_time}s</Typography>
                </Stack>
              </Flex>
              <Flex align="center" gap="xs">
                <TrendingUp className="h-4 w-4 text-success-500" />
                <Typography variant="bodySmall" color="success">-0.5s faster</Typography>
              </Flex>
            </Stack>
          </Card>

          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Flex align="center" gap="md">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <Stack gap="xs">
                  <Typography variant="label" color="muted">Avg Confidence</Typography>
                  <Typography variant="h3">{data.average_confidence}%</Typography>
                </Stack>
              </Flex>
              <Flex align="center" gap="xs">
                <TrendingUp className="h-4 w-4 text-success-500" />
                <Typography variant="bodySmall" color="success">+1.2% improvement</Typography>
              </Flex>
            </Stack>
          </Card>
        </Grid>

        {/* Processing Status */}
        <Grid cols={3} gap="lg">
          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Typography variant="h4">Processing Status</Typography>
              <Stack gap="sm">
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <CheckCircle className="h-5 w-5 text-success-500" />
                    <Typography variant="bodySmall" color="secondary">Completed</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.processed_documents}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Clock className="h-5 w-5 text-warning-500 animate-spin" />
                    <Typography variant="bodySmall" color="secondary">Processing</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.processing_documents}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <AlertCircle className="h-5 w-5 text-error-500" />
                    <Typography variant="bodySmall" color="secondary">Failed</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.failed_documents}</Typography>
                </Flex>
              </Stack>
            </Stack>
          </Card>

          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Typography variant="h4">Activity Overview</Typography>
              <Stack gap="sm">
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Calendar className="h-5 w-5 text-blue-500" />
                    <Typography variant="bodySmall" color="secondary">Today</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.documents_today}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Calendar className="h-5 w-5 text-success-500" />
                    <Typography variant="bodySmall" color="secondary">This Week</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.documents_this_week}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Calendar className="h-5 w-5 text-purple-500" />
                    <Typography variant="bodySmall" color="secondary">This Month</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.documents_this_month}</Typography>
                </Flex>
              </Stack>
            </Stack>
          </Card>

          <Card variant="elevated" padding="md">
            <Stack gap="md">
              <Typography variant="h4">Business Impact</Typography>
              <Stack gap="sm">
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <DollarSign className="h-5 w-5 text-success-500" />
                    <Typography variant="bodySmall" color="secondary">Invoices Created</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.total_invoices_created}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Users className="h-5 w-5 text-blue-500" />
                    <Typography variant="bodySmall" color="secondary">Manual Review</Typography>
                  </Flex>
                  <Typography variant="bodySmall">{data.manual_review_required}</Typography>
                </Flex>
                <Flex justify="between" align="center">
                  <Flex align="center" gap="sm">
                    <Zap className="h-5 w-5 text-warning-500" />
                    <Typography variant="bodySmall" color="secondary">Time Saved</Typography>
                  </Flex>
                  <Typography variant="bodySmall">~{Math.round(data.processed_documents * 2.5)}h</Typography>
                </Flex>
              </Stack>
            </Stack>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Card variant="elevated" padding="none">
          <Card.Header>
            <Typography variant="h4">Recent Documents</Typography>
          </Card.Header>
          <Card.Body className="p-0">
            <Stack gap="none">
              {recentData.map((doc, index) => (
                <div key={doc.id} className={`px-6 py-4 ${index < recentData.length - 1 ? 'border-b border-neutral-200' : ''}`}>
                  <Flex justify="between" align="center" className="mb-3">
                    <Flex align="center" gap="md">
                      <FileText className="h-8 w-8 text-neutral-400" />
                      <Stack gap="xs">
                        <Typography variant="bodySmall">{doc.original_filename}</Typography>
                        <Typography variant="caption" color="muted">
                          Uploaded {new Date(doc.upload_timestamp).toLocaleString()}
                        </Typography>
                      </Stack>
                    </Flex>
                    
                    <Flex align="center" gap="md">
                      <Flex align="center" gap="xs">
                        {getStatusIcon(doc.status)}
                        <Badge 
                          variant={
                            doc.status === 'completed' ? 'success' : 
                            doc.status === 'processing' ? 'warning' : 
                            doc.status === 'failed' ? 'error' : 'default'
                          }
                          size="sm"
                        >
                          {doc.status}
                        </Badge>
                      </Flex>
                      
                      {doc.confidence_score && (
                        <Typography variant="caption" color="muted">
                          {doc.confidence_score.toFixed(1)}% confidence
                        </Typography>
                      )}
                      
                      {doc.processing_time && (
                        <Typography variant="caption" color="muted">
                          {doc.processing_time}s
                        </Typography>
                      )}
                    </Flex>
                  </Flex>
                  
                  {/* OCR Results Preview */}
                  {doc.ocr_result && (
                    <div className="ml-12">
                      <Card variant="flat" padding="sm">
                        <Grid cols={2} gap="md">
                          <Stack gap="xs">
                            <Typography variant="caption" color="muted">Invoice #:</Typography>
                            <Typography variant="bodySmall">{doc.ocr_result.invoice_number || 'N/A'}</Typography>
                          </Stack>
                          <Stack gap="xs">
                            <Typography variant="caption" color="muted">Amount:</Typography>
                            <Typography variant="currencyAmount">{doc.ocr_result.total_amount || 'N/A'}</Typography>
                          </Stack>
                          <Stack gap="xs">
                            <Typography variant="caption" color="muted">Supplier:</Typography>
                            <Typography variant="bodySmall" className="truncate">{doc.ocr_result.supplier_name || 'N/A'}</Typography>
                          </Stack>
                          <Stack gap="xs">
                            <Typography variant="caption" color="muted">Date:</Typography>
                            <Typography variant="dateFormat">{doc.ocr_result.invoice_date || 'N/A'}</Typography>
                          </Stack>
                        </Grid>
                      </Card>
                    </div>
                  )}
                </div>
              ))}
            </Stack>
          </Card.Body>
        </Card>

        {/* Quick Actions */}
        <Card variant="elevated" padding="md">
          <Stack gap="md">
            <Typography variant="h4">Quick Actions</Typography>
            <Grid cols={3} gap="md">
              <Button variant="primary" startIcon={<Upload className="h-4 w-4" />}>
                Upload Documents
              </Button>
              <Button variant="secondary" startIcon={<BarChart3 className="h-4 w-4" />}>
                View Statistics
              </Button>
              <Button variant="secondary" startIcon={<Settings className="h-4 w-4" />}>
                Settings
              </Button>
            </Grid>
          </Stack>
        </Card>
      </Stack>
    </Container>
  );
};

export default Dashboard;
