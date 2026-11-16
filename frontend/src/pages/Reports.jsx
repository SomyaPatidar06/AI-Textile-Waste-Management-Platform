import React, { useState, useEffect } from 'react';
import api from '../api';
import NotificationBell from '../components/NotificationBell';
import GlassPanel from '../components/ui/GlassPanel';
import GlassCard from '../components/ui/GlassCard';
import StatCard from '../components/ui/StatCard';
import StatusBadge from '../components/ui/StatusBadge';
import GlassModal from '../components/ui/GlassModal';
import {
  FileBarChart,
  Download,
  Award,
  Leaf,
  Droplets,
  Zap,
  CheckCircle2,
  AlertCircle,
  Search,
  ExternalLink,
  Printer,
  ShieldCheck,
  Menu,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function Reports({ onToggleMobileNav }) {
  const [esgData, setEsgData] = useState(null);
  const [batches, setBatches] = useState([]);
  const [selectedBatchId, setSelectedBatchId] = useState('');
  const [certificate, setCertificate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  // Certificate Verification Tool State
  const [verifyCode, setVerifyCode] = useState('');
  const [verifyResult, setVerifyResult] = useState(null);
  const [verifyError, setVerifyError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const [esgRes, batchRes] = await Promise.all([
          api.get('/reports/esg-summary'),
          api.get('/batches?limit=50')
        ]);
        setEsgData(esgRes.data);
        setBatches(batchRes.data);
        if (batchRes.data.length > 0) {
          setSelectedBatchId(batchRes.data[0].id);
        }
      } catch (err) {
        console.error('Failed to load ESG report data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReportData();
  }, []);

  const handleDownloadCsv = async () => {
    setIsExporting(true);
    try {
      const res = await api.get('/reports/export/csv', { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'textile_waste_analyses.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
    } catch (err) {
      console.error('Failed to export CSV:', err);
      alert('Failed to download CSV export. Please ensure you are authenticated.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleGenerateCertificate = async () => {
    if (!selectedBatchId) return;
    try {
      const res = await api.get(`/reports/batch/${selectedBatchId}/certificate`);
      setCertificate(res.data);
    } catch (err) {
      alert('Failed to generate batch certificate.');
    }
  };

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    if (!verifyCode.trim()) return;

    setIsVerifying(true);
    setVerifyError('');
    setVerifyResult(null);

    try {
      const res = await api.get(`/reports/certificate/verify/${encodeURIComponent(verifyCode.trim())}`);
      setVerifyResult(res.data);
    } catch (err) {
      setVerifyError(err.response?.data?.detail || 'Certificate identifier not found in the public ledger.');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-midnight-950 ambient-mesh textile-grid">
      {/* Top Header */}
      <header className="liquid-glass border-b border-white/10 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 sticky top-0 z-30">
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
                Sustainability Intelligence & Passports
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
                ISO-14040 LCA
              </span>
            </div>
            <p className="text-xs text-seaglass-300/70">
              Quantitative avoided lifecycle impact, ESG disclosures, and verifiable circular passports
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadCsv}
            disabled={isExporting}
            className="px-4 py-2 rounded-xl bg-midnight-900/80 hover:bg-deepTeal-900/50 border border-white/10 text-frost-100 text-xs font-semibold flex items-center gap-2 transition-all shadow-glass-sm disabled:opacity-50"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            <span>{isExporting ? 'Generating CSV...' : 'Export Audit CSV'}</span>
          </button>
          <NotificationBell />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-8">
        {exportSuccess && (
          <div className="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>CSV audit export generated and downloaded successfully.</span>
          </div>
        )}

        {/* Top Quantitative ESG Savings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <StatCard
            title="Avoided Carbon Footprint"
            value={esgData?.environmental_savings?.co2_emissions_avoided_kg ? (esgData.environmental_savings.co2_emissions_avoided_kg).toLocaleString() : '0'}
            unit="kg CO2e"
            subtitle="Virgin Polyester & Cotton Displaced"
            icon={Leaf}
            accent="emerald"
            trend={{ label: 'ISO-14040 Validated', positive: true }}
          />
          <StatCard
            title="Freshwater Conserved"
            value={esgData?.environmental_savings?.water_conserved_liters ? (esgData.environmental_savings.water_conserved_liters).toLocaleString() : '0'}
            unit="Liters"
            subtitle="Agricultural Crop Water Saved"
            icon={Droplets}
            accent="teal"
            trend={{ label: 'Water Stewardship', positive: true }}
          />
          <StatCard
            title="Thermal Energy Avoided"
            value={esgData?.environmental_savings?.energy_conserved_kwh ? (esgData.environmental_savings.energy_conserved_kwh).toLocaleString() : '0'}
            unit="kWh"
            subtitle="Spinning & Scouring Energy Offset"
            icon={Zap}
            accent="seaglass"
            trend={{ label: 'Clean Energy', positive: true }}
          />
        </div>

        {/* Two-Column Workspace: Passport Generator & Public Verifier */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* LEFT: Digital Passport Issuance (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <GlassPanel elevated className="p-6 space-y-5 border-seaglass-300/20">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-frost-50 flex items-center gap-2">
                    <Award className="w-4 h-4 text-emerald-400" />
                    <span>Issue Digital Textile Circularity Passport</span>
                  </h3>
                  <p className="text-xs text-frost-300/60 mt-0.5">
                    Select a verified batch lot to compile certified circularity ratings and LCA metrics.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <label className="block text-xs font-semibold text-frost-200">
                  Select Certified Inbound Batch
                </label>
                <select
                  value={selectedBatchId}
                  onChange={(e) => setSelectedBatchId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-xs text-frost-100 focus:outline-none focus:border-emerald-500/50"
                >
                  {batches.map((b) => (
                    <option key={b.id} value={b.id} className="bg-midnight-900 text-frost-100">
                      {b.batch_code} &bull; {b.weight_kg} kg &bull; {b.declared_material} ({b.status})
                    </option>
                  ))}
                </select>

                <button
                  onClick={handleGenerateCertificate}
                  className="w-full py-2.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 font-bold text-xs uppercase tracking-wider rounded-xl shadow-glass-sm border border-emerald-400/30 flex items-center justify-center gap-2 transition-all"
                >
                  <Award className="w-4 h-4" />
                  <span>Compile Official Circularity Passport</span>
                </button>
              </div>

              {/* Certificate Preview Card */}
              {certificate && (
                <div className="mt-6 p-5 rounded-2xl bg-midnight-900/80 border border-emerald-500/30 space-y-4 shadow-glass-md animate-fadeIn">
                  <div className="flex items-start justify-between border-b border-white/10 pb-3">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 block font-bold">
                        Digital Product Passport
                      </span>
                      <h4 className="text-base font-extrabold text-frost-50 font-mono mt-0.5">
                        {certificate.certificate_id}
                      </h4>
                    </div>
                    <StatusBadge status={certificate.compliance_status} />
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div className="p-2.5 rounded-xl bg-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Batch Code</span>
                      <strong className="text-frost-50 font-mono block mt-0.5">{certificate.batch_code}</strong>
                    </div>
                    <div className="p-2.5 rounded-xl bg-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Diverted Mass</span>
                      <strong className="text-frost-50 font-mono block mt-0.5">{certificate.weight_kg} kg</strong>
                    </div>
                    <div className="p-2.5 rounded-xl bg-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Circularity Score</span>
                      <strong className="text-emerald-400 font-mono block mt-0.5">
                        {certificate.average_circularity_score?.toFixed(1)} / 100
                      </strong>
                    </div>
                    <div className="p-2.5 rounded-xl bg-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Verified Scans</span>
                      <strong className="text-frost-50 font-mono block mt-0.5">{certificate.scans_verified}</strong>
                    </div>
                  </div>

                  {/* Print & External View Actions */}
                  <div className="flex items-center justify-between pt-2">
                    <a
                      href={`/api/v1/reports/batch/${selectedBatchId}/certificate/html`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-seaglass-300 hover:text-seaglass-100 transition-colors"
                    >
                      <Printer className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Print or Save PDF Certificate</span>
                      <ExternalLink className="w-3 h-3 text-frost-300/50" />
                    </a>

                    <span className="text-[10px] text-frost-300/50 font-mono">
                      Cryptographic Stamp Active
                    </span>
                  </div>
                </div>
              )}
            </GlassPanel>
          </div>

          {/* RIGHT: Public Certificate Verification Tool (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <GlassPanel className="p-6 space-y-4 border-white/10">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-frost-100">
                  Public Certificate Authenticity Verification
                </h3>
              </div>

              <p className="text-xs text-frost-300/70 leading-relaxed">
                Supply chain auditors and recycling partners can verify any issued certificate using its unique code.
              </p>

              <form onSubmit={handleVerifyCode} className="space-y-3">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
                    <Search className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={verifyCode}
                    onChange={(e) => setVerifyCode(e.target.value)}
                    placeholder="e.g. CERT-BATCH-P6-REAL-1794740587"
                    className="w-full pl-10 pr-4 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-xs text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60 font-mono"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isVerifying}
                  className="w-full py-2 px-4 rounded-xl bg-midnight-900/80 hover:bg-deepTeal-900/50 border border-white/10 text-frost-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{isVerifying ? 'Querying Public Ledger...' : 'Validate Certificate Authenticity'}</span>
                </button>
              </form>

              {verifyError && (
                <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{verifyError}</span>
                </div>
              )}

              {verifyResult && (
                <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-3 text-xs animate-fadeIn">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-emerald-300 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Verified Authentic</span>
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                      STATUS: {verifyResult.verification_status}
                    </span>
                  </div>

                  <div className="space-y-1.5 font-mono text-[11px] text-frost-200 pt-2 border-t border-white/5">
                    <div className="flex justify-between">
                      <span className="text-frost-300/60">Batch Lot:</span>
                      <span className="font-bold">{verifyResult.batch_code}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-frost-300/60">Diverted Mass:</span>
                      <span>{verifyResult.weight_kg} kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-frost-300/60">Material:</span>
                      <span>{verifyResult.declared_material}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-frost-300/60">Circularity Rating:</span>
                      <span className="text-emerald-300 font-bold">{verifyResult.average_circularity_score} / 100</span>
                    </div>
                  </div>
                </div>
              )}
            </GlassPanel>
          </div>
        </div>
      </main>
    </div>
  );
}
