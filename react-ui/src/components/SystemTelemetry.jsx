import React from 'react';
import { Cpu, Database, Network, ShieldCheck, CheckCircle2, Lock } from 'lucide-react';

export default function SystemTelemetry() {
  const telemetryMetrics = [
    {
      label: 'Chi Go Gateway',
      status: '14ms latency',
      badge: 'HTTP 200',
      icon: Network,
      color: 'var(--accent-emerald)',
    },
    {
      label: 'LangGraph Classifier',
      status: '99.7% confidence',
      badge: 'Active DAG',
      icon: Cpu,
      color: 'var(--accent-indigo)',
    },
    {
      label: 'PostgreSQL ACID Pool',
      status: '8 active connections',
      badge: 'WAL In-Sync',
      icon: Database,
      color: 'var(--accent-blue)',
    },
    {
      label: 'Deterministic Rules',
      status: '12 policies synced',
      badge: 'Guardrail ON',
      icon: ShieldCheck,
      color: 'var(--accent-emerald)',
    },
  ];

  return (
    <div className="bento-box bento-telemetry-box">
      <div className="bento-box-header">
        <div className="box-title-group">
          <Cpu className="box-icon text-emerald" size={18} />
          <h2 className="box-title">System Telemetry &amp; MCP</h2>
        </div>
        <span className="telemetry-live-badge">
          <span className="live-pulse"></span>
          LIVE
        </span>
      </div>

      <div className="telemetry-grid">
        {telemetryMetrics.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="telemetry-card">
              <div className="telemetry-card-top">
                <div className="telemetry-icon-wrap" style={{ color: item.color }}>
                  <Icon size={14} />
                </div>
                <span className="telemetry-badge font-mono">{item.badge}</span>
              </div>
              <span className="telemetry-card-title">{item.label}</span>
              <span className="telemetry-card-status font-mono">{item.status}</span>
            </div>
          );
        })}
      </div>

      {/* Cryptographic Signature Card */}
      <div className="crypto-audit-card">
        <div className="crypto-audit-header">
          <Lock size={12} className="text-emerald" />
          <span className="crypto-label">Ed25519 Institutional Signature</span>
        </div>
        <div className="crypto-hash font-mono">
          0x8f2a410b99c4e9f3b12...ac79
        </div>
        <div className="crypto-status">
          <CheckCircle2 size={11} className="text-emerald" />
          <span>Cryptographic ledger integrity verified</span>
        </div>
      </div>
    </div>
  );
}
