import React from 'react';
import { Shield, Activity, RefreshCw, KeyRound, Sun, Moon, Database, Zap, Landmark } from 'lucide-react';

export default function Header({
  accountId,
  accounts,
  onSelectAccount,
  token,
  onRefreshToken,
  onClearToken,
  theme,
  onToggleTheme,
  onBackToPortal,
}) {
  return (
    <header className="bento-header">
      <div className="header-brand">
        <div className="brand-logo-container">
          <Shield className="brand-icon" size={24} />
          <span className="brand-glow"></span>
        </div>
        <div className="brand-info">
          <div className="brand-title-row">
            <h1 className="brand-title">Apex Credit AI</h1>
            <span className="brand-badge">COPILOT v4.2</span>
          </div>
          <span className="brand-subtitle">Autonomous Financial Servicing & Fiduciary Guardrails</span>
        </div>
      </div>

      <div className="header-center-telemetry">
        <div className="telemetry-pill">
          <span className="pulse-indicator"></span>
          <span className="telemetry-text">Chi Gateway :8080 Active (14ms)</span>
          <span className="telemetry-sep">·</span>
          <Database size={13} className="telemetry-icon" />
          <span className="telemetry-text">PostgreSQL ACID Pool: Connected</span>
        </div>
      </div>

      <div className="header-actions">
        {/* Back to HDFC NetBanking Portal Button */}
        {onBackToPortal && (
          <button
            className="btn-back-portal"
            onClick={onBackToPortal}
            title="Return to HDFC NetBanking Customer Portal"
          >
            <Landmark size={14} className="text-blue" />
            <span>HDFC NetBanking</span>
          </button>
        )}

        {/* Persona Switcher Dropdown */}
        <div className="account-selector-wrapper">
          <label htmlFor="account-select" className="sr-only">Select Persona</label>
          <select
            id="account-select"
            className="bento-select"
            value={accountId}
            onChange={(e) => onSelectAccount(e.target.value)}
          >
            {accounts.map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.id} • {acc.name} ({acc.tier || acc.status})
              </option>
            ))}
          </select>
        </div>

        {/* JWT Status & Controls */}
        <div className="jwt-controls">
          <button
            className={`jwt-pill-btn ${token ? 'valid' : 'invalid'}`}
            onClick={() => onRefreshToken(accountId)}
            title="Click to refresh JWT token"
          >
            <KeyRound size={14} />
            <span>{token ? 'JWT Active' : 'No Token (401)'}</span>
            <RefreshCw size={12} className="spin-on-hover" />
          </button>
          {token && (
            <button
              className="btn-text-danger"
              onClick={onClearToken}
              title="Clear Token to test unauthorized 401 response"
            >
              Clear
            </button>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          className="btn-icon-ghost"
          onClick={onToggleTheme}
          aria-label="Toggle Theme"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
