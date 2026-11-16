import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check, Inbox, AlertTriangle, Layers, Scan } from 'lucide-react';
import api from '../api';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const fetchNotifications = async () => {
    try {
      const [listRes, countRes] = await Promise.all([
        api.get('/notifications?limit=10'),
        api.get('/notifications/unread-count')
      ]);
      setNotifications(listRes.data);
      setUnreadCount(countRes.data.unread_count);
    } catch (err) {
      console.warn('Failed to load notifications:', err);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 20000); // 20s poll
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkAsRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.post('/notifications/mark-all-read');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  const getCategoryIcon = (cat) => {
    const c = String(cat).toUpperCase();
    if (c.includes('INVENTORY') || c.includes('BATCH')) {
      return <Layers className="w-3.5 h-3.5 text-seaglass-300" />;
    }
    if (c.includes('DEFECT') || c.includes('SCAN')) {
      return <Scan className="w-3.5 h-3.5 text-emerald-400" />;
    }
    return <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />;
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2.5 rounded-xl border border-white/10 bg-midnight-900/60 hover:bg-deepTeal-900/60 text-frost-200 hover:text-frost-50 shadow-glass-sm transition-all focus:outline-none"
        title="Notifications"
        aria-label="Open notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-mono font-bold text-white bg-rose-600 rounded-full shadow-[0_0_8px_rgba(225,29,72,0.6)]">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 sm:w-96 liquid-glass-elevated glass-specular rounded-2xl shadow-glass-lg border border-seaglass-300/20 z-50 overflow-hidden animate-fadeIn">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-midnight-950/60">
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-frost-50 text-xs uppercase tracking-wider">
                System Alerts
              </h3>
              {unreadCount > 0 && (
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">
                  {unreadCount} new
                </span>
              )}
            </div>

            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-[11px] text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
              >
                <Check className="w-3 h-3" /> Mark all read
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-80 overflow-y-auto custom-scrollbar divide-y divide-white/5">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-xs text-frost-300/40 flex flex-col items-center gap-2">
                <Inbox className="w-6 h-6 text-frost-300/20" />
                <span>No active alerts registered.</span>
              </div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && handleMarkAsRead(n.id)}
                  className={`p-3.5 text-left transition-colors cursor-pointer hover:bg-deepTeal-900/40 ${
                    !n.is_read ? 'bg-emerald-950/30' : 'bg-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      {getCategoryIcon(n.category)}
                      <span className="text-xs font-bold text-frost-50">{n.title}</span>
                    </div>
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/5 text-seaglass-300/70 border border-white/5">
                      {n.category}
                    </span>
                  </div>

                  <p className="text-xs text-frost-200/70 mt-1 line-clamp-2 leading-relaxed">
                    {n.message}
                  </p>

                  <span className="text-[10px] text-frost-300/40 mt-1.5 block font-mono">
                    {new Date(n.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
