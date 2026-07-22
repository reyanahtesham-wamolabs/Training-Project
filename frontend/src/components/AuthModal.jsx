import React, { useState } from 'react';
import { authAPI } from '../services/api';

export default function AuthModal({ onClose, onLoginSuccess }) {
  // 'signin' | 'signup' | 'otp'
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [otp, setOtp] = useState('');
  const [pendingEmail, setPendingEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onLoginSuccess({ email, password });
    } catch (err) {
      const msg = err.message || '';
      if (msg.includes('Verification Needed') || msg.toLowerCase().includes('verification')) {
        setPendingEmail(email);
        setMode('otp');
        setError('⚠️ Account not verified. A new OTP has been sent to your email.');
      } else {
        setError(msg || 'Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!name.trim()) { setError('Full name is required'); return; }
    if (password.length < 8) { setError('Password must be at least 8 characters long'); return; }
    if (!/[a-z]/.test(password)) { setError('Password must contain at least one lowercase letter'); return; }
    if (!/[A-Z]/.test(password)) { setError('Password must contain at least one uppercase letter'); return; }
    if (!/\d/.test(password)) { setError('Password must contain at least one number'); return; }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(password)) { setError('Password must contain at least one special character'); return; }
    if (/\s/.test(password)) { setError('Password must not contain whitespace'); return; }

    setLoading(true);
    try {
      await authAPI.signup({ name, email, password });
      setPendingEmail(email);
      setMode('otp');
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError('');
    if (!otp.trim()) { setError('Please enter the OTP from your email'); return; }
    setLoading(true);
    try {
      await authAPI.verifyOtp(otp, pendingEmail);
      setMode('signin');
      setEmail(pendingEmail);
      setPassword('');
      setOtp('');
      setError('');
      // Show success hint
      setError('✅ Account verified! Please sign in with your credentials.');
    } catch (err) {
      setError(err.message || 'OTP verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }} className="text-gradient">
            {mode === 'signin' ? 'Welcome Back' : mode === 'signup' ? 'Create Account' : 'Verify Email'}
          </h2>
          {onClose && <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>}
        </div>

        {/* Auth Mode Toggle (only when not on OTP step) */}
        {mode !== 'otp' && (
          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: 'var(--radius-md)', marginBottom: '20px' }}>
            <button
              type="button"
              className={`btn btn-sm ${mode === 'signin' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, border: 'none' }}
              onClick={() => { setMode('signin'); setError(''); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`btn btn-sm ${mode === 'signup' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, border: 'none' }}
              onClick={() => { setMode('signup'); setError(''); }}
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Error / Info Banner */}
        {error && (
          <div style={{
            background: error.startsWith('✅') ? 'rgba(34, 197, 94, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            border: `1px solid ${error.startsWith('✅') ? 'rgba(34, 197, 94, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
            color: error.startsWith('✅') ? '#22c55e' : 'var(--rose)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.85rem',
            marginBottom: '16px'
          }}>
            {error.startsWith('✅') ? error : `⚠️ ${error}`}
          </div>
        )}

        {/* --- SIGN IN FORM --- */}
        {mode === 'signin' && (
          <form onSubmit={handleSignIn}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input type="email" className="form-input" placeholder="name@company.com"
                value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input type="password" className="form-input" placeholder="••••••••"
                value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px', padding: '12px' }} disabled={loading}>
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        )}

        {/* --- SIGN UP FORM --- */}
        {mode === 'signup' && (
          <form onSubmit={handleSignUp}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input type="text" className="form-input" placeholder="e.g. Alex Morgan"
                value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input type="email" className="form-input" placeholder="name@company.com"
                value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input type="password" className="form-input" placeholder="e.g. Password123!"
                value={password} onChange={(e) => setPassword(e.target.value)} required />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                Min 8 chars with uppercase, lowercase, number &amp; special char (e.g. Password123!)
              </span>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px', padding: '12px' }} disabled={loading}>
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        )}

        {/* --- OTP VERIFICATION FORM --- */}
        {mode === 'otp' && (
          <form onSubmit={handleVerifyOtp}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '16px' }}>
              An OTP has been sent to <strong style={{ color: 'var(--text)' }}>{pendingEmail}</strong>. 
              If email delivery fails, check the server logs for the OTP code.
            </p>
            <div className="form-group">
              <label className="form-label">OTP Code</label>
              <input type="text" className="form-input" placeholder="Enter 6-digit OTP"
                value={otp} onChange={(e) => setOtp(e.target.value)} maxLength={6} required
                style={{ letterSpacing: '0.3rem', fontSize: '1.2rem', textAlign: 'center' }} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px', padding: '12px' }} disabled={loading}>
              {loading ? 'Verifying...' : 'Verify OTP'}
            </button>
            <button type="button" className="btn btn-secondary" style={{ width: '100%', marginTop: '8px', padding: '10px' }}
              onClick={() => { setMode('signup'); setError(''); }}>
              ← Back to Sign Up
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
