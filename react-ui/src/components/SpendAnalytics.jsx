import React from 'react';
import { PieChart, TrendingUp, Calendar, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function SpendAnalytics({ account }) {
  const balance = account?.balance !== undefined ? account.balance : 3450.20;
  const creditLimit = account?.credit_limit !== undefined ? account.credit_limit : 20000.00;
  const utilization = creditLimit > 0 ? ((balance / creditLimit) * 100).toFixed(1) : '17.2';

  const spendClusters = [
    { name: 'Tech & Cloud Ops', percent: 42, amount: '$1,449.00', color: 'var(--accent-blue)' },
    { name: 'Corporate Travel', percent: 31, amount: '$1,069.50', color: 'var(--accent-indigo)' },
    { name: 'Retail & Office Misc', percent: 27, amount: '$931.70', color: 'var(--accent-emerald)' },
  ];

  return (
    <div className="bento-box bento-analytics-box">
      <div className="bento-box-header">
        <div className="box-title-group">
          <TrendingUp className="box-icon text-blue" size={18} />
          <h2 className="box-title">Credit &amp; Spend Analytics</h2>
        </div>
        <span className="box-tag font-mono">OCT 2025</span>
      </div>

      {/* Main Gauge Summary */}
      <div className="analytics-summary-card">
        <div className="gauge-metric-group">
          <span className="analytics-label">CREDIT UTILIZATION</span>
          <div className="gauge-number-row">
            <span className="gauge-val font-mono">{utilization}%</span>
            <span className="gauge-badge-healthy">Healthy &bull; &lt;30%</span>
          </div>
          <span className="gauge-subtext">
            ${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })} of ${creditLimit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
        </div>

        <div className="risk-metric-group">
          <div className="risk-header">
            <ShieldCheck size={14} className="text-emerald" />
            <span className="risk-label">AI RISK SCORE</span>
          </div>
          <span className="risk-score font-mono">0.04</span>
          <span className="risk-badge">Ultra Safe</span>
        </div>
      </div>

      {/* Spending Breakdown Clusters */}
      <div className="spending-clusters-section">
        <span className="section-mini-heading">SPENDING BY CATEGORY CLUSTER</span>
        <div className="clusters-bar-track">
          {spendClusters.map((cluster, i) => (
            <div
              key={i}
              className="cluster-bar-segment"
              style={{ width: `${cluster.percent}%`, backgroundColor: cluster.color }}
              title={`${cluster.name}: ${cluster.percent}%`}
            ></div>
          ))}
        </div>

        <div className="clusters-legend-list">
          {spendClusters.map((cluster, i) => (
            <div key={i} className="cluster-legend-item">
              <div className="legend-name-group">
                <span className="legend-dot" style={{ backgroundColor: cluster.color }}></span>
                <span className="legend-name">{cluster.name}</span>
                <span className="legend-pct font-mono">({cluster.percent}%)</span>
              </div>
              <span className="legend-amount font-mono">{cluster.amount}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Auto-pay Banner */}
      <div className="autopay-notice-card">
        <div className="autopay-icon-col">
          <Calendar size={18} className="text-indigo" />
        </div>
        <div className="autopay-details">
          <div className="autopay-title-row">
            <span className="autopay-amount font-mono">$450.00</span>
            <span className="autopay-due">due Oct 15</span>
          </div>
          <div className="autopay-sub">
            <CheckCircle2 size={12} className="text-emerald" />
            <span>Auto-pay active: Chase Business (*9912)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
