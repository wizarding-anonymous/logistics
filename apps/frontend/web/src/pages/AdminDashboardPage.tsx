import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, ShieldCheck, DollarSign, MessageSquareWarning } from 'lucide-react';

// TODO: In a real app, this data would be fetched from a dedicated admin dashboard API endpoint.
const dashboardStats = {
  pendingKyc: 5,
  openDisputes: 3,
  pendingPayouts: 2,
  totalUsers: 152,
};

const adminSections = [
  {
    title: 'KYC Verification',
    description: 'Approve or reject supplier KYC submissions.',
    link: '/admin/kyc',
    icon: <ShieldCheck className="h-6 w-6 text-muted-foreground" />,
    stat: `${dashboardStats.pendingKyc} pending`,
  },
  {
    title: 'Payout Approvals',
    description: 'Review and approve pending payouts to suppliers.',
    link: '/admin/payouts',
    icon: <DollarSign className="h-6 w-6 text-muted-foreground" />,
    stat: `${dashboardStats.pendingPayouts} pending`,
  },
  {
    title: 'Dispute Moderation',
    description: 'Mediate and resolve disputes between users.',
    link: '/admin/disputes',
    icon: <MessageSquareWarning className="h-6 w-6 text-muted-foreground" />,
    stat: `${dashboardStats.openDisputes} open`,
  },
  {
    title: 'User Management',
    description: 'View all users and organizations on the platform.',
    link: '/admin/users',
    icon: <Users className="h-6 w-6 text-muted-foreground" />,
    stat: `${dashboardStats.totalUsers} users`,
  },
];

function AdminDashboardPage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold tracking-tight">Admin Dashboard</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {adminSections.map((section) => (
          <Link to={section.link} key={section.title}>
            <Card className="hover:bg-muted/50 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{section.title}</CardTitle>
                {section.icon}
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{section.stat}</div>
                <p className="text-xs text-muted-foreground">{section.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default AdminDashboardPage;
