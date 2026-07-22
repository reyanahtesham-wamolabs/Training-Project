import React, { useState } from 'react';

export default function EditProjectModal({ 
  project, 
  onClose, 
  onEditProject, 
  availableTags = [],
  tasks = [], 
  users = [], 
  currentUser, 
  onAssignUser 
}) {
  const [name, setName] = useState(project?.name || '');
  const [startDate, setStartDate] = useState(project?.start_date || '');
  const [endDate, setEndDate] = useState(project?.end_date || '');
  const [category, setCategory] = useState(project?.category || 'inhouse');
  const [status, setStatus] = useState(project?.status || 'planned');
  const [assignSelections, setAssignSelections] = useState({});
  const [selectedTags, setSelectedTags] = useState(
    project?.tags ? project.tags.map(t => typeof t === 'string' ? t : t.name) : []
  );

  const toggleTag = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const projectTasks = tasks.filter(t => t.project_id === project.id);
  const isAdminOrManager = currentUser?.role === 'admin' || currentUser?.role === 'manager';

  const handleAssignClick = (taskId) => {
    const userId = assignSelections[taskId];
    if (!userId) return;
    const user = users.find(u => u.id === userId);
    if (!user) return;
    onAssignUser({
      user_email: user.email,
      task_id: taskId,
      role: 'project_member'
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onEditProject({
      id: project.id,
      name,
      start_date: startDate,
      end_date: endDate,
      category,
      status,
      tags: selectedTags
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1000, overflowY: 'auto', padding: '20px' }}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px', margin: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>✏️ Edit Project</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Enterprise Dashboard Revamp"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Start Date</label>
              <input
                type="date"
                className="form-input"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">End Date</label>
              <input
                type="date"
                className="form-input"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Category</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="inhouse">In-House</option>
                <option value="upwork">Upwork</option>
                <option value="US_based">US Based</option>
                <option value="Pak_profile">Pak Profile</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select className="form-select" value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="planned">Planned</option>
                <option value="started">Started</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginTop: '12px' }}>
            <label className="form-label">Project Tags</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '4px' }}>
              {availableTags.map((tag) => {
                const isSelected = selectedTags.includes(tag);
                return (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => toggleTag(tag)}
                    className={`badge ${isSelected ? 'badge-low' : 'badge-member'}`}
                    style={{ cursor: 'pointer', padding: '6px 12px', fontSize: '0.8rem' }}
                  >
                    {isSelected ? '✓ ' : '+ '}{tag}
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ marginTop: '30px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '10px' }}>Tasks in this Project</h3>
            {projectTasks.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No tasks found for this project.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {projectTasks.map(task => {
                  const hasAssignees = task.assignments && task.assignments.length > 0;
                  return (
                    <div key={task.id} style={{ border: '1px solid var(--border-light)', padding: '12px', borderRadius: '8px', background: 'var(--bg-glass)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong style={{ display: 'block', fontSize: '0.95rem' }}>{task.name}</strong>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status: {task.status.replace('_', ' ')}</span>
                        </div>
                        {hasAssignees ? (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Assigned to: {task.assignments.map(a => a.user?.name || 'Unknown User').join(', ')}
                          </div>
                        ) : (
                          isAdminOrManager && (
                            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                              <select 
                                className="form-select" 
                                style={{ padding: '4px 8px', fontSize: '0.8rem', height: 'auto' }}
                                value={assignSelections[task.id] || ''}
                                onChange={(e) => setAssignSelections({...assignSelections, [task.id]: e.target.value})}
                              >
                                <option value="">Select User</option>
                                {users.map(u => (
                                  <option key={u.id} value={u.id}>{u.name}</option>
                                ))}
                              </select>
                              <button 
                                type="button" 
                                className="btn btn-primary btn-sm" 
                                style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                                onClick={() => handleAssignClick(task.id)}
                                disabled={!assignSelections[task.id]}
                              >
                                Assign
                              </button>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  );
}
