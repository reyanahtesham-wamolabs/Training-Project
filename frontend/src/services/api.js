const API_BASE_URL = 'http://localhost:8000';

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

export async function apiFetch(endpoint, options = {}, isRetry = false) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (
      response.status === 401 &&
      !isRetry &&
      !endpoint.includes('/Auth/login') &&
      !endpoint.includes('/Auth/refresh') &&
      !endpoint.includes('/Auth/signup_user')
    ) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        if (!isRefreshing) {
          isRefreshing = true;
          try {
            const refreshRes = await fetch(`${API_BASE_URL}/Auth/refresh`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (refreshRes.ok) {
              const refreshData = await refreshRes.json();
              const newAccessToken = refreshData.access_token;
              if (newAccessToken) {
                localStorage.setItem('access_token', newAccessToken);
                if (refreshData.refresh_token) {
                  localStorage.setItem('refresh_token', refreshData.refresh_token);
                }
                isRefreshing = false;
                onRefreshed(newAccessToken);
                return await apiFetch(endpoint, options, true);
              }
            }
          } catch (refreshErr) {
            console.warn('Token refresh error:', refreshErr);
          }

          // If refresh request failed
          isRefreshing = false;
          refreshSubscribers = [];
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.dispatchEvent(new Event('session_expired'));
        } else {
          // Queue request until token refresh completes
          return new Promise((resolve, reject) => {
            subscribeTokenRefresh(() => {
              apiFetch(endpoint, options, true).then(resolve).catch(reject);
            });
          });
        }
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `API Request Failed (${response.status})`);
    }

    return await response.json();
  } catch (err) {
    console.warn(`API call failed [${endpoint}]:`, err.message);
    throw err;
  }
}

export const authAPI = {
  login: (data) => apiFetch('/Auth/login', { method: 'POST', body: JSON.stringify(data) }),
  signup: (data) => apiFetch('/Auth/signup_user', { method: 'POST', body: JSON.stringify(data) }),
  refreshToken: (token) => apiFetch('/Auth/refresh', { method: 'POST', body: JSON.stringify({ refresh_token: token }) }),
  verifyOtp: (code, email) => apiFetch('/Auth/verify_otp', { method: 'POST', body: JSON.stringify({ otp_code: code, user_email: email }) }),
  changeName: (data) => apiFetch('/Auth/change_name', { method: 'POST', body: JSON.stringify(data) }),
  changeEmail: (data) => apiFetch('/Auth/change_email', { method: 'POST', body: JSON.stringify(data) }),
  changePassword: (data) => apiFetch('/Auth/change_password', { method: 'POST', body: JSON.stringify(data) }),
  me: () => apiFetch('/User/me'),
  softDeleteProfile: () => apiFetch('/User/soft_delete_user', { method: 'PATCH' }),
};

export const projectAPI = {
  getAll: () => apiFetch('/project/get_active_projects'),
  getActive: () => apiFetch('/project/get_active_projects'),
  getSoftDeleted: () => apiFetch('/project/get_softdeleted_projects'),
  create: (data) => apiFetch('/project/create_project', { method: 'POST', body: JSON.stringify(data) }),
  archive: (data) => apiFetch('/project/archive_project', { method: 'PATCH', body: JSON.stringify(data) }),
  update: (data) => apiFetch('/project/update_project', { method: 'PATCH', body: JSON.stringify(data) }),
  getTags: () => apiFetch('/project/get_all_tags'),
  createTag: (data) => apiFetch('/project/create_tag', { method: 'POST', body: JSON.stringify(data) }),
  hardDelete: (projectId) => apiFetch(`/project/hard_delete_project?project_id=${projectId}`, { method: 'DELETE' }),
};

