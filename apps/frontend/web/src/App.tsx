import { BrowserRouter as Router, Routes, Route, Link, Outlet } from 'react-router-dom';
import OrderDetailsPage from './pages/OrderDetailsPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CreateOrganizationPage from './pages/CreateOrganizationPage';
import OrganizationSettingsPage from './pages/OrganizationSettingsPage';
import RfqDetailsPage from './pages/RfqDetailsPage';
import RfqListPage from './pages/RfqListPage';
import CreateRfqPage from './pages/CreateRfqPage';
import InvoicePage from './pages/InvoicePage';
import InvoicesListPage from './pages/InvoicesListPage';
import AcceptInvitationPage from './pages/AcceptInvitationPage';
import ServiceCatalogPage from './pages/ServiceCatalogPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useAuthStore } from './state/authStore';
import KycPage from './pages/KycPage';
import MyServicesPage from './pages/MyServicesPage';
import CreateServicePage from './pages/CreateServicePage';
import AvailableRfqsPage from './pages/AvailableRfqsPage';
import KycVerificationPage from './pages/KycVerificationPage';
import { SearchBar } from './components/Search/SearchBar';
import SearchPage from './pages/SearchPage';

function Layout() {
  const { isAuthenticated, roles, clearTokens } = useAuthStore();
  const isSupplier = roles.includes('supplier');
  const isAdmin = roles.includes('admin');

  return (
    <div style={{ padding: '2rem' }}>
      <header className="flex justify-between items-center mb-4">
        <nav>
            <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem', padding: 0 }}>
            <li><Link to="/">Home</Link></li>
            {isAuthenticated && (
                <>
                <li><Link to="/dashboard">Dashboard</Link></li>
                {!isSupplier && !isAdmin && <li><Link to="/rfqs">My RFQs</Link></li>}
                </>
            )}
            </ul>
        </nav>
        <div className="w-1/3">
            <SearchBar />
        </div>
      </header>
      <nav>
        <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem', padding: 0 }}>
          {isAuthenticated && (
            <>
              {isSupplier && <li><Link to="/available-rfqs">Find Work</Link></li>}
              {isSupplier && <li><Link to="/my-services">My Services</Link></li>}
              {isSupplier && <li><Link to="/kyc">KYC</Link></li>}
              {isAdmin && <li><Link to="/admin/kyc">Admin KYC</Link></li>}
              <li><Link to="/invoices">Invoices</Link></li>
              <li><Link to="/catalog">Public Catalog</Link></li>
              <li><button onClick={clearTokens}>Logout</button></li>
            </>
          )}
          {!isAuthenticated && (
            <>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Register</Link></li>
            </>
          )}
        </ul>
      </nav>
      <hr style={{ margin: '1rem 0' }}/>
      <Outlet />
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<h2>Welcome to the Logistics Marketplace!</h2>} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="create-organization" element={<CreateOrganizationPage />} />
            <Route path="organization/:orgId/settings" element={<OrganizationSettingsPage />} />

            {/* RFQ Routes */}
            <Route path="rfqs" element={<RfqListPage />} />
            <Route path="rfqs/new" element={<CreateRfqPage />} />
            <Route path="rfqs/:rfqId" element={<RfqDetailsPage />} />

            {/* Order & Invoice Routes */}
            <Route path="orders/:orderId" element={<OrderDetailsPage />} />
            <Route path="orders/:orderId/dispute" element={<DisputePage />} />
            <Route path="invoices/:invoiceId" element={<InvoicePage />} />
            <Route path="invoices" element={<InvoicesListPage />} />

            {/* Supplier Routes */}
            <Route path="kyc" element={<KycPage />} />
            <Route path="my-services" element={<MyServicesPage />} />
            <Route path="my-services/new" element={<CreateServicePage />} />
            <Route path="available-rfqs" element={<AvailableRfqsPage />} />

            {/* Admin Routes */}
            <Route path="admin/kyc" element={<KycVerificationPage />} />

            <Route path="invitations/:token" element={<AcceptInvitationPage />} />
            <Route path="catalog" element={<ServiceCatalogPage />} />
            <Route path="search" element={<SearchPage />} />
          </Route>

          <Route path="*" element={<h3>Page not found</h3>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
