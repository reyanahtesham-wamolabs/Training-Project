import React from 'react';

export default function Navbar({
  currentUser,
  isLoggedIn,
  unreadNotificationsCount,
  onOpenNotifications,
  onOpenActivityLog,
  onOpenPrivacyModal,
  onOpenAuth,
  onLogout,
  onDeleteProfile,
  onOpenProfileSettings,
  onOpenCreateExternalCollaborator
}) {
  return (
    <header className="glass-panel" style={{
      borderRadius: 0,
      borderTop: 'none',
      borderLeft: 'none',
      borderRight: 'none',
      padding: '14px 28px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1, #a855f7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold',
          fontSize: '1.1rem',
          boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
        }}>
          ST
        </div>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }} className="text-gradient">
            Smart Task
          </h2>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Privacy Level Badge / Quick Edit Button */}
        {isLoggedIn && (
          <button
            className={`badge badge-${currentUser?.privacy_level || 'low'}`}
            onClick={onOpenPrivacyModal}
            style={{ cursor: 'pointer', border: 'none', padding: '6px 12px', fontSize: '0.78rem' }}
            title="Click to edit task privacy level"
          >
            🔒 Privacy: {currentUser?.privacy_level?.toUpperCase() || 'LOW'} ✎
          </button>
        )}

        {/* Create External Collaborator Button for all non-external users */}
        {isLoggedIn && !currentUser?.is_external && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={onOpenCreateExternalCollaborator}
            title="Create External Collaborator Account"
          >
            🌐 + External Collaborator
          </button>
        )}



        {/* Notifications */}
        <button
          className="btn btn-secondary btn-sm"
          style={{ position: 'relative', padding: '8px 12px' }}
          onClick={onOpenNotifications}
          title="Notifications"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
          {unreadNotificationsCount > 0 && (
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: 'var(--rose)',
              color: '#fff',
              fontSize: '0.65rem',
              fontWeight: 700,
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {unreadNotificationsCount}
            </span>
          )}
        </button>

        {/* User Info / Auth Controls */}
        {isLoggedIn ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingLeft: '12px', borderLeft: '1px solid var(--border-light)' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #06b6d4, #6366f1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.95rem'
            }}>
              {currentUser?.name?.charAt(0) || 'U'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{currentUser?.name || 'User'}</span>
              <span className={`badge badge-${currentUser?.role?.toLowerCase() || 'member'}`} style={{ fontSize: '0.62rem', padding: '1px 6px', alignSelf: 'flex-start' }}>
                {currentUser?.role || 'Member'}
              </span>
            </div>
            <button
              className="btn btn-secondary btn-sm"
              onClick={onOpenProfileSettings}
              style={{ fontSize: '0.78rem', padding: '6px 10px', marginLeft: '6px' }}
              title="Profile Settings"
            >
              Settings
            </button>
            <button
              className="btn btn-danger btn-sm"
              onClick={() => {
                if (window.confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
                  onDeleteProfile();
                }
              }}
              style={{ color: '#ffffff', fontSize: '0.78rem', padding: '6px 10px', marginLeft: '6px', backgroundColor: 'var(--rose)' }}
              title="Delete Profile"
            >
              Delete Profile
            </button>
            <button
              className="btn btn-danger btn-sm"
              onClick={onLogout}
              style={{ fontSize: '0.78rem', padding: '6px 10px', marginLeft: '6px' }}
              title="Sign Out"
            >
              Logout
            </button>
          </div>
        ) : (
          <button className="btn btn-primary btn-sm" onClick={onOpenAuth}>
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
}
