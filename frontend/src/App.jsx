import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import TaskDetailModal from './components/TaskDetailModal';
import CreateProjectModal from './components/CreateProjectModal';
import CreateTaskModal from './components/CreateTaskModal';
import AssignUserModal from './components/AssignUserModal';
import ActivityLogView from './components/ActivityLogView';
import NotificationDrawer from './components/NotificationDrawer';
import AuthModal from './components/AuthModal';
import AddTeamMemberModal from './components/AddTeamMemberModal';
import EditPrivacyModal from './components/EditPrivacyModal';

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

// Initial Demo Data Fallback
const INITIAL_PROJECTS = [
  { id: 'proj-1', name: 'Core AI Platform', category: 'inhouse', tags: ['AI/ML', 'Backend'], status: 'in_progress', archived: false, start_date: '2026-07-01', end_date: '2026-08-15' },
  { id: 'proj-2', name: 'Mobile App Redesign', category: 'upwork', tags: ['Frontend', 'Mobile'], status: 'planned', archived: false, start_date: '2026-07-10', end_date: '2026-09-01' },
  { id: 'proj-3', name: 'Legacy API Migration', category: 'US_based', tags: ['Backend', 'Database'], status: 'finished', archived: true, start_date: '2026-05-01', end_date: '2026-06-30' },
  { id: 'proj-4', name: 'DevOps & Security Hardening', category: 'Pak_profile', tags: ['DevOps', 'Security'], status: 'started', archived: false, start_date: '2026-07-05', end_date: '2026-08-30' },
];

const INITIAL_TASKS = [
  { id: 'task-1', name: 'Implement OAuth2 & JWT Verification', project_id: 'proj-1', status: 'in_progress', priority: 'high', schedule_date: '2026-07-22' },
  { id: 'task-2', name: 'Refactor Service Layer Dependency Injection', project_id: 'proj-1', status: 'finished', priority: 'medium', schedule_date: '2026-07-18' },
  { id: 'task-3', name: 'Design Glassmorphism Dashboard UI', project_id: 'proj-2', status: 'planned', priority: 'high', schedule_date: '2026-07-25' },
  { id: 'task-4', name: 'Postgres Enum & Schema Alignment', project_id: 'proj-3', status: 'finished', priority: 'low', schedule_date: '2026-06-15' },
];

const INITIAL_TEAMS = [
  { id: 'team-1', name: 'Alpha AI Core Team', project_id: 'proj-1' },
  { id: 'team-2', name: 'Mobile UI Developers', project_id: 'proj-2' },
];

const INITIAL_MEMBERS = [
  { id: 'mem-1', user_id: 'user-admin-1', email: 'reyan@example.com', name: 'Reyan Ahtesham', team_id: 'team-1', joined_at: '2026-07-01' },
  { id: 'mem-2', user_id: 'user-dev-2', email: 'developer@company.com', name: 'Lead Developer', team_id: 'team-1', joined_at: '2026-07-05' },
  { id: 'mem-3', user_id: 'user-designer-3', email: 'designer@company.com', name: 'UI Designer', team_id: 'team-2', joined_at: '2026-07-10' },
];

const INITIAL_COMMENTS = {
  'task-1': [
    {
      id: 'c-1',
      content: 'Make sure to handle refresh token expiration gracefully.',
      user_id: 'user-admin',
      user_name: 'Reyan (Admin)',
      task_id: 'task-1',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      reply: {
        id: 'r-1',
        content: 'Added automatic 401 interceptor for automatic refresh.',
        user_id: 'user-dev',
        user_name: 'Lead Developer',
        task_id: 'task-1',
        created_at: new Date(Date.now() - 1800000).toISOString()
      }
    }
  ]
};

const INITIAL_LOGS = [
  { id: 'log-1', action_type: 'create_project', message: "Project 'Core AI Platform' created by user 'Reyan'", modified_by_user_id: 'Reyan', project_id: 'proj-1', change_time: new Date(Date.now() - 86400000).toISOString() },
  { id: 'log-2', action_type: 'create_task', message: "Task 'Implement OAuth2 & JWT Verification' created", modified_by_user_id: 'Reyan', task_id: 'task-1', project_id: 'proj-1', change_time: new Date(Date.now() - 43200000).toISOString() },
  { id: 'log-3', action_type: 'assign_user', message: "User 'developer@company.com' assigned to task 'task-1'", modified_by_user_id: 'Reyan', task_id: 'task-1', change_time: new Date(Date.now() - 21600000).toISOString() },
];

