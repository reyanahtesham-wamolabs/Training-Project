import React, { useState } from 'react';

export default function NotificationDrawer({ notifications = [], onClose, onMarkAsRead, onUpdateDeliveryTime }) {
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'unread'
  const [reschedulingId, setReschedulingId] = useState(null);
  const [customDeliveryTime, setCustomDeliveryTime] = useState('');

  const handleStartReschedule = (n) => {
    setReschedulingId(n.id);
    const existing = n.delivered ? new Date(n.delivered) : new Date(Date.now() + 3600000);
    const tzOffset = existing.getTimezoneOffset() * 60000;
    const localISOTime = (new Date(existing - tzOffset)).toISOString().slice(0, 16);
    setCustomDeliveryTime(localISOTime);
  };

  const handleSaveReschedule = async (notificationId) => {
    if (!customDeliveryTime) return;
    const isoString = new Date(customDeliveryTime).toISOString();
    if (onUpdateDeliveryTime) {
      await onUpdateDeliveryTime(notificationId, isoString);
    }
    setReschedulingId(null);
  };

  const getCategory = (n) => {
    const subj = (n.subject || '').toLowerCase();
    if (n.related_task_id || subj.includes('task')) return 'tasks';
    if (n.related_project_id || subj.includes('project')) return 'projects';
    if (n.related_message_id || subj.includes('message') || subj.includes('chat')) return 'messages';
    if (n.related_comment_id || subj.includes('comment')) return 'comments';
    return 'system';
  };

  const categories = [
    { id: 'all', label: 'All Topics', icon: '🌐' },
    { id: 'tasks', label: 'Tasks', icon: '📋' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'messages', label: 'Chat', icon: '💬' },
    { id: 'comments', label: 'Comments', icon: '🗣️' }
  ];

  const getCategoryBadge = (cat) => {
    switch (cat) {
      case 'tasks':
        return { label: 'Task', color: 'var(--primary)', bg: 'rgba(99, 102, 241, 0.15)' };
      case 'projects':
        return { label: 'Project', color: 'var(--secondary)', bg: 'rgba(168, 85, 247, 0.15)' };
      case 'messages':
        return { label: 'Chat', color: 'var(--emerald)', bg: 'rgba(16, 185, 129, 0.15)' };
      case 'comments':
        return { label: 'Comment', color: 'var(--cyan)', bg: 'rgba(6, 182, 212, 0.15)' };
      default:
        return { label: 'System', color: 'var(--amber)', bg: 'rgba(245, 158, 11, 0.15)' };
    }
  };

  const unreadTotal = notifications.filter(n => !n.read).length;

  const filteredNotifications = notifications.filter(n => {
    const cat = getCategory(n);
    if (categoryFilter !== 'all') {
      if (categoryFilter === 'projects') {
        if (cat !== 'projects' && cat !== 'system') return false;
      } else {
        if (cat !== categoryFilter) return false;
      }
    }
    if (statusFilter === 'unread' && n.read) return false;
    return true;
  });

  const sortedNotifications = [...filteredNotifications].sort((a, b) => {
    const now = Date.now();
    const aTime = a.delivered ? new Date(a.delivered).getTime() : 0;
    const bTime = b.delivered ? new Date(b.delivered).getTime() : 0;

    const aDiffMin = (aTime - now) / 60000;
    const bDiffMin = (bTime - now) / 60000;

    const aIsUnder10 = aDiffMin >= 0 && aDiffMin <= 10;
    const bIsUnder10 = bDiffMin >= 0 && bDiffMin <= 10;

    if (aIsUnder10 !== bIsUnder10) return aIsUnder10 ? -1 : 1;
    if (a.read !== b.read) return a.read ? 1 : -1;
    return bTime - aTime;
  });

  return (
    <div className="modal-overlay" onClick={onClose} style={{ justifyContent: 'flex-end', padding: 0 }}>
      <div
        className="glass-panel"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '420px',
          height: '100vh',
          borderRadius: 0,
          borderRight: 'none',
          borderTop: 'none',
          borderBottom: 'none',
          padding: '20px 24px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>🔔 Notifications</h3>
            {unreadTotal > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                {unreadTotal} unread total
              </span>
            )}
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        {/* Filter Section */}
        <div style={{ marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Status Filter Toggle */}
          <div style={{ display: 'flex', background: 'rgba(255,255,255,0.04)', padding: '3px', borderRadius: 'var(--radius-sm)' }}>
            <button
              style={{
                flex: 1,
                padding: '6px',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                background: statusFilter === 'all' ? 'var(--primary)' : 'transparent',
                color: statusFilter === 'all' ? '#fff' : 'var(--text-muted)',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onClick={() => setStatusFilter('all')}
            >
              All Statuses ({notifications.length})
            </button>
            <button
              style={{
                flex: 1,
                padding: '6px',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                background: statusFilter === 'unread' ? 'var(--primary)' : 'transparent',
                color: statusFilter === 'unread' ? '#fff' : 'var(--text-muted)',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onClick={() => setStatusFilter('unread')}
            >
              Unread Only ({unreadTotal})
            </button>
          </div>

          {/* Category Filter Chips */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {categories.map((cat) => {
              const isActive = categoryFilter === cat.id;
              const count = cat.id === 'all'
                ? notifications.length
                : notifications.filter(n => getCategory(n) === cat.id).length;

              return (
                <button
                  key={cat.id}
                  onClick={() => setCategoryFilter(cat.id)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '4px 10px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.74rem',
                    fontWeight: 600,
                    border: '1px solid',
                    borderColor: isActive ? 'var(--primary)' : 'var(--border-light)',
                    background: isActive ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span>{cat.icon}</span>
                  <span>{cat.label}</span>
                  <span style={{ fontSize: '0.68rem', opacity: 0.7 }}>({count})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Notifications List */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {sortedNotifications.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '4px' }}>No notifications found</p>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>
                Try switching topic filters or clearing status filters.
              </span>
            </div>
          ) : (
            sortedNotifications.map((n) => {
              const cat = getCategory(n);
              const badge = getCategoryBadge(cat);

              const now = Date.now();
              const nTime = n.delivered ? new Date(n.delivered).getTime() : 0;
              const diffMin = (nTime - now) / 60000;
              const isUnder10m = diffMin >= 0 && diffMin <= 10;
              const isUnder3m = diffMin >= 0 && diffMin <= 3;

              return (
                <div
                  key={n.id}
                  className="glass-panel"
                  style={{
                    padding: '12px 14px',
                    opacity: n.read ? 0.6 : 1,
                    borderLeft: isUnder3m
                      ? '3px solid var(--rose)'
                      : isUnder10m
                      ? '3px solid var(--amber)'
                      : n.read
                      ? '1px solid var(--border-light)'
                      : '3px solid var(--primary)',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      <span
                        style={{
                          fontSize: '0.68rem',
                          fontWeight: 700,
                          color: badge.color,
                          background: badge.bg,
                          padding: '2px 6px',
                          borderRadius: 'var(--radius-sm)',
                          textTransform: 'uppercase'
                        }}
                      >
                        {badge.label}
                      </span>
                      {isUnder10m && (
                        <span
                          style={{
                            fontSize: '0.68rem',
                            fontWeight: 700,
                            color: '#ffffff',
                            background: isUnder3m ? 'var(--rose)' : 'var(--amber)',
                            padding: '2px 6px',
                            borderRadius: 'var(--radius-sm)',
                            textTransform: 'uppercase',
                            boxShadow: isUnder3m ? '0 0 8px rgba(239, 68, 68, 0.6)' : 'none'
                          }}
                        >
                          {isUnder3m ? '⚡ DUE IN < 3M' : '🔥 DUE IN < 10M'}
                        </span>
                      )}
                      <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{n.subject}</span>
                    </div>

                    {!n.read && (
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ fontSize: '0.68rem', padding: '1px 6px', flexShrink: 0, marginLeft: '8px' }}
                        onClick={() => onMarkAsRead(n.id)}
                      >
                        Mark Read
                      </button>
                    )}
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '6px', lineHeight: 1.4 }}>
                    {n.text}
                  </p>

                  {reschedulingId === n.id ? (
                    <div style={{ marginTop: '8px', background: 'rgba(255,255,255,0.03)', padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)' }}>
                      <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                        Reschedule Delivery Time:
                      </label>
                      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        <input
                          type="datetime-local"
                          className="form-input"
                          style={{ fontSize: '0.75rem', padding: '3px 6px', flex: 1 }}
                          value={customDeliveryTime}
                          onChange={(e) => setCustomDeliveryTime(e.target.value)}
                        />
                        <button
                          className="btn btn-primary btn-sm"
                          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                          onClick={() => handleSaveReschedule(n.id)}
                        >
                          Save
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                          onClick={() => setReschedulingId(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                        📅 Delivered: {n.delivered
                          ? new Date(n.delivered).toLocaleString([], { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
                          : '—'}
                      </span>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ fontSize: '0.68rem', padding: '2px 8px' }}
                        onClick={() => handleStartReschedule(n)}
                      >
                        ⏰ Reschedule
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
