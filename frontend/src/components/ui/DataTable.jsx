import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

/**
 * DataTable — High-legibility industrial data table.
 * Uses opaque/high-contrast cell backgrounds to prevent optical noise while keeping a frosted glass container.
 */
export default function DataTable({
  columns,
  data = [],
  isLoading = false,
  emptyMessage = 'No records found.',
  page = 1,
  pageSize = 10,
  totalItems = 0,
  onPageChange = null,
  className = ''
}) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  return (
    <div className={`liquid-glass rounded-2xl border border-white/10 overflow-hidden shadow-glass-md ${className}`}>
      <div className="overflow-x-auto custom-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-deepTeal-950/70 border-b border-white/10 text-[11px] font-semibold uppercase tracking-wider text-frost-300/80">
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`py-3.5 px-4 ${col.className || ''}`}
                  style={col.width ? { width: col.width } : {}}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-xs text-frost-100 font-normal">
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-frost-300/60">
                  <div className="inline-flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    <span>Loading data records...</span>
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-frost-300/50">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, rowIdx) => (
                <tr
                  key={row.id || rowIdx}
                  className="bg-midnight-900/40 hover:bg-deepTeal-900/40 transition-colors"
                >
                  {columns.map((col, colIdx) => (
                    <td key={colIdx} className={`py-3.5 px-4 ${col.cellClassName || ''}`}>
                      {col.render ? col.render(row, rowIdx) : row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      {onPageChange && totalItems > pageSize && (
        <div className="p-3.5 border-t border-white/10 bg-midnight-950/50 flex items-center justify-between text-xs text-frost-300/70">
          <div>
            Showing <span className="font-semibold text-frost-100 font-mono">{(page - 1) * pageSize + 1}</span> to{' '}
            <span className="font-semibold text-frost-100 font-mono">
              {Math.min(page * pageSize, totalItems)}
            </span>{' '}
            of <span className="font-semibold text-frost-100 font-mono">{totalItems}</span> entries
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onPageChange(1)}
              disabled={page <= 1}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="First Page"
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Previous Page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="px-2 font-mono font-medium text-frost-100">
              Page {page} of {totalPages}
            </span>

            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Next Page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(totalPages)}
              disabled={page >= totalPages}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Last Page"
            >
              <ChevronsRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
