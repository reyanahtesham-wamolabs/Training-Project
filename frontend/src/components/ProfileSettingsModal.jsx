import React, { useState } from 'react';
import { authAPI } from '../services/api';

export default function ProfileSettingsModal({ onClose, currentUser, loadBackendData }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [otpStep, setOtpStep] = useState(false);
  const [otpCode, setOtpCode] = useState('');

  // Form states
  const [newName, setNewName] = useState(currentUser?.name || '');
  const [newEmail, setNewEmail] = useState(currentUser?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const handleRequestChange = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (activeTab === 'profile') {
        if (newName !== currentUser.name && newEmail !== currentUser.email) {
          setError('Please change one field at a time.');
          setLoading(false);
          return;
        }

        if (newName !== currentUser.name) {
          await authAPI.changeName({ new_name: newName });
        } else if (newEmail !== currentUser.email) {
          await authAPI.changeEmail({ new_email: newEmail });
        } else {
          setError('No changes detected.');
          setLoading(false);
          return;
        }
      } else if (activeTab === 'security') {
        if (!currentPassword || !newPassword) {
          setError('Please fill out both password fields.');
          setLoading(false);
          return;
        }
        await authAPI.changePassword({ current_password: currentPassword, new_password: newPassword });
      }

      setOtpStep(true);
    } catch (err) {
      setError(err.message || 'Failed to request change.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await authAPI.verifyOtp(otpCode, currentUser.email);
      await loadBackendData(); // refresh user data
      onClose(); // close modal on success
    } catch (err) {
      setError(err.message || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content" style={{ maxWidth: '500px' }}>
        <div className="modal-header">
          <h2>Profile Settings</h2>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        {error && <div className="error-message" style={{ margin: '0 20px', padding: '10px', background: 'var(--rose)', color: 'white', borderRadius: '4px' }}>{error}</div>}

        {!otpStep ? (
          <div className="modal-body">
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
              <button 
                className={`btn ${activeTab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('profile')}
                style={{ flex: 1 }}
              >
                Profile Info
              </button>
              <button 
                className={`btn ${activeTab === 'security' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('security')}
                style={{ flex: 1 }}
              >
                Change Password
              </button>
            </div>

            <form onSubmit={handleRequestChange}>
              {activeTab === 'profile' && (
                <>
                  <div className="form-group">
                    <label>Full Name</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      value={newName} 
                      onChange={(e) => setNewName(e.target.value)} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address</label>
                    <input 
                      type="email" 
                      className="form-input" 
                      value={newEmail} 
                      onChange={(e) => setNewEmail(e.target.value)} 
                    />
                  </div>
                </>
              )}

              {activeTab === 'security' && (
                <>
                  <div className="form-group">
                    <label>Current Password</label>
                    <input 
                      type="password" 
                      className="form-input" 
                      value={currentPassword} 
                      onChange={(e) => setCurrentPassword(e.target.value)} 
                    />
                  </div>
                  <div className="form-group">
                    <label>New Password</label>
                    <input 
                      type="password" 
                      className="form-input" 
                      value={newPassword} 
                      onChange={(e) => setNewPassword(e.target.value)} 
                    />
                  </div>
                </>
              )}

              <div className="modal-footer" style={{ marginTop: '20px' }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Processing...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="modal-body">
            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <h3>Verification Required</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '10px' }}>
                We've sent a 6-character verification code to your current email address. Please enter it below to confirm this change.
              </p>
            </div>
            
            <form onSubmit={handleVerifyOtp}>
              <div className="form-group">
                <label>Verification Code (OTP)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={otpCode} 
                  onChange={(e) => setOtpCode(e.target.value)} 
                  placeholder="Enter OTP"
                  required
                />
              </div>

              <div className="modal-footer" style={{ marginTop: '20px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setOtpStep(false)}>Back</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Verifying...' : 'Verify & Apply'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
