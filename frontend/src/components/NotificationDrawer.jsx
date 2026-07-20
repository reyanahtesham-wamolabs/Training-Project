import React from 'react';

export default function NotificationDrawer({ notifications, onClose, onMarkAsRead }) {
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
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>🔔 Notifications</h3>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {(!notifications || notifications.length === 0) ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px', fontSize: '0.9rem' }}>
              No notifications.
            </p>
          ) : (
            notifications.map((n) => (
              <div 
                key={n.id} 
                className="glass-panel" 
                style={{ 
                  padding: '12px 14px', 
                  opacity: n.read ? 0.65 : 1,
                  borderLeft: n.read ? '1px solid var(--border-light)' : '3px solid var(--primary)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{n.subject}</span>
                  {!n.read && (
                    <button 
                      className="btn btn-secondary btn-sm" 
                      style={{ fontSize: '0.68rem', padding: '1px 6px' }}
                      onClick={() => onMarkAsRead(n.id)}
                    >
                      Mark Read
                    </button>
                  )}
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{n.text}</p>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px', display: 'block' }}>
                  {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
