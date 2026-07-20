import React from 'react';

export default function ActivityLogView({ logs, onClose }) {
  const getActionBadgeClass = (actionType) => {
    if (!actionType) return 'badge-member';
    const type = actionType.toLowerCase();
    if (type.includes('create')) return 'badge-low';
    if (type.includes('update') || type.includes('archive')) return 'badge-medium';
    if (type.includes('delete')) return 'badge-high';
    return 'badge-admin';
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }} className="text-gradient">
            📋 System Activity Audit Trail
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Real-time immutable activity log for tasks, projects, and user operations.
          </p>
        </div>
        {onClose && (
          <button className="btn btn-secondary btn-sm" onClick={onClose}>Close</button>
        )}
      </div>

      {(!logs || logs.length === 0) ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          <p>No activity logs recorded yet.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {logs.map((log) => (
            <div key={log.id} className="glass-panel" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span className={`badge ${getActionBadgeClass(log.action_type)}`}>
                  {log.action_type}
                </span>
                <div>
                  <p style={{ fontSize: '0.92rem', fontWeight: 500, color: 'var(--text-main)' }}>
                    {log.message}
                  </p>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                    <span>By User: <strong>{log.modified_by_user_id}</strong></span>
                    {log.project_id && <span>Project: <strong>{log.project_id}</strong></span>}
                    {log.task_id && <span>Task: <strong>{log.task_id}</strong></span>}
                  </div>
                </div>
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {new Date(log.change_time).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
