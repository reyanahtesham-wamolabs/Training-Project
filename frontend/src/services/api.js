const API_BASE_URL = 'http://localhost:8000';

export async function apiFetch(endpoint, options = {}) {
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
  login: (data) => apiFetch('/Auth/login/', { method: 'POST', body: JSON.stringify(data) }),
  signup: (data) => apiFetch('/Auth/signup_user/', { method: 'POST', body: JSON.stringify(data) }),
  verifyOtp: (code, email) => apiFetch(`/Auth/verify_otp?opt_code=${code}&user_email=${email}`, { method: 'POST' }),
  me: () => apiFetch('/User/get_all_users'),
};

export const projectAPI = {
  getAll: () => apiFetch('/project/get_all_projects/'),
  create: (data) => apiFetch('/project/create_project/', { method: 'POST', body: JSON.stringify(data) }),
  archive: (data) => apiFetch('/project/archive_project/', { method: 'PATCH', body: JSON.stringify(data) }),
  getTags: () => apiFetch('/project/get_all_tags/'),
  createTag: (data) => apiFetch('/project/create_tag/', { method: 'POST', body: JSON.stringify(data) }),
};

export const taskAPI = {
  getAll: () => apiFetch('/task/view_task/'),
  create: (data) => apiFetch('/task/create_task/', { method: 'POST', body: JSON.stringify(data) }),
  update: (data) => apiFetch('/task/update_task/', { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (taskId) => apiFetch(`/task/delete_task/?task_id=${taskId}`, { method: 'DELETE' }),
  addPrerequisite: (prereqId, dependantId) => 
    apiFetch(`/task/add_prerequisite/?prerequisite_id=${prereqId}&dependant_id=${dependantId}`, { method: 'PATCH' }),
};

export const commentAPI = {
  getByTask: (taskId) => apiFetch(`/comment/task/${taskId}/`),
  create: (data) => apiFetch('/comment/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiFetch(`/comment/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiFetch(`/comment/${id}/`, { method: 'DELETE' }),
};

export const teamAPI = {
  create: (data) => apiFetch('/Team/create_team/', { method: 'POST', body: JSON.stringify(data) }),
  addMember: (data) => apiFetch('/Team/add_member/', { method: 'POST', body: JSON.stringify(data) }),
  removeMember: (id) => apiFetch(`/Team/remove_member/${id}/`, { method: 'DELETE' }),
  getMembers: (teamId) => apiFetch(`/Team/team_members/${teamId}/`),
  sendMessage: (data) => apiFetch('/Team/send_message/', { method: 'POST', body: JSON.stringify(data) }),
  getMessages: (teamId) => apiFetch(`/Team/team_messages/${teamId}/`),
};

export const notificationAPI = {
  getMy: () => apiFetch('/Notification/my/'),
  markRead: (id) => apiFetch(`/Notification/read/${id}/`, { method: 'PATCH' }),
};

export const activityAPI = {
  getLogs: () => apiFetch('/activity/'),
};

export const userManagementAPI = {
  assignUser: (data) => apiFetch('/User/assign_user', { method: 'POST', body: JSON.stringify(data) }),
  changePrivacy: (data) => apiFetch('/User/change_user_privacy/', { method: 'PATCH', body: JSON.stringify(data) }),
};
