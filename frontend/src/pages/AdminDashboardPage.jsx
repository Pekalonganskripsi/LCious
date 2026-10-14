import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { getApiBaseUrl, getImageBaseUrl } from '../config/api';
import {
  Users,
  Store,
  Settings,
  TrendingUp,
  Star,
  Activity,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Search,
  Filter,
  Trash2,
  Edit,
  Shield,
  CheckCircle,
  XCircle,
  Eye,
  Brain,
  SlidersHorizontal,
  BarChart3,
  Download,
  FileText,
  Database,
} from 'lucide-react';

function AdminDashboardPage() {
  const { user, token, logout } = useAuthStore();
  const API_BASE = getApiBaseUrl();
  const IMAGE_BASE = getImageBaseUrl();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Stats data
  const [stats, setStats] = useState({
    totalCustomers: 0,
    totalMerchants: 0,
    totalMenus: 0,
    totalRatings: 0,
    avgRating: 0,
  });
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(null);

  // User management data
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);

  // Algorithm parameters
  const [algoParams, setAlgoParams] = useState({
    default_alpha: 0.5,
    default_k_neighbors: 10,
    price_cheap_max: 15000,
    price_medium_min: 10000,
    price_medium_max: 30000,
    price_expensive_min: 25000,
    distance_near_km: 2.0,
    distance_medium_min_km: 1.0,
    distance_medium_max_km: 5.0,
    distance_far_min_km: 4.0,
  });

  // Evaluation metrics
  const [evaluation, setEvaluation] = useState({
    mae: 0.0,
    rmse: 0.0,
    hit_rate: 0.0,
    total_ratings: 0,
    high_rating_count: 0,
    avg_rating: 0.0,
    rating_distribution: {
      "1_star": 0,
      "2_star": 0,
      "3_star": 0,
      "4_star": 0,
      "5_star": 0,
    },
    prediction_count: 0,
  });

  // Merchants data
  const [merchants, setMerchants] = useState([]);
  const [merchantSortBy, setMerchantSortBy] = useState('created_at');
  const [merchantSortOrder, setMerchantSortOrder] = useState('desc');

  // User form modal state
  const [showUserModal, setShowUserModal] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'customer',
    full_name: '',
    phone: '',
    address: '',
  });

  // Merchant menus modal state
  const [showMerchantMenusModal, setShowMerchantMenusModal] = useState(false);
  const [selectedMerchantMenus, setSelectedMerchantMenus] = useState([]);
  const [selectedMerchantName, setSelectedMerchantName] = useState('');

  // Fetch stats
  useEffect(() => {
    fetchStats();
    fetchUsers();
    fetchEvaluation();
    fetchMerchants();
    fetchAlgorithmParams(); // Fetch algorithm params on load
  }, []);

  // Filter users based on search
  useEffect(() => {
    if (searchQuery) {
      const filtered = users.filter(
        (u) =>
          u.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.role.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredUsers(filtered);
    } else {
      setFilteredUsers(users);
    }
  }, [searchQuery, users]);

  const fetchStats = async () => {
    try {
      setStatsLoading(true);
      setStatsError(null);

      const response = await fetch(`${API_BASE}/admin/stats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Stats data received:', data);
        setStats(data);
        setStatsError(null);
      } else {
        const errorText = await response.text();
        const error = `Stats fetch failed: ${response.status} - ${errorText}`;
        console.error(error);
        setStatsError(error);
      }
    } catch (error) {
      const errorMsg = `Error fetching stats: ${error.message}`;
      console.error(errorMsg);
      setStatsError(errorMsg);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchAlgorithmParams = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/algorithm-params`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAlgoParams(data);
        console.log('Algorithm params loaded from database:', data);
      }
    } catch (error) {
      console.error('Error fetching algorithm params:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchEvaluation = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/evaluation`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setEvaluation(data);
      }
    } catch (error) {
      console.error('Error fetching evaluation:', error);
    }
  };

  const fetchMerchants = async (sortBy = merchantSortBy, sortOrder = merchantSortOrder) => {
    try {
      console.log('[DEBUG] Fetching merchants with:', { sortBy, sortOrder });
      const cacheBuster = Date.now();
      const response = await fetch(
        `${API_BASE}/admin/merchants?sort_by=${sortBy}&sort_order=${sortOrder}&_=${cacheBuster}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          cache: 'no-store',
        }
      );
      if (response.ok) {
        const data = await response.json();
        console.log('[DEBUG] Received merchants:', data.merchants?.slice(0, 3).map(m => ({ shop: m.shop_name, rating: m.average_rating })));
        setMerchants(data.merchants || []);
      } else {
        console.error('[DEBUG] Fetch failed:', response.status);
      }
    } catch (error) {
      console.error('[DEBUG] Error fetching merchants:', error);
    }
  };

  const handleViewMerchantMenus = async (merchantId, merchantName) => {
    setIsLoading(true);
    try {
      // Use existing public menus endpoint and filter by merchant_id or shop_name
      const response = await fetch(`${API_BASE}/menus?limit=100`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Filter menus by merchant_id or shop_name (compatibility workaround)
        const merchantMenus = data.menus.filter(menu => {
          // Try to filter by merchant_id first (after server restart)
          if (menu.merchant_id && menu.merchant_id === merchantId) {
            return true;
          }
          // Fallback: filter by shop_name (works without restart)
          if (menu.merchant && menu.merchant.shop_name === merchantName) {
            return true;
          }
          return false;
        });

        setSelectedMerchantMenus(merchantMenus);
        setSelectedMerchantName(merchantName);
        setShowMerchantMenusModal(true);
      } else {
        alert('Failed to fetch merchant menus');
      }
    } catch (error) {
      console.error('Error fetching merchant menus:', error);
      alert('Failed to fetch merchant menus');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseMerchantMenusModal = () => {
    setShowMerchantMenusModal(false);
    setSelectedMerchantMenus([]);
    setSelectedMerchantName('');
  };

  const handleMerchantSort = (field) => {
    console.log('[DEBUG] Sort clicked:', { field, currentSort: merchantSortBy, currentOrder: merchantSortOrder });
    let newOrder = 'asc';
    if (merchantSortBy === field) {
      // Toggle order if same field
      newOrder = merchantSortOrder === 'asc' ? 'desc' : 'asc';
    }
    console.log('[DEBUG] New sort params:', { field, newOrder });
    setMerchantSortBy(field);
    setMerchantSortOrder(newOrder);
    fetchMerchants(field, newOrder);
  };

  const handleExportData = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/evaluation/data-export`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();

        // Convert to JSON and download
        const dataStr = JSON.stringify(data, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `lvious-evaluation-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);

        alert('Data exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data');
    }
  };

  const handleUpdateAlgoParams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/algorithm-params`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(algoParams),
      });
      if (response.ok) {
        alert('Algorithm parameters updated successfully!');
        // Fetch updated params from database to ensure sync
        await fetchAlgorithmParams();
      }
    } catch (error) {
      console.error('Error updating algorithm params:', error);
      alert('Failed to update algorithm parameters');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      const response = await fetch(`${API_BASE}/admin/users/${userId}/toggle-status`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        fetchUsers();
        fetchStats();
      }
    } catch (error) {
      console.error('Error toggling user status:', error);
    }
  };

  const handleOpenAddUserModal = () => {
    setIsEditMode(false);
    setEditingUser(null);
    setUserFormData({
      username: '',
      email: '',
      password: '',
      role: 'customer',
      full_name: '',
      phone: '',
      address: '',
    });
    setShowUserModal(true);
  };

  const handleOpenEditUserModal = (user) => {
    setIsEditMode(true);
    setEditingUser(user);
    setUserFormData({
      username: user.username,
      email: user.email,
      password: '', // Don't populate password for security
      role: user.role,
      full_name: user.full_name || '',
      phone: user.phone || '',
      address: user.address || '',
    });
    setShowUserModal(true);
  };

  const handleCloseUserModal = () => {
    setShowUserModal(false);
    setIsEditMode(false);
    setEditingUser(null);
    setUserFormData({
      username: '',
      email: '',
      password: '',
      role: 'customer',
      full_name: '',
      phone: '',
      address: '',
    });
  };

  const handleSaveUser = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const url = isEditMode
        ? `${API_BASE}/admin/users/${editingUser.id}`
        : `${API_BASE}/admin/users`;

      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userFormData),
      });

      if (response.ok) {
        alert(isEditMode ? 'User updated successfully!' : 'User created successfully!');
        handleCloseUserModal();
        fetchUsers();
        fetchStats();
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error saving user:', error);
      alert('Failed to save user');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert('User deleted successfully!');
        fetchUsers();
        fetchStats();
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      alert('Failed to delete user');
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="card-glass p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800">{value}</p>
        </div>
        <div className={`p-4 rounded-full ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

  const UserRow = ({ user }) => (
    <tr className="border-b border-gray-200 hover:bg-gray-50">
      <td className="px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-gray-800">{user.username}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>
      </td>
      <td className="px-6 py-4">
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            user.role === 'superadmin'
              ? 'bg-purple-100 text-purple-700'
              : user.role === 'merchant'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {user.role.toUpperCase()}
        </span>
      </td>
      <td className="px-6 py-4">
        {user.is_active ? (
          <span className="flex items-center gap-1 text-green-600">
            <CheckCircle className="w-4 h-4" />
            Active
          </span>
        ) : (
          <span className="flex items-center gap-1 text-red-600">
            <XCircle className="w-4 h-4" />
            Inactive
          </span>
        )}
      </td>
      <td className="px-6 py-4">
        <p className="text-sm text-gray-600">{new Date(user.created_at).toLocaleDateString('id-ID')}</p>
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleOpenEditUserModal(user)}
            className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
            title="Edit User"
          >
            <Edit className="w-5 h-5 text-blue-500" />
          </button>
          <button
            onClick={() => handleToggleUserStatus(user.id, user.is_active)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title={user.is_active ? 'Deactivate' : 'Activate'}
          >
            {user.is_active ? <XCircle className="w-5 h-5 text-red-500" /> : <CheckCircle className="w-5 h-5 text-green-500" />}
          </button>
          <button
            onClick={() => handleDeleteUser(user.id)}
            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
            title="Delete User"
          >
            <Trash2 className="w-5 h-5 text-red-500" />
          </button>
        </div>
      </td>
    </tr>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {user?.username}</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  fetchStats();
                  fetchUsers();
                  fetchEvaluation();
                  fetchMerchants(merchantSortBy, merchantSortOrder);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'users', label: 'User Management', icon: Users },
            { id: 'merchants', label: 'Merchants', icon: Store },
            { id: 'algorithm', label: 'Algorithm', icon: Brain },
            { id: 'evaluation', label: 'Evaluation', icon: BarChart3 },
            { id: 'settings', label: 'Settings', icon: Settings },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <StatCard
                title="Total Customers"
                value={stats.totalCustomers}
                icon={Users}
                color="bg-gradient-to-br from-blue-500 to-blue-600"
              />
              <StatCard
                title="Total Merchants"
                value={stats.totalMerchants}
                icon={Store}
                color="bg-gradient-to-br from-purple-500 to-purple-600"
              />
              <StatCard
                title="Total Menus"
                value={stats.totalMenus}
                icon={Star}
                color="bg-gradient-to-br from-yellow-500 to-orange-500"
              />
              <StatCard
                title="Total Ratings"
                value={stats.totalRatings}
                icon={Star}
                color="bg-gradient-to-br from-green-500 to-green-600"
              />
              <StatCard
                title="Average Rating"
                value={stats.avgRating.toFixed(2)}
                icon={TrendingUp}
                color="bg-gradient-to-br from-pink-500 to-red-500"
              />
              <StatCard
                title="Active Users"
                value={users.filter((u) => u.is_active).length}
                icon={Activity}
                color="bg-gradient-to-br from-indigo-500 to-purple-500"
              />
            </div>

            {/* Recent Activity */}
            <div className="card-glass p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">System Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">Hybrid Algorithm</h3>
                  <p className="text-sm text-blue-600">
                    Fuzzy Logic + Collaborative Filtering with adaptive alpha weighting
                  </p>
                </div>
                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                  <h3 className="font-semibold text-purple-800 mb-2">Recommendation Engine</h3>
                  <p className="text-sm text-purple-600">
                    Personalized culinary recommendations based on taste preferences and location
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="card-glass p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">User Management</h2>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleOpenAddUserModal}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:shadow-lg transition-all"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add User
                </button>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <Filter className="w-5 h-5 text-gray-400" />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Joined
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user) => (
                    <UserRow key={user.id} user={user} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Algorithm Tab */}
        {activeTab === 'algorithm' && (
          <div className="card-glass p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">Algorithm Parameters</h2>
                <p className="text-sm text-gray-600">Tune the hybrid recommendation algorithm</p>
              </div>
              <button
                onClick={handleUpdateAlgoParams}
                disabled={isLoading}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                <Brain className="w-5 h-5" />
                {isLoading ? 'Saving...' : 'Save Parameters'}
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Hybrid Parameters */}
              <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <SlidersHorizontal className="w-5 h-5" />
                  Hybrid Algorithm
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Alpha (α): {algoParams.default_alpha}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={algoParams.default_alpha}
                      onChange={(e) =>
                        setAlgoParams({ ...algoParams, default_alpha: parseFloat(e.target.value) })
                      }
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Weight for Fuzzy vs Collaborative Filtering (0.5 = balanced)
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      K Neighbors: {algoParams.default_k_neighbors}
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={algoParams.default_k_neighbors}
                      onChange={(e) =>
                        setAlgoParams({
                          ...algoParams,
                          default_k_neighbors: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Number of similar users for collaborative filtering
                    </p>
                  </div>
                </div>
              </div>

              {/* Price Fuzzy Parameters */}
              <div className="p-6 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4">Price Fuzzy Sets (IDR)</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Cheap Max</label>
                      <input
                        type="number"
                        value={algoParams.price_cheap_max}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            price_cheap_max: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Medium Min
                      </label>
                      <input
                        type="number"
                        value={algoParams.price_medium_min}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            price_medium_min: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Medium Max
                      </label>
                      <input
                        type="number"
                        value={algoParams.price_medium_max}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            price_medium_max: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Expensive Min
                    </label>
                    <input
                      type="number"
                      value={algoParams.price_expensive_min}
                      onChange={(e) =>
                        setAlgoParams({
                          ...algoParams,
                          price_expensive_min: parseFloat(e.target.value),
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Distance Fuzzy Parameters */}
              <div className="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4">Distance Fuzzy Sets (km)</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Near Max</label>
                      <input
                        type="number"
                        step="0.5"
                        value={algoParams.distance_near_km}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            distance_near_km: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Medium Min
                      </label>
                      <input
                        type="number"
                        step="0.5"
                        value={algoParams.distance_medium_min_km}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            distance_medium_min_km: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Medium Max
                      </label>
                      <input
                        type="number"
                        step="0.5"
                        value={algoParams.distance_medium_max_km}
                        onChange={(e) =>
                          setAlgoParams({
                            ...algoParams,
                            distance_medium_max_km: parseFloat(e.target.value),
                          })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Far Min</label>
                    <input
                      type="number"
                      step="0.5"
                      value={algoParams.distance_far_min_km}
                      onChange={(e) =>
                        setAlgoParams({
                          ...algoParams,
                          distance_far_min_km: parseFloat(e.target.value),
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Info Card */}
              <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4">Algorithm Info</h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <p>
                    <strong>Alpha (α)</strong>: Controls balance between Fuzzy Logic and Collaborative
                    Filtering
                  </p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>α = 1.0: 100% Fuzzy Logic (personal preferences)</li>
                    <li>α = 0.5: 50% Fuzzy + 50% CF (balanced)</li>
                    <li>α = 0.0: 100% Collaborative Filtering (community ratings)</li>
                  </ul>
                  <p className="mt-3">
                    <strong>Adaptive Alpha</strong>: System automatically adjusts based on user rating
                    count
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Merchants Tab */}
        {activeTab === 'merchants' && (
          <div className="card-glass p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">Merchant Management</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  Total Merchants: <span className="font-bold">{merchants.length}</span>
                </span>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleMerchantSort('shop_name')}
                    >
                      <div className="flex items-center gap-1">
                        Shop Name
                        {merchantSortBy === 'shop_name' && (
                          merchantSortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Owner
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cuisine
                    </th>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleMerchantSort('menu_count')}
                    >
                      <div className="flex items-center gap-1">
                        Menus
                        {merchantSortBy === 'menu_count' && (
                          merchantSortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleMerchantSort('rating')}
                    >
                      <div className="flex items-center gap-1">
                        Rating
                        {merchantSortBy === 'rating' && (
                          merchantSortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {merchants.map((merchant) => (
                    <tr key={merchant.id} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-800">{merchant.shop_name}</p>
                          <p className="text-sm text-gray-500">{merchant.address}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="text-sm text-gray-800">{merchant.username}</p>
                          <p className="text-xs text-gray-500">{merchant.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                          {merchant.cuisine_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-semibold text-gray-800">{merchant.menu_count}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                          <span className="text-sm font-semibold text-gray-800">
                            {merchant.average_rating.toFixed(1)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {merchant.is_active ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            Active
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600">
                            <XCircle className="w-4 h-4" />
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleViewMerchantMenus(merchant.id, merchant.shop_name)}
                          className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                        >
                          <Eye className="w-4 h-4" />
                          View Menus
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Evaluation Tab */}
        {activeTab === 'evaluation' && (
          <div className="space-y-6">
            {/* Header */}
            <div className="card-glass p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-800 mb-2">Algorithm Evaluation Metrics</h2>
                  <p className="text-sm text-gray-600">
                    Real-time performance metrics for the Hybrid Fuzzy-Collaborative Filtering algorithm
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <a
                    href="/admin-evaluation"
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:shadow-lg transition-all"
                  >
                    <BarChart3 className="w-4 h-4" />
                    Open Advanced Evaluation
                  </a>
                  <button
                    onClick={fetchEvaluation}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                  </button>
                  <button
                    onClick={handleExportData}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all"
                  >
                    <Download className="w-4 h-4" />
                    Export Data
                  </button>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                {/* MAE Card */}
                <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-blue-800">Mean Absolute Error</h3>
                    <div className="p-2 bg-blue-500 rounded-lg">
                      <TrendingUp className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-blue-900 mb-2">{evaluation.mae}</p>
                  <p className="text-xs text-blue-600">
                    Lower is better. Average difference between predicted and actual ratings.
                  </p>
                </div>

                {/* RMSE Card */}
                <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-purple-800">Root Mean Square Error</h3>
                    <div className="p-2 bg-purple-500 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-purple-900 mb-2">{evaluation.rmse}</p>
                  <p className="text-xs text-purple-600">
                    Lower is better. Accuracy of predictions using squared error.
                  </p>
                </div>

                {/* Hit Rate Card */}
                <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-green-800">Hit Rate</h3>
                    <div className="p-2 bg-green-500 rounded-lg">
                      <Star className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-green-900 mb-2">{evaluation.hit_rate}%</p>
                  <p className="text-xs text-green-600">
                    Percentage of ratings ≥ 4 stars. Higher is better.
                  </p>
                </div>
              </div>
            </div>

            {/* Detailed Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Rating Distribution */}
              <div className="card-glass p-6">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Rating Distribution
                </h3>
                <div className="space-y-3">
                  {[
                    { label: '5 Stars', count: evaluation.rating_distribution["5_star"], color: 'bg-green-500' },
                    { label: '4 Stars', count: evaluation.rating_distribution["4_star"], color: 'bg-blue-500' },
                    { label: '3 Stars', count: evaluation.rating_distribution["3_star"], color: 'bg-yellow-500' },
                    { label: '2 Stars', count: evaluation.rating_distribution["2_star"], color: 'bg-orange-500' },
                    { label: '1 Star', count: evaluation.rating_distribution["1_star"], color: 'bg-red-500' },
                  ].map((star) => (
                    <div key={star.label} className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-700 w-20">{star.label}</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                        <div
                          className={`${star.color} h-full rounded-full transition-all duration-500`}
                          style={{
                            width: evaluation.total_ratings > 0
                              ? `${(star.count / evaluation.total_ratings) * 100}%`
                              : '0%',
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-12 text-right">
                        {star.count} ({evaluation.total_ratings > 0 ? ((star.count / evaluation.total_ratings) * 100).toFixed(1) : 0}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Statistics Summary */}
              <div className="card-glass p-6">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  Statistics Summary
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Total Ratings</span>
                    <span className="font-bold text-gray-800">{evaluation.total_ratings}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">High Ratings (4-5 stars)</span>
                    <span className="font-bold text-green-600">{evaluation.high_rating_count}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Average Rating</span>
                    <span className="font-bold text-gray-800">{evaluation.avg_rating} ⭐</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Prediction Count</span>
                    <span className="font-bold text-blue-600">{evaluation.prediction_count}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Research Info */}
            <div className="card-glass p-6 bg-gradient-to-r from-blue-50 to-purple-50">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Research Notes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
                <div>
                  <p className="font-medium mb-1">Mean Absolute Error (MAE)</p>
                  <p className="text-gray-600">
                    Calculated using cross-validation: For each rating, predict using average of other ratings from the same user.
                    MAE = (1/n) × Σ|actual - predicted|
                  </p>
                </div>
                <div>
                  <p className="font-medium mb-1">Root Mean Square Error (RMSE)</p>
                  <p className="text-gray-600">
                    RMSE = √((1/n) × Σ(actual - predicted)²)
                    Penalizes larger errors more than MAE.
                  </p>
                </div>
                <div>
                  <p className="font-medium mb-1">Hit Rate</p>
                  <p className="text-gray-600">
                    Percentage of ratings that are 4 stars or higher, indicating user satisfaction.
                    Hit Rate = (ratings ≥ 4) / total ratings × 100%
                  </p>
                </div>
                <div>
                  <p className="font-medium mb-1">Export Data</p>
                  <p className="text-gray-600">
                    Click "Export Data" to download full rating history with user and menu details for further analysis.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="card-glass p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">System Settings</h2>
            <div className="space-y-6">
              {/* System Info */}
              <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  System Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-700">Application</p>
                    <p className="text-gray-600">LCious - Local Culinary Recommendation System</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Algorithm</p>
                    <p className="text-gray-600">Hybrid Fuzzy-Collaborative Filtering</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Version</p>
                    <p className="text-gray-600">1.0.0 (Research Edition)</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Database</p>
                    <p className="text-gray-600">SQLite with SQLAlchemy ORM</p>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="p-6 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Quick Actions
                </h3>
                <div className="space-y-3">
                  <button
                    onClick={() => {
                      fetchStats();
                      fetchUsers();
                      fetchEvaluation();
                      fetchMerchants(merchantSortBy, merchantSortOrder);
                      alert('All data refreshed successfully!');
                    }}
                    className="w-full px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
                  >
                    <RefreshCw className="w-5 h-5" />
                    Refresh All Data
                  </button>
                  <button
                    onClick={handleExportData}
                    className="w-full px-4 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Export Evaluation Data
                  </button>
                </div>
              </div>

              {/* Algorithm Settings */}
              <div className="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-4">Algorithm Configuration</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Configure algorithm parameters in the Algorithm tab. Changes will affect all recommendations.
                </p>
                <button
                  onClick={() => setActiveTab('algorithm')}
                  className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
                >
                  Go to Algorithm Settings
                </button>
              </div>
            </div>
          </div>
        )}

        {/* User Form Modal */}
        {showUserModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                  {isEditMode ? 'Edit User' : 'Add New User'}
                </h2>
                <button
                  onClick={handleCloseUserModal}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <XCircle className="w-6 h-6 text-gray-500" />
                </button>
              </div>

              <form onSubmit={handleSaveUser} className="space-y-4">
                {/* Username */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    required
                    value={userFormData.username}
                    onChange={(e) => setUserFormData({ ...userFormData, username: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter username"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={userFormData.email}
                    onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter email"
                  />
                </div>

                {/* Password - only show for new users or if explicitly changing */}
                {(!isEditMode) && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password *
                    </label>
                    <input
                      type="password"
                      required={!isEditMode}
                      value={userFormData.password}
                      onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter password"
                      minLength={6}
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
                  </div>
                )}

                {isEditMode && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Password (leave empty to keep current)
                    </label>
                    <input
                      type="password"
                      value={userFormData.password}
                      onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter new password"
                      minLength={6}
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
                  </div>
                )}

                {/* Role */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role *
                  </label>
                  <select
                    required
                    value={userFormData.role}
                    onChange={(e) => setUserFormData({ ...userFormData, role: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="customer">Customer</option>
                    <option value="merchant">Merchant</option>
                    <option value="admin">Admin</option>
                    <option value="superadmin">Super Admin</option>
                  </select>
                </div>

                {/* Full Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={userFormData.full_name}
                    onChange={(e) => setUserFormData({ ...userFormData, full_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter full name"
                  />
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={userFormData.phone}
                    onChange={(e) => setUserFormData({ ...userFormData, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter phone number"
                  />
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Address
                  </label>
                  <textarea
                    value={userFormData.address}
                    onChange={(e) => setUserFormData({ ...userFormData, address: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter address"
                    rows={3}
                  />
                </div>

                {/* Form Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Saving...' : (isEditMode ? 'Update User' : 'Create User')}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseUserModal}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Merchant Menus Modal */}
        {showMerchantMenusModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-8 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    {selectedMerchantName} - Menu List
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Total Menus: {selectedMerchantMenus.length}
                  </p>
                </div>
                <button
                  onClick={handleCloseMerchantMenusModal}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <XCircle className="w-6 h-6 text-gray-500" />
                </button>
              </div>

              {selectedMerchantMenus.length === 0 ? (
                <div className="text-center py-12">
                  <Star className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No menus found for this merchant</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedMerchantMenus.map((menu) => (
                    <div key={menu.id} className="card-glass overflow-hidden">
                      {menu.image_url && (
                        <div className="relative h-48 bg-gray-100">
                          <img
                            src={menu.image_url.startsWith('data:') || menu.image_url.startsWith('http')
                              ? menu.image_url
                              : `${IMAGE_BASE}${menu.image_url}`}
                            alt={menu.item_name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        </div>
                      )}
                      <div className="p-4">
                        <h3 className="font-bold text-gray-800 mb-2">{menu.item_name}</h3>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {menu.description || 'No description'}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-lg font-bold text-gradient">
                            Rp {menu.price?.toLocaleString('id-ID') || 0}
                          </span>
                          <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                            {menu.category}
                          </span>
                        </div>

                        {/* Taste Levels */}
                        <div className="flex flex-wrap gap-2 mt-3">
                          {menu.spice_level > 0 && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                              🌶️ {menu.spice_level}
                            </span>
                          )}
                          {menu.sweetness_level > 0 && (
                            <span className="px-2 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">
                              🍬 {menu.sweetness_level}
                            </span>
                          )}
                          {menu.savory_level > 0 && (
                            <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
                              🧂 {menu.savory_level}
                            </span>
                          )}
                        </div>

                        {/* Status */}
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-xs text-gray-500">
                            Popularity: {menu.popularity_score || 0}
                          </span>
                          {menu.is_available ? (
                            <span className="flex items-center gap-1 text-green-600 text-xs">
                              <CheckCircle className="w-3 h-3" />
                              Available
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-red-600 text-xs">
                              <XCircle className="w-3 h-3" />
                              Unavailable
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboardPage;
