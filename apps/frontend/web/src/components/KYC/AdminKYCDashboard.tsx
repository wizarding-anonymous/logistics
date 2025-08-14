import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Alert, AlertDescription } from '../ui/alert';
import { Textarea } from '../ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  Download, 
  Search,
  Filter,
  RefreshCw,
  AlertTriangle,
  FileText,
  Users,
  TrendingUp,
  Shield
} from 'lucide-react';

interface KYCDocument {
  id: string;
  document_type: string;
  file_name: string;
  file_size: number;
  status: 'pending' | 'approved' | 'rejected';
  rejection_reason?: string;
  virus_scan_status: string;
  validation_status: string;
  validation_errors?: string;
  uploaded_at: string;
  reviewed_at?: string;
  user: {
    id: string;
    email: string;
    roles: string[];
  };
}

interface KYCStatistics {
  document_status: Record<string, number>;
  user_stats: {
    total_users: number;
    verified_users: number;
    pending_users: number;
    rejected_users: number;
  };
}

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  inn: 'ИНН',
  ogrn: 'ОГРН',
  business_license: 'Лицензия',
  passport: 'Паспорт',
  insurance_certificate: 'Страховой сертификат',
  bank_details: 'Банковские реквизиты'
};

const STATUS_FILTERS = [
  { value: '', label: 'Все документы' },
  { value: 'pending', label: 'На рассмотрении' },
  { value: 'approved', label: 'Одобренные' },
  { value: 'rejected', label: 'Отклоненные' },
  { value: 'validation_failed', label: 'Ошибки валидации' },
  { value: 'virus_infected', label: 'Заражены вирусом' }
];

