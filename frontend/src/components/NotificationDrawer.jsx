import React from 'react';

export default function NotificationDrawer({ notifications, onClose, onMarkAsRead }) {
  const unread = notifications.filter(n => !n.read);
  const read = notifications.filter(n => n.read);
  const all = [...unread, ...read]; // unread first

  return (
    <div className="modal-overlay" onClick={onClose} style={{ justifyContent: 'flex-end', padding: 0 }}>
      <div
        className="glass-panel"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '380px',
          height: '100vh',
          borderRadius: 0,
          borderRight: 'none',
          borderTop: 'none',
          borderBottom: 'none',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '2px' }}>🔔 Notifications</h3>
            {unread.length > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                {unread.length} unread
              </span>
            )}
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {(!notifications || notifications.length === 0) ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔔</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>You're all caught up!</p>
            </div>
          ) : (
            all.map((n) => (
              <div
                key={n.id}
                className="glass-panel"
                style={{
                  padding: '12px 14px',
                  opacity: n.read ? 0.55 : 1,
                  borderLeft: n.read ? '1px solid var(--border-light)' : '3px solid var(--primary)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{n.subject}</span>
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
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{n.text}</p>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block' }}>
                  {n.delivered
                    ? new Date(n.delivered).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
                    : '—'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
