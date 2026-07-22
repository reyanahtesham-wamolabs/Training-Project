import React, { useState } from 'react';

export default function AssignUserModal({ tasks, users = [], teamMembers = [], projectTeamMembers = null, currentUser, onClose, onAssignUser }) {
  const isMemberOnly = currentUser?.role === 'member';
  const [userEmail, setUserEmail] = useState(isMemberOnly ? (currentUser?.email || '') : '');
  const [taskId, setTaskId] = useState(tasks[0]?.id || '');

  // Merge users array and teamMembers array to ensure all valid users appear
  const userMap = new Map();

  if (projectTeamMembers && Array.isArray(projectTeamMembers)) {
    projectTeamMembers.forEach(m => {
      if (m && m.email) {
        userMap.set(m.email, { id: m.user_id || m.id, name: m.name || m.email, email: m.email });
      }
    });
  } else {
    users.forEach(u => {
      if (u && u.email && !u.is_external) {
        userMap.set(u.email, { id: u.id, name: u.name || u.email, email: u.email });
      }
    });
    teamMembers.forEach(m => {
      if (m && m.email && !userMap.has(m.email)) {
        userMap.set(m.email, { id: m.user_id || m.id, name: m.name || m.email, email: m.email });
      }
    });
  }

  if (currentUser?.email && !userMap.has(currentUser.email) && !currentUser.is_external) {
    userMap.set(currentUser.email, { id: currentUser.id || 'me', name: currentUser.name || 'You', email: currentUser.email });
  }

  let assignableUsers = Array.from(userMap.values());

  const selectedTask = tasks.find(t => t.id === taskId);
  const assignedUserIds = selectedTask?.assigned_user_ids || [];
  const assignedUserEmails = selectedTask?.assigned_user_emails || [];

  const isUserAlreadyAssigned = (u) => {
    return (u.id && assignedUserIds.includes(u.id)) || (u.email && assignedUserEmails.includes(u.email));
  };

  const isCurrentMemberAssigned = isMemberOnly && isUserAlreadyAssigned({ id: currentUser?.id, email: currentUser?.email });

  const handleSubmit = (e) => {
    e.preventDefault();
    const targetEmail = isMemberOnly ? currentUser?.email : userEmail;
    if (!targetEmail || !targetEmail.trim() || !taskId) return;
    onAssignUser({
      user_email: targetEmail,
      task_id: taskId
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>
            {isMemberOnly ? '✋ Assign Yourself to Task' : '👤 Assign User to Task'}
          </h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          {isMemberOnly 
            ? 'As a team member, you can assign yourself to available tasks.'
            : 'Assign a team member to a task. Note: External collaborators cannot be assigned tasks.'}
        </p>

        {isCurrentMemberAssigned && (
          <div style={{ padding: '8px 12px', background: 'rgba(239,68,68,0.1)', border: '1px solid var(--rose)', borderRadius: 'var(--radius-sm)', color: 'var(--rose)', fontSize: '0.8rem', marginBottom: '14px' }}>
            ⚠️ You are already assigned to task "{selectedTask?.name}".
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Task</label>
            <select className="form-select" value={taskId} onChange={(e) => setTaskId(e.target.value)} required>
              <option value="" disabled>Select a Task</option>
              {tasks.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Select User</label>
            <select 
              className="form-select" 
              value={isMemberOnly ? (currentUser?.email || '') : userEmail} 
              onChange={(e) => setUserEmail(e.target.value)} 
              disabled={isMemberOnly}
              required
            >
              {!isMemberOnly && <option value="" disabled>Select a User</option>}
              {assignableUsers.map((u) => {
                const assigned = isUserAlreadyAssigned(u);
                return (
                  <option key={u.id} value={u.email} disabled={assigned}>
                    {u.name} ({u.email}) {assigned ? '— (Already Assigned)' : u.email === currentUser?.email ? '— (You)' : ''}
                  </option>
                );
              })}
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