export const AdminKYCDashboard: React.FC = () => {
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [statistics, setStatistics] = useState<KYCStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);
  
  // Review modal
  const [reviewingDocument, setReviewingDocument] = useState<KYCDocument | null>(null);
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [documentsResponse, statsResponse] = await Promise.all([
        fetch(`/api/v1/admin/kyc/documents?status=${statusFilter}&limit=${itemsPerPage}&offset=${(currentPage - 1) * itemsPerPage}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }),
        fetch('/api/v1/admin/kyc/statistics', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
      ]);

      if (!documentsResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to fetch KYC data');
      }

      const documentsData = await documentsResponse.json();
      const statsData = await statsResponse.json();

      setDocuments(documentsData);
      setStatistics(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter, currentPage]);

  const handleReview = async () => {
    if (!reviewingDocument || !reviewAction) return;

    try {
      setReviewLoading(true);

      const endpoint = reviewAction === 'approve' 
        ? `/api/v1/admin/kyc/documents/${reviewingDocument.id}/approve`
        : `/api/v1/admin/kyc/documents/${reviewingDocument.id}/reject`;

      const body = reviewAction === 'reject' 
        ? { reason: rejectionReason }
        : undefined;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: body ? JSON.stringify(body) : undefined
      });

      if (!response.ok) {
        throw new Error('Failed to review document');
      }

      // Refresh data
      await fetchData();
      
      // Close modal
      setReviewingDocument(null);
      setReviewAction(null);
      setRejectionReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to review document');
    } finally {
      setReviewLoading(false);
    }
  };

  const downloadDocument = async (documentId: string, fileName: string) => {
    try {
      const response = await fetch(`/api/v1/admin/kyc/documents/${documentId}/download-url`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get download URL');
      }

      const { download_url } = await response.json();
      window.open(download_url, '_blank');
    } catch (err) {
      console.error('Failed to download document:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="success" className="bg-green-100 text-green-800">Одобрено</Badge>;
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">На рассмотрении</Badge>;
      case 'rejected':
        return <Badge variant="destructive" className="bg-red-100 text-red-800">Отклонено</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const filteredDocuments = documents.filter(doc => 
    searchQuery === '' || 
    doc.user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading && !documents.length) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin mr-2" />
        Загрузка данных...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Всего пользователей</p>
                  <p className="text-2xl font-bold">{statistics.user_stats.total_users}</p>
                </div>
                <Users className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Верифицированы</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.user_stats.verified_users}</p>
                </div>
                <Shield className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">На рассмотрении</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.user_stats.pending_users}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Отклонены</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.user_stats.rejected_users}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Управление документами KYC</CardTitle>
          <CardDescription>
            Просмотр и модерация загруженных документов
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Поиск по email или имени файла..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Фильтр по статусу" />
              </SelectTrigger>
              <SelectContent>
                {STATUS_FILTERS.map(filter => (
                  <SelectItem key={filter.value} value={filter.value}>
                    {filter.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Обновить
            </Button>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Documents Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Пользователь</TableHead>
                  <TableHead>Документ</TableHead>
                  <TableHead>Тип</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead>Валидация</TableHead>
                  <TableHead>Загружен</TableHead>
                  <TableHead>Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocuments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                      <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Документы не найдены</p>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDocuments.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{doc.user.email}</p>
                          <p className="text-sm text-gray-500">
                            {doc.user.roles.join(', ')}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{doc.file_name}</p>
                          <p className="text-sm text-gray-500">
                            {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        {DOCUMENT_TYPE_LABELS[doc.document_type] || doc.document_type}
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(doc.status)}
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <Badge 
                            variant={doc.virus_scan_status === 'clean' ? 'success' : 
                                   doc.virus_scan_status === 'infected' ? 'destructive' : 'secondary'}
                            className="text-xs"
                          >
                            {doc.virus_scan_status === 'clean' ? 'Чистый' : 
                             doc.virus_scan_status === 'infected' ? 'Заражен' : 'Проверяется'}
                          </Badge>
                          <Badge 
                            variant={doc.validation_status === 'valid' ? 'success' : 
                                   doc.validation_status === 'invalid' ? 'destructive' : 'secondary'}
                            className="text-xs"
                          >
                            {doc.validation_status === 'valid' ? 'Валидный' : 
                             doc.validation_status === 'invalid' ? 'Невалидный' : 'Проверяется'}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(doc.uploaded_at).toLocaleDateString('ru-RU')}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadDocument(doc.id, doc.file_name)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          {doc.status === 'pending' && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setReviewingDocument(doc);
                                  setReviewAction('approve');
                                }}
                                className="text-green-600 hover:text-green-700"
                              >
                                <CheckCircle className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setReviewingDocument(doc);
                                  setReviewAction('reject');
                                }}
                                className="text-red-600 hover:text-red-700"
                              >
                                <XCircle className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Review Modal */}
      <Dialog open={!!reviewingDocument} onOpenChange={() => setReviewingDocument(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {reviewAction === 'approve' ? 'Одобрить документ' : 'Отклонить документ'}
            </DialogTitle>
            <DialogDescription>
              {reviewingDocument && (
                <>
                  Документ: {reviewingDocument.file_name}<br />
                  Пользователь: {reviewingDocument.user.email}<br />
                  Тип: {DOCUMENT_TYPE_LABELS[reviewingDocument.document_type] || reviewingDocument.document_type}
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          {reviewAction === 'reject' && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Причина отклонения</label>
              <Textarea
                placeholder="Укажите причину отклонения документа..."
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                rows={3}
              />
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setReviewingDocument(null)}
              disabled={reviewLoading}
            >
              Отмена
            </Button>
            <Button
              onClick={handleReview}
              disabled={reviewLoading || (reviewAction === 'reject' && !rejectionReason.trim())}
              variant={reviewAction === 'approve' ? 'default' : 'destructive'}
            >
              {reviewLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin mr-2" />
              ) : reviewAction === 'approve' ? (
                <CheckCircle className="h-4 w-4 mr-2" />
              ) : (
                <XCircle className="h-4 w-4 mr-2" />
              )}
              {reviewAction === 'approve' ? 'Одобрить' : 'Отклонить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};