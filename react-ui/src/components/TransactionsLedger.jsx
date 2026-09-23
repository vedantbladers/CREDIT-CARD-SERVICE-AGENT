import React, { useState } from 'react';
import { Receipt, Plane, Laptop, Cloud, Coffee, AlertCircle, ArrowUpRight, CheckCircle2 } from 'lucide-react';

export default function TransactionsLedger({ onSelectPrompt }) {
  const [filter, setFilter] = useState('all');

  const transactions = [
    {
      id: 'tx-1',
      merchant: 'Delta Air Lines',
      subtext: 'Direct Flight SFO -> JFK',
      category: 'Travel & Transport',
      time: 'Today, 10:14 AM',
      amount: -850.00,
      status: 'Settled',
      icon: Plane,
      iconColor: 'var(--accent-blue)',
      canDispute: true,
    },
    {
      id: 'tx-2',
      merchant: 'Electronics Depot NY',
      subtext: 'POS Terminal 402 - Flagged',
      category: 'Consumer Electronics',
      time: 'Yesterday, 8:40 PM',
      amount: -349.00,
      status: 'Disputed via AI',
      disputeTag: '#DSP-8821',
      icon: Laptop,
      iconColor: 'var(--accent-rose)',
      canDispute: true,
    },
    {
      id: 'tx-3',
      merchant: 'AWS Cloud Services',
      subtext: 'Monthly Cluster Compute',
      category: 'Tech & Infrastructure',
      time: 'Oct 01, 09:12 AM',
      amount: -1420.50,
      status: 'Settled',
      icon: Cloud,
      iconColor: 'var(--accent-indigo)',
      canDispute: false,
    },
    {
      id: 'tx-4',
      merchant: 'Starbucks Coffee',
      subtext: 'Card Present Contactless',
      category: 'Dining & Catering',
      time: 'Sep 30, 08:15 AM',
      amount: -8.40,
      status: 'Settled',
      icon: Coffee,
      iconColor: 'var(--accent-amber)',
      canDispute: false,
    },
  ];

  const filteredTransactions = transactions.filter((t) => {
    if (filter === 'disputed') return t.status.includes('Disputed');
    if (filter === 'settled') return t.status === 'Settled';
    return true;
  });

  const handleDisputeClick = (tx) => {
    const promptText = `I noticed an unauthorized charge of $${Math.abs(tx.amount).toFixed(2)} from ${tx.merchant}. Please dispute this charge under policy guardrails.`;
    if (onSelectPrompt) {
      onSelectPrompt(promptText);
    }
  };

  return (
    <div className="bento-box bento-transactions-box">
      <div className="bento-box-header">
        <div className="box-title-group">
          <Receipt className="box-icon text-indigo" size={18} />
          <h2 className="box-title">Transactions &amp; Servicing Ledger</h2>
        </div>
        <div className="filter-pill-group">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All (142)
          </button>
          <button
            className={`filter-btn ${filter === 'disputed' ? 'active' : ''}`}
            onClick={() => setFilter('disputed')}
          >
            Disputed (1)
          </button>
          <button
            className={`filter-btn ${filter === 'settled' ? 'active' : ''}`}
            onClick={() => setFilter('settled')}
          >
            Settled
          </button>
        </div>
      </div>

      <div className="transactions-list">
        {filteredTransactions.map((tx) => {
          const Icon = tx.icon;
          return (
            <div key={tx.id} className="transaction-row">
              <div className="tx-icon-col" style={{ backgroundColor: `${tx.iconColor}15`, color: tx.iconColor }}>
                <Icon size={16} />
              </div>

              <div className="tx-details-col">
                <div className="tx-merchant-row">
                  <span className="tx-merchant">{tx.merchant}</span>
                  {tx.disputeTag && (
                    <span className="tx-dispute-pill">
                      <AlertCircle size={10} />
                      {tx.disputeTag}
                    </span>
                  )}
                </div>
                <div className="tx-sub-row">
                  <span>{tx.category}</span>
                  <span className="tx-sep">&bull;</span>
                  <span>{tx.time}</span>
                </div>
              </div>

              <div className="tx-action-col">
                <span className="tx-amount font-mono">
                  -${Math.abs(tx.amount).toFixed(2)}
                </span>
                {tx.status === 'Disputed via AI' ? (
                  <span className="badge-provisional-credit">Provisional $349 Credited</span>
                ) : tx.canDispute ? (
                  <button
                    className="btn-tx-dispute"
                    onClick={() => handleDisputeClick(tx)}
                    title="Click to auto-dispute this transaction with AI Copilot"
                  >
                    <span>Dispute</span>
                    <ArrowUpRight size={12} />
                  </button>
                ) : (
                  <span className="badge-settled">
                    <CheckCircle2 size={11} className="text-emerald" />
                    Settled
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="transactions-footer">
        <span className="footer-crypto-note font-mono">
          TLS 1.3 &bull; Institutional Ed25519 Signed Ledger
        </span>
        <span className="footer-count">Showing 4 of 142 records</span>
      </div>
    </div>
  );
}
