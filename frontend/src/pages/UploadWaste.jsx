import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import NotificationBell from '../components/NotificationBell';
import GlassPanel from '../components/ui/GlassPanel';
import GlassCard from '../components/ui/GlassCard';
import StatusBadge from '../components/ui/StatusBadge';
import GlassModal from '../components/ui/GlassModal';
import {
  UploadCloud,
  FileImage,
  AlertTriangle,
  CheckCircle2,
  Leaf,
  Droplets,
  Zap,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Eye,
  EyeOff,
  Layers,
  Sparkles,
  Sliders,
  ShieldAlert,
  ArrowRight,
  Maximize2,
  Check,
  Activity,
  Boxes,
  HelpCircle,
  Menu
} from 'lucide-react';

export default function UploadWaste({ onToggleMobileNav }) {
  const [batches, setBatches] = useState([]);
  const [selectedBatchId, setSelectedBatchId] = useState('');
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Interactive Inspection Canvas State
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);
  const [selectedBoxIdx, setSelectedBoxIdx] = useState(null);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  // Operator Verification & Override Modal State
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideMaterial, setOverrideMaterial] = useState('');
  const [overrideDefect, setOverrideDefect] = useState('');
  const [operatorNotes, setOperatorNotes] = useState('');
  const [isOverridden, setIsOverridden] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState('');

  // Recent Scans History State
  const [recentScans, setRecentScans] = useState([]);

  // Fetch batches and recent scans on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [batchRes, scansRes] = await Promise.all([
          api.get('/batches?limit=50'),
          api.get('/analysis?limit=5')
        ]);
        setBatches(batchRes.data);
        setRecentScans(scansRes.data);
      } catch (err) {
        console.warn('Failed to load initial studio data:', err);
      }
    };
    fetchData();
  }, []);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    if (selected.size > 10 * 1024 * 1024) {
      setError('File exceeds 10 MB payload limit.');
      return;
    }

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(selected.type)) {
      setError('Unsupported file type. Please upload JPEG, PNG, or WEBP.');
      return;
    }

    setError('');
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
    setResult(null);
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    setSelectedBoxIdx(null);
    setIsOverridden(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange({ target: { files: [e.dataTransfer.files[0]] } });
    }
  };

  const handleScan = async (e) => {
    if (e) e.preventDefault();
    if (!file) {
      setError('Please select or drag an image into the studio canvas.');
      return;
    }

    setIsUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    if (selectedBatchId) {
      formData.append('batch_id', selectedBatchId);
    }

    try {
      const res = await api.post('/analysis/scan', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      setOverrideMaterial(res.data.material_prediction.replace(' (Visual Estimate)', ''));
      setOverrideDefect(res.data.defect_prediction);

      // Refresh recent scans list
      const updated = await api.get('/analysis?limit=5');
      setRecentScans(updated.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Inference pipeline failure. Please retry.');
    } finally {
      setIsUploading(false);
    }
  };

  // Canvas Pan Handlers
  const handleMouseDown = (e) => {
    if (zoomLevel <= 1) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPanOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetViewport = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    setSelectedBoxIdx(null);
  };

  const handleApplyOverride = (e) => {
    e.preventDefault();
    if (!result) return;

    setResult((prev) => ({
      ...prev,
      material_prediction: `${overrideMaterial} (Operator Confirmed)`,
      defect_prediction: overrideDefect,
      requires_manual_inspection: false,
      uncertainty_reason: `Verified by Operator: ${operatorNotes || 'Physical visual confirmation logged.'}`
    }));

    setIsOverridden(true);
    setShowOverrideModal(false);
    setFeedbackSuccess('Operator correction committed to session.');
    setTimeout(() => setFeedbackSuccess(''), 4000);
  };

  // Parse bounding boxes safely
  const boundingBoxes = result?.bounding_boxes
    ? (typeof result.bounding_boxes === 'string'
        ? JSON.parse(result.bounding_boxes)
        : result.bounding_boxes)
    : [];

  // Parse recommendations safely
  const recommendations = result?.recommendations
    ? (typeof result.recommendations === 'string'
        ? JSON.parse(result.recommendations)
        : result.recommendations)
    : [];

  // Parse scoring breakdown safely
  const scoringBreakdown = result?.scoring_breakdown
    ? (typeof result.scoring_breakdown === 'string'
        ? JSON.parse(result.scoring_breakdown)
        : result.scoring_breakdown)
    : null;

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-midnight-950 ambient-mesh textile-grid">
      {/* Top Application Header */}
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
                AI Textile Inspection Studio
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
                ONNX FastPath
              </span>
            </div>
            <p className="text-xs text-seaglass-300/70">
              Multi-scale spatial defect localization and circularity characterization
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <NotificationBell />
        </div>
      </header>

      {/* Main Studio Viewport */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-between text-xs text-rose-300 shadow-glass-sm animate-fadeIn">
            <div className="flex items-center gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError('')}
              className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 transition-colors"
            >
              Dismiss
            </button>
          </div>
        )}

        {feedbackSuccess && (
          <div className="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{feedbackSuccess}</span>
          </div>
        )}

        {/* Top Control Bar: Batch Link & Supported Specs */}
        <GlassPanel className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 flex-1 max-w-xl">
            <label className="text-xs font-semibold text-frost-200 tracking-wide shrink-0">
              Assigned Inventory Lot:
            </label>
            <select
              value={selectedBatchId}
              onChange={(e) => setSelectedBatchId(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-midnight-900/80 border border-white/10 text-xs text-frost-100 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">-- Standalone Inspection (No Batch Assigned) --</option>
              {batches.map((b) => (
                <option key={b.id} value={b.id} className="bg-midnight-900 text-frost-100">
                  {b.batch_code} ({b.weight_kg} kg &bull; {b.status})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-frost-300/60 font-mono">
            <span>Option B Optical Governance Active</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          </div>
        </GlassPanel>

        {/* Inspection Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* LEFT COLUMN: Image Inspection Canvas (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <GlassPanel className="overflow-hidden border border-white/10 shadow-glass-md flex flex-col">
              {/* Canvas Header & Optical Controls */}
              <div className="p-3.5 border-b border-white/10 bg-midnight-950/60 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <FileImage className="w-4 h-4 text-emerald-400" />
                  <span className="font-semibold text-frost-100">
                    {file ? file.name : 'Optical Sensor Viewport'}
                  </span>
                  {file && (
                    <span className="text-[10px] text-frost-300/50 font-mono">
                      ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                    </span>
                  )}
                </div>

                {previewUrl && (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setZoomLevel((z) => Math.min(z + 0.25, 3))}
                      className="p-1.5 rounded-lg border border-white/10 hover:bg-white/10 text-frost-200 transition-colors"
                      title="Zoom In"
                    >
                      <ZoomIn className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setZoomLevel((z) => Math.max(z - 0.25, 0.75))}
                      className="p-1.5 rounded-lg border border-white/10 hover:bg-white/10 text-frost-200 transition-colors"
                      title="Zoom Out"
                    >
                      <ZoomOut className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={resetViewport}
                      className="p-1.5 rounded-lg border border-white/10 hover:bg-white/10 text-frost-200 transition-colors"
                      title="Reset View"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                    <div className="w-px h-4 bg-white/10 mx-1" />
                    <button
                      onClick={() => setShowBoxes(!showBoxes)}
                      className={`px-2 py-1 rounded-lg border text-[11px] font-semibold flex items-center gap-1 transition-colors ${
                        showBoxes
                          ? 'bg-emerald-600/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-white/5 border-white/10 text-frost-300/60'
                      }`}
                      title="Toggle Defect Overlays"
                    >
                      {showBoxes ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                      <span>Overlays</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Viewport Canvas Body */}
              <div
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className={`relative min-h-[380px] sm:min-h-[440px] flex items-center justify-center p-4 overflow-hidden bg-midnight-950/80 ${
                  zoomLevel > 1 ? 'cursor-grab active:cursor-grabbing' : 'cursor-default'
                }`}
              >
                {!previewUrl ? (
                  /* Empty / Dropzone State */
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                    className="w-full h-full min-h-[340px] border-2 border-dashed border-white/15 rounded-2xl flex flex-col items-center justify-center p-6 text-center hover:border-emerald-500/40 transition-colors"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-deepTeal-800/40 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4 shadow-glass-glow">
                      <UploadCloud className="w-8 h-8" />
                    </div>
                    <h3 className="text-base font-bold text-frost-50">
                      Drag and drop textile swatch
                    </h3>
                    <p className="text-xs text-frost-300/60 mt-1 max-w-sm">
                      Upload high-resolution fabric scans in JPEG, PNG, or WEBP (up to 10 MB).
                    </p>

                    <label className="mt-5 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 font-bold text-xs uppercase tracking-wider shadow-glass-md border border-emerald-400/30 cursor-pointer transition-all">
                      Browse Files
                      <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                ) : (
                  /* Image with Spatial Bounding Box Overlays */
                  <div
                    className="relative inline-block select-none transition-transform duration-75 ease-out"
                    style={{
                      transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                      transformOrigin: 'center center'
                    }}
                  >
                    <img
                      src={previewUrl}
                      alt="Textile specimen under inspection"
                      className="max-h-[500px] w-auto rounded-xl object-contain shadow-glass-lg border border-white/10 pointer-events-none"
                    />

                    {/* Spatial Bounding Boxes */}
                    {showBoxes &&
                      boundingBoxes.map((box, idx) => {
                        const coords = box.box_2d || [0, 0, 0, 0];
                        const [ymin, xmin, ymax, xmax] = coords;
                        const top = `${ymin * 100}%`;
                        const left = `${xmin * 100}%`;
                        const height = `${(ymax - ymin) * 100}%`;
                        const width = `${(xmax - xmin) * 100}%`;
                        const isSelected = selectedBoxIdx === idx;

                        return (
                          <div
                            key={idx}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedBoxIdx(isSelected ? null : idx);
                            }}
                            className={`absolute transition-all cursor-pointer rounded pointer-events-auto ${
                              isSelected
                                ? 'border-2 border-emerald-400 bg-emerald-500/25 ring-2 ring-emerald-400/40 shadow-glass-glow'
                                : 'border-2 border-rose-400/90 bg-rose-500/15 hover:bg-rose-500/25'
                            }`}
                            style={{ top, left, width, height }}
                          >
                            <span className="absolute -top-6 left-0 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-midnight-950/90 text-frost-50 border border-white/20 whitespace-nowrap shadow-sm">
                              Approx. {box.label || 'Defect'} ({(box.confidence * 100).toFixed(0)}%)
                            </span>
                          </div>
                        );
                      })}
                  </div>
                )}
              </div>

              {/* Action Trigger Bar */}
              {previewUrl && (
                <div className="p-4 border-t border-white/10 bg-midnight-950/70 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <label className="px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 text-xs font-semibold text-frost-200 cursor-pointer">
                      Replace Image
                      <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                    </label>
                    <button
                      onClick={() => {
                        setFile(null);
                        setPreviewUrl('');
                        setResult(null);
                      }}
                      className="px-3 py-1.5 rounded-lg border border-rose-500/20 hover:bg-rose-500/10 text-xs font-semibold text-rose-300"
                    >
                      Clear
                    </button>
                  </div>

                  <button
                    onClick={handleScan}
                    disabled={isUploading}
                    className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-md border border-emerald-400/30 flex items-center gap-2 transition-all disabled:opacity-50"
                  >
                    {isUploading ? (
                      <>
                        <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                        <span>Running Neural Vision...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 text-emerald-300" />
                        <span>Execute AI Analysis</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </GlassPanel>

            {/* Quick Inspection Guide / Legend & Coarse Guidance Disclaimer */}
            <div className="space-y-2">
              <div className="grid grid-cols-3 gap-3 text-[11px] text-frost-300/70">
                <div className="p-3 rounded-xl liquid-glass border border-white/5 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0" />
                  <span>Green: Validated Weave</span>
                </div>
                <div className="p-3 rounded-xl liquid-glass border border-white/5 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400 shrink-0" />
                  <span>Red: Candidate Anomaly (Visual Guidance)</span>
                </div>
                <div className="p-3 rounded-xl liquid-glass border border-white/5 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shrink-0" />
                  <span>Amber: Manual Review</span>
                </div>
              </div>
              <div className="px-3.5 py-2 rounded-xl bg-midnight-950/60 border border-white/5 text-[11px] text-frost-300/60 flex items-center gap-2">
                <span className="text-emerald-400">ℹ️</span>
                <span>Coarse candidate anomaly sectors highlight approximate regions for bench inspection; not pixel-level segmentations.</span>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: AI Results Intelligence Panel (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            {!result ? (
              /* Awaiting Scan Placeholder */
              <GlassPanel className="p-8 text-center min-h-[460px] flex flex-col items-center justify-center border-dashed border-white/10">
                <div className="w-14 h-14 rounded-2xl bg-midnight-900/60 border border-white/10 flex items-center justify-center text-seaglass-300/40 mb-3">
                  <Activity className="w-7 h-7" />
                </div>
                <h4 className="text-sm font-bold text-frost-100">
                  Ready for Optical Characterization
                </h4>
                <p className="text-xs text-frost-300/50 mt-1 max-w-xs leading-relaxed">
                  Upload an image and run analysis to receive material estimates, spatial anomaly tags, and circularity LCA scores.
                </p>
              </GlassPanel>
            ) : (
              /* Full AI Characterization Results */
              <div className="space-y-4 animate-fadeIn">
                {/* 1. Primary Classification Card */}
                <GlassPanel elevated className="p-5 space-y-4 border-seaglass-300/20">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-frost-300/60">
                        Visual Material Classification
                      </span>
                      <h3 className="text-xl font-extrabold text-frost-50 mt-0.5">
                        {result.material_prediction}
                      </h3>
                      <span className="text-[10px] text-frost-300/50 block mt-0.5 font-mono">
                        6-Class Natural Fibers (Abaca, Cotton, Hessian, Linen, Silk, Wool)
                      </span>
                    </div>
                    <StatusBadge status={result.waste_category} />
                  </div>

                  {/* Confidence Bar */}
                  <div>
                    <div className="flex justify-between text-xs text-frost-300/70 mb-1.5 font-mono">
                      <span>Model Confidence</span>
                      <span className="font-bold text-frost-50">
                        {(result.material_confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 w-full bg-midnight-900 rounded-full overflow-hidden p-0.5 border border-white/10">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(result.material_confidence * 100, 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Option B Governance Notice */}
                  <div className="p-2.5 rounded-xl bg-midnight-900/60 border border-white/5 text-[11px] text-seaglass-300/80 flex items-start gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>
                      Option B Governance: Optical RGB classification is a visual estimate and cannot replace chemical fiber dissolution.
                    </span>
                  </div>

                  {/* Uncertainty / Inspection Alert */}
                  {result.requires_manual_inspection && (
                    <div className="p-3 rounded-xl bg-amber-500/15 border border-amber-500/30 text-xs text-amber-200 flex items-start gap-2.5">
                      <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block font-bold">Manual Inspection Advised</strong>
                        <span className="text-[11px] text-amber-300/80 leading-relaxed">
                          {result.uncertainty_reason || 'Low statistical margin detected across multi-class distributions.'}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Operator Correction Button */}
                  <button
                    onClick={() => setShowOverrideModal(true)}
                    className="w-full py-2 px-3 rounded-xl border border-white/10 hover:bg-white/5 text-xs font-semibold text-frost-200 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Sliders className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{isOverridden ? 'Operator Correction Applied' : 'Adjust / Verify Classification'}</span>
                  </button>
                </GlassPanel>

                {/* 2. Defect Characterization & Spatial Metrics */}
                <GlassPanel className="p-5 space-y-3 border-white/10">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-frost-300/60">
                      Surface Anomaly Characterization
                    </span>
                    <StatusBadge status={result.defect_prediction} />
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-midnight-900/50 border border-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Primary Anomaly</span>
                      <strong className="text-frost-100 font-semibold mt-0.5 block">
                        {result.defect_prediction}
                      </strong>
                    </div>
                    <div className="p-3 rounded-xl bg-midnight-900/50 border border-white/5">
                      <span className="text-[10px] text-frost-300/50 block uppercase">Candidate Sectors</span>
                      <strong className="text-frost-100 font-semibold mt-0.5 block font-mono">
                        {boundingBoxes.length} Guidance Regions
                      </strong>
                    </div>
                  </div>
                  <p className="text-[10px] text-frost-300/50 leading-relaxed">
                    Candidate sectors flag coarse regions with potential anomalies for operator bench review.
                  </p>
                </GlassPanel>

                {/* 3. Five-Factor Circularity Scoring Meter */}
                <GlassPanel className="p-5 space-y-4 border-white/10">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-frost-300/60">
                        Circularity Rating (5-Factor Formula)
                      </span>
                      <div className="flex items-baseline gap-2 mt-0.5">
                        <span className="text-2xl font-extrabold font-mono text-emerald-300">
                          {result.circularity_score?.toFixed(1)}
                        </span>
                        <span className="text-xs text-frost-300/60 font-mono">/ 100</span>
                      </div>
                    </div>
                    <StatusBadge status={result.circularity_category || 'Recoverable'} />
                  </div>

                  {/* 5 Component Sliders / Meters */}
                  {scoringBreakdown && (
                    <div className="space-y-2 pt-2 border-t border-white/5 text-[11px]">
                      <div>
                        <div className="flex justify-between text-frost-300/70 mb-1">
                          <span>Material Recyclability (35%)</span>
                          <span className="font-mono text-frost-100">{scoringBreakdown.material_recyclability}</span>
                        </div>
                        <div className="h-1.5 w-full bg-midnight-900 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${scoringBreakdown.material_recyclability}%` }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-frost-300/70 mb-1">
                          <span>Condition Integrity (20%)</span>
                          <span className="font-mono text-frost-100">{scoringBreakdown.material_condition}</span>
                        </div>
                        <div className="h-1.5 w-full bg-midnight-900 rounded-full overflow-hidden">
                          <div className="h-full bg-teal-400 rounded-full" style={{ width: `${scoringBreakdown.material_condition}%` }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-frost-300/70 mb-1">
                          <span>Reuse Potential (20%)</span>
                          <span className="font-mono text-frost-100">{scoringBreakdown.reuse_potential}</span>
                        </div>
                        <div className="h-1.5 w-full bg-midnight-900 rounded-full overflow-hidden">
                          <div className="h-full bg-seaglass-300 rounded-full" style={{ width: `${scoringBreakdown.reuse_potential}%` }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-frost-300/70 mb-1">
                          <span>Eco Efficiency (15%)</span>
                          <span className="font-mono text-frost-100">{scoringBreakdown.environmental_benefit}</span>
                        </div>
                        <div className="h-1.5 w-full bg-midnight-900 rounded-full overflow-hidden">
                          <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${scoringBreakdown.environmental_benefit}%` }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-frost-300/70 mb-1">
                          <span>Processing Feasibility (10%)</span>
                          <span className="font-mono text-frost-100">{scoringBreakdown.processing_feasibility}</span>
                        </div>
                        <div className="h-1.5 w-full bg-midnight-900 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-400 rounded-full" style={{ width: `${scoringBreakdown.processing_feasibility}%` }} />
                        </div>
                      </div>
                    </div>
                  )}
                </GlassPanel>

                {/* 4. Actionable 7-Pathway Recycling Recommendations */}
                <GlassPanel className="p-5 space-y-3 border-white/10">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-frost-300/60 block">
                    Actionable Recovery Pathways
                  </span>
                  <div className="space-y-2">
                    {recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-midnight-900/60 border border-white/5 text-xs text-frost-100 flex items-start gap-2.5 leading-relaxed"
                      >
                        <ArrowRight className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </GlassPanel>

                {/* 5. LCA Environmental Impact Forecast */}
                {result.environmental_impact && (
                  <GlassPanel className="p-5 border-white/10 space-y-3">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-frost-300/60 block">
                      Lifecycle Avoided Emissions (Per Batch Weight)
                    </span>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2.5 rounded-xl bg-midnight-900/50 border border-white/5">
                        <span className="text-xs font-extrabold font-mono text-emerald-300 block">
                          {result.environmental_impact.co2_savings_kg} kg
                        </span>
                        <span className="text-[10px] text-frost-300/50 uppercase">CO2 Avoided</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-midnight-900/50 border border-white/5">
                        <span className="text-xs font-extrabold font-mono text-seaglass-300 block">
                          {Number(result.environmental_impact.water_savings_liters).toLocaleString()} L
                        </span>
                        <span className="text-[10px] text-frost-300/50 uppercase">H2O Conserved</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-midnight-900/50 border border-white/5">
                        <span className="text-xs font-extrabold font-mono text-cyan-300 block">
                          {result.environmental_impact.energy_savings_kwh} kWh
                        </span>
                        <span className="text-[10px] text-frost-300/50 uppercase">Clean Energy</span>
                      </div>
                    </div>
                  </GlassPanel>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Operator Verification Modal */}
      <GlassModal
        isOpen={showOverrideModal}
        onClose={() => setShowOverrideModal(false)}
        title="Operator Classification Override"
        subtitle="Record physical manual verification notes according to facility QA standards."
      >
        <form onSubmit={handleApplyOverride} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-frost-200 mb-1">
              Confirmed Material Composition
            </label>
            <input
              type="text"
              required
              value={overrideMaterial}
              onChange={(e) => setOverrideMaterial(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-frost-200 mb-1">
              Confirmed Defect Classification
            </label>
            <input
              type="text"
              required
              value={overrideDefect}
              onChange={(e) => setOverrideDefect(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-frost-200 mb-1">
              Inspection Notes / Reason
            </label>
            <textarea
              rows={3}
              value={operatorNotes}
              onChange={(e) => setOperatorNotes(e.target.value)}
              placeholder="e.g. Verified by visual bench microscope: sample weave structure confirmed."
              className="w-full px-3.5 py-2.5 bg-midnight-900/60 border border-white/10 rounded-xl text-sm text-frost-50 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
            <button
              type="button"
              onClick={() => setShowOverrideModal(false)}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/5 text-xs font-semibold text-frost-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-frost-50 text-xs font-bold uppercase tracking-wider shadow-glass-sm"
            >
              Confirm Override
            </button>
          </div>
        </form>
      </GlassModal>
    </div>
  );
}
