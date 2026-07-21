import React, { useState } from 'react';

const ACTION_LABELS = {
  create_project: 'Create Project',
  update_project: 'Update Project',
  archive_project: 'Archive Project',
  delete_project: 'Delete Project',
  create_tag: 'Create Tag',
  create_task: 'Create Task',
  update_task: 'Update Task',
  delete_task: 'Delete Task',
  add_prerequisite: 'Add Prerequisite',
  create_user: 'Create User',
  update_user: 'Update User',
  delete_user: 'Delete User',
  modify_user_status: 'Modify Status',
  change_user_privacy: 'Change Privacy',
  assign_user: 'Assign User',
};

const ACTION_BADGE = {
  create_project: 'badge-low',
  update_project: 'badge-medium',
  archive_project: 'badge-medium',
  delete_project: 'badge-high',
  create_tag: 'badge-low',
  create_task: 'badge-low',
  update_task: 'badge-medium',
  delete_task: 'badge-high',
  add_prerequisite: 'badge-admin',
  create_user: 'badge-low',
  update_user: 'badge-medium',
  delete_user: 'badge-high',
  modify_user_status: 'badge-medium',
  change_user_privacy: 'badge-admin',
  assign_user: 'badge-admin',
};

export default function ActivityLogView({ logs, onClose }) {
  const [filter, setFilter] = useState('all');

  const categories = ['all', 'create', 'update', 'delete', 'archive', 'assign'];

  const filteredLogs = (logs || []).filter((log) => {
    if (filter === 'all') return true;
    const type = (log.action_type || '').toLowerCase();
    return type.includes(filter);
  });

  const getLabel = (action_type) => ACTION_LABELS[action_type] || action_type?.replace(/_/g, ' ') || '—';
  const getBadge = (action_type) => ACTION_BADGE[action_type] || 'badge-member';

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }} className="text-gradient">
            📋 System Activity Audit Trail
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            {logs?.length ?? 0} events recorded · Real-time immutable log
          </p>
        </div>
        {onClose && (
          <button className="btn btn-secondary btn-sm" onClick={onClose}>Close</button>
        )}
      </div>

      {/* Filter pills */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            className={`btn btn-sm ${filter === cat ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '4px 12px', fontSize: '0.78rem', textTransform: 'capitalize' }}
            onClick={() => setFilter(cat)}
          >
            {cat === 'all' ? 'All Events' : cat}
          </button>
        ))}
      </div>

      {(!filteredLogs || filteredLogs.length === 0) ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>📋</div>
          <p>{filter === 'all' ? 'No activity logs recorded yet.' : `No "${filter}" events found.`}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredLogs.map((log) => (
            <div
              key={log.id}
              className="glass-panel"
              style={{ padding: '14px 18px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', flex: 1, minWidth: 0 }}>
                <span className={`badge ${getBadge(log.action_type)}`} style={{ flexShrink: 0, marginTop: '2px' }}>
                  {getLabel(log.action_type)}
                </span>
                <div style={{ minWidth: 0 }}>
                  <p style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-main)', wordBreak: 'break-word' }}>
                    {log.message}
                  </p>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px', flexWrap: 'wrap' }}>
                    {log.project_id && <span>Project: <strong>{log.project_id.slice(0, 8)}…</strong></span>}
                    {log.task_id && <span>Task: <strong>{log.task_id.slice(0, 8)}…</strong></span>}
                  </div>
                </div>
              </div>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', flexShrink: 0 }}>
                {log.change_time
                  ? new Date(log.change_time).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
                  : '—'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
