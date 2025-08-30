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
    if (confidence >= 95) return 'text-green-600';
    if (confidence >= 90) return 'text-yellow-600';
    if (confidence >= 80) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Statistics & Analytics</h1>
        <p className="mt-2 text-gray-600">
          Detailed insights into OCR processing performance and system usage.
        </p>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <FileText className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.overview.total_documents)}</p>
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
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.overview.success_rate)}</p>
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
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.overview.average_confidence)}</p>
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
              <p className="text-2xl font-bold text-gray-900">{data.overview.average_processing_time}s</p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Type Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">File Type Distribution</h3>
          <div className="space-y-3">
            {data.file_type_distribution.map((item) => (
              <div key={item.type} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-primary-500 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-900">{item.type}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{formatNumber(item.count)}</span>
                  <span className="text-sm font-medium text-gray-900">{formatPercentage(item.percentage)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence Distribution</h3>
          <div className="space-y-3">
            {data.confidence_distribution.map((item) => (
              <div key={item.range} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-900">{item.range}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{formatNumber(item.count)}</span>
                  <span className="text-sm font-medium text-gray-900">{formatPercentage(item.percentage)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Processing Time Analysis */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Time Distribution</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {data.processing_time_distribution.map((item) => (
            <div key={item.range} className="text-center">
              <div className="text-2xl font-bold text-primary-600">{formatNumber(item.count)}</div>
              <div className="text-sm text-gray-500">{item.range}</div>
              <div className="text-xs text-gray-400">{formatPercentage(item.percentage)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Suppliers */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Suppliers by Volume</h3>
        <div className="space-y-3">
          {data.top_suppliers.map((supplier, index) => (
            <div key={supplier.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-sm font-medium text-primary-600">{index + 1}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{supplier.name}</p>
                  <p className="text-xs text-gray-500">{formatNumber(supplier.count)} documents</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-sm font-medium ${getConfidenceColor(supplier.avg_confidence)}`}>
                  {formatPercentage(supplier.avg_confidence)} avg confidence
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Trends</h3>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          {data.monthly_trends.map((month) => (
            <div key={month.month} className="text-center">
              <div className="text-lg font-bold text-primary-600">{formatNumber(month.documents)}</div>
              <div className="text-sm text-gray-500">{month.month}</div>
              <div className="text-xs text-gray-400">{formatPercentage(month.success_rate)} success</div>
            </div>
          ))}
        </div>
      </div>

      {/* Business Impact */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Invoices Created</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.overview.total_invoices_created)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Manual Review Required</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.overview.manual_review_required)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Zap className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Time Saved</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.overview.time_saved_hours)}h</p>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Performance Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Performance (Last 7 Days)</h3>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          {data.daily_stats.map((day) => (
            <div key={day.date} className="text-center">
              <div className="text-lg font-bold text-primary-600">{formatNumber(day.documents)}</div>
              <div className="text-sm text-gray-500">{new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
              <div className="text-xs text-green-600">{formatPercentage(day.success_rate)} success</div>
              <div className="text-xs text-blue-600">{formatPercentage(day.avg_confidence)} confidence</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;