const INITIAL_NOTIFICATIONS = [
  { id: 'n-1', subject: 'Assigned to Task', text: 'You have been assigned to task OAuth2 & JWT Verification.', read: false, created_at: new Date().toISOString() },
  { id: 'n-2', subject: 'New Comment', text: 'Reyan added a new comment on your task.', read: true, created_at: new Date(Date.now() - 7200000).toISOString() },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState(INITIAL_PROJECTS);
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [teams, setTeams] = useState(INITIAL_TEAMS);
  const [teamMembers, setTeamMembers] = useState(INITIAL_MEMBERS);
  const [commentsMap, setCommentsMap] = useState(INITIAL_COMMENTS);
  const [activityLogs, setActivityLogs] = useState(INITIAL_LOGS);
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  // Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const [currentUser, setCurrentUser] = useState({
    id: 'user-admin-1',
    name: 'Reyan Ahtesham',
    email: 'reyan@example.com',
    role: 'Admin',
    privacy_level: 'low'
  });

  // Modal States
  const [selectedTask, setSelectedTask] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [showAssignUser, setShowAssignUser] = useState(false);
  const [showAddTeamMember, setShowAddTeamMember] = useState(false);
  const [showEditPrivacy, setShowEditPrivacy] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showActivityDrawer, setShowActivityDrawer] = useState(false);

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

  // Sync with API on mount if backend is alive
  useEffect(() => {
    async function loadBackendData() {
      try {
        const fetchedProjects = await projectAPI.getAll();
        if (fetchedProjects && Array.isArray(fetchedProjects)) setProjects(fetchedProjects);
      } catch {}

      try {
        const fetchedTasks = await taskAPI.getAll();
        if (fetchedTasks && Array.isArray(fetchedTasks)) setTasks(fetchedTasks);
      } catch {}

      try {
        const fetchedLogs = await activityAPI.getLogs();
        if (fetchedLogs && Array.isArray(fetchedLogs)) setActivityLogs(fetchedLogs);
      } catch {}

      try {
        const fetchedNotifs = await notificationAPI.getMy();
        if (fetchedNotifs && Array.isArray(fetchedNotifs)) setNotifications(fetchedNotifs);
      } catch {}
    }
    loadBackendData();
  }, [isLoggedIn]);

  // Auth Handlers
  const handleLogin = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      if (response && response.access_token) {
        localStorage.setItem('access_token', response.access_token);
      }
      showToast('Logged in successfully!');
    } catch (err) {
      showToast('Signed in (Demo Mode)', 'info');
    }
    setIsLoggedIn(true);
    setCurrentUser({
      id: `user-${Date.now()}`,
      name: credentials.email.split('@')[0],
      email: credentials.email,
      role: 'Admin',
      privacy_level: 'low'
    });
    setShowAuthModal(false);
    addLog('login', `User '${credentials.email}' signed in`);
  };

  const handleSignup = async (userData) => {
    try {
      await authAPI.signup(userData);
      showToast('Account registered! Please check email for OTP verification.');
    } catch (err) {
      showToast('Signed up successfully! (Demo Mode)', 'info');
    }
    setIsLoggedIn(true);
    setCurrentUser({
      id: `user-${Date.now()}`,
      name: userData.name,
      email: userData.email,
      role: 'Member',
      privacy_level: 'low'
    });
    setShowAuthModal(false);
    addLog('create_user', `New user registered: '${userData.email}'`);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    showToast('Logged out successfully', 'info');
    addLog('logout', `User '${currentUser.email}' signed out`);
  };

  // Team Handlers
  const handleAddTeamMember = async (email, teamId) => {
    try {
      await teamAPI.addMember({ email, team_id: teamId });
      showToast(`User ${email} added to team successfully!`);
    } catch (err) {
      showToast(`User ${email} added to team (Demo Mode)`, 'info');
    }

    const newMember = {
      id: `mem-${Date.now()}`,
      user_id: `user-${Date.now()}`,
      email,
      name: email.split('@')[0],
      team_id: teamId,
      joined_at: new Date().toISOString()
    };
    setTeamMembers([...teamMembers, newMember]);
    setShowAddTeamMember(false);
    addLog('assign_user', `User '${email}' added to team '${teamId}'`);
  };

  const handleRemoveTeamMember = async (memberId) => {
    try {
      await teamAPI.removeMember(memberId);
    } catch {}
    setTeamMembers(teamMembers.filter(m => m.id !== memberId));
    showToast('Member removed from team', 'danger');
  };

  // Entity Handlers
  const handleCreateProject = async (projData) => {
    try {
      await projectAPI.create(projData);
      showToast('Project created successfully!');
    } catch (err) {
      showToast('Project created locally (Demo Mode)', 'info');
    }
    const newProj = { ...projData, id: `proj-${Date.now()}` };
    setProjects([newProj, ...projects]);
    setShowCreateProject(false);
    addLog('create_project', `Project '${newProj.name}' created by ${currentUser.name}`, newProj.id);
  };

  const handleCreateTask = async (taskData) => {
    try {
      await taskAPI.create(taskData);
      showToast('Task created successfully!');
    } catch (err) {
      showToast('Task created locally (Demo Mode)', 'info');
    }
    const newTask = { ...taskData, id: `task-${Date.now()}` };
    setTasks([newTask, ...tasks]);
    setShowCreateTask(false);
    addLog('create_task', `Task '${newTask.name}' created`, newTask.id, newTask.project_id);
  };

  const handleArchiveProject = async (projectId, archiveStatus) => {
    try {
      await projectAPI.archive({ id: projectId, archive: archiveStatus });
    } catch {}
    setProjects(projects.map(p => p.id === projectId ? { ...p, archived: archiveStatus } : p));
    showToast(`Project ${archiveStatus ? 'archived' : 'unarchived'}`);
    addLog('archive_project', `Project '${projectId}' archive state changed to ${archiveStatus}`, null, projectId);
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      await taskAPI.update({ id: taskId, status: newStatus });
    } catch {}
    setTasks(tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    if (selectedTask && selectedTask.id === taskId) {
      setSelectedTask({ ...selectedTask, status: newStatus });
    }
    showToast(`Task status updated to ${newStatus.replace('_', ' ')}`);
    addLog('update_task', `Task status updated to ${newStatus}`, taskId);
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await taskAPI.delete(taskId);
    } catch {}
    setTasks(tasks.filter(t => t.id !== taskId));
    setSelectedTask(null);
    showToast('Task deleted', 'danger');
    addLog('delete_task', `Task '${taskId}' deleted`, taskId);
  };

  const handleAddComment = async (taskId, content, parentCommentId) => {
    const newComment = {
      id: `comm-${Date.now()}`,
      content,
      user_id: currentUser.id,
      user_name: currentUser.name,
      task_id: taskId,
      parent_comment_id: parentCommentId,
      created_at: new Date().toISOString(),
      reply: null
    };

    try {
      await commentAPI.create({ content, task_id: taskId, parent_comment_id: parentCommentId });
    } catch {}

    const existingTaskComments = commentsMap[taskId] || [];
    if (parentCommentId) {
      const updated = existingTaskComments.map(c => {
        if (c.id === parentCommentId) {
          return { ...c, reply: newComment };
        }
        return c;
      });
      setCommentsMap({ ...commentsMap, [taskId]: updated });
    } else {
      setCommentsMap({ ...commentsMap, [taskId]: [newComment, ...existingTaskComments] });
    }
    showToast(parentCommentId ? 'Reply added' : 'Comment posted');
  };

  const handleAssignUser = async (data) => {
    try {
      await userManagementAPI.assignUser(data);
      showToast(`User ${data.user_email} assigned successfully!`);
    } catch (err) {
      showToast(`Assigned ${data.user_email} (Demo Mode)`, 'info');
    }
    setShowAssignUser(false);
    addLog('assign_user', `User '${data.user_email}' assigned to task '${data.task_id}' as ${data.role}`, data.task_id);
  };

  const handleChangePrivacy = async (newLevel) => {
    try {
      await userManagementAPI.changePrivacy({ level: newLevel });
    } catch {}
    setCurrentUser({ ...currentUser, privacy_level: newLevel });
    showToast(`Privacy level updated to ${newLevel.toUpperCase()}`);
    addLog('change_user_privacy', `User privacy level updated to ${newLevel.toUpperCase()}`);
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
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

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
                      onClick={() => setSelectedTask(t)}
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
                        <button 
                          className={`btn btn-sm ${p.archived ? 'btn-secondary' : 'btn-danger'}`}
                          onClick={() => handleArchiveProject(p.id, !p.archived)}
                        >
                          {p.archived ? 'Unarchive' : 'Archive'}
                        </button>
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
                      onClick={() => setSelectedTask(t)}
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
                <button className="btn btn-primary" onClick={() => setShowAddTeamMember(true)}>+ Add User to Team</button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
                {teams.map((team) => {
                  const members = teamMembers.filter(m => m.team_id === team.id);
                  return (
                    <div key={team.id} className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{team.name}</h3>
                        <span className="badge badge-admin">Team ID: {team.id}</span>
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
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onLoginSuccess={handleLogin}
          onSignupSuccess={handleSignup}
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
          onMarkAsRead={(id) => setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n))}
        />
      )}

      {showActivityDrawer && (
        <div className="modal-overlay" onClick={() => setShowActivityDrawer(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <ActivityLogView logs={activityLogs} onClose={() => setShowActivityDrawer(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
