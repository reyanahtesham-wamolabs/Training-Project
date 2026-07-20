import React, { useState } from 'react';

export default function AssignUserModal({ tasks, onClose, onAssignUser }) {
  const [userEmail, setUserEmail] = useState('');
  const [taskId, setTaskId] = useState(tasks[0]?.id || '');
  const [role, setRole] = useState('project_member');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!userEmail.trim() || !taskId) return;
    onAssignUser({
      user_email: userEmail,
      task_id: taskId,
      role
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>👤 Assign User to Task</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Assign a team member to a task. Note: User must already be a member of the project's team.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">User Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="e.g. member@company.com"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Select Task</label>
            <select className="form-select" value={taskId} onChange={(e) => setTaskId(e.target.value)} required>
              <option value="" disabled>Select a Task</option>
              {tasks.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.project_id})</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Role</label>
            <select className="form-select" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="project_member">Project Member</option>
              <option value="project_admin">Project Admin</option>
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary">Assign User</button>
          </div>
        </form>
      </div>
    </div>
  );
}
