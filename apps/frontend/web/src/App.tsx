import { BrowserRouter as Router, Routes, Route, Link, Outlet } from 'react-router-dom';
import OrderDetailsPage from './pages/OrderDetailsPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CreateOrganizationPage from './pages/CreateOrganizationPage';
import OrganizationSettingsPage from './pages/OrganizationSettingsPage';
import RfqDetailsPage from './pages/RfqDetailsPage';
import InvoicePage from './pages/InvoicePage';
import AcceptInvitationPage from './pages/AcceptInvitationPage';
import ServiceCatalogPage from './pages/ServiceCatalogPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useAuthStore } from './state/authStore';

function Layout() {
  const { isAuthenticated, clearTokens } = useAuthStore();

  return (
    <div style={{ padding: '2rem' }}>
      <nav>
        <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem', padding: 0 }}>
          <li><Link to="/">Home</Link></li>
          {isAuthenticated && (
            <>
              <li><Link to="/dashboard">Dashboard</Link></li>
              <li><Link to="/create-organization">Create Organization</Link></li>
              <li><Link to="/catalog">Service Catalog</Link></li>
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
            <Route path="rfqs/:rfqId" element={<RfqDetailsPage />} />
            <Route path="orders/:orderId" element={<OrderDetailsPage />} />
            <Route path="orders/:orderId/invoice" element={<InvoicePage />} />
            <Route path="invitations/:token" element={<AcceptInvitationPage />} />
            <Route path="catalog" element={<ServiceCatalogPage />} />
          </Route>

          <Route path="*" element={<h3>Page not found</h3>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
