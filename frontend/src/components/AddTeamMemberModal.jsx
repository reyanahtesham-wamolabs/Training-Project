import React, { useState } from 'react';

export default function AddTeamMemberModal({ teams, onClose, onAddMember }) {
  const [email, setEmail] = useState('');
  const [teamId, setTeamId] = useState(teams[0]?.id || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !teamId) return;
    setLoading(true);
    try {
      await onAddMember(email, teamId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>👥 Add User to Team</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Invite a registered user to join a project team by entering their email address.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">User Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="e.g. colleague@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Select Project Team</label>
            <select className="form-select" value={teamId} onChange={(e) => setTeamId(e.target.value)} required>
              <option value="" disabled>Select a Team</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name} (Project: {t.project_id || t.id})</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding...' : 'Add to Team'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
