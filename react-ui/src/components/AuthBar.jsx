import React from 'react';

const ACCOUNTS = [
  { id: 'ACC-1001', name: 'Alice Johnson', status: 'Active (0 waivers, 18mo, $10k limit)' },
  { id: 'ACC-1002', name: 'Bob Smith', status: 'Active (1 waiver, 3mo, $5k limit)' },
  { id: 'ACC-1003', name: 'Charlie Brown', status: 'Suspended (2 waivers, 24mo, $15k limit)' },
  { id: 'ACC-1004', name: 'Dana Scully', status: 'Fraud Alert (0 waivers, 14mo, $7.5k limit)' },
];

export default function AuthBar({ accountId, token, onSelectAccount, onRefreshToken, onClearToken }) {
  const currentAccount = ACCOUNTS.find((a) => a.id === accountId) || ACCOUNTS[0];

  return (
    <section className="auth-bar">
      <div className="auth-info">
        <label className="account-select-label" htmlFor="account-select">
          <span>Cardholder:</span>
          <select
            id="account-select"
            className="account-select"
            value={accountId}
            onChange={(e) => onSelectAccount(e.target.value)}
          >
            {ACCOUNTS.map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.id} - {acc.name} [{acc.status}]
              </option>
            ))}
          </select>
        </label>
        <span className={`status-pill ${token ? 'valid' : 'missing'}`}>
          {token ? 'JWT Active (Go Gateway Verified)' : 'No JWT Token (401 Rejection)'}
        </span>
      </div>
      <div className="auth-actions">
        <button className="btn-secondary" onClick={() => onRefreshToken(accountId)}>
          Refresh Token
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

