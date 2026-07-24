import React, { useState, useEffect, useRef } from 'react';
import { teamAPI } from '../services/api';

export default function ProjectDetailView({ 
  project, 
  projects = [],
  tasks = [], 
  teams = [], 
  teamMembers = [], 
  commentsMap = {},
  currentUser, 
  onBack, 
  onSelectTask,
  onCreateTaskForProject,
  onAssignUserForProject,
  onAddTeamMemberForTeam,
  onRemoveTeamMember,
  onEditProject,
  onArchiveProject
}) {
  const [activeSubTab, setActiveSubTab] = useState('tasks'); // 'tasks' | 'chat' | 'members'
  
  // Tasks Tab Filters
  const [taskSearch, setTaskSearch] = useState('');
  const [taskStatusFilter, setTaskStatusFilter] = useState('all');
  const [taskPriorityFilter, setTaskPriorityFilter] = useState('all');
  const [taskAssignmentFilter, setTaskAssignmentFilter] = useState('all');
  const [taskDateSort, setTaskDateSort] = useState('none');

  // Find Team corresponding to this project
  const projectTeam = teams.find(t => t.project_id === project.id) || { id: project.id, name: `${project.name} Team` };
  const membersOfThisProject = teamMembers.filter(m => m.team_id === projectTeam.id);

  const isOverallAdminOrManager = ['admin', 'manager'].includes(currentUser?.role?.toLowerCase());
  const isProjectAdmin = membersOfThisProject.some(m => 
    (m.user_id === currentUser?.id || m.email === currentUser?.email) && 
    m.project_role === 'project_admin'
  );
  const canManageProject = isOverallAdminOrManager || isProjectAdmin;

  // Chat State
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(true);
  const [chatError, setChatError] = useState('');
  const messagesEndRef = useRef(null);

  // Fetch Chat Messages & Setup WebSocket
  useEffect(() => {
    if (activeSubTab !== 'chat' || !projectTeam.id) return;

    let isMounted = true;
    const fetchMessages = async () => {
      try {
        const data = await teamAPI.getMessages(projectTeam.id);
        if (isMounted && Array.isArray(data)) {
          setMessages(data);
        }
      } catch (err) {
        console.warn("Failed to fetch project chat messages:", err);
      } finally {
        if (isMounted) setChatLoading(false);
      }
    };

    fetchMessages();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    const port = '8000';
    const wsUrl = `${protocol}//${host}:${port}/Team/ws/team_chat/${projectTeam.id}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);
      socket.onmessage = (event) => {
        try {
          const incomingMsg = JSON.parse(event.data);
          if (incomingMsg && incomingMsg.id && isMounted) {
            setMessages((prev) => {
              if (prev.some((m) => m.id === incomingMsg.id)) return prev;
              return [...prev, incomingMsg];
            });
          }
        } catch (e) {
          console.warn("Failed to parse incoming WebSocket message:", e);
        }
      };
    } catch (err) {
      console.warn("WebSocket connection error:", err);
    }

    return () => {
      isMounted = false;
      if (socket) socket.close();
    };
  }, [activeSubTab, projectTeam.id]);

  useEffect(() => {
    if (activeSubTab === 'chat') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, activeSubTab]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !projectTeam.id) return;
    try {
      const content = newMessage;
      setNewMessage('');
      const sentMsg = await teamAPI.sendMessage({ team_id: projectTeam.id, content });
      if (sentMsg && sentMsg.id) {
        setMessages((prev) => {
          if (prev.some((m) => m.id === sentMsg.id)) return prev;
          return [...prev, sentMsg];
        });
      }
    } catch (err) {
      setChatError(err.message || 'Failed to send message');
    }
  };

  const getMemberDetails = (memberId) => {
    const m = teamMembers.find(member => member.id === memberId || member.user_id === memberId);
    return m ? { name: m.name || m.email, email: m.email } : { name: 'Team Member', email: '' };
  };

  // Filter Tasks for this Project
  const projectTasks = tasks.filter(t => t.project_id === project.id && !t.soft_delete);
  const filteredProjectTasks = projectTasks.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(taskSearch.toLowerCase());
    const matchesStatus = taskStatusFilter === 'all' || t.status === taskStatusFilter;
    const matchesPriority = taskPriorityFilter === 'all' || t.priority?.toLowerCase() === taskPriorityFilter.toLowerCase();
    const matchesAssignment = taskAssignmentFilter === 'all' || 
      (taskAssignmentFilter === 'assigned_to_me' && (
        (t.assigned_user_ids && t.assigned_user_ids.includes(currentUser?.id)) ||
        (t.assigned_user_emails && t.assigned_user_emails.includes(currentUser?.email))
      ));
    return matchesSearch && matchesStatus && matchesPriority && matchesAssignment;
  }).sort((a, b) => {
    if (taskDateSort === 'schedule_asc') {
      return (a.schedule_date || '9999-99-99').localeCompare(b.schedule_date || '9999-99-99');
    }
    if (taskDateSort === 'schedule_desc') {
      return (b.schedule_date || '').localeCompare(a.schedule_date || '');
    }
    if (taskDateSort === 'due_asc') {
      return (a.due_date || '9999-99-99').localeCompare(b.due_date || '9999-99-99');
    }
    if (taskDateSort === 'due_desc') {
      return (b.due_date || '').localeCompare(a.due_date || '');
    }
    return 0;
  });

  return (
    <div style={{ animation: 'fadeIn 0.2s ease' }}>
      {/* Header Banner & Breadcrumb */}
      <div style={{ marginBottom: '24px' }}>
        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onBack}
          style={{ marginBottom: '14px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
        >
          ← Back to All Projects
        </button>

        <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className={`badge badge-${project.status}`}>{project.status?.replace('_', ' ')}</span>
              <span className="badge badge-member" style={{ fontSize: '0.75rem', textTransform: 'capitalize' }}>
                📁 {project.category?.replace('_', ' ')}
              </span>
              <span style={{ fontSize: '0.78rem', color: project.archived ? 'var(--rose)' : 'var(--emerald)' }}>
                {project.archived ? '🔒 Archived' : '⚡ Active'}
              </span>
            </div>

            <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }} className="text-gradient">
              {project.name}
            </h1>

            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
              📅 Timeline: <strong>{project.start_date || 'N/A'}</strong> → <strong>{project.end_date || 'N/A'}</strong>
            </p>

            {project.tags && project.tags.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '12px' }}>
                {project.tags.map(t => (
                  <span key={t} className="badge badge-admin" style={{ fontSize: '0.7rem', padding: '3px 10px' }}>
                    #{t}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {canManageProject && (
              <>
                <button className="btn btn-secondary btn-sm" onClick={() => onEditProject(project)}>
                  ✏️ Edit Project
                </button>
                <button 
                  className={`btn btn-sm ${project.archived ? 'btn-secondary' : 'btn-danger'}`}
                  onClick={() => onArchiveProject(project.id, !project.archived)}
                >
                  {project.archived ? 'Unarchive' : 'Archive'}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Sub-Tab Navigation Bar */}
      <div style={{ display: 'flex', gap: '12px', borderBottom: '1px solid var(--border-light)', marginBottom: '24px', paddingBottom: '2px' }}>
        <button 
          className={`btn ${activeSubTab === 'tasks' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('tasks')}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', display: 'flex', gap: '8px', alignItems: 'center' }}
        >
          📋 Task Board
          <span className="badge badge-secondary" style={{ fontSize: '0.72rem', background: 'rgba(255,255,255,0.15)' }}>
            {projectTasks.length}
          </span>
        </button>

        <button 
          className={`btn ${activeSubTab === 'chat' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('chat')}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', display: 'flex', gap: '8px', alignItems: 'center' }}
        >
          💬 Team Chat
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: 'var(--emerald)' }}></span>
        </button>

        <button 
          className={`btn ${activeSubTab === 'members' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveSubTab('members')}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', display: 'flex', gap: '8px', alignItems: 'center' }}
        >
          👥 Team Members
          <span className="badge badge-secondary" style={{ fontSize: '0.72rem', background: 'rgba(255,255,255,0.15)' }}>
            {membersOfThisProject.length}
          </span>
        </button>
      </div>

      {/* SUB-TAB 1: TASKS BOARD */}
      {activeSubTab === 'tasks' && (
        <div>
          {/* Controls & Filter Bar */}
          <div className="glass-panel" style={{ padding: '16px', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
              <input 
                type="text" 
                className="form-input" 
                placeholder="🔍 Search project tasks..." 
                value={taskSearch}
                onChange={(e) => setTaskSearch(e.target.value)}
                style={{ maxWidth: '240px' }}
              />

              <select 
                className="form-select" 
                value={taskStatusFilter} 
                onChange={(e) => setTaskStatusFilter(e.target.value)}
                style={{ maxWidth: '160px' }}
              >
                <option value="all">All Statuses</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="finished">Finished</option>
              </select>

              <select 
                className="form-select" 
                value={taskPriorityFilter} 
                onChange={(e) => setTaskPriorityFilter(e.target.value)}
                style={{ maxWidth: '160px' }}
              >
                <option value="all">All Priorities</option>
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>

              <select 
                className="form-select" 
                value={taskAssignmentFilter} 
                onChange={(e) => setTaskAssignmentFilter(e.target.value)}
                style={{ maxWidth: '160px' }}
              >
                <option value="all">All Tasks</option>
                <option value="assigned_to_me">Assigned to Me 👤</option>
              </select>

              <select 
                className="form-select" 
                value={taskDateSort} 
                onChange={(e) => setTaskDateSort(e.target.value)}
                style={{ maxWidth: '200px' }}
              >
                <option value="none">No Date Sorting</option>
                <option value="schedule_asc">Schedule (Earliest First)</option>
                <option value="schedule_desc">Schedule (Latest First)</option>
                <option value="due_asc">Due Date (Earliest First)</option>
                <option value="due_desc">Due Date (Latest First)</option>
              </select>
            </div>

            {!currentUser?.is_external && (
              <div style={{ display: 'flex', gap: '10px' }}>
                <button 
                  className="btn btn-secondary"
                  onClick={() => onAssignUserForProject(project.id, membersOfThisProject)}
                >
                  👤 Assign User
                </button>
                {((currentUser?.role === 'admin' || currentUser?.role === 'manager') || membersOfThisProject.some(m => m.user_id === currentUser?.id)) && (
                  <button 
                    className="btn btn-primary"
                    onClick={() => onCreateTaskForProject(project.id)}
                  >
                    + Create Task in Project
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Task List Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filteredProjectTasks.length === 0 ? (
              <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No tasks found in this project matching the selected filters.
              </div>
            ) : (
              filteredProjectTasks.map((t) => (
                <div 
                  key={t.id} 
                  className="glass-panel" 
                  onClick={() => onSelectTask(t)}
                  style={{ padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span className={`badge badge-${t.priority?.toLowerCase()}`}>{t.priority}</span>
                    <div>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '4px' }}>{t.name}</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          📅 <strong>Scheduled:</strong> {t.schedule_date || 'N/A'} | <strong>Due:</strong> {t.due_date || 'N/A'}
                        </span>
                        {t.assigned_user_names && t.assigned_user_names.length > 0 && (
                          <span style={{ fontSize: '0.78rem', color: 'var(--primary)', fontWeight: 600 }}>
                            👤 Assigned: {t.assigned_user_names.join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      💬 {(commentsMap[t.id] || []).length} comments
                    </span>
                    <span className={`badge badge-${t.status}`}>{t.status?.replace('_', ' ')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* SUB-TAB 2: TEAM CHAT */}
      {activeSubTab === 'chat' && (
        <div className="glass-panel" style={{ height: '600px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Chat Header */}
          <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-light)', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>💬 {project.name} Team Chat</h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--emerald)' }}>● Live WebSocket Active</span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {membersOfThisProject.length} Team Members Connected
            </span>
          </div>

          {/* Messages Feed */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {chatLoading ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', margin: 'auto' }}>Loading chat messages...</div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', margin: 'auto' }}>
                No messages in {project.name} team chat yet. Send a message to start!
              </div>
            ) : (
              messages.map(msg => {
                const sender = getMemberDetails(msg.member_id);
                const isMe = sender.email === currentUser?.email;

                return (
                  <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: isMe ? 'flex-end' : 'flex-start' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', padding: '0 4px' }}>
                      {isMe ? 'You' : sender.name} • {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                    <div style={{
                      padding: '12px 18px',
                      borderRadius: 'var(--radius-md)',
                      background: isMe ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
                      border: isMe ? 'none' : '1px solid var(--border-light)',
                      color: isMe ? '#fff' : 'var(--text-main)',
                      maxWidth: '75%',
                      wordBreak: 'break-word',
                      fontSize: '0.92rem',
                      lineHeight: '1.4'
                    }}>
                      {msg.content}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-light)', background: 'rgba(0,0,0,0.2)' }}>
            {chatError && <div style={{ color: 'var(--rose)', fontSize: '0.8rem', marginBottom: '8px' }}>{chatError}</div>}
            <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '12px' }}>
              <input 
                type="text" 
                className="form-input" 
                placeholder={`Message #${project.name} team...`}
                value={newMessage}
                onChange={(e) => { setNewMessage(e.target.value); setChatError(''); }}
                style={{ flex: 1 }}
              />
              <button type="submit" className="btn btn-primary" disabled={!newMessage.trim()}>Send Message</button>
            </form>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: TEAM & MEMBERS */}
      {activeSubTab === 'members' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>👥 Assigned Team Members</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                All users assigned to {project.name}'s project team workspace.
              </p>
            </div>
            {canManageProject && (
              <button 
                className="btn btn-primary"
                onClick={() => onAddTeamMemberForTeam(projectTeam.id)}
              >
                + Add User to Team
              </button>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '18px' }}>
            {membersOfThisProject.length === 0 ? (
              <div className="glass-panel" style={{ padding: '40px', gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>
                No members assigned to this team yet.
              </div>
            ) : (
              membersOfThisProject.map(m => (
                <div key={m.id} className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 700 }}>
                      {(m.name || m.email || 'U')[0].toUpperCase()}
                    </div>
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: '0 0 2px 0' }}>{m.name || 'Team Member'}</h4>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>{m.email}</span>
                      <span className="badge badge-member" style={{ fontSize: '0.68rem' }}>
                        {m.project_role === 'project_admin' ? 'Project Admin' : 'Project Member'}
                      </span>
                    </div>
                  </div>
                  {canManageProject && onRemoveTeamMember && (
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ color: 'var(--rose)', borderColor: 'rgba(239,68,68,0.3)', padding: '6px 12px' }}
                      title="Remove Member"
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to remove ${m.name || m.email} from this team?`)) {
                          onRemoveTeamMember(m.id);
                        }
                      }}
                    >
                      🗑️ Remove
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
