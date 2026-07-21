import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, isAdmin }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' },
    { id: 'projects', label: 'Projects', icon: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' },
    { id: 'tasks', label: 'Tasks & Board', icon: 'M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11' },
    { id: 'teams', label: 'Teams & Chat', icon: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z' },
    { id: 'activity', label: 'Audit Logs', icon: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' },
  ];

  if (isAdmin) {
    menuItems.push({ id: 'users', label: 'User Management', icon: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z' });
  }


  return (
    <aside style={{
      width: '230px',
      background: 'rgba(15, 23, 42, 0.5)',
      borderRight: '1px solid var(--border-light)',
      padding: '24px 16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      <div style={{ padding: '0 12px 12px', fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.05em' }}>
        Main Menu
      </div>
      {menuItems.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: isActive ? 'linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.1))' : 'transparent',
              border: isActive ? '1px solid var(--border-glow)' : '1px solid transparent',
              color: isActive ? '#ffffff' : 'var(--text-muted)',
              fontWeight: isActive ? 600 : 500,
              fontSize: '0.9rem',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease'
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={isActive ? 'var(--primary)' : 'currentColor'} strokeWidth="2">
              <path d={item.icon}></path>
            </svg>
            {item.label}
          </button>
        );
      })}
    </aside>
  );
}
