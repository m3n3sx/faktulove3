import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  FileText, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Trash2,
  CheckCircle,
  Clock,
  AlertCircle,
  Calendar,
  DollarSign
} from 'lucide-react';
import axios from 'axios';
import { Button, Grid, Select, Input } from '../design-system';

const DocumentsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

  // Fetch documents with filters
  const { data: documents, isLoading } = useQuery(
    ['documents', searchTerm, statusFilter, dateFilter],
    async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (dateFilter !== 'all') params.append('date_filter', dateFilter);
      
      const response = await axios.get(`/api/ocr/documents/?${params.toString()}`);
      return response.data;
    },
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  );

  // Mock data for development
  const mockDocuments = {
    results: [
      {
        id: 1,
        original_filename: 'invoice_2024_001.pdf',
        status: 'completed',
        confidence_score: 96.5,
        processing_time: 2.3,
        upload_timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        file_size: 1024000,
        ocr_result: {
          invoice_number: 'FV/2024/001',
          total_amount: '1230.00',
          supplier_name: 'ACME Corp Sp. z o.o.',
          supplier_nip: '1234567890',
          buyer_name: 'Test Company Sp. z o.o.',
          buyer_nip: '0987654321',
          invoice_date: '2024-01-15',
          due_date: '2024-02-15',
          currency: 'PLN',
          net_amount: '1000.00',
          vat_amount: '230.00',
          line_items: [
            {
              description: 'Web Development Services',
              quantity: '1',
              unit_price: '1000.00',
              net_amount: '1000.00',
              vat_rate: '23%'
            }
          ]
        }
      },
      {
        id: 2,
        original_filename: 'receipt_restaurant.jpg',
        status: 'processing',
        confidence_score: null,
        processing_time: null,
        upload_timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        file_size: 512000,
        ocr_result: null
      },
      {
        id: 3,
        original_filename: 'invoice_2024_002.pdf',
        status: 'completed',
        confidence_score: 89.2,
        processing_time: 3.1,
        upload_timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        file_size: 2048000,
        ocr_result: {
          invoice_number: 'FV/2024/002',
          total_amount: '567.89',
          supplier_name: 'Tech Solutions S.A.',
          supplier_nip: '1112223333',
          buyer_name: 'Another Company Ltd.',
          buyer_nip: '4445556666',
          invoice_date: '2024-01-14',
          due_date: '2024-02-14',
          currency: 'PLN',
          net_amount: '461.70',
          vat_amount: '106.19',
          line_items: [
            {
              description: 'Software License',
              quantity: '1',
              unit_price: '461.70',
              net_amount: '461.70',
              vat_rate: '23%'
            }
          ]
        }
      }
    ],
    count: 3,
    next: null,
    previous: null
  };

  const data = documents || mockDocuments;

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

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const viewDocument = (doc) => {
    console.log('Viewing document:', doc);
    // In a real app, this would open a modal or navigate to detail page
  };

  const downloadDocument = (doc) => {
    console.log('Downloading document:', doc);
    // In a real app, this would trigger a download
  };

  const deleteDocument = (docId) => {
    console.log('Deleting document:', docId);
    // In a real app, this would show confirmation and delete
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <p className="mt-2 text-gray-600">
          View and manage all uploaded documents and their OCR processing results.
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-6 rounded-md-lg shadow-sm">
        <Grid cols={4} gap="md">
          {/* Search */}
          <Input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            icon={<Search className="h-4 w-4" />}
            iconPosition="start"
          />

          {/* Status Filter */}
          <Select
            value={statusFilter}
            onChange={(value) => setStatusFilter(value)}
            placeholder="All Status"
            options={[
              { value: 'all', label: 'All Status' },
              { value: 'completed', label: 'Completed' },
              { value: 'processing', label: 'Processing' },
              { value: 'failed', label: 'Failed' },
              { value: 'pending', label: 'Pending' }
            ]}
          />

          {/* Date Filter */}
          <Select
            value={dateFilter}
            onChange={(value) => setDateFilter(value)}
            placeholder="All Time"
            options={[
              { value: 'all', label: 'All Time' },
              { value: 'today', label: 'Today' },
              { value: 'week', label: 'This Week' },
              { value: 'month', label: 'This Month' },
              { value: 'year', label: 'This Year' }
            ]}
          />

          {/* Results Count */}
          <div className="flex items-center justify-end text-sm text-gray-500">
            {data.count} document{data.count !== 1 ? 's' : ''} found
          </div>
        </Grid>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-md-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Document List</h3>
        </div>
        
        {isLoading ? (
          <div className="p-6 text-center">
            <Clock className="h-8 w-8 text-gray-400 animate-spin mx-auto" />
            <p className="mt-2 text-gray-500">Loading documents...</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {data.results.map((doc) => (
              <div key={doc.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <FileText className="h-10 w-10 text-gray-400 mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-lg font-medium text-gray-900">{doc.original_filename}</h4>
                        <div className="flex items-center">
                          {getStatusIcon(doc.status)}
                          <span className={`ml-1 text-sm font-medium ${getStatusColor(doc.status)}`}>
                            {doc.status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>•</span>
                        <span>Uploaded {new Date(doc.upload_timestamp).toLocaleString()}</span>
                        {doc.processing_time && (
                          <>
                            <span>•</span>
                            <span>Processed in {doc.processing_time}s</span>
                          </>
                        )}
                        {doc.confidence_score && (
                          <>
                            <span>•</span>
                            <span>{doc.confidence_score.toFixed(1)}% confidence</span>
                          </>
                        )}
                      </div>

                      {/* OCR Results Summary */}
                      {doc.ocr_result && (
                        <div className="mt-4 bg-gray-50 rounded-md-lg p-4">
                          <h5 className="text-sm font-medium text-gray-900 mb-3">Extracted Data</h5>
                          <Grid cols={2} gap="md">
                            <div>
                              <span className="text-gray-500">Invoice #:</span>
                              <p className="font-medium">{doc.ocr_result.invoice_number || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Total Amount:</span>
                              <p className="font-medium">{doc.ocr_result.total_amount} {doc.ocr_result.currency}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Supplier:</span>
                              <p className="font-medium truncate">{doc.ocr_result.supplier_name || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Date:</span>
                              <p className="font-medium">{doc.ocr_result.invoice_date || 'N/A'}</p>
                            </div>
                          </Grid>
                          
                          {/* Detailed Information */}
                          <Grid cols={4} gap="sm">
                            <div>
                              <span className="text-gray-500">Supplier NIP:</span>
                              <p className="font-medium">{doc.ocr_result.supplier_nip || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Buyer NIP:</span>
                              <p className="font-medium">{doc.ocr_result.buyer_nip || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Net Amount:</span>
                              <p className="font-medium">{doc.ocr_result.net_amount} {doc.ocr_result.currency}</p>
                            </div>
                            <div>
                              <span className="text-gray-500">VAT Amount:</span>
                              <p className="font-medium">{doc.ocr_result.vat_amount} {doc.ocr_result.currency}</p>
                            </div>
                          </Grid>

                          {/* Line Items */}
                          {doc.ocr_result.line_items && doc.ocr_result.line_items.length > 0 && (
                            <div className="mt-4">
                              <h6 className="text-sm font-medium text-gray-900 mb-2">Line Items</h6>
                              <div className="bg-white rounded-md border">
                                {doc.ocr_result.line_items.map((item, index) => (
                                  <div key={index} className="p-3 border-b last:border-b-0">
                                    <div className="flex justify-between items-start">
                                      <div className="flex-1">
                                        <p className="font-medium">{item.description}</p>
                                        <p className="text-sm text-gray-500">
                                          Qty: {item.quantity} × {item.unit_price} {doc.ocr_result.currency}
                                        </p>
                                      </div>
                                      <div className="text-right">
                                        <p className="font-medium">{item.net_amount} {doc.ocr_result.currency}</p>
                                        <p className="text-sm text-gray-500">VAT: {item.vat_rate}</p>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => viewDocument(doc)}
                      aria-label="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => downloadDocument(doc)}
                      aria-label="Download"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => deleteDocument(doc.id)}
                      aria-label="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {(data.next || data.previous) && (
        <div className="bg-white px-6 py-3 rounded-md-lg shadow-sm">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Showing {data.results.length} of {data.count} documents
            </div>
            <div className="flex space-x-2">
              <Button
                disabled={!data.previous}
                variant="secondary"
              >
                Previous
              </Button>
              <Button
                disabled={!data.next}
                variant="secondary"
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;
