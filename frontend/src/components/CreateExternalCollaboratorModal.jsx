import React, { useState } from 'react';
import { userManagementAPI } from '../services/api';

export default function CreateExternalCollaboratorModal({ projects = [], onClose, onSuccess, showToast }) {
  const activeProjects = projects.filter(p => !p.archived && !p.soft_delete);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [projectId, setProjectId] = useState(activeProjects[0]?.id || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [createdResult, setCreatedResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) return;
    if (!projectId) {
      setError('Please select a project workspace.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await userManagementAPI.createExternalCollaborator({
        name,
        email,
        project_id: projectId,
      });

      setCreatedResult(res);
      if (showToast) showToast('External collaborator created successfully!', 'success');
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to create external collaborator');
    } finally {
      setLoading(false);
    }
  };

  const handleDone = () => {
    if (onClose) onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>🌐 Create External Collaborator</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        {error && (
          <div style={{ background: 'rgba(244,63,94,0.15)', border: '1px solid var(--rose)', color: 'var(--rose)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', marginBottom: '16px', fontSize: '0.85rem' }}>
            ⚠️ {error}
          </div>
        )}

        {!createdResult ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Jane Doe (Vendor)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="e.g. jane@external.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Assign to Project Workspace</label>
              {activeProjects.length === 0 ? (
                <div style={{ padding: '10px', background: 'rgba(245,158,11,0.1)', border: '1px solid var(--amber)', color: 'var(--amber)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
                  ⚠️ No active project workspaces available. Please create a project first.
                </div>
              ) : (
                <select
                  className="form-select"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  required
                >
                  <option value="" disabled>Select a Project</option>
                  {activeProjects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={loading || activeProjects.length === 0}>
                {loading ? 'Creating...' : 'Create Collaborator'}
              </button>
            </div>
          </form>
        ) : (
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '20px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--emerald)' }}>
            <h3 style={{ color: 'var(--emerald)', fontSize: '1.1rem', fontWeight: 700, marginBottom: '10px' }}>
              ✅ Collaborator Account Created!
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
              The collaborator account for <strong>{createdResult.email || email}</strong> has been created and assigned to the project.
            </p>
            {createdResult.temp_password && (
              <div style={{ padding: '10px 14px', background: 'rgba(16,185,129,0.1)', border: '1px solid var(--emerald)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', marginBottom: '16px' }}>
                🔑 Temporary Password: <code style={{ color: '#fff', fontWeight: 700 }}>{createdResult.temp_password}</code>
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-primary" onClick={handleDone}>Done</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
