import React from 'react';

export default function AuthBar({ accountId, token, onRefreshToken, onClearToken }) {
  return (
    <section className="auth-bar">
      <div className="auth-info">
        <span>
          Active Cardholder: <strong>Alice Johnson ({accountId})</strong>
        </span>
        <span className={`status-pill ${token ? 'valid' : 'missing'}`}>
          {token ? 'JWT Active (Chi Protected)' : 'No JWT Token'}
        </span>
      </div>
      <div className="auth-actions">
        <button className="btn-secondary" onClick={onRefreshToken}>
          Refresh Test Token
        </button>
        {token && (
          <button className="btn-danger" onClick={onClearToken}>
            Clear Token (Test 401)
          </button>
        )}
      </div>
    </section>
  );
}
