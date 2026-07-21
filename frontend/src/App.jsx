import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import TaskDetailModal from './components/TaskDetailModal';
import CreateProjectModal from './components/CreateProjectModal';
import EditProjectModal from './components/EditProjectModal';
import CreateTaskModal from './components/CreateTaskModal';
import AssignUserModal from './components/AssignUserModal';
import ActivityLogView from './components/ActivityLogView';
import NotificationDrawer from './components/NotificationDrawer';
import AuthModal from './components/AuthModal';
import AddTeamMemberModal from './components/AddTeamMemberModal';
import EditPrivacyModal from './components/EditPrivacyModal';
import TeamChatModal from './components/TeamChatModal';

import { 
  authAPI,
  projectAPI, 
  taskAPI, 
  commentAPI, 
  activityAPI, 
  notificationAPI, 
  userManagementAPI,
  teamAPI
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [teams, setTeams] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [commentsMap, setCommentsMap] = useState({});
  const [activityLogs, setActivityLogs] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [users, setUsers] = useState([]);

  // Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const [currentUser, setCurrentUser] = useState({
    id: '',
    name: 'Admin User',
    email: 'admin@company.com',
    role: 'Admin',
    privacy_level: 'low'
  });

  // Modal States
  const [selectedTask, setSelectedTask] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showEditProject, setShowEditProject] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [showAssignUser, setShowAssignUser] = useState(false);
  const [showAddTeamMember, setShowAddTeamMember] = useState(false);
  const [showEditPrivacy, setShowEditPrivacy] = useState(false);

  const [showNotifications, setShowNotifications] = useState(false);
  const [showActivityDrawer, setShowActivityDrawer] = useState(false);
  const [activeChatTeam, setActiveChatTeam] = useState(null);

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [tagFilter, setTagFilter] = useState('all');

  // Toast State
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  // Sync with API on mount & interval polling for dynamic DB updates
  const loadBackendData = async () => {
    if (!localStorage.getItem('access_token')) return;

    try {
      const fetchedProjects = await projectAPI.getAll();
      if (Array.isArray(fetchedProjects)) setProjects(fetchedProjects);
    } catch {}

    try {
      const fetchedTasks = await taskAPI.getAll();
      if (Array.isArray(fetchedTasks)) setTasks(fetchedTasks);
    } catch {}

    try {
      let fetchedTeams = await teamAPI.getAll().catch(() => teamAPI.getUserTeams());
      if (Array.isArray(fetchedTeams)) {
        setTeams(fetchedTeams);
        // Use the admin endpoint that returns all members with user name+email
        try {
          const allMembers = await teamAPI.getAllMembers();
          if (Array.isArray(allMembers)) setTeamMembers(allMembers);
        } catch {
          // Non-admin users: fetch per-team (only teams they belong to)
          let allMembers = [];
          for (const t of fetchedTeams) {
            try {
              const members = await teamAPI.getMembers(t.id);
              if (Array.isArray(members)) allMembers = allMembers.concat(members);
            } catch {}
          }
          setTeamMembers(allMembers);
        }
      }
    } catch {}

    try {
      let fetchedLogs;
      try {
        fetchedLogs = await activityAPI.getLogs();
      } catch {
        fetchedLogs = await activityAPI.getOwnLogs();
      }
      if (Array.isArray(fetchedLogs)) setActivityLogs(fetchedLogs);
    } catch {}

    try {
      const fetchedNotifs = await notificationAPI.getMy();
      if (Array.isArray(fetchedNotifs)) setNotifications(fetchedNotifs);
    } catch {}

    if (currentUser?.role === 'admin') {
      try {
        const fetchedUsers = await userManagementAPI.getAllUsers();
        if (Array.isArray(fetchedUsers)) setUsers(fetchedUsers);
      } catch {}
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      loadBackendData();
      const interval = setInterval(loadBackendData, 3000);
      return () => clearInterval(interval);
    } else {
      setProjects([]);
      setTasks([]);
      setTeams([]);
      setTeamMembers([]);
      setCommentsMap({});
      setActivityLogs([]);
      setNotifications([]);
      setUsers([]);
    }
  }, [isLoggedIn]);

  const fetchTaskComments = async (taskId) => {
    try {
      const comments = await commentAPI.getByTask(taskId);
      if (Array.isArray(comments)) {
        setCommentsMap(prev => ({ ...prev, [taskId]: comments }));
      }
    } catch {}
  };

  const handleSelectTask = (task) => {
    setSelectedTask(task);
    if (task && task.id) {
      fetchTaskComments(task.id);
    }
  };

  // Auth Handlers
  const handleLogin = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      if (response && response.access_token) {
        localStorage.setItem('access_token', response.access_token);
        // Fetch real user data from the backend
        try {
          const me = await authAPI.me();
          setCurrentUser({
            id: me.id || '',
            name: me.name || credentials.email.split('@')[0],
            email: me.email || credentials.email,
            role: me.role || 'member',
            privacy_level: me.privacy_level || 'high',
          });
        } catch {
          // Fallback if /me fails
          setCurrentUser({
            id: '',
            name: credentials.email.split('@')[0],
            email: credentials.email,
            role: 'member',
            privacy_level: 'high',
          });
        }
        setIsLoggedIn(true);
        showToast('Logged in successfully!');
        setShowAuthModal(false);
        loadBackendData();
      }
    } catch (err) {
      // Re-throw so AuthModal can display the error
      throw err;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    showToast('Logged out successfully', 'info');
  };

  // Team Handlers
  const handleAddTeamMember = async (email, teamId) => {
    try {
      await teamAPI.addMember({ email, team_id: teamId });
      showToast(`User ${email} added to team successfully!`);
      loadBackendData();
      setShowAddTeamMember(false);
    } catch (err) {
      showToast(err.message || 'Failed to add member', 'danger');
    }
  };

  const handleModifyUserStatus = async (email, active) => {
    try {
      await userManagementAPI.modifyStatus({ email, active });
      showToast(`User ${email} status updated to ${active ? 'Active' : 'Inactive'}`);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to update user status', 'danger');
    }
  };

  const handleModifyUserRole = async (email, role) => {
    try {
      await userManagementAPI.modifyStatus({ email, role });
      showToast(`User ${email} role updated to ${role}`);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to update user role', 'danger');
    }
  };

  const handleRemoveTeamMember = async (memberId) => {
    try {
      await teamAPI.removeMember(memberId);
      showToast('Member removed from team', 'danger');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to remove member', 'danger');
    }
  };

  // Entity Handlers
  const handleCreateProject = async (projData) => {
    try {
      await projectAPI.create(projData);
      showToast('Project created successfully!');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to create project', 'danger');
    }
    setShowCreateProject(false);
  };

  const handleEditProject = async (projData) => {
    try {
      await projectAPI.update(projData);
      showToast('Project updated successfully!');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to update project', 'danger');
    }
    setShowEditProject(false);
    setEditingProject(null);
  };

  const handleCreateTask = async (taskData) => {
    try {
      await taskAPI.create(taskData);
      showToast('Task created successfully!');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to create task', 'danger');
    }
    setShowCreateTask(false);
  };

  const handleArchiveProject = async (projectId, archiveStatus) => {
    try {
      await projectAPI.archive({ id: projectId, archive: archiveStatus });
      showToast(`Project ${archiveStatus ? 'archived' : 'unarchived'}`);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to archive project', 'danger');
    }
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      await taskAPI.update({ id: taskId, status: newStatus });
      showToast(`Task status updated to ${newStatus.replace('_', ' ')}`);
      loadBackendData();
      if (selectedTask && selectedTask.id === taskId) {
        setSelectedTask(prev => ({ ...prev, status: newStatus }));
      }
    } catch (err) {
      showToast(err.message || 'Failed to update task status', 'danger');
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await taskAPI.delete(taskId);
      showToast('Task deleted', 'danger');
      setSelectedTask(null);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to delete task', 'danger');
    }
  };

  const handleAddComment = async (taskId, content, parentCommentId) => {
    try {
      await commentAPI.create({ content, task_id: taskId, parent_comment_id: parentCommentId });
      showToast(parentCommentId ? 'Reply added' : 'Comment posted');
      fetchTaskComments(taskId);
    } catch (err) {
      showToast(err.message || 'Failed to post comment', 'danger');
    }
  };

  const handleAssignUser = async (data) => {
    try {
      await userManagementAPI.assignUser(data);
      showToast(`User ${data.user_email} assigned successfully!`);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to assign user', 'danger');
    }
    setShowAssignUser(false);
  };

  const handleChangePrivacy = async (newLevel) => {
    try {
      await userManagementAPI.changePrivacy({ level: newLevel });
      setCurrentUser(prev => ({ ...prev, privacy_level: newLevel }));
      showToast(`Privacy level updated to ${newLevel.toUpperCase()}`);
    } catch (err) {
      showToast(err.message || 'Failed to update privacy level', 'danger');
    }
  };

  const addLog = (action_type, message, task_id = null, project_id = null) => {
    const newLog = {
      id: `log-${Date.now()}`,
      action_type,
      message,
      modified_by_user_id: currentUser.name,
      task_id,
      project_id,
      change_time: new Date().toISOString()
    };
    setActivityLogs([newLog, ...activityLogs]);
  };

  // Collect all unique tags from projects
  const allAvailableTags = Array.from(
    new Set(projects.flatMap(p => p.tags || []))
  );

  // Filtered Projects List
  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter;
    const matchesTag = tagFilter === 'all' || (p.tags && p.tags.includes(tagFilter));
    return matchesSearch && matchesStatus && matchesCategory && matchesTag;
  });

  // Filtered Tasks List
  const filteredTasks = tasks.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || t.status === statusFilter;
    const parentProject = projects.find(p => p.id === t.project_id);
    const matchesCategory = categoryFilter === 'all' || (parentProject && parentProject.category === categoryFilter);
    const matchesTag = tagFilter === 'all' || (parentProject && parentProject.tags && parentProject.tags.includes(tagFilter));
    return matchesSearch && matchesStatus && matchesCategory && matchesTag;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="app-container">
      {/* Toast Banner */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: toast.type === 'danger' ? 'var(--rose)' : toast.type === 'info' ? 'var(--cyan)' : 'var(--emerald)',
          color: '#fff',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 9999,
          fontWeight: 600,
          fontSize: '0.9rem',
          animation: 'fadeIn 0.2s ease'
        }}>
          {toast.msg}
        </div>
      )}

      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} isAdmin={currentUser?.role === 'admin'} />

      {/* Main Content Area */}
      <div className="main-content">
        <Navbar 
          currentUser={currentUser}
          isLoggedIn={isLoggedIn}
          unreadNotificationsCount={unreadCount}
          onOpenNotifications={() => setShowNotifications(true)}
          onOpenActivityLog={() => setShowActivityDrawer(true)}
          onOpenPrivacyModal={() => setShowEditPrivacy(true)}
          onOpenAuth={() => setShowAuthModal(true)}
          onLogout={handleLogout}
        />

        <main className="content-body">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div>
              <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }} className="text-gradient">
                    Welcome back, {currentUser.name}! 👋
                  </h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
                    Enterprise task overview, team membership controls, and privacy settings.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-secondary" onClick={() => setShowCreateProject(true)}>+ New Project</button>
                  <button className="btn btn-primary" onClick={() => setShowCreateTask(true)}>+ Create Task</button>
                </div>
              </div>

              {/* Metric Stats Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '18px', marginBottom: '32px' }}>
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Total Projects</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: 'var(--primary)' }}>{projects.length}</div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--emerald)' }}>● {projects.filter(p => !p.archived).length} Active</span>
                </div>
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Active Tasks</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: 'var(--secondary)' }}>{tasks.length}</div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--cyan)' }}>● {tasks.filter(t => t.status === 'in_progress').length} In Progress</span>
                </div>
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Audit Logs</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: 'var(--cyan)' }}>{activityLogs.length}</div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recorded Events</span>
                </div>
                <div 
                  className="glass-panel" 
                  onClick={() => setShowEditPrivacy(true)}
                  style={{ padding: '20px', cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Your Privacy Level</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--primary)' }}>Edit ✎</span>
                  </div>
                  <div style={{ marginTop: '8px' }}>
                    <span className={`badge badge-${currentUser.privacy_level}`} style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
                      🔒 {currentUser.privacy_level.toUpperCase()}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '6px', display: 'block' }}>Task Visibility Filter</span>
                </div>
              </div>

              {/* Recent Tasks List Preview */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>📌 Recent Active Tasks</h3>
                  <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('tasks')}>View All Tasks →</button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {tasks.slice(0, 4).map(t => (
                    <div 
                      key={t.id} 
                      className="glass-panel" 
                      onClick={() => handleSelectTask(t)}
                      style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span className={`badge badge-${t.priority?.toLowerCase()}`}>{t.priority}</span>
                        <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{t.name}</span>
                      </div>
                      <span className={`badge badge-${t.status}`}>{t.status.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Projects Tab */}
          {activeTab === 'projects' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Project Workspaces</h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Filter projects by category, tags, and status.</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowCreateProject(true)}>+ New Project</button>
              </div>

              {/* Multi-Feature Search & Filter Bar */}
              <div className="glass-panel" style={{ padding: '16px', marginBottom: '24px', display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="🔍 Search projects by name..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ maxWidth: '260px' }}
                />

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Category:</span>
                  <select 
                    className="form-select" 
                    value={categoryFilter} 
                    onChange={(e) => setCategoryFilter(e.target.value)} 
                    style={{ maxWidth: '160px' }}
                  >
                    <option value="all">All Categories</option>
                    <option value="inhouse">In-House</option>
                    <option value="upwork">Upwork</option>
                    <option value="US_based">US Based</option>
                    <option value="Pak_profile">Pak Profile</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Tag:</span>
                  <select 
                    className="form-select" 
                    value={tagFilter} 
                    onChange={(e) => setTagFilter(e.target.value)} 
                    style={{ maxWidth: '160px' }}
                  >
                    <option value="all">All Tags</option>
                    {allAvailableTags.map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Status:</span>
                  <select 
                    className="form-select" 
                    value={statusFilter} 
                    onChange={(e) => setStatusFilter(e.target.value)} 
                    style={{ maxWidth: '160px' }}
                  >
                    <option value="all">All Statuses</option>
                    <option value="planned">Planned</option>
                    <option value="started">Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="finished">Finished</option>
                  </select>
                </div>

                {(categoryFilter !== 'all' || tagFilter !== 'all' || statusFilter !== 'all' || searchQuery) && (
                  <button 
                    className="btn btn-secondary btn-sm" 
                    onClick={() => { setCategoryFilter('all'); setTagFilter('all'); setStatusFilter('all'); setSearchQuery(''); }}
                    style={{ marginLeft: 'auto' }}
                  >
                    Reset Filters
                  </button>
                )}
              </div>

              {/* Projects Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {filteredProjects.length === 0 ? (
                  <div className="glass-panel" style={{ padding: '40px', gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No projects found matching the selected category or tag filters.
                  </div>
                ) : (
                  filteredProjects.map((p) => (
                    <div key={p.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                          <span className={`badge badge-${p.status}`}>{p.status.replace('_', ' ')}</span>
                          <span className="badge badge-member" style={{ fontSize: '0.68rem', textTransform: 'capitalize' }}>
                            📁 {p.category?.replace('_', ' ')}
                          </span>
                        </div>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px' }}>{p.name}</h3>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                          📅 {p.start_date} → {p.end_date}
                        </p>

                        {p.tags && p.tags.length > 0 && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                            {p.tags.map(t => (
                              <span key={t} className="badge badge-admin" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                                #{t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-light)', paddingTop: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.78rem', color: p.archived ? 'var(--rose)' : 'var(--emerald)' }}>
                          {p.archived ? '🔒 Archived' : '⚡ Active'}
                        </span>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            className="btn btn-sm btn-secondary"
                            onClick={() => {
                              setEditingProject(p);
                              setShowEditProject(true);
                            }}
                          >
                            Edit
                          </button>
                          <button 
                            className={`btn btn-sm ${p.archived ? 'btn-secondary' : 'btn-danger'}`}
                            onClick={() => handleArchiveProject(p.id, !p.archived)}
                          >
                            {p.archived ? 'Unarchive' : 'Archive'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Tasks Tab */}
          {activeTab === 'tasks' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Task Board & Comments</h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Filter tasks by name, category, or project tags.</p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-secondary" onClick={() => setShowAssignUser(true)}>👤 Assign User</button>
                  <button className="btn btn-primary" onClick={() => setShowCreateTask(true)}>+ Create Task</button>
                </div>
              </div>

              {/* Filter Bar */}
              <div className="glass-panel" style={{ padding: '16px', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="🔍 Search tasks..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ maxWidth: '260px' }}
                />

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Category:</span>
                  <select className="form-select" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} style={{ maxWidth: '160px' }}>
                    <option value="all">All Categories</option>
                    <option value="inhouse">In-House</option>
                    <option value="upwork">Upwork</option>
                    <option value="US_based">US Based</option>
                    <option value="Pak_profile">Pak Profile</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Tag:</span>
                  <select className="form-select" value={tagFilter} onChange={(e) => setTagFilter(e.target.value)} style={{ maxWidth: '160px' }}>
                    <option value="all">All Tags</option>
                    {allAvailableTags.map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Tasks List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {filteredTasks.length === 0 ? (
                  <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No tasks found matching the current filters.
                  </div>
                ) : (
                  filteredTasks.map((t) => (
                    <div 
                      key={t.id} 
                      className="glass-panel" 
                      onClick={() => handleSelectTask(t)}
                      style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <span className={`badge badge-${t.priority?.toLowerCase()}`}>{t.priority}</span>
                        <div>
                          <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>{t.name}</h4>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Project: {t.project_id}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          💬 {(commentsMap[t.id] || []).length} comments
                        </span>
                        <span className={`badge badge-${t.status}`}>{t.status.replace('_', ' ')}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Teams & User Membership Tab */}
          {activeTab === 'teams' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>👥 Project Teams & Members</h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Manage project teams and add users to teams.</p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>

                  <button className="btn btn-primary" onClick={() => setShowAddTeamMember(true)}>+ Add User to Team</button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
                {teams.map((team) => {
                  const members = teamMembers.filter(m => m.team_id === team.id);
                  return (
                    <div key={team.id} className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <div>
                          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{team.name}</h3>
                          <span className="badge badge-admin" style={{ marginTop: '4px', display: 'inline-block' }}>Team ID: {team.id}</span>
                        </div>
                        <button 
                          className="btn btn-primary btn-sm" 
                          onClick={() => setActiveChatTeam(team)}
                        >
                          💬 Chat
                        </button>
                      </div>

                      <div style={{ marginBottom: '16px' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Team Members ({members.length}):</span>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                          {members.length === 0 ? (
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>No members added yet.</p>
                          ) : (
                            members.map((m) => (
                              <div key={m.id} className="glass-panel" style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                  <div style={{ width: '26px', height: '26px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700 }}>
                                    {m.name ? m.name.charAt(0) : 'U'}
                                  </div>
                                  <div>
                                    <span style={{ fontWeight: 600 }}>{m.name || m.email}</span>
                                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>{m.email}</span>
                                  </div>
                                </div>
                                <button 
                                  className="btn btn-danger btn-sm" 
                                  style={{ padding: '2px 6px', fontSize: '0.7rem' }}
                                  onClick={() => handleRemoveTeamMember(m.id)}
                                >
                                  Remove
                                </button>
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Audit Logs Tab */}
          {activeTab === 'activity' && (
            <ActivityLogView logs={activityLogs} />
          )}

          {/* Users Management Tab (Admin Only) */}
          {activeTab === 'users' && currentUser?.role === 'admin' && (
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>🧑‍💼 User Management</h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Manage system users, assign roles, and toggle account access.</p>
                </div>
              </div>
              
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      <th style={{ padding: '12px', fontWeight: 600 }}>User</th>
                      <th style={{ padding: '12px', fontWeight: 600 }}>Role</th>
                      <th style={{ padding: '12px', fontWeight: 600 }}>Status</th>
                      <th style={{ padding: '12px', fontWeight: 600 }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.id} style={{ borderBottom: '1px solid var(--border-light)', fontSize: '0.9rem' }}>
                        <td style={{ padding: '12px' }}>
                          <div style={{ fontWeight: 600 }}>{u.name}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{u.email}</div>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <select 
                            className="form-input" 
                            style={{ padding: '4px 8px', width: 'auto', display: 'inline-block' }}
                            value={u.role.value || u.role} 
                            onChange={(e) => handleModifyUserRole(u.email, e.target.value)}
                            disabled={u.email === currentUser.email} // Prevent admin from changing own role easily
                          >
                            <option value="member">Member</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                          </select>
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span className={`badge ${u.active ? 'badge-emerald' : 'badge-rose'}`} style={{ backgroundColor: u.active ? 'var(--emerald)' : 'var(--rose)', color: '#fff' }}>
                            {u.active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td style={{ padding: '12px' }}>
                          {u.email !== currentUser.email && (
                            <button 
                              className={`btn btn-sm ${u.active ? 'btn-danger' : 'btn-primary'}`} 
                              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                              onClick={() => handleModifyUserStatus(u.email, !u.active)}
                            >
                              {u.active ? 'Deactivate' : 'Activate'}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}


          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="glass-panel" style={{ padding: '28px', maxWidth: '560px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 800 }}>⚙️ Account & Privacy Settings</h1>
                <button className="btn btn-primary btn-sm" onClick={() => setShowEditPrivacy(true)}>
                  Edit Privacy Level 🔒
                </button>
              </div>
              <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Current Privacy Level</span>
                <div style={{ marginTop: '8px' }}>
                  <span className={`badge badge-${currentUser.privacy_level}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
                    🔒 {currentUser.privacy_level.toUpperCase()}
                  </span>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '12px' }}>
                  Click the <strong>Edit Privacy Level</strong> button above or the Privacy badge in the header to modify visibility settings.
                </p>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Modals */}
      {(showAuthModal || !isLoggedIn) && (
        <AuthModal
          onClose={isLoggedIn ? () => setShowAuthModal(false) : undefined}
          onLoginSuccess={handleLogin}
        />
      )}

      {showEditPrivacy && (
        <EditPrivacyModal
          currentLevel={currentUser.privacy_level}
          onClose={() => setShowEditPrivacy(false)}
          onSavePrivacy={handleChangePrivacy}
        />
      )}

      {showAddTeamMember && (
        <AddTeamMemberModal
          teams={teams}
          onClose={() => setShowAddTeamMember(false)}
          onAddMember={handleAddTeamMember}
        />
      )}

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          comments={commentsMap[selectedTask.id] || []}
          onClose={() => setSelectedTask(null)}
          onAddComment={handleAddComment}
          onUpdateStatus={handleUpdateTaskStatus}
          onDeleteTask={handleDeleteTask}
        />
      )}

      {showCreateProject && (
        <CreateProjectModal
          onClose={() => setShowCreateProject(false)}
          onCreateProject={handleCreateProject}
        />
      )}

      {showEditProject && editingProject && (
        <EditProjectModal
          project={editingProject}
          onClose={() => {
            setShowEditProject(false);
            setEditingProject(null);
          }}
          onEditProject={handleEditProject}
        />
      )}

      {showCreateTask && (
        <CreateTaskModal
          projects={projects}
          onClose={() => setShowCreateTask(false)}
          onCreateTask={handleCreateTask}
        />
      )}

      {showAssignUser && (
        <AssignUserModal
          tasks={tasks}
          onClose={() => setShowAssignUser(false)}
          onAssignUser={handleAssignUser}
        />
      )}

      {showNotifications && (
        <NotificationDrawer
          notifications={notifications}
          onClose={() => setShowNotifications(false)}
          onMarkAsRead={async (id) => {
            // Optimistic UI update immediately
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
            // Persist to backend
            try { await notificationAPI.markRead(id); } catch {}
          }}
        />
      )}

      {showActivityDrawer && (
        <div className="modal-overlay" onClick={() => setShowActivityDrawer(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <ActivityLogView logs={activityLogs} onClose={() => setShowActivityDrawer(false)} />
          </div>
        </div>
      )}

      {activeChatTeam && (
        <TeamChatModal 
          team={activeChatTeam} 
          teamMembers={teamMembers} 
          currentUser={currentUser} 
          onClose={() => setActiveChatTeam(null)} 
        />
      )}
    </div>
  );
}
