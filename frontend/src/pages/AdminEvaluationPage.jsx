/**
 * Admin Evaluation Page - Research-Oriented Auto-Evaluation System
 *
 * Professional evaluation dashboard for research purposes with:
 * - Detailed statistical analysis
 * - Comprehensive algorithm comparison
 * - Research-friendly presentation
 * - Export capabilities
 */
import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { getApiBaseUrl } from '../config/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Activity,
  TrendingUp,
  Play,
  Download,
  RefreshCw,
  FileText,
  BarChart3,
  Calculator,
  Users,
  Calendar,
  GitCompare,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Database,
  Sparkles,
  Star,
  Award,
  Target,
  TrendingDown,
  FileSpreadsheet,
  Info,
  BookOpen,
  Flame,
} from 'lucide-react';

function AdminEvaluationPage() {
  const { token } = useAuthStore();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoEvaluationResults, setAutoEvaluationResults] = useState(null);
  const [refreshStatus, setRefreshStatus] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  // Auto-refresh settings
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [lastRefreshTime, setLastRefreshTime] = useState(null);

  useEffect(() => {
    // Initial load - fetch cached results
    fetchAutoEvaluationResults();

    // Set up auto-refresh every 30 seconds
    let intervalId;
    if (autoRefreshEnabled) {
      intervalId = setInterval(() => {
        fetchAutoEvaluationResults(false); // Don't show loading on auto-refresh
      }, 30000); // 30 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefreshEnabled]);

  const fetchAutoEvaluationResults = async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true);
    }

    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/admin/auto-evaluation/results?force_refresh=false`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();

        if (data.status === 'success' && data.results) {
          setAutoEvaluationResults(data.results);
          setRefreshStatus({
            is_refreshing: data.is_refreshing || false,
            message: data.is_refreshing ? 'Evaluasi baru berjalan di latar belakang...' : 'Hasil terkini ditampilkan'
          });
        } else if (data.status === 'refreshing') {
          // Evaluation is running in background
          if (data.current_results) {
            setAutoEvaluationResults(data.current_results);
          }
          setRefreshStatus({
            is_refreshing: true,
            message: 'Evaluasi baru berjalan di latar belakang...'
          });
        } else if (data.status === 'initializing') {
          setRefreshStatus({
            is_refreshing: true,
            message: 'Evaluasi pertama berjalan di latar belakang...'
          });
        }

        setLastRefreshTime(new Date());
      }
    } catch (error) {
      console.error('Error fetching auto-evaluation results:', error);
      setRefreshStatus({
        is_refreshing: false,
        message: 'Terjadi kesalahan saat mengambil hasil evaluasi'
      });
    } finally {
      if (showLoading) {
        setIsLoading(false);
      }
    }
  };

  const forceRefreshEvaluation = async () => {
    setIsRefreshing(true);
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/admin/auto-evaluation/trigger?trigger_type=manual`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        setRefreshStatus({
          is_refreshing: true,
          message: 'Evaluasi manual dipicu. Hasil akan muncul setelah selesai...'
        });

        // Poll for results every 5 seconds
        const pollInterval = setInterval(async () => {
          const pollResponse = await fetch(`${API_BASE}/admin/auto-evaluation/results`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (pollResponse.ok) {
            const pollData = await pollResponse.json();
            if (pollData.status === 'success' && !pollData.is_refreshing) {
              setAutoEvaluationResults(pollData.results);
              setRefreshStatus({
                is_refreshing: false,
                message: 'Evaluasi selesai! Hasil terbaru ditampilkan.'
              });
              clearInterval(pollInterval);
              setIsRefreshing(false);
              fetchAutoEvaluationResults(false); // Refresh data
            }
          }
        }, 5000);

        // Stop polling after 5 minutes
        setTimeout(() => {
          clearInterval(pollInterval);
          setIsRefreshing(false);
        }, 300000);
      }
    } catch (error) {
      console.error('Error triggering evaluation:', error);
      setRefreshStatus({
        is_refreshing: false,
        message: 'Gagal memicu evaluasi'
      });
      setIsRefreshing(false);
    }
  };

  const downloadExcelReport = async () => {
    try {
      const API_BASE = getApiBaseUrl();
      const response = await fetch(`${API_BASE}/admin/auto-evaluation/download-excel`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evaluation_results_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const error = await response.json();
        alert(`Gagal mengunduh laporan: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error downloading Excel:', error);
      alert('Terjadi kesalahan saat mengunduh laporan');
    }
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return '0';
    return typeof num === 'number' ? num.toFixed(4) : '0';
  };

  const formatPercentage = (num) => {
    if (num === null || num === undefined) return '0%';
    return `${(num * 100).toFixed(2)}%`;
  };

  // Chart colors - Research-friendly color scheme
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1', '#14B8A6'];

  // Quality rating helper
  const getQualityRating = (mae, rmse) => {
    if (mae < 0.6 && rmse < 0.8) return { label: 'Excellent', color: 'green', bg: 'bg-green-50', text: 'text-green-700' };
    if (mae < 0.8 && rmse < 1.0) return { label: 'Good', color: 'blue', bg: 'bg-blue-50', text: 'text-blue-700' };
    if (mae < 1.0 && rmse < 1.3) return { label: 'Fair', color: 'yellow', bg: 'bg-yellow-50', text: 'text-yellow-700' };
    return { label: 'Poor', color: 'red', bg: 'bg-red-50', text: 'text-red-700' };
  };

  // Research summary card component
  const ResearchMetricCard = ({ title, value, subtitle, icon: Icon, color, trend }) => (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
        {trend && (
          <div className="flex items-center text-sm">
            {trend > 0 ? (
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
            )}
            <span className={trend > 0 ? 'text-green-600' : 'text-red-600'}>
              {Math.abs(trend)}%
            </span>
          </div>
        )}
      </div>
      <div className="text-3xl font-bold text-gray-800 mb-1">{value}</div>
      <div className="text-sm font-medium text-gray-600">{title}</div>
      {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
    </div>
  );

  // Rating badge component
  const RatingBadge = ({ rating, total }) => {
    const percentage = (rating / total * 100).toFixed(1);
    const getColor = () => {
      if (rating >= 4) return 'bg-green-100 text-green-700';
      if (rating >= 3) return 'bg-yellow-100 text-yellow-700';
      return 'bg-red-100 text-red-700';
    };

    return (
      <div className={`px-3 py-2 rounded-lg ${getColor()} text-center`}>
        <div className="text-lg font-bold">{rating.toFixed(1)}</div>
        <div className="text-xs opacity-75">{percentage}%</div>
      </div>
    );
  };

  if (isLoading && !autoEvaluationResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-700 font-medium">Memuat hasil evaluasi otomatis...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
              <Flame className="w-8 h-8 text-orange-600" />
              Evaluasi Sistem Rekomendasi Hybrid
            </h1>
            <p className="text-gray-600">
              Dashboard penelitian untuk sistem rekomendasi Hybrid Fuzzy-Collaborative Filtering
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => fetchAutoEvaluationResults(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Data
            </button>
            <button
              onClick={forceRefreshEvaluation}
              disabled={isRefreshing}
              className={`flex items-center gap-2 px-4 py-2 transition-colors ${
                isRefreshing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-500 hover:bg-green-600'
              } text-white rounded-lg`}
            >
              <Play className="w-4 h-4" />
              {isRefreshing ? 'Sedang Berjalan...' : 'Jalankan Evaluasi Baru'}
            </button>
            <button
              onClick={downloadExcelReport}
              disabled={!autoEvaluationResults}
              className={`flex items-center gap-2 px-4 py-2 transition-colors ${
                !autoEvaluationResults
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-purple-500 hover:bg-purple-600'
              } text-white rounded-lg`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              Download Excel
            </button>
          </div>
        </div>

        {/* Status Messages */}
        {refreshStatus && (
          <div className={`mb-6 p-4 rounded-lg ${
            refreshStatus.is_refreshing ? 'bg-yellow-50 border border-yellow-200' : 'bg-green-50 border border-green-200'
          }`}>
            <div className="flex items-center gap-2">
              {refreshStatus.is_refreshing ? (
                <>
                  <Clock className="w-5 h-5 text-yellow-600" />
                  <span className="text-yellow-800">{refreshStatus.message}</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-800">{refreshStatus.message}</span>
                </>
              )}
            </div>
            {lastRefreshTime && (
              <p className="text-sm text-gray-600 mt-2">
                Terakhir diupdate: {lastRefreshTime.toLocaleTimeString()}
              </p>
            )}
          </div>
        )}

        {/* Auto-refresh indicator */}
        <div className="mb-6 flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={autoRefreshEnabled}
              onChange={(e) => setAutoRefreshEnabled(e.target.checked)}
              className="rounded"
            />
            Auto-refresh setiap 30 detik
          </label>
          {autoRefreshEnabled && (
            <Sparkles className="w-4 h-4 text-green-500" />
          )}
        </div>

        {/* Main Content */}
        {autoEvaluationResults ? (
          <div>
            {/* Research Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <ResearchMetricCard
                title="Total Ratings"
                value={autoEvaluationResults.total_ratings || 0}
                subtitle="Dataset size"
                icon={Star}
                color="purple"
              />
              <ResearchMetricCard
                title="Active Customers"
                value={autoEvaluationResults.total_customers || 0}
                subtitle="Unique users"
                icon={Users}
                color="blue"
              />
              <ResearchMetricCard
                title="Total Menus"
                value={autoEvaluationResults.total_menus || 0}
                subtitle="Available items"
                icon={Calculator}
                color="green"
              />
              <ResearchMetricCard
                title="Data Sparsity"
                value={autoEvaluationResults.data_sparsity?.sparsity_percentage ?
                  `${autoEvaluationResults.data_sparsity.sparsity_percentage.toFixed(1)}%` : 'N/A'}
                subtitle="Matrix sparsity"
                icon={Activity}
                color="orange"
              />
            </div>

            {/* Detailed Statistics Section */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              <div className="flex items-center mb-6">
                <BarChart3 className="w-6 h-6 text-blue-600 mr-3" />
                <h2 className="text-2xl font-bold text-gray-800">Statistik Dataset</h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Rating Statistics */}
                <div>
                  <h3 className="font-bold text-lg mb-4 text-gray-700">Dataset Statistics</h3>
                  {autoEvaluationResults.data_sparsity && (
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                        <span className="font-medium text-green-800">👥 Total Users</span>
                        <span className="text-2xl font-bold text-green-600">
                          {autoEvaluationResults.data_sparsity.total_users || 0}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                        <span className="font-medium text-blue-800">🍽️ Total Menus</span>
                        <span className="text-2xl font-bold text-blue-600">
                          {autoEvaluationResults.data_sparsity.total_menus || 0}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                        <span className="font-medium text-purple-800">⭐ Total Ratings</span>
                        <span className="text-2xl font-bold text-purple-600">
                          {autoEvaluationResults.data_sparsity.total_ratings || 0}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                        <span className="font-medium text-orange-800">📊 Sparsity</span>
                        <span className="text-2xl font-bold text-orange-600">
                          {autoEvaluationResults.data_sparsity.sparsity_percentage ?
                            `${autoEvaluationResults.data_sparsity.sparsity_percentage.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-800">📈 Density</span>
                        <span className="text-2xl font-bold text-gray-600">
                          {autoEvaluationResults.data_sparsity.density_percentage ?
                            `${autoEvaluationResults.data_sparsity.density_percentage.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Data Characteristics */}
                <div>
                  <h3 className="font-bold text-lg mb-4 text-gray-700">Data Characteristics</h3>
                  {autoEvaluationResults.data_sparsity && (
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                        <span className="font-medium text-blue-800">Possible Ratings</span>
                        <span className="text-xl font-bold text-blue-600">
                          {autoEvaluationResults.data_sparsity.possible_ratings || 0}
                        </span>
                      </div>
                      <div className={`flex justify-between items-center p-3 rounded-lg ${
                        autoEvaluationResults.data_sparsity.sparsity_percentage > 70
                          ? 'bg-red-50 border border-red-200'
                          : autoEvaluationResults.data_sparsity.sparsity_percentage > 40
                          ? 'bg-yellow-50 border border-yellow-200'
                          : 'bg-green-50 border border-green-200'
                      }`}>
                        <span className="font-medium">Sparsity Level</span>
                        <span className={`text-lg font-bold ${
                          autoEvaluationResults.data_sparsity.sparsity_percentage > 70
                            ? 'text-red-600'
                            : autoEvaluationResults.data_sparsity.sparsity_percentage > 40
                            ? 'text-yellow-600'
                            : 'text-green-600'
                        }`}>
                          {autoEvaluationResults.data_sparsity.sparsity_level || 'N/A'}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Research Notes */}
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-start">
                      <BookOpen className="w-4 h-4 text-blue-600 mr-2 mt-1 flex-shrink-0" />
                      <div className="text-sm text-blue-800">
                        <strong className="font-semibold">Research Notes:</strong> Dataset ini memiliki{' '}
                        {autoEvaluationResults.data_sparsity?.sparsity_percentage ?
                          `${autoEvaluationResults.data_sparsity.sparsity_percentage.toFixed(1)}%` : 'N/A'} sparsity,
                        mengindikasikan{' '}
                        {autoEvaluationResults.data_sparsity?.sparsity_percentage > 70 ?
                          'cold start problem yang signifikan' :
                          autoEvaluationResults.data_sparsity?.sparsity_percentage > 40 ?
                          'cold start problem yang moderat' :
                          'data yang cukup dense'
                        }.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Research Notes */}
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start">
                  <BookOpen className="w-5 h-5 text-blue-600 mr-3 mt-1" />
                  <div className="text-sm text-blue-800">
                    <strong className="font-semibold">Research Notes:</strong> Dataset ini terdiri dari{' '}
                    {autoEvaluationResults.total_customers || 0} pengguna aktif yang memberikan{' '}
                    {autoEvaluationResults.total_ratings || 0} rating pada{' '}
                    {autoEvaluationResults.total_menus || 0} menu. Sparsity sebesar{' '}
                    {autoEvaluationResults.sparsity ? `${(autoEvaluationResults.sparsity * 100).toFixed(1)}%` : 'N/A'}{' '}
                    menunjukkan tingkat kepadasan data rating.
                  </div>
                </div>
              </div>
            </div>

            {/* Research Tabs */}
            <div className="bg-white rounded-xl shadow-lg mb-8">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px overflow-x-auto">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'overview'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4" />
                      Overview
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('cv-results')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'cv-results'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Calculator className="w-4 h-4" />
                      Cross-Validation
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('alpha-optimization')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'alpha-optimization'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Alpha Optimization
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('algorithm-comparison')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'algorithm-comparison'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <GitCompare className="w-4 h-4" />
                      Algorithms
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('statistical-tests')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'statistical-tests'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Statistical Tests
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('baselines')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'baselines'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Baselines
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('per-user')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'per-user'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Per-User
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('temporal')}
                    className={`px-4 md:px-6 py-3 text-sm md:text-base font-medium whitespace-nowrap transition-colors ${
                      activeTab === 'temporal'
                        ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Temporal
                    </div>
                  </button>
                </nav>
              </div>
            </div>

            {/* Research Results Section */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <Flame className="w-6 h-6 text-orange-600 mr-3" />
                  <h2 className="text-2xl font-bold text-gray-800">Hasil Evaluasi Sistem Rekomendasi</h2>
                </div>
                {autoEvaluationResults.best_alpha && (
                  <div className={`px-4 py-2 rounded-lg ${getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).bg}`}>
                    <div className="flex items-center gap-2">
                      <Award className="w-5 h-5" />
                      <span className={`font-bold ${getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).text}`}>
                        {getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).label}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Best Configuration Highlight */}
              {autoEvaluationResults.best_alpha && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl mb-8 border border-blue-200">
                  <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center">
                    <Target className="w-5 h-5 mr-2" />
                    Best Configuration: Alpha = {autoEvaluationResults.best_alpha.value}
                  </h3>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Mean Absolute Error</div>
                      <div className="text-2xl font-bold text-blue-600">{formatNumber(autoEvaluationResults.best_alpha.mae)}</div>
                      <div className="text-xs text-gray-500 mt-1">↓ Lower is better</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Root Mean Square Error</div>
                      <div className="text-2xl font-bold text-green-600">{formatNumber(autoEvaluationResults.best_alpha.rmse)}</div>
                      <div className="text-xs text-gray-500 mt-1">↓ Lower is better</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Hit Rate</div>
                      <div className="text-2xl font-bold text-purple-600">{formatNumber(autoEvaluationResults.best_alpha.hit_rate * 100)}%</div>
                      <div className="text-xs text-gray-500 mt-1">↑ Higher is better</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Quality Rating</div>
                      <div className={`text-2xl font-bold ${getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).text}`}>
                        {getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).label}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">System performance</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab Content */}
              {activeTab === 'overview' && (
                <div>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-bold mb-3 text-gray-700">MAE by Alpha Value</h3>
                      {autoEvaluationResults.cv_results && (
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={Object.values(autoEvaluationResults.cv_results)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="alpha" label={{ value: 'Alpha (α)', position: 'insideBottom', offset: -5 }} />
                            <YAxis label={{ value: 'MAE', angle: -90, position: 'insideLeft' }} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="avg_mae" fill="#3B82F6" name="MAE" />
                          </BarChart>
                        </ResponsiveContainer>
                      )}
                    </div>

                    <div>
                      <h3 className="font-bold mb-3 text-gray-700">RMSE by Alpha Value</h3>
                      {autoEvaluationResults.cv_results && (
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={Object.values(autoEvaluationResults.cv_results)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="alpha" label={{ value: 'Alpha (α)', position: 'insideBottom', offset: -5 }} />
                            <YAxis label={{ value: 'RMSE', angle: -90, position: 'insideLeft' }} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="avg_rmse" fill="#10B981" name="RMSE" />
                          </BarChart>
                        </ResponsiveContainer>
                      )}
                    </div>
                  </div>

                  {/* Performance Interpretation */}
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start">
                      <Info className="w-5 h-5 text-gray-600 mr-3 mt-1" />
                      <div className="text-sm text-gray-700">
                        <strong className="font-semibold">Interpretasi:</strong> Grafik menunjukkan bagaimana error rate (MAE dan RMSE) berubah terhadap parameter alpha.
                        Alpha = 0 (Collaborative Filtering murni) memberikan error terendah, menunjukkan bahwa collaborative filtering lebih efektif untuk dataset ini.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'cv-results' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Hasil Cross-Validation Lengkap</h2>
                  <p className="text-gray-600 mb-6">Hasil evaluasi menggunakan k-fold cross-validation dengan berbagai nilai alpha</p>

                  {autoEvaluationResults.cv_results ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gradient-to-r from-blue-50 to-purple-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Alpha (α)</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">MAE ↓</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">RMSE ↓</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Hit Rate ↑</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Std Dev (MAE)</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Std Dev (RMSE)</th>
                            <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Rating</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {Object.entries(autoEvaluationResults.cv_results).sort((a, b) => {
                            const alphaA = parseFloat(a[0].split('_')[1]);
                            const alphaB = parseFloat(b[0].split('_')[1]);
                            return alphaA - alphaB;
                          }).map(([key, data]) => {
                            const alpha = key.split('_')[1];
                            const quality = getQualityRating(data.avg_mae, data.avg_rmse);
                            const isBest = autoEvaluationResults.best_alpha?.value == alpha;

                            return (
                              <tr key={key} className={isBest ? 'bg-green-50' : 'hover:bg-gray-50'}>
                                <td className="px-4 py-3">
                                  {isBest && <Award className="inline w-4 h-4 text-green-600 mr-1" />}
                                  <span className={isBest ? 'font-bold text-green-700' : 'font-medium'}>{alpha}</span>
                                </td>
                                <td className="px-4 py-3 text-gray-900">{formatNumber(data.avg_mae)}</td>
                                <td className="px-4 py-3 text-gray-900">{formatNumber(data.avg_rmse)}</td>
                                <td className="px-4 py-3 text-gray-900">{formatNumber(data.avg_hit_rate * 100)}%</td>
                                <td className="px-4 py-3 text-gray-600 text-sm">±{formatNumber(data.std_mae)}</td>
                                <td className="px-4 py-3 text-gray-600 text-sm">±{formatNumber(data.std_rmse)}</td>
                                <td className="px-4 py-3">
                                  <span className={`px-2 py-1 rounded text-xs font-bold ${quality.bg} ${quality.text}`}>
                                    {quality.label}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data cross-validation</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'alpha-optimization' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Optimasi Parameter Alpha</h2>
                  <p className="text-gray-600 mb-6">
                    Analisis performa sistem dengan berbagai nilai alpha (α) untuk menemukan konfigurasi optimal
                  </p>

                  {autoEvaluationResults.alpha_optimization_chart ? (
                    <div className="space-y-6">
                      {/* Alpha Optimization Chart */}
                      <div>
                        <h3 className="font-bold text-lg mb-4 text-gray-700">Error Rate vs Alpha Value</h3>
                        <ResponsiveContainer width="100%" height={400}>
                          <LineChart data={autoEvaluationResults.alpha_optimization_chart}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                              dataKey="alpha"
                              label={{ value: 'Alpha (α) - Fuzzy Weight', position: 'insideBottom', offset: -5 }}
                            />
                            <YAxis
                              label={{ value: 'Error Rate', angle: -90, position: 'insideLeft' }}
                            />
                            <Tooltip />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="mae"
                              stroke="#3B82F6"
                              name="MAE"
                              strokeWidth={3}
                              dot={{ fill: '#3B82F6', r: 6 }}
                              activeDot={{ r: 8 }}
                            />
                            <Line
                              type="monotone"
                              dataKey="rmse"
                              stroke="#10B981"
                              name="RMSE"
                              strokeWidth={3}
                              dot={{ fill: '#10B981', r: 6 }}
                              activeDot={{ r: 8 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Alpha Interpretation Guide */}
                      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                        <h3 className="font-bold text-lg mb-4 text-blue-800">Interpretasi Nilai Alpha</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-white p-4 rounded-lg">
                            <div className="font-bold text-gray-800 mb-2">α = 0.0</div>
                            <div className="text-sm text-gray-600">Collaborative Filtering Murni</div>
                            <div className="text-xs text-gray-500 mt-1">Hanya menggunakan collaborative filtering</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="font-bold text-gray-800 mb-2">α = 0.5</div>
                            <div className="text-sm text-gray-600">Hyybrid Balance</div>
                            <div className="text-xs text-gray-500 mt-1">Kombinasi 50-50 fuzzy dan CF</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="font-bold text-gray-800 mb-2">α = 0.8</div>
                            <div className="text-sm text-gray-600">Fuzzy Dominan</div>
                            <div className="text-xs text-gray-500 mt-1">80% fuzzy, 20% collaborative</div>
                          </div>
                          <div className="bg-white p-4 rounded-lg">
                            <div className="font-bold text-gray-800 mb-2">α = 1.0</div>
                            <div className="text-sm text-gray-600">Fuzzy Logic Murni</div>
                            <div className="text-xs text-gray-500 mt-1">Hanya menggunakan fuzzy logic</div>
                          </div>
                        </div>
                      </div>

                      {/* Best Alpha Highlight */}
                      {autoEvaluationResults.best_alpha && (
                        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                          <div className="flex items-center mb-4">
                            <Award className="w-6 h-6 text-green-600 mr-3" />
                            <h3 className="font-bold text-lg text-green-800">Best Alpha Configuration</h3>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Optimal Alpha</div>
                              <div className="text-2xl font-bold text-green-600">
                                {autoEvaluationResults.best_alpha.value}
                              </div>
                            </div>
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Performance Rating</div>
                              <div className={`text-xl font-bold ${
                                getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).text
                              }`}>
                                {getQualityRating(autoEvaluationResults.best_alpha.mae, autoEvaluationResults.best_alpha.rmse).label}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Research Notes */}
                      <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-purple-600 mr-3 mt-1" />
                          <div className="text-sm text-purple-800">
                            <strong className="font-semibold">Research Insights:</strong> Grafik menunjukkan bahwa error rate meningkat seiring
                            dengan peningkatan nilai alpha. Ini mengindikasikan bahwa collaborative filtering lebih efektif daripada fuzzy logic
                            untuk dataset saat ini. Nilai alpha optimal adalah {autoEvaluationResults.best_alpha?.value || 'N/A'} dengan MAE{' '}
                            {autoEvaluationResults.best_alpha ? formatNumber(autoEvaluationResults.best_alpha.mae) : 'N/A'}.
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data optimasi alpha</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'algorithm-comparison' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Perbandingan Algoritma</h2>
                  <p className="text-gray-600 mb-6">Perbandingan performa antara Collaborative Filtering murni, Hybrid, dan Fuzzy Logic murni</p>

                  {autoEvaluationResults.algorithm_comparison ? (
                    <div className="space-y-6">
                      {/* Winner Announcement */}
                      {autoEvaluationResults.algorithm_comparison.winner && (
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200">
                          <div className="flex items-center">
                            <Award className="w-8 h-8 text-green-600 mr-3" />
                            <div>
                              <div className="text-sm text-green-600 font-medium mb-1">WINNER</div>
                              <div className="text-2xl font-bold text-green-800">
                                {autoEvaluationResults.algorithm_comparison.winner}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Algorithm Comparison Table */}
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gradient-to-r from-blue-50 to-purple-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Algorithm</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Alpha (α)</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">MAE ↓</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">RMSE ↓</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Hit Rate ↑</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Rating</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(autoEvaluationResults.algorithm_comparison)
                              .filter(([key]) => !['winner', 'winner_mae', 'total_ratings', 'test_size'].includes(key))
                              .map(([algoName, algoData], idx) => {
                                const quality = getQualityRating(algoData.mae, algoData.rmse);
                                const isWinner = algoName === autoEvaluationResults.algorithm_comparison.winner;

                                return (
                                  <tr key={idx} className={isWinner ? 'bg-green-50' : 'hover:bg-gray-50'}>
                                    <td className="px-4 py-3">
                                      {isWinner && <Award className="inline w-4 h-4 text-green-600 mr-1" />}
                                      <span className={isWinner ? 'font-bold text-green-700' : 'font-medium'}>
                                        {algoName}
                                      </span>
                                    </td>
                                    <td className="px-4 py-3 font-medium">{algoData.alpha || 'N/A'}</td>
                                    <td className="px-4 py-3">{formatNumber(algoData.mae)}</td>
                                    <td className="px-4 py-3">{formatNumber(algoData.rmse)}</td>
                                    <td className="px-4 py-3">{algoData.hit_rate ? formatNumber(algoData.hit_rate * 100) + '%' : 'N/A'}</td>
                                    <td className="px-4 py-3">
                                      <span className={`px-2 py-1 rounded text-xs font-bold ${quality.bg} ${quality.text}`}>
                                        {quality.label}
                                      </span>
                                    </td>
                                  </tr>
                                );
                              })}
                          </tbody>
                        </table>
                      </div>

                      {/* Winner Statistics */}
                      {autoEvaluationResults.algorithm_comparison.winner_mae && (
                        <div className="bg-green-50 p-4 rounded-lg">
                          <p className="text-green-800">
                            <strong>Winner Performance:</strong> MAE{' '}
                            {formatNumber(autoEvaluationResults.algorithm_comparison.winner_mae)}
                          </p>
                        </div>
                      )}

                      {/* Research Notes */}
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-blue-600 mr-3 mt-1" />
                          <div className="text-sm text-blue-800">
                            <strong className="font-semibold">Interpretasi:</strong>{' '}
                            {autoEvaluationResults.algorithm_comparison.winner === 'Collaborative Filtering Only' ?
                              'Collaborative Filtering murni memiliki error prediksi terendah, menunjukkan bahwa untuk dataset ini, collaborative filtering lebih efektif daripada hybrid atau fuzzy logic murni.' :
                              autoEvaluationResults.algorithm_comparison.winner === 'Hybrid (Current System)' ?
                              'Sistem Hybrid menunjukkan performa terbaik, mengindikasikan bahwa kombinasi fuzzy logic dan collaborative filtering memberikan hasil optimal.' :
                              `${autoEvaluationResults.algorithm_comparison.winner} menunjukkan performa terbaik untuk dataset ini.`
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data perbandingan algoritma</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'statistical-tests' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Statistical Significance Testing</h2>
                  <p className="text-gray-600 mb-6">Uji signifikansi statistik untuk memastikan perbedaan performa antar algoritma</p>

                  {autoEvaluationResults.statistical_test ? (
                    <div className="space-y-6">
                      {/* Significance Result */}
                      {autoEvaluationResults.statistical_test.is_significant !== undefined && (
                        <div className={`p-6 rounded-xl border-2 ${
                          autoEvaluationResults.statistical_test.is_significant
                            ? 'bg-green-50 border-green-200'
                            : 'bg-yellow-50 border-yellow-200'
                        }`}>
                          <div className="flex items-center mb-4">
                            {autoEvaluationResults.statistical_test.is_significant ? (
                              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
                            ) : (
                              <AlertCircle className="w-8 h-8 text-yellow-600 mr-3" />
                            )}
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Test Result</div>
                              <div className={`text-2xl font-bold ${
                                autoEvaluationResults.statistical_test.is_significant
                                  ? 'text-green-700'
                                  : 'text-yellow-700'
                              }`}>
                                {autoEvaluationResults.statistical_test.is_significant ? 'SIGNIFIKAN' : 'TIDAK SIGNIFIKAN'}
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Mean Difference</div>
                              <div className="text-2xl font-bold text-blue-600">
                                {autoEvaluationResults.statistical_test.mean_difference ?
                                  formatNumber(autoEvaluationResults.statistical_test.mean_difference) : 'N/A'}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Difference in means</div>
                            </div>
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Mean Error Alpha 1</div>
                              <div className="text-2xl font-bold text-purple-600">
                                {autoEvaluationResults.statistical_test.mean_error_alpha1 ?
                                  formatNumber(autoEvaluationResults.statistical_test.mean_error_alpha1) : 'N/A'}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">{autoEvaluationResults.statistical_test.alpha1 || 'N/A'}</div>
                            </div>
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Mean Error Alpha 2</div>
                              <div className="text-2xl font-bold text-green-600">
                                {autoEvaluationResults.statistical_test.mean_error_alpha2 ?
                                  formatNumber(autoEvaluationResults.statistical_test.mean_error_alpha2) : 'N/A'}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">{autoEvaluationResults.statistical_test.alpha2 || 'N/A'}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Test Statistics Detail */}
                      <div className="bg-gray-50 p-6 rounded-lg">
                        <h3 className="font-bold text-lg mb-4 text-gray-700">Detail Statistik Uji</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {autoEvaluationResults.statistical_test.alpha1_identifier && (
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Alpha 1</div>
                              <div className="text-xl font-bold text-gray-800">{autoEvaluationResults.statistical_test.alpha1_identifier}</div>
                            </div>
                          )}
                          {autoEvaluationResults.statistical_test.alpha2_identifier && (
                            <div className="bg-white p-4 rounded-lg">
                              <div className="text-sm text-gray-600 mb-1">Alpha 2</div>
                              <div className="text-xl font-bold text-gray-800">{autoEvaluationResults.statistical_test.alpha2_identifier}</div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Complete Statistical Metrics - Research Grade */}
                      <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
                        <h3 className="font-bold text-lg mb-4 text-gray-700">📊 Complete Statistical Metrics (Research Grade)</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

                          {/* P-Value */}
                          {autoEvaluationResults.statistical_test.p_value && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-blue-500">
                              <div className="text-sm text-gray-600 mb-1">P-Value</div>
                              <div className="text-xl font-bold text-blue-600">
                                {autoEvaluationResults.statistical_test.p_value < 0.001
                                  ? `&lt; 0.001`
                                  : formatNumber(autoEvaluationResults.statistical_test.p_value)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                {autoEvaluationResults.statistical_test.p_value < 0.001
                                  ? 'Very Significant (p &lt; 0.001)'
                                  : autoEvaluationResults.statistical_test.p_value < 0.05
                                    ? 'Significant (p &lt; 0.05)'
                                    : 'Not Significant'}
                              </div>
                            </div>
                          )}

                          {/* T-Statistic */}
                          {autoEvaluationResults.statistical_test.t_statistic && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-green-500">
                              <div className="text-sm text-gray-600 mb-1">T-Statistic</div>
                              <div className="text-xl font-bold text-green-600">
                                {formatNumber(autoEvaluationResults.statistical_test.t_statistic)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Paired t-test statistic</div>
                            </div>
                          )}

                          {/* Effect Size (Cohen's d) */}
                          {autoEvaluationResults.statistical_test.effect_size && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-purple-500">
                              <div className="text-sm text-gray-600 mb-1">Effect Size (Cohen's d)</div>
                              <div className="text-xl font-bold text-purple-600">
                                {formatNumber(autoEvaluationResults.statistical_test.effect_size)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                {autoEvaluationResults.statistical_test.effect_interpretation || 'Effect magnitude'}
                              </div>
                            </div>
                          )}

                          {/* 95% CI Lower */}
                          {autoEvaluationResults.statistical_test.ci_95_lower !== undefined && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-orange-500">
                              <div className="text-sm text-gray-600 mb-1">95% CI Lower</div>
                              <div className="text-xl font-bold text-orange-600">
                                {formatNumber(autoEvaluationResults.statistical_test.ci_95_lower)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Confidence interval lower bound</div>
                            </div>
                          )}

                          {/* 95% CI Upper */}
                          {autoEvaluationResults.statistical_test.ci_95_upper !== undefined && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-red-500">
                              <div className="text-sm text-gray-600 mb-1">95% CI Upper</div>
                              <div className="text-xl font-bold text-red-600">
                                {formatNumber(autoEvaluationResults.statistical_test.ci_95_upper)}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Confidence interval upper bound</div>
                            </div>
                          )}

                          {/* Number of Runs */}
                          {autoEvaluationResults.statistical_test.n_runs && (
                            <div className="bg-white p-4 rounded-lg border-l-4 border-teal-500">
                              <div className="text-sm text-gray-600 mb-1">Statistical Power</div>
                              <div className="text-xl font-bold text-teal-600">
                                {autoEvaluationResults.statistical_test.n_runs} runs
                              </div>
                              <div className="text-xs text-gray-500 mt-1">Sample size for reliability</div>
                            </div>
                          )}
                        </div>

                        {/* Complete 95% CI Display */}
                        {autoEvaluationResults.statistical_test.ci_95_lower !== undefined &&
                         autoEvaluationResults.statistical_test.ci_95_upper !== undefined && (
                          <div className="mt-4 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
                            <div className="text-sm text-gray-700 mb-2">
                              <strong>95% Confidence Interval:</strong> [{formatNumber(autoEvaluationResults.statistical_test.ci_95_lower)}, {formatNumber(autoEvaluationResults.statistical_test.ci_95_upper)}]
                            </div>
                            <div className="text-xs text-gray-600">
                              The true mean difference lies within this range with 95% confidence.
                              {autoEvaluationResults.statistical_test.ci_95_lower < 0 && autoEvaluationResults.statistical_test.ci_95_upper > 0
                                ? " ⚠️ CI contains 0 - results may not be reliable"
                                : " ✅ CI does not contain 0 - results are statistically reliable"}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Interpretation */}
                      {autoEvaluationResults.statistical_test.interpretation && (
                        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                          <div className="flex items-start">
                            <BookOpen className="w-5 h-5 text-purple-600 mr-3 mt-1" />
                            <div className="text-sm text-purple-800">
                              <strong className="font-semibold">Interpretasi:</strong> {autoEvaluationResults.statistical_test.interpretation}
                              {autoEvaluationResults.statistical_test.is_significant && (
                                <span className="ml-2">✅ Perbedaan antara kedua algoritma signifikan secara statistik.</span>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data statistical test</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'baselines' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Baseline Comparison</h2>
                  <p className="text-gray-600 mb-6">Perbandingan dengan algoritma baseline untuk validasi performa</p>

                  {autoEvaluationResults.baseline_comparison ? (
                    <div className="space-y-6">
                      {/* Winner Announcement */}
                      {autoEvaluationResults.baseline_comparison.winner && (
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200">
                          <div className="flex items-center">
                            <Award className="w-8 h-8 text-green-600 mr-3" />
                            <div>
                              <div className="text-sm text-green-600 font-medium mb-1">BEST ALGORITHM</div>
                              <div className="text-2xl font-bold text-green-800">
                                {autoEvaluationResults.baseline_comparison.winner}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Baseline Comparison Table */}
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gradient-to-r from-blue-50 to-purple-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Algorithm</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">MAE ↓</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">RMSE ↓</th>
                              <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Performance</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(autoEvaluationResults.baseline_comparison)
                              .filter(([key]) => !['winner', 'winner_mae', 'total_ratings', 'test_size'].includes(key))
                              .map(([algoName, algoData], idx) => {
                                const quality = getQualityRating(algoData.mae, algoData.rmse || algoData.mae * 1.2);
                                const isWinner = algoName === autoEvaluationResults.baseline_comparison.winner;

                                return (
                                  <tr key={idx} className={isWinner ? 'bg-green-50' : 'hover:bg-gray-50'}>
                                    <td className="px-4 py-3">
                                      {isWinner && <Award className="inline w-4 h-4 text-green-600 mr-1" />}
                                      <span className={isWinner ? 'font-bold text-green-700' : 'font-medium'}>
                                        {algoName}
                                      </span>
                                    </td>
                                    <td className="px-4 py-3">{formatNumber(algoData.mae)}</td>
                                    <td className="px-4 py-3">{algoData.rmse ? formatNumber(algoData.rmse) : 'N/A'}</td>
                                    <td className="px-4 py-3">
                                      <span className={`px-2 py-1 rounded text-xs font-bold ${quality.bg} ${quality.text}`}>
                                        {quality.label}
                                      </span>
                                    </td>
                                  </tr>
                                );
                              })}
                          </tbody>
                        </table>
                      </div>

                      {/* Performance Summary */}
                      {(() => {
                        const baselines = Object.entries(autoEvaluationResults.baseline_comparison)
                          .filter(([key]) => !['winner', 'winner_mae', 'total_ratings', 'test_size'].includes(key))
                          .map(([, data]) => data);

                        return (
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                              <div className="text-sm text-green-600 mb-1">Excellent</div>
                              <div className="text-xl font-bold text-green-700">
                                {baselines.filter(b => getQualityRating(b.mae, b.rmse || b.mae * 1.2).label === 'Excellent').length} algorithms
                              </div>
                            </div>
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                              <div className="text-sm text-blue-600 mb-1">Good</div>
                              <div className="text-xl font-bold text-blue-700">
                                {baselines.filter(b => getQualityRating(b.mae, b.rmse || b.mae * 1.2).label === 'Good').length} algorithms
                              </div>
                            </div>
                            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                              <div className="text-sm text-yellow-600 mb-1">Fair/Poor</div>
                              <div className="text-xl font-bold text-yellow-700">
                                {baselines.filter(b => ['Fair', 'Poor'].includes(getQualityRating(b.mae, b.rmse || b.mae * 1.2).label)).length} algorithms
                              </div>
                            </div>
                          </div>
                        );
                      })()}

                      {/* Research Notes */}
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-blue-600 mr-3 mt-1" />
                          <div className="text-sm text-blue-800">
                            <strong className="font-semibold">Research Notes:</strong>{' '}
                            {autoEvaluationResults.baseline_comparison.winner} mencapai performa terbaik
                            {autoEvaluationResults.baseline_comparison.winner_mae && ` dengan MAE ${formatNumber(autoEvaluationResults.baseline_comparison.winner_mae)}`}.
                            Ini menunjukkan bahwa algoritma tersebut lebih efektif daripada metode baseline lainnya untuk dataset ini.
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data baseline comparison</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'per-user' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Per-User Error Analysis</h2>
                  <p className="text-gray-600 mb-6">Analisis error prediksi per segmen pengguna untuk memahami pola performa</p>

                  {autoEvaluationResults.per_user_analysis ? (
                    <div className="space-y-6">
                      {/* User Segment Analysis */}
                      {autoEvaluationResults.per_user_analysis.user_segments && Object.keys(autoEvaluationResults.per_user_analysis.user_segments).length > 0 ? (
                        <div>
                          <h3 className="font-bold text-lg mb-4 text-gray-700">Error by User Segment</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {Object.entries(autoEvaluationResults.per_user_analysis.user_segments).map(([segmentName, segmentData], idx) => {
                              const quality = getQualityRating(segmentData.avg_mae || 0.8, segmentData.avg_mae * 1.2 || 1.0);

                              return (
                                <div key={idx} className={`p-4 rounded-lg border-2 ${quality.bg.replace('50', '200')}`}>
                                  <div className="flex items-center justify-between mb-3">
                                    <h4 className="font-bold text-gray-800">{segmentName}</h4>
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${quality.bg} ${quality.text}`}>
                                      {quality.label}
                                    </span>
                                  </div>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Users:</span>
                                      <span className="font-medium">{segmentData.count || 0}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Avg MAE:</span>
                                      <span className="font-medium">{formatNumber(segmentData.avg_mae || 0)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Std Dev:</span>
                                      <span className="font-medium text-gray-500">±{formatNumber(segmentData.std_mae || 0)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Range:</span>
                                      <span className="font-medium text-gray-500">
                                        {formatNumber(segmentData.min_error || 0)} - {formatNumber(segmentData.max_error || 0)}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-4 bg-yellow-50 rounded-lg">
                          <AlertCircle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                          <p className="text-yellow-700">Data segmentasi pengguna belum tersedia</p>
                        </div>
                      )}

                      {/* Best and Worst Predictions */}
                      {(autoEvaluationResults.per_user_analysis.best_predictions?.length > 0 ||
                        autoEvaluationResults.per_user_analysis.worst_predictions?.length > 0) ? (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* Best Predictions */}
                          {autoEvaluationResults.per_user_analysis.best_predictions?.length > 0 && (
                            <div>
                              <h3 className="font-bold text-lg mb-4 text-green-700 flex items-center">
                                <TrendingUp className="w-5 h-5 mr-2" />
                                Best Predictions (Lowest Error)
                              </h3>
                              <div className="space-y-2">
                                {autoEvaluationResults.per_user_analysis.best_predictions.map((pred, idx) => (
                                  <div key={idx} className="bg-green-50 p-4 rounded-lg border border-green-200">
                                    <div className="flex justify-between items-start">
                                      <div>
                                        <div className="font-medium text-green-900">
                                          {pred.customer_name || `Customer ${idx + 1}`}
                                        </div>
                                        <div className="text-sm text-green-700">
                                          {pred.menu_name || `Menu ${idx + 1}`}
                                        </div>
                                      </div>
                                      <div className="text-right">
                                        <div className="text-lg font-bold text-green-600">
                                          {formatNumber(pred.error || 0)}
                                        </div>
                                        <div className="text-xs text-green-600">Error</div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Worst Predictions */}
                          {autoEvaluationResults.per_user_analysis.worst_predictions?.length > 0 && (
                            <div>
                              <h3 className="font-bold text-lg mb-4 text-red-700 flex items-center">
                                <TrendingDown className="w-5 h-5 mr-2" />
                                Worst Predictions (Highest Error)
                              </h3>
                              <div className="space-y-2">
                                {autoEvaluationResults.per_user_analysis.worst_predictions.map((pred, idx) => (
                                  <div key={idx} className="bg-red-50 p-4 rounded-lg border border-red-200">
                                    <div className="flex justify-between items-start">
                                      <div>
                                        <div className="font-medium text-red-900">
                                          {pred.customer_name || `Customer ${idx + 1}`}
                                        </div>
                                        <div className="text-sm text-red-700">
                                          {pred.menu_name || `Menu ${idx + 1}`}
                                        </div>
                                      </div>
                                      <div className="text-right">
                                        <div className="text-lg font-bold text-red-600">
                                          {formatNumber(pred.error || 0)}
                                        </div>
                                        <div className="text-xs text-red-600">Error</div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-center py-4 bg-yellow-50 rounded-lg">
                          <AlertCircle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                          <p className="text-yellow-700">Data prediksi terbaik/terburuk belum tersedia</p>
                        </div>
                      )}

                      {/* Summary Statistics */}
                      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                        <h3 className="font-bold text-lg mb-4 text-blue-800">Summary Statistics</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="bg-white p-3 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Total Analyzed</div>
                            <div className="text-xl font-bold text-gray-800">
                              {autoEvaluationResults.per_user_analysis.total_analyzed || 0}
                            </div>
                          </div>
                          <div className="bg-white p-3 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Overall MAE</div>
                            <div className="text-xl font-bold text-blue-600">
                              {formatNumber(autoEvaluationResults.per_user_analysis.overall_mae || 0)}
                            </div>
                          </div>
                          <div className="bg-white p-3 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Total Users</div>
                            <div className="text-xl font-bold text-green-600">
                              {autoEvaluationResults.total_customers || 0}
                            </div>
                          </div>
                          <div className="bg-white p-3 rounded-lg">
                            <div className="text-sm text-gray-600 mb-1">Total Ratings</div>
                            <div className="text-xl font-bold text-purple-600">
                              {autoEvaluationResults.total_ratings || 0}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Research Insights */}
                      <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-purple-600 mr-3 mt-1" />
                          <div className="text-sm text-purple-800">
                            <strong className="font-semibold">Research Insights:</strong> Analisis per-user memberikan pemahaman
                            mendalam tentang performa sistem di berbagai segmen pengguna.{' '}
                            {autoEvaluationResults.per_user_analysis.total_analyzed > 0 ?
                              `Dianalisis ${autoEvaluationResults.per_user_analysis.total_analyzed} prediksi dengan MAE overall ${formatNumber(autoEvaluationResults.per_user_analysis.overall_mae)}.` :
                              'Data lengkap akan tersedia setelah evaluasi berikutnya.'
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data per-user analysis</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'temporal' && (
                <div>
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Temporal Trends Analysis</h2>
                  <p className="text-gray-600 mb-6">Analisis tren performa sistem dari waktu ke waktu</p>

                  {autoEvaluationResults.temporal_analysis ? (
                    <div className="space-y-6">
                      {/* Trend Summary */}
                      <div className={`p-6 rounded-xl border-2 ${
                        autoEvaluationResults.temporal_analysis.trend === 'improving' ? 'bg-green-50 border-green-200' :
                        autoEvaluationResults.temporal_analysis.trend === 'declining' ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'
                      }`}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {autoEvaluationResults.temporal_analysis.trend === 'improving' ? (
                              <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
                            ) : autoEvaluationResults.temporal_analysis.trend === 'declining' ? (
                              <TrendingDown className="w-8 h-8 text-red-600 mr-3" />
                            ) : (
                              <Activity className="w-8 h-8 text-gray-600 mr-3" />
                            )}
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Overall Trend</div>
                              <div className={`text-2xl font-bold ${
                                autoEvaluationResults.temporal_analysis.trend === 'improving' ? 'text-green-700' :
                                autoEvaluationResults.temporal_analysis.trend === 'declining' ? 'text-red-700' : 'text-gray-700'
                              }`}>
                                {autoEvaluationResults.temporal_analysis.trend === 'improving' ? 'IMPROVING' :
                                 autoEvaluationResults.temporal_analysis.trend === 'declining' ? 'DECLINING' : 'STABLE'}
                              </div>
                            </div>
                          </div>
                          {autoEvaluationResults.temporal_analysis.improvement_percentage !== undefined && (
                            <div className="text-right">
                              <div className="text-sm text-gray-600 mb-1">Improvement</div>
                              <div className="text-2xl font-bold text-blue-600">
                                {formatNumber(autoEvaluationResults.temporal_analysis.improvement_percentage)}%
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Statistics */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white p-4 rounded-lg border">
                          <div className="text-sm text-gray-600 mb-1">Total Ratings</div>
                          <div className="text-2xl font-bold text-gray-800">
                            {autoEvaluationResults.temporal_analysis.total_ratings || 0}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">Total analyzed</div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border">
                          <div className="text-sm text-gray-600 mb-1">Daily Metrics</div>
                          <div className="text-2xl font-bold text-gray-800">
                            {autoEvaluationResults.temporal_analysis.daily_metrics?.length || 0}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">Days analyzed</div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border">
                          <div className="text-sm text-gray-600 mb-1">Trend Direction</div>
                          <div className="text-lg font-bold text-gray-800">
                            {autoEvaluationResults.temporal_analysis.trend || 'N/A'}
                          </div>
                        </div>
                      </div>

                      {/* Daily Metrics Chart */}
                      {autoEvaluationResults.temporal_analysis.daily_metrics && autoEvaluationResults.temporal_analysis.daily_metrics.length > 0 && (
                        <div>
                          <h3 className="font-bold text-lg mb-4 text-gray-700">Daily Average Ratings Over Time</h3>
                          <ResponsiveContainer width="100%" height={350}>
                            <LineChart data={autoEvaluationResults.temporal_analysis.daily_metrics}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis
                                dataKey="date"
                                label={{ value: 'Date', position: 'insideBottom', offset: -5 }}
                              />
                              <YAxis
                                label={{ value: 'Avg Rating', angle: -90, position: 'insideLeft' }}
                                domain={[0, 5]}
                              />
                              <Tooltip />
                              <Legend />
                              <Line
                                type="monotone"
                                dataKey="avg_rating"
                                stroke="#3B82F6"
                                name="Average Rating"
                                strokeWidth={2}
                                dot={{ fill: '#3B82F6', r: 4 }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}

                      {/* Research Insights */}
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="flex items-start">
                          <BookOpen className="w-5 h-5 text-blue-600 mr-3 mt-1" />
                          <div className="text-sm text-blue-800">
                            <strong className="font-semibold">Research Notes:</strong>
                            {autoEvaluationResults.temporal_analysis.trend === 'improving' ?
                              ' Sistem menunjukkan peningkatan performa dari waktu ke waktu, mengindikasikan bahwa sistem semakin akurat seiring bertambahnya data.' :
                              autoEvaluationResults.temporal_analysis.trend === 'declining' ?
                              ' Terdapat penurunan performa yang perlu diinvestigasi lebih lanjut.' :
                              ' Performa sistem relatif stabil selama periode pengamatan.'}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">Tidak ada data temporal trends</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white p-12 rounded-xl shadow-lg text-center">
            <Database className="w-20 h-20 mx-auto mb-6 text-gray-300" />
            <h2 className="text-2xl font-bold text-gray-700 mb-3">Belum Ada Hasil Evaluasi</h2>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Evaluasi otomatis akan berjalan saat ada data baru atau Anda dapat memicunya secara manual.
            </p>
            <div className="space-y-3 max-w-sm mx-auto">
              <button
                onClick={forceRefreshEvaluation}
                className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
              >
                <div className="flex items-center justify-center gap-2">
                  <Play className="w-5 h-5" />
                  Jalankan Evaluasi Pertama
                </div>
              </button>
              <div className="text-sm text-gray-500 bg-gray-50 p-4 rounded-lg">
                <div className="flex items-start">
                  <Info className="w-4 h-4 text-gray-400 mr-2 mt-1 flex-shrink-0" />
                  <p>Evaluasi pertama mungkin memakan waktu beberapa menit tergantung ukuran dataset.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminEvaluationPage;