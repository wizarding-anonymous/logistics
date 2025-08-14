import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  CheckCircle, 
  Clock, 
  XCircle, 
  AlertTriangle, 
  FileText, 
  Download,
  RefreshCw,
  Shield
} from 'lucide-react';

interface KYCDocument {
  id: string;
  document_type: string;
  file_name: string;
  status: 'pending' | 'approved' | 'rejected';
  rejection_reason?: string;
  virus_scan_status: string;
  validation_status: string;
  validation_errors?: string;
  uploaded_at: string;
  reviewed_at?: string;
}

interface KYCStatusData {
  status: 'not_started' | 'pending' | 'approved' | 'rejected';
  required_documents: string[];
  submitted_documents: string[];
  approved_documents: string[];
  rejected_documents: string[];
}

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  inn: 'ИНН',
  ogrn: 'ОГРН',
  business_license: 'Лицензия',
  passport: 'Паспорт',
  insurance_certificate: 'Страховой сертификат',
  bank_details: 'Банковские реквизиты'
};

export const KYCStatus: React.FC = () => {
  const [kycStatus, setKycStatus] = useState<KYCStatusData | null>(null);
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKYCData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statusResponse, documentsResponse] = await Promise.all([
        fetch('/api/v1/auth/users/me/kyc-status', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }),
        fetch('/api/v1/auth/users/me/kyc-documents', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
      ]);

      if (!statusResponse.ok || !documentsResponse.ok) {
        throw new Error('Failed to fetch KYC data');
      }

      const statusData = await statusResponse.json();
      const documentsData = await documentsResponse.json();

      setKycStatus(statusData);
      setDocuments(documentsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load KYC data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKYCData();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="success" className="bg-green-100 text-green-800">Одобрено</Badge>;
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">На рассмотрении</Badge>;
      case 'rejected':
        return <Badge variant="destructive" className="bg-red-100 text-red-800">Отклонено</Badge>;
      default:
        return <Badge variant="outline">Не начато</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getOverallStatusMessage = () => {
    if (!kycStatus) return '';

    switch (kycStatus.status) {
      case 'approved':
        return 'Ваша организация успешно верифицирована! Теперь вы можете предоставлять услуги на платформе.';
      case 'pending':
        return 'Ваши документы находятся на рассмотрении. Мы уведомим вас о результатах проверки.';
      case 'rejected':
        return 'Некоторые документы были отклонены. Пожалуйста, загрузите исправленные версии.';
      default:
        return 'Для начала работы на платформе необходимо пройти верификацию организации.';
    }
  };

  const downloadDocument = async (documentId: string, fileName: string) => {
    try {
      const response = await fetch(`/api/v1/auth/users/me/kyc-documents/${documentId}/download-url`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get download URL');
      }

      const { download_url } = await response.json();
      
      // Open download URL in new tab
      window.open(download_url, '_blank');
    } catch (err) {
      console.error('Failed to download document:', err);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <RefreshCw className="h-6 w-6 animate-spin mr-2" />
          Загрузка статуса KYC...
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Ошибка загрузки данных: {error}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchKYCData}
                className="ml-2"
              >
                Повторить
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-500" />
              <div>
                <CardTitle>Статус верификации KYC</CardTitle>
                <CardDescription>Проверка документов организации</CardDescription>
              </div>
            </div>
            {kycStatus && getStatusBadge(kycStatus.status)}
          </div>
        </CardHeader>
        <CardContent>
          <Alert className={`
            ${kycStatus?.status === 'approved' ? 'border-green-200 bg-green-50' : ''}
            ${kycStatus?.status === 'rejected' ? 'border-red-200 bg-red-50' : ''}
            ${kycStatus?.status === 'pending' ? 'border-yellow-200 bg-yellow-50' : ''}
          `}>
            <AlertDescription className="text-sm">
              {getOverallStatusMessage()}
            </AlertDescription>
          </Alert>

          {/* Progress Summary */}
          {kycStatus && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {kycStatus.required_documents.length}
                </div>
                <div className="text-sm text-gray-600">Требуется</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {kycStatus.submitted_documents.length}
                </div>
                <div className="text-sm text-gray-600">Подано</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {kycStatus.approved_documents.length}
                </div>
                <div className="text-sm text-gray-600">Одобрено</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {kycStatus.rejected_documents.length}
                </div>
                <div className="text-sm text-gray-600">Отклонено</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Загруженные документы</CardTitle>
            <Button variant="outline" size="sm" onClick={fetchKYCData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Обновить
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Документы не загружены</p>
              <p className="text-sm">Загрузите необходимые документы для верификации</p>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => (
                <div key={doc.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(doc.status)}
                      <div>
                        <h4 className="font-medium">
                          {DOCUMENT_TYPE_LABELS[doc.document_type] || doc.document_type}
                        </h4>
                        <p className="text-sm text-gray-500">{doc.file_name}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(doc.status)}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => downloadDocument(doc.id, doc.file_name)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Загружено: {new Date(doc.uploaded_at).toLocaleDateString('ru-RU')}</p>
                    {doc.reviewed_at && (
                      <p>Рассмотрено: {new Date(doc.reviewed_at).toLocaleDateString('ru-RU')}</p>
                    )}
                  </div>

                  {/* Validation Status */}
                  <div className="mt-2 flex space-x-4 text-xs">
                    <span className={`
                      px-2 py-1 rounded
                      ${doc.virus_scan_status === 'clean' ? 'bg-green-100 text-green-800' : 
                        doc.virus_scan_status === 'infected' ? 'bg-red-100 text-red-800' : 
                        'bg-gray-100 text-gray-800'}
                    `}>
                      Антивирус: {doc.virus_scan_status === 'clean' ? 'Чистый' : 
                                 doc.virus_scan_status === 'infected' ? 'Заражен' : 'Проверяется'}
                    </span>
                    <span className={`
                      px-2 py-1 rounded
                      ${doc.validation_status === 'valid' ? 'bg-green-100 text-green-800' : 
                        doc.validation_status === 'invalid' ? 'bg-red-100 text-red-800' : 
                        'bg-gray-100 text-gray-800'}
                    `}>
                      Валидация: {doc.validation_status === 'valid' ? 'Валидный' : 
                                 doc.validation_status === 'invalid' ? 'Невалидный' : 'Проверяется'}
                    </span>
                  </div>

                  {/* Rejection Reason */}
                  {doc.status === 'rejected' && doc.rejection_reason && (
                    <Alert variant="destructive" className="mt-3">
                      <XCircle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Причина отклонения:</strong> {doc.rejection_reason}
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Validation Errors */}
                  {doc.validation_errors && doc.validation_errors !== '[]' && (
                    <Alert variant="destructive" className="mt-3">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Ошибки валидации:</strong> {doc.validation_errors}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Required Documents Checklist */}
      {kycStatus && (
        <Card>
          <CardHeader>
            <CardTitle>Необходимые документы</CardTitle>
            <CardDescription>
              Для завершения верификации необходимо предоставить все документы
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {kycStatus.required_documents.map((docType) => {
                const isSubmitted = kycStatus.submitted_documents.includes(docType);
                const isApproved = kycStatus.approved_documents.includes(docType);
                const isRejected = kycStatus.rejected_documents.includes(docType);

                return (
                  <div key={docType} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {isApproved ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : isRejected ? (
                        <XCircle className="h-5 w-5 text-red-500" />
                      ) : isSubmitted ? (
                        <Clock className="h-5 w-5 text-yellow-500" />
                      ) : (
                        <div className="h-5 w-5 border-2 border-gray-300 rounded-full" />
                      )}
                      <span className="font-medium">
                        {DOCUMENT_TYPE_LABELS[docType] || docType}
                      </span>
                    </div>
                    <div>
                      {isApproved && <Badge variant="success">Одобрено</Badge>}
                      {isRejected && <Badge variant="destructive">Отклонено</Badge>}
                      {isSubmitted && !isApproved && !isRejected && (
                        <Badge variant="secondary">На рассмотрении</Badge>
                      )}
                      {!isSubmitted && <Badge variant="outline">Не загружено</Badge>}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};