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
        return 'text-green-600';
      case 'processing':
        return 'text-yellow-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of your OCR processing activity and system performance.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <FileText className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{data.total_documents?.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-1 text-green-600">+12% from last month</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{data.success_rate}%</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <Zap className="h-4 w-4 text-green-500" />
              <span className="ml-1 text-green-600">+2.3% improvement</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg Processing Time</p>
              <p className="text-2xl font-bold text-gray-900">{data.average_processing_time}s</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-1 text-green-600">-0.5s faster</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg Confidence</p>
              <p className="text-2xl font-bold text-gray-900">{data.average_confidence}%</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-1 text-green-600">+1.2% improvement</span>
            </div>
          </div>
        </div>
      </div>

      {/* Processing Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="ml-2 text-sm text-gray-600">Completed</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.processed_documents}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-yellow-500 animate-spin" />
                <span className="ml-2 text-sm text-gray-600">Processing</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.processing_documents}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="ml-2 text-sm text-gray-600">Failed</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.failed_documents}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Activity Overview</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-blue-500" />
                <span className="ml-2 text-sm text-gray-600">Today</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.documents_today}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-green-500" />
                <span className="ml-2 text-sm text-gray-600">This Week</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.documents_this_week}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-purple-500" />
                <span className="ml-2 text-sm text-gray-600">This Month</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.documents_this_month}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Business Impact</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <DollarSign className="h-5 w-5 text-green-500" />
                <span className="ml-2 text-sm text-gray-600">Invoices Created</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.total_invoices_created}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-blue-500" />
                <span className="ml-2 text-sm text-gray-600">Manual Review</span>
              </div>
              <span className="text-sm font-medium text-gray-900">{data.manual_review_required}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="h-5 w-5 text-yellow-500" />
                <span className="ml-2 text-sm text-gray-600">Time Saved</span>
              </div>
              <span className="text-sm font-medium text-gray-900">~{Math.round(data.processed_documents * 2.5)}h</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Documents</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {recentData.map((doc) => (
            <div key={doc.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <FileText className="h-8 w-8 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{doc.original_filename}</p>
                    <p className="text-xs text-gray-500">
                      Uploaded {new Date(doc.upload_timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    {getStatusIcon(doc.status)}
                    <span className={`ml-2 text-sm font-medium ${getStatusColor(doc.status)}`}>
                      {doc.status}
                    </span>
                  </div>
                  
                  {doc.confidence_score && (
                    <div className="text-sm text-gray-500">
                      {doc.confidence_score.toFixed(1)}% confidence
                    </div>
                  )}
                  
                  {doc.processing_time && (
                    <div className="text-sm text-gray-500">
                      {doc.processing_time}s
                    </div>
                  )}
                </div>
              </div>
              
              {/* OCR Results Preview */}
              {doc.ocr_result && (
                <div className="mt-3 pl-12">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Invoice #:</span>
                        <p className="font-medium">{doc.ocr_result.invoice_number || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Amount:</span>
                        <p className="font-medium">{doc.ocr_result.total_amount || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Supplier:</span>
                        <p className="font-medium truncate">{doc.ocr_result.supplier_name || 'N/A'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Date:</span>
                        <p className="font-medium">{doc.ocr_result.invoice_date || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <Upload className="h-4 w-4 mr-2" />
            Upload Documents
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <BarChart3 className="h-4 w-4 mr-2" />
            View Statistics
          </button>
          <button className="flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
