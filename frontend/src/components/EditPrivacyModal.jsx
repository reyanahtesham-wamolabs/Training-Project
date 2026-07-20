import React, { useState } from 'react';

export default function EditPrivacyModal({ currentLevel, onClose, onSavePrivacy }) {
  const [level, setLevel] = useState(currentLevel || 'low');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSavePrivacy(level);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const privacyOptions = [
    {
      id: 'low',
      title: 'Low (Public)',
      badgeClass: 'badge-low',
      desc: 'All authenticated system users can view tasks assigned to you.'
    },
    {
      id: 'medium',
      title: 'Medium (Team Members Only)',
      badgeClass: 'badge-medium',
      desc: 'Only users who share a project team with you can view tasks assigned to you.'
    },
    {
      id: 'high',
      title: 'High (System Admin Only)',
      badgeClass: 'badge-high',
      desc: 'Strictly hidden from non-admin users. Only System Admins can view your assigned tasks.'
    }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>🔒 Edit Privacy Settings</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Customize your task visibility rules. This controls who can view tasks assigned to your account.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
            {privacyOptions.map((opt) => {
              const isSelected = level === opt.id;
              return (
                <div
                  key={opt.id}
                  className="glass-panel"
                  onClick={() => setLevel(opt.id)}
                  style={{
                    padding: '16px',
                    cursor: 'pointer',
                    border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-light)',
                    background: isSelected ? 'rgba(99, 102, 241, 0.12)' : 'var(--bg-card)',
                    borderRadius: 'var(--radius-md)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <input
                        type="radio"
                        name="privacy_level"
                        checked={isSelected}
                        onChange={() => setLevel(opt.id)}
                      />
                      <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{opt.title}</span>
                    </div>
                    <span className={`badge ${opt.badgeClass}`}>{opt.id}</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginLeft: '26px' }}>
                    {opt.desc}
                  </p>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Privacy Level'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