export const taskAPI = {
  getAll: () => apiFetch('/task/get_active_tasks'),
  getActive: () => apiFetch('/task/get_active_tasks'),
  getSoftDeleted: () => apiFetch('/task/get_softdeleted_tasks'),
  getUserTasks: () => apiFetch('/task/get_user_tasks', { method: 'POST' }),
  create: (data) => apiFetch('/task/create_task', { method: 'POST', body: JSON.stringify(data) }),
  update: (data) => apiFetch('/task/update_task', { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (taskId) => apiFetch(`/task/delete_task?task_id=${taskId}`, { method: 'DELETE' }),
  hardDelete: (taskId) => apiFetch(`/task/hard_delete_task?task_id=${taskId}`, { method: 'DELETE' }),
  addPrerequisite: (prereqId, dependantId) =>
    apiFetch(`/task/add_prerequisite?prerequisite_id=${prereqId}&dependant_id=${dependantId}`, { method: 'PATCH' }),
};

export const commentAPI = {
  getByTask: (taskId) => apiFetch(`/comment/task/${taskId}`),
  create: (data) => apiFetch('/comment', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiFetch(`/comment/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiFetch(`/comment/${id}`, { method: 'DELETE' }),
};

export const teamAPI = {
  getAll: () => apiFetch('/Team/get_all_teams'),
  getUserTeams: () => apiFetch('/Team/get_user_teams'),
  getAllMembers: () => apiFetch('/Team/all_members'),
  create: (data) => apiFetch('/Team/create_team', { method: 'POST', body: JSON.stringify(data) }),
  addMember: (data) => apiFetch('/Team/add_member', { method: 'POST', body: JSON.stringify(data) }),
  removeMember: (id) => apiFetch(`/Team/remove_member/${id}`, { method: 'DELETE' }),
  getMembers: (teamId) => apiFetch(`/Team/team_members/${teamId}`),
  sendMessage: (data) => apiFetch('/Team/send_message', { method: 'POST', body: JSON.stringify(data) }),
  getMessages: (teamId) => apiFetch(`/Team/team_messages/${teamId}`),
};

export const notificationAPI = {
  getMy: () => apiFetch('/Notification/my'),
  markRead: (id) => apiFetch(`/Notification/read/${id}`, { method: 'PATCH' }),
  updateDeliveryTime: (id, delivered) => apiFetch(`/Notification/update_delivery_time/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ delivered })
  }),
};

export const activityAPI = {
  getLogs: () => apiFetch('/activity/get_all_logs'),
  getOwnLogs: () => apiFetch('/activity/get_own_logs'),
};

export const userManagementAPI = {
  assignUser: (data) => apiFetch('/User/assign_user', { method: 'POST', body: JSON.stringify(data) }),
  unassignUser: (data) => apiFetch('/User/unassign_user', { method: 'POST', body: JSON.stringify(data) }),
  changePrivacy: (data) => apiFetch('/User/change_user_privacy', { method: 'PATCH', body: JSON.stringify(data) }),
  getAllUsers: () => apiFetch('/User/get_all_users'),
  getActiveUsers: () => apiFetch('/User/get_active_users'),
  getSoftDeletedUsers: () => apiFetch('/User/get_softdeleted_users'),
  modifyStatus: (data) => apiFetch('/User/modify_user_status', { method: 'PATCH', body: JSON.stringify(data) }),
  changeRole: (data) => apiFetch('/User/change_user_role', { method: 'POST', body: JSON.stringify(data) }),
  createExternalCollaborator: (data) => apiFetch('/User/create_external_collaborator', { method: 'POST', body: JSON.stringify(data) }),
  hardDeleteUser: (userId) => apiFetch(`/User/hard_delete_user/${userId}`, { method: 'DELETE' }),
};

export const taskReminderAPI = {
  createOrUpdate: async (taskId, data) => {
    const res = await apiFetch(`/TaskReminder/${taskId}`, { method: 'POST', body: JSON.stringify(data) });
    return res;
  },
  get: async (taskId) => {
    const res = await apiFetch(`/TaskReminder/${taskId}`);
    return res;
  },
  delete: async (taskId) => {
    const res = await apiFetch(`/TaskReminder/${taskId}`, { method: 'DELETE' });
    return res;
  }
};
