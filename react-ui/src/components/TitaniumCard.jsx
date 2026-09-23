import React, { useState } from 'react';
import { Wifi, CreditCard, Lock, Unlock, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react';

const PERSONA_CARD_DATA = {
  'ACC-1001': {
    cardLast4: '4289',
    cardFull: '4532 8901 4289 4289',
    cvv: '842',
    exp: '09/29',
    tier: 'Tier 1 Prime',
  },
  'ACC-1002': {
    cardLast4: '5612',
    cardFull: '4111 2304 7819 5612',
    cvv: '319',
    exp: '11/27',
    tier: 'Standard Active',
  },
  'ACC-1003': {
    cardLast4: '8831',
    cardFull: '5425 9012 3456 8831',
    cvv: '402',
    exp: '04/26',
    tier: 'Suspended Facility',
  },
  'ACC-1004': {
    cardLast4: '9012',
    cardFull: '3782 8210 9901 9012',
    cvv: '718',
    exp: '08/28',
    tier: 'Security Review',
  },
};

export default function TitaniumCard({ account, onToggleFreeze, onTriggerVirtualCard }) {
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);

  // Derive persona metadata fallback
  const accountKey = account?.id || account?.account_number || 'ACC-1001';
  const meta = PERSONA_CARD_DATA[accountKey] || PERSONA_CARD_DATA['ACC-1001'];

  // Account details or fallback defaults
  const balance = account?.balance !== undefined ? account.balance : 3450.20;
  const creditLimit = account?.credit_limit !== undefined ? account.credit_limit : 20000.00;
  const availableCredit = Math.max(0, creditLimit - balance);
  const utilization = creditLimit > 0 ? ((balance / creditLimit) * 100).toFixed(1) : 0;
  const isFrozen = account?.is_frozen || false;
  const cardholderName = account?.name || 'ALEXANDER WRIGHT';
  const tier = account?.tier || meta.tier;
  const cardLast4 = account?.card_last4 || meta.cardLast4;
  const cardFull = account?.card_full || meta.cardFull;
  const cvv = showDetails ? (account?.cvv || meta.cvv) : '•••';
  const exp = account?.exp || meta.exp;
  const maskedPan = showDetails ? cardFull : `•••• •••• •••• ${cardLast4}`;

  const copyCardNumber = () => {
    navigator.clipboard?.writeText(cardFull.replace(/\s+/g, ''));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bento-box bento-card-box">
      <div className="bento-box-header">
        <div className="box-title-group">
          <CreditCard className="box-icon text-indigo" size={18} />
          <h2 className="box-title">Active Instrument</h2>
        </div>
        <div className="card-status-wrapper">
          <span className={`status-dot ${isFrozen ? 'frozen' : 'active'}`}></span>
          <span className="card-status-label">{isFrozen ? 'Card Frozen' : 'Unfrozen · Active'}</span>
        </div>
      </div>

      {/* 3D Glassmorphic Titanium Card Preview */}
      <div className={`titanium-card-container ${isFrozen ? 'card-frozen' : ''}`}>
        <div className="titanium-card-shine"></div>
        <div className="card-top-row">
          <div className="card-brand-tag">
            <span className="card-logo-apex">APEX</span>
            <span className="card-logo-type">TITANIUM CORP</span>
          </div>
          <div className="card-contactless">
            <Wifi className="rotate-90 text-slate-300" size={20} />
          </div>
        </div>

        {/* EMV Gold Chip & Hologram */}
        <div className="card-chip-row">
          <div className="emv-chip">
            <div className="chip-line line-1"></div>
            <div className="chip-line line-2"></div>
            <div className="chip-line line-3"></div>
            <div className="chip-core"></div>
          </div>
          <div className="hologram-seal">
            <ShieldCheck size={14} className="holo-icon" />
            <span>FIDO2</span>
          </div>
        </div>

        {/* Masked PAN */}
        <div className="card-number-row" onClick={copyCardNumber} title="Click to copy card number">
          <span className="card-pan-font">{maskedPan}</span>
          {copied && <span className="copied-badge">Copied!</span>}
        </div>

        {/* Cardholder & Expiry */}
        <div className="card-bottom-row">
          <div className="card-field">
            <span className="card-field-label">CARDHOLDER</span>
            <span className="card-field-value">{cardholderName.toUpperCase()}</span>
          </div>
          <div className="card-field-group">
            <div className="card-field">
              <span className="card-field-label">EXPIRES</span>
              <span className="card-field-value">{exp}</span>
            </div>
            {showDetails && (
              <div className="card-field">
                <span className="card-field-label">CVV</span>
                <span className="card-field-value">{cvv}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Financial Numbers & Utilization Gauge */}
      <div className="card-metrics-grid">
        <div className="metric-cell">
          <span className="metric-label">Current Balance</span>
          <span className="metric-value font-mono">${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          <span className="metric-subtext">Statement cycle in 14 days</span>
        </div>
        <div className="metric-cell">
          <span className="metric-label">Available Credit</span>
          <span className="metric-value font-mono text-emerald">${availableCredit.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          <span className="metric-subtext">Limit: ${creditLimit.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>

      {/* Utilization Bar */}
      <div className="utilization-meter-container">
        <div className="utilization-label-row">
          <span>Revolving Line Utilization</span>
          <span className="font-mono">{utilization}%</span>
        </div>
        <div className="utilization-track">
          <div
            className={`utilization-fill ${Number(utilization) > 50 ? 'danger' : Number(utilization) > 30 ? 'warning' : 'healthy'}`}
            style={{ width: `${Math.min(100, Math.max(5, utilization))}%` }}
          ></div>
        </div>
      </div>

      {/* Card Action Controls */}
      <div className="card-controls-row">
        <button
          className={`btn-control-toggle ${isFrozen ? 'unfreeze-action' : 'freeze-action'}`}
          onClick={onToggleFreeze}
        >
          {isFrozen ? (
            <>
              <Unlock size={14} />
              <span>Unfreeze Card</span>
            </>
          ) : (
            <>
              <Lock size={14} />
              <span>Freeze Physical Card</span>
            </>
          )}
        </button>

        <button
          className="btn-control-secondary"
          onClick={() => setShowDetails(!showDetails)}
          title="Toggle CVV & Full PAN details"
        >
          {showDetails ? <EyeOff size={14} /> : <Eye size={14} />}
          <span>{showDetails ? 'Hide CVV' : 'Reveal CVV'}</span>
        </button>

        <button
          className="btn-control-secondary"
          onClick={onTriggerVirtualCard}
          title="Generate temporary single-use virtual card token"
        >
          <Sparkles size={14} className="text-indigo" />
          <span>+ Virtual Card</span>
        </button>
      </div>
    </div>
  );
}
