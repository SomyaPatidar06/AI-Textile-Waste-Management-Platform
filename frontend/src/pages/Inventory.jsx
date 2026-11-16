import React, { useState, useEffect } from 'react';
import api from '../api';
import NotificationBell from '../components/NotificationBell';
import GlassPanel from '../components/ui/GlassPanel';
import GlassCard from '../components/ui/GlassCard';
import StatusBadge from '../components/ui/StatusBadge';
import GlassModal from '../components/ui/GlassModal';
import FormField from '../components/ui/FormField';
import DataTable from '../components/ui/DataTable';
import EmptyState from '../components/ui/EmptyState';
import {
  Boxes,
  Plus,
  Search,
  Filter,
  History,
  AlertTriangle,
  ArrowRight,
  Clock,
  CheckCircle2,
  X,
  Layers,
  MapPin,
  Calendar,
  Scale,
  Menu,
  Sparkles
} from 'lucide-react';

export default function Inventory({ onToggleMobileNav }) {
  const [batches, setBatches] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedBatchHistory, setSelectedBatchHistory] = useState(null);
  const [statusTransitionModal, setStatusTransitionModal] = useState(null); // { batchId, nextStatus, notes }

  // New batch form state
  const [newBatch, setNewBatch] = useState({
    batch_code: '',
    weight_kg: '',
    declared_material: 'Cotton',
    source_type: 'Post-Consumer Garments',
    location: '',
    notes: '',
  });

  const fetchBatches = async () => {
    setIsLoading(true);
    setError('');
    try {
      let url = '/batches?limit=100';
      if (statusFilter) url += `&status=${statusFilter}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      const res = await api.get(url);
      setBatches(res.data);
    } catch (err) {
      console.error('Failed to load inventory batches:', err);
      setError('Failed to fetch batches from server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, [statusFilter, search]);

  const handleCreateBatch = async (e) => {
    e.preventDefault();
    try {
      await api.post('/batches', {
        ...newBatch,
        weight_kg: parseFloat(newBatch.weight_kg),
      });
      setShowCreateModal(false);
      setNewBatch({
        batch_code: '',
        weight_kg: '',
        declared_material: 'Cotton',
        source_type: 'Post-Consumer Garments',
        location: '',
        notes: '',
      });
      fetchBatches();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create batch');
    }
  };

  const handleExecuteStatusTransition = async (e) => {
    e.preventDefault();
    if (!statusTransitionModal) return;

    try {
      await api.patch(`/batches/${statusTransitionModal.batchId}/status`, {
        status: statusTransitionModal.nextStatus,
        notes: statusTransitionModal.notes || `Transitioned to ${statusTransitionModal.nextStatus}`,
      });
      setStatusTransitionModal(null);
      fetchBatches();
    } catch (err) {
      alert(err.response?.data?.detail || 'Status transition failed.');
    }
  };

  const viewHistory = async (batchId) => {
    try {
      const res = await api.get(`/batches/${batchId}`);
      setSelectedBatchHistory(res.data);
    } catch (err) {
      alert('Could not retrieve audit trail for this batch.');
    }
  };

  const getNextStatus = (current) => {
    switch (current) {
      case 'COLLECTED': return 'SORTED';
      case 'SORTED': return 'PROCESSED';
      case 'PROCESSED': return 'DISPATCHED';
      default: return null;
    }
  };

  // DataTable columns definition
  const columns = [
    {
      header: 'Batch Identifier',
      accessor: 'batch_code',
      className: 'font-mono text-frost-50 font-bold',
      render: (row) => (
        <div>
          <span className="font-mono font-bold text-frost-50">{row.batch_code}</span>
          {row.location && (
            <span className="text-[10px] text-frost-300/50 flex items-center gap-1 mt-0.5">
              <MapPin className="w-2.5 h-2.5 text-seaglass-300/60" /> {row.location}
            </span>
          )}
        </div>
      )
    },
    {
      header: 'Declared Material',
      accessor: 'declared_material',
      render: (row) => (
        <span className="font-medium text-frost-100">{row.declared_material}</span>
      )
    },
    {
      header: 'Total Mass',
      accessor: 'weight_kg',
      render: (row) => (
        <span className="font-mono text-emerald-400 font-bold">{row.weight_kg} kg</span>
      )
    },
    {
      header: 'Source Lot Type',
      accessor: 'source_type',
      render: (row) => (
        <span className="text-frost-300/80">{row.source_type}</span>
      )
    },
    {
      header: 'Current Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />
    },
    {
      header: 'Actions',
      accessor: 'actions',
      cellClassName: 'text-right',
      render: (row) => {
        const next = getNextStatus(row.status);
        return (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => viewHistory(row.id)}
              className="p-1.5 rounded-lg border border-white/10 hover:bg-white/10 text-frost-300 hover:text-frost-50 transition-colors"
              title="Audit Trail Timeline"
            >
              <History className="w-3.5 h-3.5" />
            </button>

            {next && (
              <button
                onClick={() =>
                  setStatusTransitionModal({
                    batchId: row.id,
                    batchCode: row.batch_code,
                    currentStatus: row.status,
                    nextStatus: next,
                    notes: `Advanced to ${next} sorting stage.`
                  })
                }
                className="px-2.5 py-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-semibold flex items-center gap-1 transition-colors"
              >
                <span>Advance to {next}</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            )}
          </div>
        );
      }
    }
  ];

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-midnight-950 ambient-mesh textile-grid">
      {/* Top Header */}
      <header className="liquid-glass border-b border-white/10 px-6 py-4 flex items-center justify-between sticky top-0 z-30">
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
                Textile Batch Inventory
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
                Audit Trail Tracked
              </span>
            </div>
            <p className="text-xs text-seaglass-300/70">
              Facility consignment intake, material sorting stages, and state machine lifecycle
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-emerald-400/30 flex items-center gap-1.5 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register Batch</span>
          </button>
          <NotificationBell />
        </div>
      </header>

      {/* Main Inventory Workspace */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Search & Filter Toolbar */}
        <GlassPanel className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-frost-300/40">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by batch code, material, location..."
              className="w-full pl-10 pr-4 py-2 bg-midnight-900/60 border border-white/10 rounded-xl text-xs text-frost-50 placeholder-frost-300/30 focus:outline-none focus:border-emerald-500/60"
            />
          </div>

          {/* Status Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1 sm:pb-0 text-xs font-medium text-frost-300">
            <span className="text-[10px] uppercase font-mono tracking-wider mr-1 text-frost-300/50">
              Filter:
            </span>
            {['', 'COLLECTED', 'SORTED', 'PROCESSED', 'DISPATCHED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg border transition-all text-xs ${
                  statusFilter === st
                    ? 'bg-emerald-600/25 border-emerald-500/40 text-emerald-300 font-bold shadow-glass-sm'
                    : 'bg-midnight-900/40 border-white/5 hover:bg-white/5 text-frost-300/70'
                }`}
              >
                {st || 'All Batches'}
              </button>
            ))}
          </div>
        </GlassPanel>

        {/* Inventory DataTable */}
        <DataTable
          columns={columns}
          data={batches}
          isLoading={isLoading}
          emptyMessage="No matching textile batches found in the inventory registry."
        />
      </main>

      {/* Register Batch Modal */}
      <GlassModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Register Inbound Textile Lot"
        subtitle="Initialize physical consignment into the automated sorting state machine."
      >
        <form onSubmit={handleCreateBatch} className="space-y-4">
          <FormField
            label="Batch Identifier Code"
            required
            value={newBatch.batch_code}
            onChange={(e) => setNewBatch({ ...newBatch, batch_code: e.target.value })}
            placeholder="e.g. BATCH-2026-COTTON-04"
            helperText="Unique uppercase identifier for tracking across conveyors."
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Consignment Mass (kg)"
              type="number"
              required
              step="0.1"
              min="0.1"
              value={newBatch.weight_kg}
              onChange={(e) => setNewBatch({ ...newBatch, weight_kg: e.target.value })}
              placeholder="e.g. 350.5"
            />

            <FormField
              label="Declared Fiber Composition"
              type="select"
              required
              value={newBatch.declared_material}
              onChange={(e) => setNewBatch({ ...newBatch, declared_material: e.target.value })}
              options={[
                { value: 'Cotton', label: 'Cotton (Natural Cellulose)' },
                { value: 'Polyester', label: 'Polyester (Synthetic Polymer)' },
                { value: 'Poly-Cotton Blend', label: 'Poly-Cotton Blend (Mixed)' },
                { value: 'Denim', label: 'Denim (Heavy Cotton Twill)' },
                { value: 'Wool', label: 'Wool (Natural Protein)' },
                { value: 'Silk', label: 'Silk (Continuous Filament)' },
                { value: 'Linen', label: 'Linen (Flax Fiber)' },
                { value: 'Nylon', label: 'Nylon (Polyamide)' },
              ]}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField
              label="Source Consignment Type"
              type="select"
              required
              value={newBatch.source_type}
              onChange={(e) => setNewBatch({ ...newBatch, source_type: e.target.value })}
              options={[
                { value: 'Post-Consumer Garments', label: 'Post-Consumer Garments' },
                { value: 'Pre-Consumer Factory Scrap', label: 'Pre-Consumer Factory Scrap' },
                { value: 'Industrial Linens & Rags', label: 'Industrial Linens & Rags' },
                { value: 'Retail Overstock & Returns', label: 'Retail Overstock & Returns' },
              ]}
            />

            <FormField
              label="Facility Location / Bay"
              value={newBatch.location}
              onChange={(e) => setNewBatch({ ...newBatch, location: e.target.value })}
              placeholder="e.g. North Bay 4"
            />
          </div>

          <FormField
            label="Intake Notes & Observations"
            type="textarea"
            rows={2}
            value={newBatch.notes}
            onChange={(e) => setNewBatch({ ...newBatch, notes: e.target.value })}
            placeholder="e.g. Received from municipal sorting partner in dry conditions."
          />

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/5 text-xs font-semibold text-frost-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-emerald-400/30"
            >
              Confirm Registration
            </button>
          </div>
        </form>
      </GlassModal>

      {/* Status History Timeline Modal */}
      <GlassModal
        isOpen={!!selectedBatchHistory}
        onClose={() => setSelectedBatchHistory(null)}
        title={`Audit Trail: ${selectedBatchHistory?.batch_code}`}
        subtitle={`Immutable historical status transitions for batch lot #${selectedBatchHistory?.id?.slice(0, 8)}`}
      >
        <div className="space-y-4">
          <div className="p-3.5 rounded-xl bg-midnight-900/60 border border-white/5 grid grid-cols-3 gap-2 text-center text-xs">
            <div>
              <span className="text-[10px] text-frost-300/50 uppercase block">Total Mass</span>
              <span className="font-mono font-bold text-frost-50">{selectedBatchHistory?.weight_kg} kg</span>
            </div>
            <div>
              <span className="text-[10px] text-frost-300/50 uppercase block">Material</span>
              <span className="font-semibold text-frost-50">{selectedBatchHistory?.declared_material}</span>
            </div>
            <div>
              <span className="text-[10px] text-frost-300/50 uppercase block">Current Stage</span>
              <StatusBadge status={selectedBatchHistory?.status} />
            </div>
          </div>

          <h4 className="text-xs font-bold uppercase tracking-wider text-frost-200 pt-2">
            State Machine Progression
          </h4>

          <div className="space-y-3 relative pl-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
            {selectedBatchHistory?.status_history?.map((h, idx) => (
              <div key={h.id || idx} className="relative">
                <span className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-midnight-950" />
                <div className="p-3 rounded-xl bg-midnight-900/50 border border-white/5 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-frost-50">
                      {h.old_status ? `${h.old_status} → ${h.new_status}` : `Initial: ${h.new_status}`}
                    </span>
                    <span className="text-[10px] font-mono text-frost-300/50">
                      {h.created_at || h.timestamp
                        ? new Date(h.created_at || h.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })
                        : 'Recorded'}
                    </span>
                  </div>
                  {h.notes && (
                    <p className="text-xs text-frost-300/70 italic">"{h.notes}"</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4 border-t border-white/10">
            <button
              onClick={() => setSelectedBatchHistory(null)}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-frost-100"
            >
              Close Audit Log
            </button>
          </div>
        </div>
      </GlassModal>

      {/* Confirm Status Transition Dialog Modal */}
      <GlassModal
        isOpen={!!statusTransitionModal}
        onClose={() => setStatusTransitionModal(null)}
        title={`Advance Lifecycle Stage: ${statusTransitionModal?.batchCode}`}
        subtitle={`Transitioning consignment from ${statusTransitionModal?.currentStatus} to ${statusTransitionModal?.nextStatus}.`}
      >
        <form onSubmit={handleExecuteStatusTransition} className="space-y-4">
          <FormField
            label="Operator Progression Notes"
            type="textarea"
            rows={3}
            required
            value={statusTransitionModal?.notes || ''}
            onChange={(e) =>
              setStatusTransitionModal({
                ...statusTransitionModal,
                notes: e.target.value
              })
            }
            placeholder="e.g. Completed optical sorting gate. Mechanical shredder feed engaged."
            helperText="Notes are committed to the immutable cryptographic audit trail."
          />

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
            <button
              type="button"
              onClick={() => setStatusTransitionModal(null)}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/5 text-xs font-semibold text-frost-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm border border-emerald-400/30"
            >
              Advance to {statusTransitionModal?.nextStatus}
            </button>
          </div>
        </form>
      </GlassModal>
    </div>
  );
}
