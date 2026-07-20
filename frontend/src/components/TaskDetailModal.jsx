import React, { useState } from 'react';

export default function TaskDetailModal({ task, comments, onClose, onAddComment, onUpdateStatus, onDeleteTask }) {
  const [newCommentText, setNewCommentText] = useState('');
  const [replyingToId, setReplyingToId] = useState(null);
  const [replyText, setReplyText] = useState('');

  if (!task) return null;

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

        {/* Task Details Metadata */}
        <div className="glass-panel" style={{ padding: '14px', marginBottom: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Scheduled Date</span>
            <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{task.schedule_date || 'N/A'}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Project</span>
            <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>{task.project_name || task.project_id}</p>
          </div>
        </div>

        {/* Status Quick Changer */}
        <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
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
          <button className="btn btn-danger btn-sm" style={{ marginLeft: 'auto' }} onClick={() => onDeleteTask(task.id)}>
            Delete Task
          </button>
        </div>

        {/* Comments Section */}
        <div style={{ borderTop: '1px solid var(--border-light)', paddingTop: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            💬 Task Comments & Replies ({comments?.length || 0})
          </h3>

          {/* New Comment Input */}
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

          {/* Comments List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {(!comments || comments.length === 0) ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>No comments yet. Be the first to comment!</p>
            ) : (
              comments.map((c) => (
                <div key={c.id} className="glass-panel" style={{ padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--primary)' }}>
                      {c.user_name || c.user_id}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '8px' }}>{c.content}</p>

                  {/* Reply display (1-level reply constraint) */}
                  {c.reply ? (
                    <div style={{
                      marginLeft: '16px',
                      paddingLeft: '12px',
                      borderLeft: '2px solid var(--secondary)',
                      background: 'rgba(168, 85, 247, 0.05)',
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      marginTop: '8px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: 'var(--secondary)' }}>
                        <span>↳ {c.reply.user_name || c.reply.user_id}</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {new Date(c.reply.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>{c.reply.content}</p>
                    </div>
                  ) : (
                    <div>
                      {replyingToId === c.id ? (
                        <div style={{ marginTop: '8px', marginLeft: '16px' }}>
                          <input
                            type="text"
                            className="form-input"
                            placeholder="Write a single reply..."
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
                          style={{ fontSize: '0.75rem', padding: '2px 8px', marginTop: '4px' }}
                          onClick={() => setReplyingToId(c.id)}
                        >
                          ↳ Reply
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
