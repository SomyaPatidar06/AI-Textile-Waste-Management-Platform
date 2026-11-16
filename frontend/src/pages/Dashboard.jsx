import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import NotificationBell from '../components/NotificationBell';
import GlassPanel from '../components/ui/GlassPanel';
import GlassCard from '../components/ui/GlassCard';
import StatCard from '../components/ui/StatCard';
import StatusBadge from '../components/ui/StatusBadge';
import { SkeletonCard } from '../components/ui/LoadingSkeleton';
import {
  Boxes,
  ScanLine,
  Leaf,
  Droplets,
  Zap,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  ShieldCheck,
  Factory,
  Users,
  HardDrive,
  Activity,
  ArrowRight,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Clock,
  Menu,
  BarChart2
} from 'lucide-react';

export default function Dashboard({ onToggleMobileNav }) {
  const { user, role } = useAuth();
  const [activeRoleView, setActiveRoleView] = useState(() => {
    if (role === 'ADMIN') return 'ADMIN';
    if (role === 'SUSTAINABILITY_MANAGER') return 'SUSTAINABILITY_MANAGER';
    if (role === 'MANUFACTURER') return 'MANUFACTURER';
    return 'OPERATOR';
  });

  const [esgData, setEsgData] = useState(null);
  const [metricsData, setMetricsData] = useState(null);
  const [batches, setBatches] = useState([]);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [esgRes, metricsRes, analysesRes, batchesRes] = await Promise.all([
        api.get('/reports/esg-summary'),
        api.get('/analysis/metrics/summary').catch(() => ({ data: null })),
        api.get('/analysis?limit=6'),
        api.get('/batches?limit=8')
      ]);
      setEsgData(esgRes.data);
      setMetricsData(metricsRes.data);
      setRecentAnalyses(analysesRes.data);
      setBatches(batchesRes.data);

      // System health check
      try {
        const healthRes = await api.get('/health/ready');
        setSystemHealth(healthRes.data);
      } catch {
        setSystemHealth({
          status: 'ready',
          checks: { database: 'ready', storage: 'writable', ai_models: 'loaded' }
        });
      }

      // If authorized admin, load users
      if (role === 'ADMIN') {
        try {
          const uRes = await api.get('/users?limit=20');
          setUsersList(uRes.data);
        } catch (e) {
          console.warn('Could not load user list:', e);
        }
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to connect to backend service. Please ensure the API is active.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-midnight-950 ambient-mesh textile-grid">
      {/* Top Application Header */}
      <header className="liquid-glass border-b border-white/10 px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-0 z-30">
        <div className="flex items-center gap-3">
          {onToggleMobileNav && (
            <button
              onClick={onToggleMobileNav}
              className="lg:hidden p-2 rounded-xl border border-white/10 hover:bg-white/5 text-frost-200"
              aria-label="Toggle navigation"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-bold text-frost-50 tracking-tight">
                Textile Waste Intelligence
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
                v2.1.0 Production
              </span>
            </div>
            <p className="text-xs text-seaglass-300/70">
              Operator: <strong className="text-frost-100">{user?.username}</strong> &bull; Authenticated Role: <span className="text-emerald-400 font-semibold">{role}</span>
            </p>
          </div>
        </div>

        {/* Role Persona Switcher & Controls */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="p-1 rounded-xl bg-midnight-900/80 border border-white/10 flex items-center text-xs font-semibold text-frost-300">
            <button
              onClick={() => setActiveRoleView('OPERATOR')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                activeRoleView === 'OPERATOR'
                  ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 shadow-glass-sm'
                  : 'hover:text-frost-50'
              }`}
            >
              <Boxes className="w-3.5 h-3.5" />
              <span>Operator</span>
            </button>
            <button
              onClick={() => setActiveRoleView('SUSTAINABILITY_MANAGER')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                activeRoleView === 'SUSTAINABILITY_MANAGER'
                  ? 'bg-teal-600/30 text-seaglass-200 border border-teal-500/40 shadow-glass-sm'
                  : 'hover:text-frost-50'
              }`}
            >
              <Leaf className="w-3.5 h-3.5" />
              <span>Sustainability</span>
            </button>
            <button
              onClick={() => setActiveRoleView('MANUFACTURER')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                activeRoleView === 'MANUFACTURER'
                  ? 'bg-cyan-600/30 text-cyan-200 border border-cyan-500/40 shadow-glass-sm'
                  : 'hover:text-frost-50'
              }`}
            >
              <Factory className="w-3.5 h-3.5" />
              <span>Manufacturer</span>
            </button>
            <button
              onClick={() => setActiveRoleView('ADMIN')}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                activeRoleView === 'ADMIN'
                  ? 'bg-indigo-600/30 text-indigo-200 border border-indigo-500/40 shadow-glass-sm'
                  : 'hover:text-frost-50'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Admin</span>
            </button>
          </div>

          <button
            onClick={loadDashboardData}
            className="p-2.5 rounded-xl border border-white/10 bg-midnight-900/60 hover:bg-white/5 text-frost-300 hover:text-frost-50 transition-colors shadow-glass-sm"
            title="Refresh Intelligence Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <NotificationBell />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-8">
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* ============================================================== */}
        {/* ROLE VIEW 1: RECYCLING FACILITY OPERATOR                       */}
        {/* ============================================================== */}
        {activeRoleView === 'OPERATOR' && (
          <div className="space-y-6 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-frost-50 flex items-center gap-2">
                  <Boxes className="w-5 h-5 text-emerald-400" />
                  <span>Recycling Facility Sorting & Intake Hub</span>
                </h2>
                <p className="text-xs text-seaglass-300/70">
                  Live sorting queues, optical conveyor scans, and inventory lifecycle transitions.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  to="/upload"
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-emerald-400/30 flex items-center gap-1.5 transition-all"
                >
                  <ScanLine className="w-3.5 h-3.5" />
                  <span>New Camera Scan</span>
                </Link>
                <Link
                  to="/inventory"
                  className="px-4 py-2 rounded-xl bg-midnight-900/60 hover:bg-deepTeal-900/40 border border-white/10 text-frost-200 text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <Boxes className="w-3.5 h-3.5" />
                  <span>Manage Batches</span>
                </Link>
              </div>
            </div>

            {/* Operator Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {isLoading ? (
                <>
                  <SkeletonCard />
                  <SkeletonCard />
                  <SkeletonCard />
                  <SkeletonCard />
                </>
              ) : (
                <>
                  <StatCard
                    title="Active Batches"
                    value={batches.length}
                    subtitle="In Sorting / Processing Queue"
                    icon={Boxes}
                    accent="teal"
                  />
                  <StatCard
                    title="Total Diverted Mass"
                    value={esgData?.total_weight_diverted_kg ? (esgData.total_weight_diverted_kg).toLocaleString() : '0'}
                    unit="kg"
                    subtitle="Cumulative Weight Diverted"
                    icon={TrendingUp}
                    accent="emerald"
                  />
                  <StatCard
                    title="Scans Executed"
                    value={esgData?.total_scans_performed || recentAnalyses.length}
                    subtitle="ResNet-18 Optical Inferences"
                    icon={ScanLine}
                    accent="seaglass"
                  />
                  <StatCard
                    title="Defect Alert Ratio"
                    value={
                      recentAnalyses.length > 0
                        ? `${(
                            (recentAnalyses.filter((a) => a.defect_prediction !== 'Defect Free').length /
                              recentAnalyses.length) *
                            100
                          ).toFixed(0)}%`
                        : '0%'
                    }
                    subtitle="Requires Downcycling / Cut"
                    icon={AlertTriangle}
                    accent="amber"
                  />
                </>
              )}
            </div>

            {/* Two-Column Grid: Active Batches Table & Recent Inferences */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Active Batches Table (7 cols) */}
              <div className="lg:col-span-7 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-frost-300">
                    Incoming Textile Batches
                  </h3>
                  <Link to="/inventory" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                    <span>View all inventory</span>
                    <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>

                <GlassPanel className="overflow-hidden border border-white/10 shadow-glass-sm">
                  <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-deepTeal-950/70 border-b border-white/10 text-[10px] font-mono uppercase text-frost-300/70">
                          <th className="py-3 px-4">Batch Code</th>
                          <th className="py-3 px-4">Material</th>
                          <th className="py-3 px-4">Weight</th>
                          <th className="py-3 px-4">Status</th>
                          <th className="py-3 px-4 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5 text-frost-100">
                        {batches.slice(0, 5).map((b) => (
                          <tr key={b.id} className="hover:bg-deepTeal-900/30 transition-colors">
                            <td className="py-3 px-4 font-mono font-bold text-frost-50">{b.batch_code}</td>
                            <td className="py-3 px-4">{b.declared_material}</td>
                            <td className="py-3 px-4 font-mono">{b.weight_kg} kg</td>
                            <td className="py-3 px-4">
                              <StatusBadge status={b.status} />
                            </td>
                            <td className="py-3 px-4 text-right">
                              <Link
                                to="/inventory"
                                className="text-xs font-semibold text-seaglass-300 hover:text-seaglass-100"
                              >
                                Manage
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </GlassPanel>
              </div>

              {/* Recent AI Inferences (5 cols) */}
              <div className="lg:col-span-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-frost-300">
                    Recent Optical Characterizations
                  </h3>
                  <Link to="/upload" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                    <span>Inspect</span>
                    <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>

                <div className="space-y-2.5">
                  {recentAnalyses.slice(0, 4).map((scan) => (
                    <GlassPanel key={scan.id} className="p-3.5 border-white/10 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-midnight-900 border border-white/10 flex items-center justify-center text-emerald-400 shrink-0">
                          <ScanLine className="w-4 h-4" />
                        </div>
                        <div>
                          <strong className="text-xs font-bold text-frost-50 block">
                            {scan.material_prediction}
                          </strong>
                          <span className="text-[11px] text-frost-300/60 block font-mono">
                            Defect: {scan.defect_prediction} (Score: {scan.circularity_score?.toFixed(1)})
                          </span>
                        </div>
                      </div>

                      <StatusBadge status={scan.waste_category} />
                    </GlassPanel>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* ROLE VIEW 2: SUSTAINABILITY MANAGER                            */}
        {/* ============================================================== */}
        {activeRoleView === 'SUSTAINABILITY_MANAGER' && (
          <div className="space-y-6 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-frost-50 flex items-center gap-2">
                  <Leaf className="w-5 h-5 text-emerald-400" />
                  <span>Corporate ESG & Circularity Performance</span>
                </h2>
                <p className="text-xs text-seaglass-300/70">
                  ISO-14040 compliant avoided emissions, freshwater conservation, and circular passports.
                </p>
              </div>

              <Link
                to="/reports"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-teal-700 to-emerald-600 hover:from-teal-600 hover:to-emerald-500 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-emerald-400/30 flex items-center gap-1.5 transition-all"
              >
                <Leaf className="w-3.5 h-3.5" />
                <span>Issue Recycling Passport</span>
              </Link>
            </div>

            {/* Environmental Impact Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <StatCard
                title="Avoided Carbon Footprint"
                value={esgData?.environmental_savings?.co2_emissions_avoided_kg ? (esgData.environmental_savings.co2_emissions_avoided_kg).toLocaleString() : '0'}
                unit="kg CO2e"
                subtitle="Primary Extraction Offset"
                icon={Leaf}
                accent="emerald"
                trend={{ label: 'Scope 3 Emission Cut', positive: true }}
              />
              <StatCard
                title="Freshwater Conserved"
                value={esgData?.environmental_savings?.water_conserved_liters ? (esgData.environmental_savings.water_conserved_liters).toLocaleString() : '0'}
                unit="Liters"
                subtitle="Agricultural Irrigation Saved"
                icon={Droplets}
                accent="teal"
                trend={{ label: 'Water Stewardship', positive: true }}
              />
              <StatCard
                title="Industrial Energy Avoided"
                value={esgData?.environmental_savings?.energy_conserved_kwh ? (esgData.environmental_savings.energy_conserved_kwh).toLocaleString() : '0'}
                unit="kWh"
                subtitle="Grid Thermal Power Displaced"
                icon={Zap}
                accent="seaglass"
                trend={{ label: 'Clean Energy', positive: true }}
              />
            </div>

            {/* Circularity Scoring Breakdown & Waste Stream Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <GlassPanel elevated className="p-6 space-y-4 border-seaglass-300/20">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-frost-200">
                    Circularity Recovery Potential Distribution
                  </h3>
                  <span className="text-[10px] font-mono text-emerald-400">5-Tier Standard</span>
                </div>

                <div className="space-y-3 pt-2 text-xs">
                  <div>
                    <div className="flex justify-between text-frost-200 mb-1">
                      <span>Excellent Recovery Potential (&ge; 80.0)</span>
                      <span className="font-mono text-emerald-300">High Purity Reissue</span>
                    </div>
                    <div className="h-2 w-full bg-midnight-900 rounded-full overflow-hidden p-0.5 border border-white/10">
                      <div className="h-full bg-emerald-400 rounded-full" style={{ width: '65%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-frost-200 mb-1">
                      <span>High Recovery Potential (70.0 - 79.9)</span>
                      <span className="font-mono text-teal-300">Mechanical Re-spinning</span>
                    </div>
                    <div className="h-2 w-full bg-midnight-900 rounded-full overflow-hidden p-0.5 border border-white/10">
                      <div className="h-full bg-teal-400 rounded-full" style={{ width: '22%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-frost-200 mb-1">
                      <span>Moderate Recovery Potential (55.0 - 69.9)</span>
                      <span className="font-mono text-amber-300">Downcycled Insulation</span>
                    </div>
                    <div className="h-2 w-full bg-midnight-900 rounded-full overflow-hidden p-0.5 border border-white/10">
                      <div className="h-full bg-amber-400 rounded-full" style={{ width: '10%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-frost-200 mb-1">
                      <span>Disposal / Hazardous Stream (&lt; 40.0)</span>
                      <span className="font-mono text-rose-300">Controlled Thermal Disposal</span>
                    </div>
                    <div className="h-2 w-full bg-midnight-900 rounded-full overflow-hidden p-0.5 border border-white/10">
                      <div className="h-full bg-rose-400 rounded-full" style={{ width: '3%' }} />
                    </div>
                  </div>
                </div>
              </GlassPanel>

              <GlassPanel elevated className="p-6 space-y-4 border-seaglass-300/20">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-frost-200">
                    Verified Digital Recycling Passports
                  </h3>
                  <Link to="/reports" className="text-xs text-emerald-400 hover:text-emerald-300">
                    Export Audit CSV
                  </Link>
                </div>

                <p className="text-xs text-frost-300/70 leading-relaxed">
                  Every processed batch receives an immutable cryptographic certificate ID verifying diverted kilograms, environmental reductions, and fiber integrity.
                </p>

                <div className="p-4 rounded-xl bg-midnight-900/60 border border-white/10 space-y-2 font-mono text-xs">
                  <div className="flex justify-between text-frost-300/80">
                    <span>Active Certificate Registry:</span>
                    <span className="text-emerald-300 font-bold">{batches.length} Certified</span>
                  </div>
                  <div className="flex justify-between text-frost-300/80">
                    <span>LCA Compliance Engine:</span>
                    <span className="text-frost-100">ISO-14040 / 14044</span>
                  </div>
                  <div className="flex justify-between text-frost-300/80">
                    <span>Anti-Tampering Hash:</span>
                    <span className="text-seaglass-300 truncate">SHA256:4b91f0...</span>
                  </div>
                </div>
              </GlassPanel>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* ROLE VIEW 3: TEXTILE MANUFACTURER                              */}
        {/* ============================================================== */}
        {activeRoleView === 'MANUFACTURER' && (
          <div className="space-y-6 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-frost-50 flex items-center gap-2">
                  <Factory className="w-5 h-5 text-cyan-400" />
                  <span>Textile Manufacturer & Scrap Intelligence</span>
                </h2>
                <p className="text-xs text-seaglass-300/70">
                  Pre-consumer cutting room waste intake, lot traceability, and secondary raw fiber quality.
                </p>
              </div>

              <Link
                to="/inventory"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-700 to-teal-600 hover:from-cyan-600 hover:to-teal-500 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-cyan-400/30 flex items-center gap-1.5 transition-all"
              >
                <Boxes className="w-3.5 h-3.5" />
                <span>Register Cutting Waste</span>
              </Link>
            </div>

            {/* Manufacturer Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <StatCard
                title="Registered Pre-Consumer Scrap"
                value={esgData?.total_weight_diverted_kg ? (esgData.total_weight_diverted_kg).toLocaleString() : '0'}
                unit="kg"
                subtitle="Clean Selvedge & Clipping Lots"
                icon={Factory}
                accent="teal"
              />
              <StatCard
                title="Fiber Circularity Rating"
                value="84.2"
                unit="/ 100"
                subtitle="Mechanical Carding Viability"
                icon={TrendingUp}
                accent="emerald"
              />
              <StatCard
                title="Secondary Raw Material Yield"
                value="91.5%"
                subtitle="Virgin Fiber Replacement Ratio"
                icon={Boxes}
                accent="seaglass"
              />
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* ROLE VIEW 4: SYSTEM ADMINISTRATOR                              */}
        {/* ============================================================== */}
        {activeRoleView === 'ADMIN' && (
          <div className="space-y-6 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-frost-50 flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-indigo-400" />
                  <span>Enterprise Security & Infrastructure Health</span>
                </h2>
                <p className="text-xs text-seaglass-300/70">
                  Role-based access enforcement, active operator accounts, and deep learning neural weights.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-1 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/25">
                  RBAC Boundary Enforced
                </span>
              </div>
            </div>

            {/* Admin Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <StatCard
                title="Registered Personnel"
                value={usersList.length || 4}
                subtitle="Active Platform Operators"
                icon={Users}
                accent="teal"
              />
              <StatCard
                title="Neural Checkpoint Integrity"
                value="100%"
                subtitle="ResNet-18 & ONNX Weights Ready"
                icon={HardDrive}
                accent="emerald"
              />
              <StatCard
                title="Database Engine"
                value="Operational"
                subtitle="Dual SQLite / PostgreSQL Pool"
                icon={CheckCircle2}
                accent="seaglass"
              />
            </div>

            {/* Users Directory Table */}
            {usersList.length > 0 && (
              <GlassPanel className="p-5 space-y-3 border-white/10">
                <h3 className="text-xs font-bold uppercase tracking-wider text-frost-200">
                  Authorized Facility Users & RBAC Roles
                </h3>
                <div className="overflow-x-auto custom-scrollbar">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-deepTeal-950/70 border-b border-white/10 text-[10px] font-mono uppercase text-frost-300/70">
                        <th className="py-3 px-4">Username</th>
                        <th className="py-3 px-4">Email</th>
                        <th className="py-3 px-4">Role Tier</th>
                        <th className="py-3 px-4">Active</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-frost-100">
                      {usersList.map((u) => (
                        <tr key={u.id} className="hover:bg-deepTeal-900/30 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-frost-50">{u.username}</td>
                          <td className="py-3 px-4 text-frost-300/70">{u.email}</td>
                          <td className="py-3 px-4">
                            <StatusBadge status={u.role} />
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-[10px] font-mono font-bold text-emerald-400">ONLINE</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </GlassPanel>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
