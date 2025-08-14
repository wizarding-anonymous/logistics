import React, { useState, useCallback } from 'react';
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { CheckCircle, AlertCircle, Upload, FileText, X } from 'lucide-react';

interface KYCDocumentUploadProps {
  onUploadComplete?: (documentId: string) => void;
  onUploadError?: (error: string) => void;
}

interface UploadFile {
  file: File;
  documentType: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  documentId?: string;
}

const DOCUMENT_TYPES = [
  { value: 'inn', label: 'ИНН (Налоговый номер)', description: 'Справка о постановке на налоговый учет' },
  { value: 'ogrn', label: 'ОГРН (Регистрационный номер)', description: 'Свидетельство о государственной регистрации' },
  { value: 'business_license', label: 'Лицензия', description: 'Лицензия на осуществление деятельности' },
  { value: 'passport', label: 'Паспорт', description: 'Паспорт руководителя организации' },
  { value: 'insurance_certificate', label: 'Страховой сертификат', description: 'Сертификат страхования ответственности' },
  { value: 'bank_details', label: 'Банковские реквизиты', description: 'Справка из банка с реквизитами' }
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];

export const KYCDocumentUpload: React.FC<KYCDocumentUploadProps> = ({
  onUploadComplete,
  onUploadError
}) => {
  const [uploads, setUploads] = useState<UploadFile[]>([]);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!selectedDocumentType) {
      onUploadError?.('Пожалуйста, выберите тип документа');
      return;
    }

    const newUploads: UploadFile[] = acceptedFiles.map(file => ({
      file,
      documentType: selectedDocumentType,
      progress: 0,
      status: 'pending'
    }));

    setUploads(prev => [...prev, ...newUploads]);

    // Start upload process for each file
    newUploads.forEach((upload, index) => {
      uploadFile(upload, uploads.length + index);
    });
  }, [selectedDocumentType, uploads.length, onUploadError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif']
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false
  });

  const uploadFile = async (upload: UploadFile, index: number) => {
    try {
      // Update status to uploading
      setUploads(prev => prev.map((u, i) => 
        i === index ? { ...u, status: 'uploading' } : u
      ));

      // Step 1: Get upload URL
      const uploadUrlResponse = await fetch('/api/v1/auth/users/me/kyc-documents/upload-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          document_type: upload.documentType,
          file_name: upload.file.name
        })
      });

      if (!uploadUrlResponse.ok) {
        throw new Error('Failed to get upload URL');
      }

      const { upload_url, file_key } = await uploadUrlResponse.json();

      // Step 2: Upload file to S3
      const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: upload.file,
        headers: {
          'Content-Type': upload.file.type
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file');
      }

      // Update progress
      setUploads(prev => prev.map((u, i) => 
        i === index ? { ...u, progress: 50, status: 'processing' } : u
      ));

      // Step 3: Create document record
      const fileHash = await calculateFileHash(upload.file);
      
      const documentResponse = await fetch('/api/v1/auth/users/me/kyc-documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          document_type: upload.documentType,
          file_storage_key: file_key,
          file_name: upload.file.name,
          file_size: upload.file.size,
          file_hash: fileHash
        })
      });

      if (!documentResponse.ok) {
        const errorData = await documentResponse.json();
        throw new Error(errorData.detail || 'Failed to create document record');
      }

      const document = await documentResponse.json();

      // Update status to completed
      setUploads(prev => prev.map((u, i) => 
        i === index ? { 
          ...u, 
          progress: 100, 
          status: 'completed',
          documentId: document.id 
        } : u
      ));

      onUploadComplete?.(document.id);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      
      setUploads(prev => prev.map((u, i) => 
        i === index ? { 
          ...u, 
          status: 'error',
          error: errorMessage 
        } : u
      ));

      onUploadError?.(errorMessage);
    }
  };

  const calculateFileHash = async (file: File): Promise<string> => {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  const removeUpload = (index: number) => {
    setUploads(prev => prev.filter((_, i) => i !== index));
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'uploading':
      case 'processing':
        return <div className="h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <FileText className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (upload: UploadFile) => {
    switch (upload.status) {
      case 'pending':
        return 'Ожидание загрузки';
      case 'uploading':
        return 'Загрузка файла...';
      case 'processing':
        return 'Обработка документа...';
      case 'completed':
        return 'Загружено успешно';
      case 'error':
        return upload.error || 'Ошибка загрузки';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Загрузка документов KYC</CardTitle>
          <CardDescription>
            Загрузите необходимые документы для верификации вашей организации
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Document Type Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Тип документа</label>
            <Select value={selectedDocumentType} onValueChange={setSelectedDocumentType}>
              <SelectTrigger>
                <SelectValue placeholder="Выберите тип документа" />
              </SelectTrigger>
              <SelectContent>
                {DOCUMENT_TYPES.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    <div>
                      <div className="font-medium">{type.label}</div>
                      <div className="text-sm text-gray-500">{type.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* File Drop Zone */}
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
              ${!selectedDocumentType ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} disabled={!selectedDocumentType} />
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-blue-600">Отпустите файл для загрузки...</p>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">
                  Перетащите файл сюда или нажмите для выбора
                </p>
                <p className="text-sm text-gray-500">
                  Поддерживаются: PDF, JPEG, PNG, TIFF (до 10 МБ)
                </p>
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {uploads.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-medium">Загружаемые файлы:</h4>
              {uploads.map((upload, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(upload.status)}
                      <div>
                        <p className="font-medium">{upload.file.name}</p>
                        <p className="text-sm text-gray-500">
                          {DOCUMENT_TYPES.find(t => t.value === upload.documentType)?.label}
                        </p>
                      </div>
                    </div>
                    {upload.status === 'error' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeUpload(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{getStatusText(upload)}</span>
                      {upload.status === 'uploading' || upload.status === 'processing' ? (
                        <span>{upload.progress}%</span>
                      ) : null}
                    </div>
                    
                    {(upload.status === 'uploading' || upload.status === 'processing') && (
                      <Progress value={upload.progress} className="h-2" />
                    )}
                    
                    {upload.status === 'error' && upload.error && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{upload.error}</AlertDescription>
                      </Alert>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Requirements Info */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Требования к документам:</strong>
              <ul className="mt-2 space-y-1 text-sm">
                <li>• Документы должны быть четкими и читаемыми</li>
                <li>• Все данные должны быть видны полностью</li>
                <li>• Документы не должны быть старше 6 месяцев</li>
                <li>• Поддерживаемые форматы: PDF, JPEG, PNG, TIFF</li>
                <li>• Максимальный размер файла: 10 МБ</li>
              </ul>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};