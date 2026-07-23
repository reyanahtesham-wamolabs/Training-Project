import React, { useState } from 'react';
import { userManagementAPI } from '../services/api';

export default function TaskDetailModal({ 
  task, 
  projects = [], 
  allTasks = [],
  teams = [],
  users = [],
  teamMembers = [],
  comments, 
  currentUser,
  onClose, 
  onAddComment, 
  onEditComment,
  onDeleteComment,
  onUpdateStatus, 
  onUpdatePriority,
  onUpdateDates,
  onAddPrerequisite,
  onDeleteTask,
  onUnassignUser,
  onAssignUser
}) {
  const [newCommentText, setNewCommentText] = useState('');
  const [replyingToId, setReplyingToId] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editText, setEditText] = useState('');
  const [selectedPrereqId, setSelectedPrereqId] = useState('');

  // Date & Assign editing state
  const [isEditingDates, setIsEditingDates] = useState(false);
  const [newScheduleDate, setNewScheduleDate] = useState('');
  const [newDueDate, setNewDueDate] = useState('');
  const [assignLoading, setAssignLoading] = useState(false);
  const [isAssigningUser, setIsAssigningUser] = useState(false);
  const [selectedAssignUserEmail, setSelectedAssignUserEmail] = useState('');

  const isOverallAdminOrManager = ['admin', 'manager'].includes(currentUser?.role?.toLowerCase());
  const isProjectAdmin = teamMembers.some(m => 
    (m.user_id === currentUser?.id || m.email === currentUser?.email) &&
    m.project_role === 'project_admin'
  );
  const canDeleteAssignment = isOverallAdminOrManager || isProjectAdmin;
  const canDeleteTask = isOverallAdminOrManager || isProjectAdmin;

  // Filter ONLY project team members for this task
  const projectTeam = teams.find(t => t.project_id === task?.project_id || t.id === task?.project_id);
  const projectTeamMembers = teamMembers.filter(m => 
    (projectTeam && m.team_id === projectTeam.id) || m.team_id === task?.project_id
  );

  const assignableUsersMap = new Map();
  projectTeamMembers.forEach(m => {
    if (m && m.email) {
      assignableUsersMap.set(m.email, { id: m.user_id || m.id, name: m.name || m.email, email: m.email });
    }
  });

  const currentlyAssignedEmails = task?.assigned_user_emails || (task?.assignments ? task.assignments.map(a => a.user_email) : []);
  const currentlyAssignedIds = task?.assigned_user_ids || (task?.assignments ? task.assignments.map(a => a.user_id) : []);

  const unassignedProjectTeamMembers = Array.from(assignableUsersMap.values()).filter(u => 
    !currentlyAssignedEmails.includes(u.email) && !currentlyAssignedIds.includes(u.id)
  );

  const handleAssignSelectedUser = async () => {
    if (!selectedAssignUserEmail) return;
    setAssignLoading(true);
    try {
      if (onAssignUser) {
        await onAssignUser({
          user_email: selectedAssignUserEmail,
          task_id: task.id
        });
      } else {
        await userManagementAPI.assignUser({
          user_email: selectedAssignUserEmail,
          task_id: task.id
        });
      }
      setIsAssigningUser(false);
      setSelectedAssignUserEmail('');
      if (onClose) onClose();
    } catch (err) {
      alert(err.message || 'Failed to assign user');
    } finally {
      setAssignLoading(false);
    }
  };

  const handleDeleteAssignment = async (userEmail, userId) => {
    if (!window.confirm('Are you sure you want to remove this user from the task?')) return;
    setAssignLoading(true);
    try {
      if (onUnassignUser) {
        await onUnassignUser({ task_id: task.id, user_email: userEmail, user_id: userId });
      } else {
        await userManagementAPI.unassignUser({
          task_id: task.id,
          user_email: userEmail,
          user_id: userId
        });
        alert('Assignment deleted successfully!');
        if (onClose) onClose();
      }
    } catch (err) {
      alert(err.message || 'Failed to delete assignment');
    } finally {
      setAssignLoading(false);
    }
  };

  const handleSelfAssign = async () => {
    if (!currentUser?.email) return;
    setAssignLoading(true);
    try {
      await userManagementAPI.assignUser({
        user_email: currentUser.email,
        task_id: task.id,
        role: 'project_member'
      });
      alert('You have successfully assigned yourself to this task!');
      if (onClose) onClose();
    } catch (err) {
      alert(err.message || 'Failed to assign task');
    } finally {
      setAssignLoading(false);
    }
  };

  if (!task) return null;

  const handleOpenEditDates = () => {
    setNewScheduleDate(task.schedule_date || '');
    setNewDueDate(task.due_date || '');
    setIsEditingDates(true);
  };

  const handleSaveDates = () => {
    if (onUpdateDates) {
      onUpdateDates(task.id, {
        schedule_date: newScheduleDate || null,
        due_date: newDueDate || null
      });
    }
    setIsEditingDates(false);
  };

  const handleSubmitComment = (e) => {
    e.preventDefault();
    if (!newCommentText.trim()) return;
    onAddComment(task.id, newCommentText, null);
    setNewCommentText('');
  };

  const handleSubmitReply = (parentId) => {
    if (!replyText.trim()) return;
    onAddComment(task.id, replyText, parentId);
    setReplyText('');
    setReplyingToId(null);
  };

  const handleSaveEdit = (commentId) => {
    if (!editText.trim()) return;
    onEditComment(commentId, editText, task.id);
    setEditingCommentId(null);
    setEditText('');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '640px' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '6px' }}>
              <span className={`badge badge-${task.priority?.toLowerCase() || 'low'}`}>
                {task.priority} Priority
              </span>
              <span className={`badge badge-${task.status?.toLowerCase() || 'planned'}`}>
                {task.status?.replace('_', ' ')}
              </span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>{task.name}</h2>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} style={{ padding: '4px 8px' }}>✕</button>
        </div>

        {/* Task Details Metadata & Dates */}
        {(() => {
          const isAssigned = 
            currentUser?.role === 'admin' ||
            currentUser?.role === 'manager' ||
            (task.assigned_user_ids && task.assigned_user_ids.includes(currentUser?.id)) ||
            (task.assigned_user_emails && task.assigned_user_emails.includes(currentUser?.email));
          const canEditTask = !currentUser?.is_external && isAssigned;

          return (
            <>
              <div className="glass-panel" style={{ padding: '16px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                    📅 Task Timeline & Project
                  </span>
                  {!isEditingDates && canEditTask && (
                    <button 
                      className="btn btn-secondary btn-sm" 
                      onClick={handleOpenEditDates}
                      style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                    >
                      ✏️ Edit Dates
                    </button>
                  )}
                </div>

                {!isEditingDates ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Schedule Date</span>
                      <p style={{ fontSize: '0.9rem', fontWeight: 600, margin: '2px 0 0 0' }}>{task.schedule_date || 'N/A'}</p>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Due Date</span>
                      <p style={{ fontSize: '0.9rem', fontWeight: 600, margin: '2px 0 0 0' }}>{task.due_date || 'N/A'}</p>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Project</span>
                      <p style={{ fontSize: '0.9rem', fontWeight: 600, margin: '2px 0 0 0' }}>
                        {task.project_name || projects.find(p => p.id === task.project_id)?.name || 'Unknown Project'}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '14px' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '2px' }}>
                          Previous Schedule Date: <strong style={{ color: 'var(--text-main)' }}>{task.schedule_date || 'None'}</strong>
                        </span>
                        <label className="form-label" style={{ fontSize: '0.8rem', marginTop: '6px' }}>New Schedule Date</label>
                        <input
                          type="date"
                          className="form-input"
                          value={newScheduleDate}
                          onChange={(e) => setNewScheduleDate(e.target.value)}
                        />
                      </div>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '2px' }}>
                          Previous Due Date: <strong style={{ color: 'var(--text-main)' }}>{task.due_date || 'None'}</strong>
                        </span>
                        <label className="form-label" style={{ fontSize: '0.8rem', marginTop: '6px' }}>New Due Date</label>
                        <input
                          type="date"
                          className="form-input"
                          value={newDueDate}
                          onChange={(e) => setNewDueDate(e.target.value)}
                        />
                      </div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => setIsEditingDates(false)}>
                        Cancel
                      </button>
                      <button className="btn btn-primary btn-sm" onClick={handleSaveDates}>
                        Save Dates
                      </button>
                    </div>
                  </div>
                )}

                {/* Assigned Team Members Section */}
                <div style={{ marginTop: '14px', borderTop: '1px solid var(--border-light)', paddingTop: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      👥 Assigned Team Members:
                    </span>
                    {canDeleteAssignment && !isAssigningUser && (
                      <button 
                        className="btn btn-secondary btn-sm"
                        style={{ fontSize: '0.75rem', padding: '3px 8px' }}
                        onClick={() => {
                          setSelectedAssignUserEmail(unassignedProjectTeamMembers[0]?.email || '');
                          setIsAssigningUser(true);
                        }}
                      >
                        👤 + Assign User
                      </button>
                    )}
                  </div>

                  {isAssigningUser && (
                    <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)', marginBottom: '12px' }}>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                        Select Project Team Member:
                      </label>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <select
                          className="form-select"
                          style={{ flex: 1, fontSize: '0.85rem' }}
                          value={selectedAssignUserEmail}
                          onChange={(e) => setSelectedAssignUserEmail(e.target.value)}
                        >
                          {unassignedProjectTeamMembers.length === 0 ? (
                            <option value="" disabled>No unassigned project team members available</option>
                          ) : (
                            unassignedProjectTeamMembers.map(u => (
                              <option key={u.email} value={u.email}>
                                {u.name} ({u.email})
                              </option>
                            ))
                          )}
                        </select>
                        <button
                          className="btn btn-primary btn-sm"
                          disabled={assignLoading || !selectedAssignUserEmail}
                          onClick={handleAssignSelectedUser}
                        >
                          Assign
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => setIsAssigningUser(false)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                  {task.assignments && task.assignments.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {task.assignments.map((ass) => {
                        const uId = ass.user_id || ass.user?.id || ass.id;
                        const uEmail = ass.user_email || ass.user?.email || ass.email;
                        const uName = ass.user_name || ass.user?.name || ass.name || uEmail || 'Assigned Member';

                        return (
                          <span key={ass.id || uId} className="badge badge-admin" style={{ fontSize: '0.8rem', padding: '4px 10px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                            👤 {uName}
                            {canDeleteAssignment && (
                              <button
                                title="Delete assignment"
                                style={{
                                  background: 'transparent',
                                  border: 'none',
                                  color: '#ef4444',
                                  cursor: 'pointer',
                                  padding: '0 2px',
                                  fontSize: '0.85rem',
                                  lineHeight: 1,
                                  fontWeight: 'bold'
                                }}
                                disabled={assignLoading}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteAssignment(uEmail, uId);
                                }}
                              >
                                ✕
                              </button>
                            )}
                          </span>
                        );
                      })}
                    </div>
                  ) : task.assigned_user_names && task.assigned_user_names.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {task.assigned_user_names.map((name, idx) => {
                        const userEmail = task.assigned_user_emails?.[idx];
                        const userId = task.assigned_user_ids?.[idx];
                        return (
                          <span key={idx} className="badge badge-admin" style={{ fontSize: '0.8rem', padding: '4px 10px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                            👤 {name}
                            {canDeleteAssignment && (
                              <button
                                title="Delete assignment"
                                style={{
                                  background: 'transparent',
                                  border: 'none',
                                  color: '#ef4444',
                                  cursor: 'pointer',
                                  padding: '0 2px',
                                  fontSize: '0.85rem',
                                  lineHeight: 1,
                                  fontWeight: 'bold'
                                }}
                                disabled={assignLoading}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteAssignment(userEmail, userId);
                                }}
                              >
                                ✕
                              </button>
                            )}
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      No members assigned yet
                    </span>
                  )}
                </div>
              </div>

              {/* Task Controls - Only for assigned users */}
              {canEditTask ? (
                <>
                  <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Update Status:</span>
                    {['planned', 'in_progress', 'finished'].map((st) => (
                      <button
                        key={st}
                        className={`btn btn-sm ${task.status === st ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onUpdateStatus(task.id, st)}
                      >
                        {st.replace('_', ' ')}
                      </button>
                    ))}
                    {canDeleteTask && (
                      <button className="btn btn-danger btn-sm" style={{ marginLeft: 'auto' }} onClick={() => onDeleteTask(task.id)}>
                        Delete Task
                      </button>
                    )}
                  </div>

                  <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Update Priority:</span>
                    {['low', 'medium', 'high'].map((pr) => (
                      <button
                        key={pr}
                        className={`btn btn-sm ${task.priority?.toLowerCase() === pr ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onUpdatePriority && onUpdatePriority(task.id, pr)}
                      >
                        {pr.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>🔒 Task editing is restricted to assigned users.</span>
                  {!currentUser?.is_external && (
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={handleSelfAssign}
                      disabled={assignLoading}
                      style={{ fontSize: '0.78rem' }}
                    >
                      {assignLoading ? 'Assigning...' : '✋ Assign Myself to Task'}
                    </button>
                  )}
                </div>
              )}
            </>
          );
        })()}

        {/* Prerequisites & Dependencies */}
        <div className="glass-panel" style={{ padding: '14px', marginBottom: '20px' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
            🔗 Prerequisite Tasks (Task Dependencies)
          </span>
          {(() => {
            const activePrereqs = (task.prerequisites || []).filter(pre => !pre.soft_delete);
            return activePrereqs.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                {activePrereqs.map((pre) => {
                  const isFinished = pre.status === 'finished';
                  return (
                    <div key={pre.id} className="badge badge-secondary" style={{ padding: '4px 8px', display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span>{pre.name}</span>
                      <span className={`badge badge-${isFinished ? 'finished' : 'planned'}`} style={{ fontSize: '0.65rem' }}>
                        {isFinished ? '✓ Finished' : '⏳ Pending'}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '12px', fontStyle: 'italic' }}>
                No prerequisites set for this task.
              </p>
            );
          })()}

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <select
              className="form-select"
              style={{ fontSize: '0.8rem', padding: '4px 8px' }}
              value={selectedPrereqId}
              onChange={(e) => setSelectedPrereqId(e.target.value)}
            >
              <option value="">Select a prerequisite task...</option>
              {allTasks
                .filter(t => t.id !== task.id && t.project_id === task.project_id && !t.soft_delete)
                .map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.status.replace('_', ' ')})
                  </option>
                ))
              }
            </select>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              style={{ padding: '4px 10px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
              disabled={!selectedPrereqId}
              onClick={() => {
                if (selectedPrereqId && onAddPrerequisite) {
                  onAddPrerequisite(selectedPrereqId, task.id);
                  setSelectedPrereqId('');
                }
              }}
            >
              + Link Prerequisite
            </button>
          </div>
        </div>

        {/* Comments Section */}
        <div style={{ borderTop: '1px solid var(--border-light)', paddingTop: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            💬 Task Comments & Replies ({comments?.length || 0})
          </h3>

          {/* New Comment Input */}
          {currentUser?.is_external ? (
            <div style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic', marginBottom: '20px' }}>
              🔒 External Collaborators are in view-only mode for task comments.
            </div>
          ) : (
            <form onSubmit={handleSubmitComment} style={{ marginBottom: '20px' }}>
              <textarea
                className="form-textarea"
                placeholder="Write a comment..."
                value={newCommentText}
                onChange={(e) => setNewCommentText(e.target.value)}
                style={{ minHeight: '70px', marginBottom: '8px' }}
              />
              <button type="submit" className="btn btn-primary btn-sm">Post Comment</button>
            </form>
          )}

          {/* Comments List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {(!comments || comments.length === 0) ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>No comments yet. Be the first to comment!</p>
            ) : (
              comments.map((c) => {
                const canEditMain = currentUser?.id === c.user_id;
                const canDeleteMain = currentUser?.id === c.user_id || isOverallAdminOrManager || isProjectAdmin;

                return (
                  <div key={c.id} className="glass-panel" style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--primary)' }}>
                        {c.user_name || 'Unknown User'}
                      </span>
                      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {canEditMain && (
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ padding: '1px 6px', fontSize: '0.7rem' }}
                            onClick={() => { setEditingCommentId(c.id); setEditText(c.content); }}
                          >
                            ✎ Edit
                          </button>
                        )}
                        {canDeleteMain && (
                          <button
                            className="btn btn-danger btn-sm"
                            style={{ padding: '1px 6px', fontSize: '0.7rem' }}
                            onClick={() => {
                              if (window.confirm('Delete this comment?')) {
                                onDeleteComment(c.id, task.id);
                              }
                            }}
                          >
                            🗑 Delete
                          </button>
                        )}
                      </div>
                    </div>

                    {editingCommentId === c.id ? (
                      <div style={{ marginTop: '6px' }}>
                        <input
                          type="text"
                          className="form-input"
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          style={{ marginBottom: '6px', fontSize: '0.85rem' }}
                        />
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button className="btn btn-primary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => handleSaveEdit(c.id)}>Save</button>
                          <button className="btn btn-secondary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => setEditingCommentId(null)}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '8px' }}>{c.content}</p>
                    )}

                    {/* Replies list (flat, multi-user replies on the same level) */}
                    {c.replies && c.replies.length > 0 && (
                      <div style={{
                        marginLeft: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                        marginTop: '8px'
                      }}>
                        {c.replies.map((reply) => {
                          const canEditReply = currentUser?.id === reply.user_id;
                          const canDeleteReply = currentUser?.id === reply.user_id || isOverallAdminOrManager || isProjectAdmin;

                          return (
                            <div key={reply.id} style={{
                              paddingLeft: '12px',
                              borderLeft: '2px solid var(--secondary)',
                              background: 'rgba(168, 85, 247, 0.05)',
                              padding: '8px 12px',
                              borderRadius: 'var(--radius-sm)'
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', fontWeight: 600, color: 'var(--secondary)' }}>
                                <span>↳ {reply.user_name || 'Unknown User'}</span>
                                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                    {new Date(reply.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </span>
                                  {canEditReply && (
                                    <button
                                      className="btn btn-secondary btn-sm"
                                      style={{ padding: '1px 6px', fontSize: '0.68rem' }}
                                      onClick={() => { setEditingCommentId(reply.id); setEditText(reply.content); }}
                                    >
                                      ✎ Edit
                                    </button>
                                  )}
                                  {canDeleteReply && (
                                    <button
                                      className="btn btn-danger btn-sm"
                                      style={{ padding: '1px 6px', fontSize: '0.68rem' }}
                                      onClick={() => {
                                        if (window.confirm('Delete this reply?')) {
                                          onDeleteComment(reply.id, task.id);
                                        }
                                      }}
                                    >
                                      🗑 Delete
                                    </button>
                                  )}
                                </div>
                              </div>

                              {editingCommentId === reply.id ? (
                                <div style={{ marginTop: '6px' }}>
                                  <input
                                    type="text"
                                    className="form-input"
                                    value={editText}
                                    onChange={(e) => setEditText(e.target.value)}
                                    style={{ marginBottom: '6px', fontSize: '0.85rem' }}
                                  />
                                  <div style={{ display: 'flex', gap: '6px' }}>
                                    <button className="btn btn-primary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => handleSaveEdit(reply.id)}>Save</button>
                                    <button className="btn btn-secondary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => setEditingCommentId(null)}>Cancel</button>
                                  </div>
                                </div>
                              ) : (
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', margin: '4px 0 0' }}>{reply.content}</p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Reply Input Form */}
                    {!currentUser?.is_external && (
                      <div style={{ marginTop: '8px' }}>
                        {replyingToId === c.id ? (
                          <div style={{ marginTop: '8px', marginLeft: '16px' }}>
                            <input
                              type="text"
                              className="form-input"
                              placeholder="Write a reply..."
                              value={replyText}
                              onChange={(e) => setReplyText(e.target.value)}
                              style={{ marginBottom: '6px', fontSize: '0.85rem' }}
                            />
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button className="btn btn-primary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => handleSubmitReply(c.id)}>Send Reply</button>
                              <button className="btn btn-secondary btn-sm" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={() => setReplyingToId(null)}>Cancel</button>
                            </div>
                          </div>
                        ) : (
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ fontSize: '0.75rem', padding: '2px 8px', marginTop: '6px' }}
                            onClick={() => setReplyingToId(c.id)}
                          >
                            💬 Reply
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
