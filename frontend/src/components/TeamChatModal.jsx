import React, { useState, useEffect, useRef } from 'react';
import { teamAPI } from '../services/api';

export default function TeamChatModal({ team, teamMembers, currentUser, onClose }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const fetchMessages = async () => {
    try {
      const data = await teamAPI.getMessages(team.id);
      if (Array.isArray(data)) {
        setMessages(data);
      }
    } catch (err) {
      console.warn("Failed to fetch messages:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, [team.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    try {
      await teamAPI.sendMessage({ team_id: team.id, content: newMessage });
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      setError(err.message || 'Failed to send message');
    }
  };

  const getMemberDetails = (memberId) => {
    const m = teamMembers.find(member => member.id === memberId);
    return m ? { name: m.name || m.email, email: m.email } : { name: 'Unknown', email: '' };
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1000 }}>
      <div 
        className="modal-content" 
        onClick={(e) => e.stopPropagation()} 
        style={{ 
          maxWidth: '500px', 
          width: '100%', 
          height: '600px', 
          display: 'flex', 
          flexDirection: 'column',
          padding: '0'
        }}
      >
        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>💬 {team.name} Chat</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Team ID: {team.id}</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>✕</button>
        </div>

        {/* Messages Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', background: 'var(--bg-card)' }}>
          {loading ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading messages...</div>
          ) : messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', margin: 'auto' }}>No messages yet. Start the conversation!</div>
          ) : (
            messages.map(msg => {
              const sender = getMemberDetails(msg.member_id);
              const isMe = sender.email === currentUser.email;

              return (
                <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: isMe ? 'flex-end' : 'flex-start' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', padding: '0 4px' }}>
                    {isMe ? 'You' : sender.name} • {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    background: isMe ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
                    border: isMe ? 'none' : '1px solid var(--border-light)',
                    color: isMe ? '#fff' : 'var(--text-main)',
                    maxWidth: '85%',
                    wordBreak: 'break-word',
                    fontSize: '0.9rem'
                  }}>
                    {msg.content}
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-light)' }}>
          {error && <div style={{ color: 'var(--rose)', fontSize: '0.8rem', marginBottom: '8px' }}>{error}</div>}
          <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px' }}>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Type a message..." 
              value={newMessage}
              onChange={(e) => { setNewMessage(e.target.value); setError(''); }}
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn btn-primary" disabled={!newMessage.trim()}>Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}
