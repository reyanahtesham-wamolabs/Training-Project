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
import CreateTagModal from './components/CreateTagModal';
import ProfileSettingsModal from './components/ProfileSettingsModal';
import CreateExternalCollaboratorModal from './components/CreateExternalCollaboratorModal';
import ProjectDetailView from './components/ProjectDetailView';

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
  const [dbTags, setDbTags] = useState([]);

  const defaultUser = {
    id: '',
    name: 'User',
    email: '',
    role: 'member',
    privacy_level: 'high',
    is_external: false
  };

  // Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const [currentUser, setCurrentUser] = useState(defaultUser);

  // Modal States
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [taskModalProjectId, setTaskModalProjectId] = useState(null);
  const [teamModalTeamId, setTeamModalTeamId] = useState(null);
  const [assignUserProjectId, setAssignUserProjectId] = useState(null);
  const [assignUserProjectMembers, setAssignUserProjectMembers] = useState(null);
  const [assignUserTaskId, setAssignUserTaskId] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showEditProject, setShowEditProject] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [showAssignUser, setShowAssignUser] = useState(false);
  const [showAddTeamMember, setShowAddTeamMember] = useState(false);
  const [showEditPrivacy, setShowEditPrivacy] = useState(false);
  const [showCreateTag, setShowCreateTag] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  const [showCreateExternalCollaborator, setShowCreateExternalCollaborator] = useState(false);

  const [showNotifications, setShowNotifications] = useState(false);
  const [showActivityDrawer, setShowActivityDrawer] = useState(false);
  const [activeChatTeam, setActiveChatTeam] = useState(null);
  const [toastedNotifIds, setToastedNotifIds] = useState(new Set());

  const checkAndNotifyUrgentNotifications = (notifList) => {
    if (!Array.isArray(notifList)) return;
    const now = Date.now();
    notifList.forEach(n => {
      if (!n.delivered || n.read) return;
      const deliveryTime = new Date(n.delivered).getTime();
      const diffMinutes = (deliveryTime - now) / 60000;

      if (diffMinutes >= 0 && diffMinutes <= 3 && !toastedNotifIds.has(n.id)) {
        showToast(`⏰ Urgent Reminder (< 3 mins): ${n.subject} - ${n.text}`, 'danger');
        setToastedNotifIds(prev => new Set(prev).add(n.id));
      }
    });
  };

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [tagFilter, setTagFilter] = useState('all');
  const [prioritySort, setPrioritySort] = useState('none');
  const [assignmentFilter, setAssignmentFilter] = useState('all');
  const [taskAssignmentFilter, setTaskAssignmentFilter] = useState('all');
  const [taskProjectFilter, setTaskProjectFilter] = useState('all');
  const [dateSort, setDateSort] = useState('none');

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
      if (Array.isArray(fetchedProjects)) {
        const sanitizedProjects = fetchedProjects.map(p => ({
          ...p,
          tags: p.tags ? p.tags.map(t => typeof t === 'string' ? t : t.name) : []
        }));
        setProjects(sanitizedProjects);
      }
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
      if (Array.isArray(fetchedNotifs)) {
        setNotifications(fetchedNotifs);
        checkAndNotifyUrgentNotifications(fetchedNotifs);
      }
    } catch {}

    try {
      const fetchedTags = await projectAPI.getTags();
      if (Array.isArray(fetchedTags)) setDbTags(fetchedTags);
    } catch {}

    if (currentUser?.role === 'admin' || currentUser?.role === 'manager') {
      try {
        const fetchedUsers = await userManagementAPI.getAllUsers();
        if (Array.isArray(fetchedUsers)) setUsers(fetchedUsers);
      } catch {}
    }
  };

  useEffect(() => {
    const handleAutoLogout = () => {
      setIsLoggedIn(false);
      setCurrentUser(null);
      showToast('Session expired. Please log in again.', 'info');
    };
    window.addEventListener('auth:logout', handleAutoLogout);
    return () => window.removeEventListener('auth:logout', handleAutoLogout);
  }, []);

  // 60-Second Notification Polling & Urgent < 3 min Toast Check
  useEffect(() => {
    if (!isLoggedIn) return;

    const pollInterval = setInterval(async () => {
      try {
        const fetchedNotifs = await notificationAPI.getMy();
        if (Array.isArray(fetchedNotifs)) {
          setNotifications(fetchedNotifs);
          checkAndNotifyUrgentNotifications(fetchedNotifs);
        }
      } catch (err) {
        console.warn("Notification polling failed:", err);
      }
    }, 60000);

    return () => clearInterval(pollInterval);
  }, [isLoggedIn, toastedNotifIds]);

  useEffect(() => {
    if (isLoggedIn) {
      const fetchUserData = async () => {
        try {
          const me = await authAPI.me();
          setCurrentUser({
            id: me.id || '',
            name: me.name || me.email.split('@')[0],
            email: me.email,
            role: me.role || 'member',
            privacy_level: me.privacy_level || 'high',
            is_external: me.is_external || false,
          });
        } catch (err) {
          console.warn("Failed to fetch user profile on reload:", err);
        }
      };

      if (!currentUser?.id) {
        fetchUserData();
      }

      loadBackendData();
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
  }, [isLoggedIn, currentUser?.id, currentUser?.role]);

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
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
        // Fetch real user data from the backend
        try {
          const me = await authAPI.me();
          setCurrentUser({
            id: me.id || '',
            name: me.name || credentials.email.split('@')[0],
            email: me.email || credentials.email,
            role: me.role || 'member',
            privacy_level: me.privacy_level || 'high',
            is_external: me.is_external || false,
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
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false);
    setCurrentUser(defaultUser);

    // Reset Data States
    setProjects([]);
    setTasks([]);
    setTeams([]);
    setTeamMembers([]);
    setCommentsMap({});
    setActivityLogs([]);
    setNotifications([]);
    setUsers([]);
    setDbTags([]);

    // Reset UI States
    setActiveTab('dashboard');
    setSelectedProject(null);
    setSelectedTask(null);

    // Reset Filter States
    setSearchQuery('');
    setStatusFilter('all');
    setCategoryFilter('all');
    setTagFilter('all');
    setPrioritySort('none');
    setAssignmentFilter('all');
    setTaskAssignmentFilter('all');
    setTaskProjectFilter('all');
    setDateSort('none');

    showToast('Logged out successfully', 'info');
  };

  const handleDeleteProfile = async () => {
    try {
      await authAPI.softDeleteProfile();
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setIsLoggedIn(false);
      setCurrentUser(defaultUser);

      // Reset Data States
      setProjects([]);
      setTasks([]);
      setTeams([]);
      setTeamMembers([]);
      setCommentsMap({});
      setActivityLogs([]);
      setNotifications([]);
      setUsers([]);
      setDbTags([]);

      // Reset UI States
      setActiveTab('dashboard');
      setSelectedProject(null);
      setSelectedTask(null);

      // Reset Filter States
      setSearchQuery('');
      setStatusFilter('all');
      setCategoryFilter('all');
      setTagFilter('all');
      setPrioritySort('none');
      setAssignmentFilter('all');
      setTaskAssignmentFilter('all');
      setTaskProjectFilter('all');
      setDateSort('none');

      showToast('Your profile has been deleted.', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to delete profile', 'danger');
    }
  };

  // Team Handlers
  const handleAddTeamMember = async (email, teamId, projectRole = 'project_member') => {
    try {
      await teamAPI.addMember({ email, team_id: teamId, project_role: projectRole });
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

  const handleCreateTag = async (tagData) => {
    try {
      await projectAPI.createTag(tagData);
      showToast('Tag created successfully!');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to create tag', 'danger');
    }
    setShowCreateTag(false);
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

  const handleRestoreTask = async (taskId) => {
    try {
      await taskAPI.update({ id: taskId, status: 'planned', soft_delete: false });
      showToast('Task restored from bin successfully!', 'success');
      loadBackendData();
      if (selectedTask && selectedTask.id === taskId) {
        setSelectedTask(prev => ({ ...prev, status: 'planned', soft_delete: false }));
      }
    } catch (err) {
      showToast(err.message || 'Failed to restore task', 'danger');
    }
  };

  const handleHardDeleteProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to PERMANENTLY delete this project? This action cannot be undone.')) return;
    try {
      await projectAPI.hardDelete(projectId);
      showToast('Project permanently deleted', 'danger');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to permanently delete project', 'danger');
    }
  };

  const handleHardDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to PERMANENTLY delete this task? This action cannot be undone.')) return;
    try {
      await taskAPI.hardDelete(taskId);
      showToast('Task permanently deleted', 'danger');
      if (selectedTask && selectedTask.id === taskId) setSelectedTask(null);
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to permanently delete task', 'danger');
    }
  };

  const handleHardDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to PERMANENTLY delete this user profile? This action cannot be undone.')) return;
    try {
      await userManagementAPI.hardDeleteUser(userId);
      showToast('User profile permanently deleted', 'danger');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to permanently delete user', 'danger');
    }
  };

  const handleUpdateTaskPriority = async (taskId, newPriority) => {
    try {
      await taskAPI.update({ id: taskId, priority: newPriority });
      showToast(`Task priority updated to ${newPriority.toUpperCase()}`, 'success');
      loadBackendData();
      if (selectedTask && selectedTask.id === taskId) {
        setSelectedTask(prev => ({ ...prev, priority: newPriority }));
      }
    } catch (err) {
      showToast(err.message || 'Failed to update task priority', 'danger');
    }
  };

  const handleUpdateTaskDates = async (taskId, datePayload) => {
    try {
      await taskAPI.update({ id: taskId, ...datePayload });
      showToast('Task dates updated successfully', 'success');
      loadBackendData();
      if (selectedTask && selectedTask.id === taskId) {
        setSelectedTask(prev => ({ ...prev, ...datePayload }));
      }
    } catch (err) {
      showToast(err.message || 'Failed to update task dates', 'danger');
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

  const handleAddPrerequisite = async (prereqId, dependantId) => {
    try {
      await taskAPI.addPrerequisite(prereqId, dependantId);
      showToast('Prerequisite linked successfully!', 'success');
      loadBackendData();
    } catch (err) {
      showToast(err.message || 'Failed to add prerequisite', 'danger');
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

  const handleEditComment = async (commentId, newContent, taskId) => {
    try {
      await commentAPI.update(commentId, { content: newContent });
      showToast('Comment updated', 'success');
      fetchTaskComments(taskId);
    } catch (err) {
      showToast(err.message || 'Failed to update comment', 'danger');
    }
  };

  const handleDeleteComment = async (commentId, taskId) => {
    try {
      await commentAPI.delete(commentId);
      showToast('Comment deleted', 'info');
      fetchTaskComments(taskId);
    } catch (err) {
      showToast(err.message || 'Failed to delete comment', 'danger');
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

  const handleUnassignUser = async (data) => {
    try {
      await userManagementAPI.unassignUser(data);
      showToast('Task assignment deleted successfully!');
      await loadBackendData();
      if (selectedTask && selectedTask.id === data.task_id) {
        const updatedTasks = await taskAPI.getAll();
        if (Array.isArray(updatedTasks)) {
          setTasks(updatedTasks);
          const currentT = updatedTasks.find(t => t.id === data.task_id);
          if (currentT) setSelectedTask(currentT);
        }
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete task assignment', 'danger');
      throw err;
    }
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
      modified_by_user_id: currentUser?.name || 'Guest',
      task_id,
      project_id,
      change_time: new Date().toISOString()
    };
    setActivityLogs([newLog, ...activityLogs]);
  };

  // Collect all unique tags from projects
  const allAvailableTags = Array.from(
    new Set([
      ...dbTags.map(t => t.name),
      ...projects.flatMap(p => p.tags || [])
    ])
  );

  const isTaskAssignedToUser = (task, user) => {
    if (!task || !user) return false;
    if (Array.isArray(task.assigned_user_ids) && (
      (user.id && task.assigned_user_ids.includes(user.id)) ||
      (user.email && task.assigned_user_ids.includes(user.email))
    )) {
      return true;
    }
    if (Array.isArray(task.assigned_user_emails) && user.email && task.assigned_user_emails.includes(user.email)) {
      return true;
    }
    if (Array.isArray(task.assignments)) {
      return task.assignments.some(a => {
        if (!a) return false;
        const uid = a.user_id || a.user?.id;
        const uemail = a.user_email || a.user?.email || a.email;
        return (user.id && uid === user.id) || (user.email && uemail === user.email);
      });
    }
    return false;
  };

  // Set of project IDs assigned to the current user (via team membership or task assignment)
  const userAssignedProjectIds = new Set([
    ...teams
      .filter(t => teamMembers.some(m => (m.user_id === currentUser?.id || m.email === currentUser?.email) && m.team_id === t.id))
      .map(t => t.project_id),
    ...tasks
      .filter(t => isTaskAssignedToUser(t, currentUser))
      .map(t => t.project_id)
  ]);

  // Filtered Projects List
  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter;
    const matchesTag = tagFilter === 'all' || (p.tags && p.tags.includes(tagFilter));
    const matchesAssignment = assignmentFilter === 'all' || (assignmentFilter === 'assigned_to_me' && userAssignedProjectIds.has(p.id));
    return matchesSearch && matchesStatus && matchesCategory && matchesTag && matchesAssignment;
  });

  // Filtered Tasks List
  const priorityRank = { high: 3, medium: 2, low: 1 };
  const filteredTasks = tasks.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || t.status === statusFilter;
    const parentProject = projects.find(p => p.id === t.project_id);
    const matchesCategory = categoryFilter === 'all' || (parentProject && parentProject.category === categoryFilter);
    const matchesTag = tagFilter === 'all' || (parentProject && parentProject.tags && parentProject.tags.includes(tagFilter));
    const matchesTaskAssignment = taskAssignmentFilter === 'all' || 
      (taskAssignmentFilter === 'assigned_to_me' && isTaskAssignedToUser(t, currentUser));
    const matchesProject = taskProjectFilter === 'all' || t.project_id === taskProjectFilter;
    const isNotSoftDeleted = !t.soft_delete;

    return isNotSoftDeleted && matchesSearch && matchesStatus && matchesCategory && matchesTag && matchesTaskAssignment && matchesProject;
  }).sort((a, b) => {
    if (dateSort === 'schedule_asc') {
      return (a.schedule_date || '9999-99-99').localeCompare(b.schedule_date || '9999-99-99');
    }
    if (dateSort === 'schedule_desc') {
      return (b.schedule_date || '').localeCompare(a.schedule_date || '');
    }
    if (dateSort === 'due_asc') {
      return (a.due_date || '9999-99-99').localeCompare(b.due_date || '9999-99-99');
    }
    if (dateSort === 'due_desc') {
      return (b.due_date || '').localeCompare(a.due_date || '');
    }
    if (prioritySort === 'high_first') {
      return (priorityRank[b.priority?.toLowerCase()] || 0) - (priorityRank[a.priority?.toLowerCase()] || 0);
    }
    if (prioritySort === 'low_first') {
      return (priorityRank[a.priority?.toLowerCase()] || 0) - (priorityRank[b.priority?.toLowerCase()] || 0);
    }
    return 0;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const todayStr = new Date().toISOString().split('T')[0];
  const assignedProjectsCount = projects.length;

  // Filter tasks specifically assigned to current user
  const userAssignedTasks = tasks.filter(t => 
    (t.assigned_user_ids && t.assigned_user_ids.includes(currentUser?.id)) ||
    (t.assigned_user_emails && t.assigned_user_emails.includes(currentUser?.email))
  );

  const assignedTasksCount = userAssignedTasks.length;
  const delayedTasksCount = userAssignedTasks.filter(t => {
    if (!t.due_date || t.status === 'finished') return false;
    return t.due_date < todayStr;
  }).length;

  const isOverallAdminOrManager = ['admin', 'manager'].includes(currentUser?.role?.toLowerCase());

  const canManageProject = (project) => {
    if (isOverallAdminOrManager) return true;
    const projectTeam = teams.find(t => t.project_id === project.id);
    if (!projectTeam) return false;
    return teamMembers.some(m => 
      m.team_id === projectTeam.id && 
      (m.user_id === currentUser?.id || m.email === currentUser?.email) && 
      m.project_role === 'project_admin'
    );
  };

  const canAssignUser = isOverallAdminOrManager || teamMembers.some(m => 
    (m.user_id === currentUser?.id || m.email === currentUser?.email) && 
    m.project_role === 'project_admin'
  );

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
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} isAdmin={currentUser?.role === 'admin'} userRole={currentUser?.role} />

      {/* Main Content Area */}
      <div className="main-content">
        <Navbar 
          currentUser={currentUser}
          isLoggedIn={isLoggedIn}
          unreadNotificationsCount={unreadCount}
          onOpenNotifications={() => setShowNotifications(true)}
          onOpenActivityLog={() => setShowActivityDrawer(true)}
          onLogout={handleLogout} 
          onOpenExternalModal={() => setShowCreateExternal(true)}
          onOpenPrivacyModal={() => setShowEditPrivacy(true)}
          onOpenAuth={() => setShowAuthModal(true)}
          unreadNotificationCount={unreadCount}
          onToggleNotifications={() => setShowNotifications(prev => !prev)}
        />

        <main className="content-body">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div>
              <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }} className="text-gradient">
                    Welcome back, {currentUser?.name || 'User'}! 👋
                  </h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
                    Enterprise task overview, team membership controls, and privacy settings.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {!currentUser?.is_external && (
                    <>
                      {isOverallAdminOrManager && (
                        <button className="btn btn-secondary" onClick={() => setShowCreateProject(true)}>+ New Project</button>
                      )}
                      <button className="btn btn-primary" onClick={() => setShowCreateTask(true)}>+ Create Task</button>
                    </>
                  )}
                </div>
              </div>

              {/* Metric Stats Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '18px', marginBottom: '32px' }}>
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>📂 Assigned Projects</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: 'var(--primary)' }}>{assignedProjectsCount}</div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--emerald)' }}>● {projects.filter(p => !p.archived).length} Active Projects</span>
                </div>

                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>📋 Assigned Tasks</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: 'var(--secondary)' }}>{assignedTasksCount}</div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--cyan)' }}>● {userAssignedTasks.filter(t => t.status === 'in_progress').length} In Progress</span>
                </div>

                <div className="glass-panel" style={{ padding: '20px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>⏰ Delayed Tasks</span>
                  <div style={{ fontSize: '2.2rem', fontWeight: 800, marginTop: '4px', color: delayedTasksCount > 0 ? 'var(--rose)' : 'var(--emerald)' }}>{delayedTasksCount}</div>
                  <span style={{ fontSize: '0.75rem', color: delayedTasksCount > 0 ? 'var(--rose)' : 'var(--emerald)' }}>
                    {delayedTasksCount > 0 ? `⚠️ ${delayedTasksCount} Past Due Date` : '✓ All Tasks On Schedule'}
                  </span>
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
                    <span className={`badge badge-${currentUser?.privacy_level || 'low'}`} style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
                      🔒 {currentUser?.privacy_level?.toUpperCase() || 'LOW'}
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
            selectedProject ? (
              <ProjectDetailView 
                project={selectedProject}
                projects={projects}
                tasks={tasks}
                teams={teams}
                teamMembers={teamMembers}
                commentsMap={commentsMap}
                currentUser={currentUser}
                onBack={() => setSelectedProject(null)}
                onSelectTask={handleSelectTask}
                onCreateTaskForProject={(projId) => {
                  setTaskModalProjectId(projId);
                  setShowCreateTask(true);
                }}
                onAssignUserForProject={(projId, members, taskId) => {
                  setAssignUserProjectId(projId);
                  setAssignUserProjectMembers(members);
                  setAssignUserTaskId(taskId || null);
                  setShowAssignUser(true);
                }}
                onAddTeamMemberForTeam={(teamId) => {
                  setTeamModalTeamId(teamId);
                  setShowAddTeamMember(true);
                }}
                onRemoveTeamMember={handleRemoveTeamMember}
                onEditProject={(p) => {
                  setEditingProject(p);
                  setShowEditProject(true);
                }}
                onArchiveProject={handleArchiveProject}
              />
            ) : (
              <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                  <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Project Workspaces</h1>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Filter projects by category, tags, and status.</p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-secondary" onClick={() => setShowCreateTag(true)}>+ Create Tag</button>
                  {isOverallAdminOrManager && (
                    <button className="btn btn-primary" onClick={() => setShowCreateProject(true)}>+ New Project</button>
                  )}
                </div>
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

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Assignment:</span>
                  <select 
                    className="form-select" 
                    value={assignmentFilter} 
                    onChange={(e) => setAssignmentFilter(e.target.value)} 
                    style={{ maxWidth: '170px' }}
                  >
                    <option value="all">All Projects</option>
                    <option value="assigned_to_me">👤 Assigned to Me</option>
                  </select>
                </div>

                {(categoryFilter !== 'all' || tagFilter !== 'all' || statusFilter !== 'all' || assignmentFilter !== 'all' || searchQuery) && (
                  <button 
                    className="btn btn-secondary btn-sm" 
                    onClick={() => { setCategoryFilter('all'); setTagFilter('all'); setStatusFilter('all'); setAssignmentFilter('all'); setSearchQuery(''); }}
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
                            className="btn btn-sm btn-primary"
                            onClick={() => setSelectedProject(p)}
                          >
                            🚀 Open Workspace
                          </button>
                          {canManageProject(p) && (
                            <>
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
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )
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
                  {!currentUser?.is_external && (
                    <>
                      {canAssignUser && (
                        <button className="btn btn-secondary" onClick={() => setShowAssignUser(true)}>👤 Assign User</button>
                      )}
                      <button className="btn btn-primary" onClick={() => setShowCreateTask(true)}>+ Create Task</button>
                    </>
                  )}
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

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Assignment:</span>
                  <select className="form-select" value={taskAssignmentFilter} onChange={(e) => setTaskAssignmentFilter(e.target.value)} style={{ maxWidth: '170px' }}>
                    <option value="all">All Tasks</option>
                    <option value="assigned_to_me">Assigned to Me 👤</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Project:</span>
                  <select className="form-select" value={taskProjectFilter} onChange={(e) => setTaskProjectFilter(e.target.value)} style={{ maxWidth: '180px' }}>
                    <option value="all">All Projects</option>
                    {projects.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Sort Dates:</span>
                  <select className="form-select" value={dateSort} onChange={(e) => setDateSort(e.target.value)} style={{ maxWidth: '210px' }}>
                    <option value="none">No Date Sorting</option>
                    <option value="schedule_asc">Schedule Date (Earliest First)</option>
                    <option value="schedule_desc">Schedule Date (Latest First)</option>
                    <option value="due_asc">Due Date (Earliest First)</option>
                    <option value="due_desc">Due Date (Latest First)</option>
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
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', marginTop: '2px' }}>
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                              📁 {projects.find(p => p.id === t.project_id)?.name || 'Unknown Project'}
                            </span>
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
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                        <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>{team.name}</h3>
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

          {/* Recycle Bin / Trash Tab */}
          {activeTab === 'bin' && currentUser?.role !== 'member' && (
            <div>
              <div style={{ marginBottom: '24px' }}>
                <h1 style={{ fontSize: '1.6rem', fontWeight: 800, margin: '0 0 6px 0' }}>🗑️ Recycle Bin & Trash</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Manage archived projects and soft-deleted tasks. You can restore them back anytime.
                </p>
              </div>

              {/* Archived Projects */}
              <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  📁 Archived Projects ({projects.filter(p => p.archived || p.soft_delete).length})
                </h2>

                {projects.filter(p => p.archived || p.soft_delete).length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                    No archived projects in recycle bin.
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
                    {projects.filter(p => p.archived || p.soft_delete).map(p => (
                      <div key={p.id} className="glass-panel" style={{ padding: '18px', borderLeft: '3px solid var(--rose)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                          <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>{p.name}</h3>
                          <span className="badge badge-archived">Archived</span>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                          Category: {p.category} | Created: {p.start_date || 'N/A'}
                        </p>
                        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ flex: 1 }}
                            onClick={() => handleArchiveProject(p.id, false)}
                          >
                            ♻️ Restore
                          </button>
                          <button
                            className="btn btn-danger btn-sm"
                            style={{ flex: 1 }}
                            onClick={() => handleHardDeleteProject(p.id)}
                          >
                            🔴 Delete Permanently
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Archived / Soft-Deleted Tasks */}
              <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  📋 Archived & Deleted Tasks ({tasks.filter(t => t.status === 'archived' || t.soft_delete).length})
                </h2>

                {tasks.filter(t => t.status === 'archived' || t.soft_delete).length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                    No archived or deleted tasks in recycle bin.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {tasks.filter(t => t.status === 'archived' || t.soft_delete).map(t => {
                      const parentProject = projects.find(p => p.id === t.project_id);
                      return (
                        <div key={t.id} className="glass-panel" style={{ padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>{t.name}</span>
                              <span className={`badge badge-${t.priority?.toLowerCase() || 'medium'}`}>{t.priority}</span>
                            </div>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              Project: {parentProject ? parentProject.name : 'Unassigned'} | Due: {t.due_date || 'N/A'}
                            </span>
                          </div>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              className="btn btn-secondary btn-sm"
                              onClick={() => handleRestoreTask(t.id)}
                            >
                              ♻️ Restore
                            </button>
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() => handleHardDeleteTask(t.id)}
                            >
                              🔴 Delete Permanently
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Soft-Deleted Profiles */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  👤 Deleted User Profiles ({users.filter(u => u.soft_delete).length})
                </h2>

                {users.filter(u => u.soft_delete).length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                    No soft-deleted user profiles in recycle bin.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {users.filter(u => u.soft_delete).map(u => (
                      <div key={u.id} className="glass-panel" style={{ padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>{u.name}</span>
                            <span className="badge badge-archived">Soft Deleted</span>
                          </div>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Email: {u.email} | Role: {u.role}
                          </span>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleModifyUserStatus(u.email, true)}
                          >
                            ♻️ Restore
                          </button>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleHardDeleteUser(u.id)}
                          >
                            🔴 Delete Permanently
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
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
                            disabled={u.email === currentUser?.email} // Prevent admin from changing own role easily
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
                          {u.email !== currentUser?.email && (
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
                  <span className={`badge badge-${currentUser?.privacy_level || 'low'}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
                    🔒 {currentUser?.privacy_level?.toUpperCase() || 'LOW'}
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
          currentLevel={currentUser?.privacy_level || 'high'}
          onClose={() => setShowEditPrivacy(false)}
          onSavePrivacy={handleChangePrivacy}
        />
      )}

      {showAddTeamMember && (
        <AddTeamMemberModal
          teams={teams}
          users={users}
          initialTeamId={teamModalTeamId}
          onClose={() => { setShowAddTeamMember(false); setTeamModalTeamId(null); }}
          onAddMember={handleAddTeamMember}
        />
      )}

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          projects={projects}
          allTasks={tasks}
          teams={teams}
          users={users}
          teamMembers={teamMembers}
          comments={commentsMap[selectedTask.id] || []}
          currentUser={currentUser}
          onClose={() => setSelectedTask(null)}
          onAddComment={handleAddComment}
          onEditComment={handleEditComment}
          onDeleteComment={handleDeleteComment}
          onUpdateStatus={handleUpdateTaskStatus}
          onUpdatePriority={handleUpdateTaskPriority}
          onUpdateDates={handleUpdateTaskDates}
          onAddPrerequisite={handleAddPrerequisite}
          onDeleteTask={handleDeleteTask}
          onUnassignUser={handleUnassignUser}
          onAssignUser={handleAssignUser}
        />
      )}

      {showCreateTag && (
        <CreateTagModal 
          onClose={() => setShowCreateTag(false)}
          onCreateTag={handleCreateTag}
        />
      )}

      {showCreateProject && (
        <CreateProjectModal
          onClose={() => setShowCreateProject(false)}
          onCreateProject={handleCreateProject}
          availableTags={allAvailableTags}
        />
      )}

      {showEditProject && editingProject && (
        <EditProjectModal
          project={editingProject}
          onClose={() => {
            setEditingProject(null);
            setShowEditProject(false);
          }}
          onEditProject={handleEditProject}
          availableTags={allAvailableTags}
          tasks={tasks}
          users={users}
          currentUser={currentUser}
          onAssignUser={handleAssignUser}
        />
      )}

      {showCreateTask && (
        <CreateTaskModal
          projects={projects}
          initialProjectId={taskModalProjectId}
          onClose={() => { setShowCreateTask(false); setTaskModalProjectId(null); }}
          onCreateTask={handleCreateTask}
        />
      )}

      {showAssignUser && (
        <AssignUserModal
          tasks={assignUserProjectId ? tasks.filter(t => t.project_id === assignUserProjectId) : tasks}
          initialTaskId={assignUserTaskId}
          users={users}
          teamMembers={teamMembers}
          projectTeamMembers={assignUserProjectMembers}
          currentUser={currentUser}
          onClose={() => {
            setShowAssignUser(false);
            setAssignUserProjectId(null);
            setAssignUserProjectMembers(null);
            setAssignUserTaskId(null);
          }}
          onAssignUser={handleAssignUser}
        />
      )}

      {showNotifications && (
        <NotificationDrawer
          notifications={notifications}
          onClose={() => setShowNotifications(false)}
          onMarkAsRead={async (id) => {
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
            try { await notificationAPI.markRead(id); } catch {}
          }}
          onUpdateDeliveryTime={async (id, delivered) => {
            try {
              await notificationAPI.updateDeliveryTime(id, delivered);
              showToast('Notification delivery time rescheduled!', 'success');
              loadBackendData();
            } catch (err) {
              showToast(err.message || 'Failed to reschedule delivery time', 'danger');
            }
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

      {showProfileSettings && (
        <ProfileSettingsModal
          currentUser={currentUser}
          onClose={() => setShowProfileSettings(false)}
          loadBackendData={loadBackendData}
        />
      )}

      {showCreateExternalCollaborator && (
        <CreateExternalCollaboratorModal
          projects={projects}
          onClose={() => setShowCreateExternalCollaborator(false)}
          onSuccess={loadBackendData}
          showToast={showToast}
        />
      )}
    </div>
  );
}
