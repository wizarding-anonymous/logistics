import React from 'react';
import { Badge } from '../ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { Shield, ShieldCheck, ShieldAlert, ShieldX, Clock } from 'lucide-react';

interface VerificationBadgeProps {
  status: 'not_started' | 'pending' | 'approved' | 'rejected';
  level?: 'basic' | 'enhanced' | 'premium';
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const VERIFICATION_LEVELS = {
  basic: {
    label: 'Базовая верификация',
    description: 'Основные документы проверены',
    color: 'bg-blue-100 text-blue-800 border-blue-200'
  },
  enhanced: {
    label: 'Расширенная верификация',
    description: 'Полная проверка документов и деятельности',
    color: 'bg-green-100 text-green-800 border-green-200'
  },
  premium: {
    label: 'Премиум верификация',
    description: 'Максимальный уровень доверия',
    color: 'bg-purple-100 text-purple-800 border-purple-200'
  }
};

const STATUS_CONFIG = {
  not_started: {
    icon: Shield,
    label: 'Не верифицирован',
    description: 'Верификация не начата',
    color: 'bg-gray-100 text-gray-800 border-gray-200'
  },
  pending: {
    icon: Clock,
    label: 'На проверке',
    description: 'Документы находятся на рассмотрении',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200'
  },
  approved: {
    icon: ShieldCheck,
    label: 'Верифицирован',
    description: 'Поставщик успешно прошел верификацию',
    color: 'bg-green-100 text-green-800 border-green-200'
  },
  rejected: {
    icon: ShieldX,
    label: 'Отклонен',
    description: 'Верификация отклонена',
    color: 'bg-red-100 text-red-800 border-red-200'
  }
};

export const VerificationBadge: React.FC<VerificationBadgeProps> = ({
  status,
  level = 'basic',
  size = 'md',
  showText = true,
  className = ''
}) => {
  const statusConfig = STATUS_CONFIG[status];
  const levelConfig = status === 'approved' ? VERIFICATION_LEVELS[level] : null;
  const IconComponent = statusConfig.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-2.5 py-1.5',
    lg: 'text-base px-3 py-2'
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  const badgeContent = (
    <Badge
      variant="outline"
      className={`
        inline-flex items-center gap-1.5 font-medium border
        ${levelConfig ? levelConfig.color : statusConfig.color}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      <IconComponent className={iconSizes[size]} />
      {showText && (
        <span>
          {status === 'approved' && levelConfig ? levelConfig.label : statusConfig.label}
        </span>
      )}
    </Badge>
  );

  const tooltipContent = (
    <div className="space-y-2">
      <div className="font-medium">
        {status === 'approved' && levelConfig ? levelConfig.label : statusConfig.label}
      </div>
      <div className="text-sm text-gray-600">
        {status === 'approved' && levelConfig ? levelConfig.description : statusConfig.description}
      </div>
      {status === 'approved' && (
        <div className="text-xs text-gray-500 border-t pt-2">
          ✓ Документы проверены<br />
          ✓ Деятельность подтверждена<br />
          ✓ Соответствует требованиям платформы
        </div>
      )}
    </div>
  );

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          {badgeContent}
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          {tooltipContent}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Compact version for lists and cards
export const VerificationIcon: React.FC<{
  status: VerificationBadgeProps['status'];
  level?: VerificationBadgeProps['level'];
  className?: string;
}> = ({ status, level = 'basic', className = '' }) => {
  return (
    <VerificationBadge
      status={status}
      level={level}
      size="sm"
      showText={false}
      className={className}
    />
  );
};

// Full verification status display
export const VerificationStatus: React.FC<{
  status: VerificationBadgeProps['status'];
  level?: VerificationBadgeProps['level'];
  verifiedAt?: string;
  className?: string;
}> = ({ status, level = 'basic', verifiedAt, className = '' }) => {
  const statusConfig = STATUS_CONFIG[status];
  const levelConfig = status === 'approved' ? VERIFICATION_LEVELS[level] : null;

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <VerificationBadge status={status} level={level} size="md" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900">
          {status === 'approved' && levelConfig ? levelConfig.label : statusConfig.label}
        </div>
        <div className="text-sm text-gray-500">
          {status === 'approved' && levelConfig ? levelConfig.description : statusConfig.description}
        </div>
        {verifiedAt && status === 'approved' && (
          <div className="text-xs text-gray-400 mt-1">
            Верифицирован {new Date(verifiedAt).toLocaleDateString('ru-RU')}
          </div>
        )}
      </div>
    </div>
  );
};