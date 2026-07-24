import React, { useState } from 'react';

export default function AddTeamMemberModal({ teams, users = [], initialTeamId, onClose, onAddMember }) {
  const [email, setEmail] = useState('');
  const [teamId, setTeamId] = useState(initialTeamId || teams[0]?.id || '');
  const [projectRole, setProjectRole] = useState('project_member');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const targetTeamId = initialTeamId || teamId;
    if (!email.trim() || !targetTeamId) return;
    setLoading(true);
    try {
      await onAddMember(email, targetTeamId, projectRole);
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
          Select a registered user to join a project team.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select User</label>
            <select className="form-select" value={email} onChange={(e) => setEmail(e.target.value)} required>
              <option value="" disabled>Select a User</option>
              {users.filter(u => u && u.active !== false && !u.soft_delete).map((u) => (
                <option key={u.id} value={u.email}>{u.name} ({u.email})</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              Select Project Team {initialTeamId ? '(Workspace Locked 🔒)' : ''}
            </label>
            <select
              className="form-select"
              value={initialTeamId || teamId}
              onChange={(e) => setTeamId(e.target.value)}
              disabled={!!initialTeamId}
              required
            >
              <option value="" disabled>Select a Team</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Project Role</label>
            <select className="form-select" value={projectRole} onChange={(e) => setProjectRole(e.target.value)}>
              <option value="project_member">Project Member</option>
              <option value="project_admin">Project Admin</option>
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
