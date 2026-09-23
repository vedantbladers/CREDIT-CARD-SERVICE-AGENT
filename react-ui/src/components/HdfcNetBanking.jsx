import React, { useState } from 'react';
import {
  Shield,
  Lock,
  Sparkles,
  Bot,
  CreditCard,
  Landmark,
  ArrowRight,
  ArrowUpRight,
  Eye,
  EyeOff,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Send,
  Zap,
  HelpCircle,
  FileText,
  Smartphone,
  Repeat,
  ShieldCheck,
  Plane,
  Laptop,
  Cloud,
  Coffee,
} from 'lucide-react';
import './HdfcNetBanking.css';

export default function HdfcNetBanking({
  account,
  accounts,
  onSelectAccount,
  onOpenAgent,
}) {
  const [showSavingsNumber, setShowSavingsNumber] = useState(false);
  const [activeTab, setActiveTab] = useState('accounts');

  // Customer & Account resolution
  const customerName = account?.name || 'Alice Johnson';
  const customerId = account?.id === 'ACC-1002' ? '5820194' : account?.id === 'ACC-1003' ? '3049182' : account?.id === 'ACC-1004' ? '9182049' : '4918204';
  const cardLast4 = account?.card_last4 || (account?.id === 'ACC-1002' ? '5612' : account?.id === 'ACC-1003' ? '8831' : account?.id === 'ACC-1004' ? '9012' : '4289');
  const balance = account?.balance !== undefined ? account.balance : 3450.20;
  const creditLimit = account?.credit_limit !== undefined ? account.credit_limit : 10000.00;
  const availableCredit = Math.max(0, creditLimit - balance);
  const isFrozen = account?.is_frozen || false;

  const handleDisputeClick = (merchant, amount) => {
    const prompt = `I noticed an unauthorized charge of $${amount.toFixed(2)} from ${merchant}. Please dispute this charge under policy guardrails.`;
    onOpenAgent(prompt);
  };

  return (
    <div className="hdfc-portal-root">
      {/* 1. Top Utility & Security Bar */}
      <div className="hdfc-top-utility-bar">
        <div className="hdfc-security-badge">
          <Lock size={12} />
          <span>HDFC Bank 256-Bit SSL Secured NetBanking • VeriSign Identity Certified</span>
        </div>
        <div className="hdfc-top-links">
          <span>Session IP: 103.21.24.12</span>
          <span className="sep">|</span>
          <span>Last Login: Today, 14:18 IST</span>
          <span className="sep">|</span>
          <span>Virtual Keypad: Active</span>
        </div>
      </div>

      {/* 2. Main HDFC Brand Header */}
      <header className="hdfc-brand-header">
        <div className="hdfc-brand-left">
          {/* Authentic HDFC Geometric Logo */}
          <div className="hdfc-emblem-box" onClick={() => setActiveTab('accounts')}>
            <div className="hdfc-logo-graphic">
              <div className="hdfc-logo-squares">
                <div className="hdfc-blue-bracket"></div>
                <div className="hdfc-red-center"></div>
              </div>
            </div>
            <div className="hdfc-brand-text">
              <span className="hdfc-bank-name">HDFC BANK</span>
              <span className="hdfc-netbanking-tag">One NetBanking • Corporate &amp; Retail</span>
            </div>
          </div>
        </div>

        <div className="hdfc-header-right">
          {/* Persona Switcher Dropdown */}
          <div className="hdfc-persona-dropdown-wrap">
            <span className="hdfc-persona-label">Persona:</span>
            <select
              className="hdfc-persona-select"
              value={account?.id || 'ACC-1001'}
              onChange={(e) => onSelectAccount(e.target.value)}
            >
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.id} • {acc.name} ({acc.tier || acc.status})
                </option>
              ))}
            </select>
          </div>

          <div className="hdfc-customer-badge">
            <span className="hdfc-customer-name">Welcome, {customerName}</span>
            <span className="hdfc-customer-id">Customer ID: {customerId} • KYC Level 3</span>
          </div>

          {/* Quick Header CTA to open Copilot */}
          <button
            className="btn-open-copilot-header"
            onClick={() => onOpenAgent()}
            title="Open Apex Autonomous Credit AI Servicing Copilot"
          >
            <Bot size={15} />
            <span>Apex AI Copilot</span>
            <Sparkles size={13} className="sparkle-icon" />
          </button>

          <button
            className="btn-logout-portal"
            onClick={() => alert('Session locked. To switch view or simulate other personas, use the persona dropdown.')}
            title="Secure Logout"
          >
            Secure Exit
          </button>
        </div>
      </header>

      {/* 3. Navigation Tabs Bar */}
      <nav className="hdfc-nav-bar">
        <ul className="hdfc-nav-list">
          <li
            className={`hdfc-nav-item ${activeTab === 'accounts' ? 'active' : ''}`}
            onClick={() => setActiveTab('accounts')}
          >
            <Landmark size={15} />
            <span>Accounts &amp; Deposits</span>
          </li>
          <li
            className={`hdfc-nav-item ${activeTab === 'funds' ? 'active' : ''}`}
            onClick={() => setActiveTab('funds')}
          >
            <Repeat size={15} />
            <span>Funds Transfer</span>
          </li>
          <li
            className={`hdfc-nav-item ${activeTab === 'billpay' ? 'active' : ''}`}
            onClick={() => setActiveTab('billpay')}
          >
            <Smartphone size={15} />
            <span>BillPay &amp; Recharge</span>
          </li>
          <li
            className={`hdfc-nav-item ${activeTab === 'cards' ? 'active' : ''}`}
            onClick={() => setActiveTab('cards')}
          >
            <CreditCard size={15} />
            <span>Cards (Titanium Prime)</span>
          </li>
          <li className="hdfc-nav-item" onClick={() => alert('Fast Loan Facility: Up to ₹15,00,000 pre-approved.')}>
            <span>Loans</span>
          </li>
          <li className="hdfc-nav-item" onClick={() => alert('Demat & Mutual Fund SIP portal available.')}>
            <span>Investments</span>
          </li>
          <li className="hdfc-nav-item" onClick={() => onOpenAgent('Can you check if I have any fee waivers or promotional upgrades available?')}>
            <span>Offers</span>
            <span className="nav-offer-tag">5 New</span>
          </li>
        </ul>
      </nav>

      {/* 4. Main Banking Dashboard */}
      <main className="hdfc-main-content">
        {/* Welcome & Security Strip */}
        <div className="hdfc-welcome-banner">
          <div className="welcome-text-col">
            <h2>Namaste, {customerName}</h2>
            <p>Relationship Branch: Mumbai Fort Corporate Hub • IFSC: HDFC0000060 • Private Banking Client</p>
          </div>
          <div className="welcome-info-pills">
            <span className="info-pill kyc-verified">
              <ShieldCheck size={14} />
              <span>Full Re-KYC Verified</span>
            </span>
            <span className="info-pill">
              <Calendar size={14} />
              <span>Statement Cycle: 15th of month</span>
            </span>
          </div>
        </div>

        {/* 5. FEATURED PROMINENT AI COPILOT CALLOUT BANNER */}
        <div className="hdfc-copilot-spotlight">
          <div className="spotlight-left">
            <div className="spotlight-icon-gem">
              <Bot size={28} className="text-white" />
            </div>
            <div className="spotlight-text-group">
              <div className="spotlight-badge-row">
                <span className="spotlight-badge">Institutional Copilot Integration</span>
                <span className="spotlight-tech-tag">Claude 3.7 • LangGraph • PostgreSQL MCP</span>
              </div>
              <h3 className="spotlight-title">Apex Autonomous Credit Servicing Copilot</h3>
              <p className="spotlight-desc">
                Need an immediate annual fee waiver, credit limit enhancement, or wish to dispute an unauthorized charge?
                Resolve your servicing requests through our deterministic fiduciary policy engine with guaranteed ACID atomic commits.
              </p>
            </div>
          </div>

          <div className="spotlight-right">
            <button className="btn-launch-spotlight" onClick={() => onOpenAgent()}>
              <span>Launch AI Servicing Copilot</span>
              <ArrowRight size={16} />
            </button>
            <span className="spotlight-guarantee-note">
              <Shield size={12} />
              <span>Zero LLM Hallucinations • Governed by 12 Statutory Rules</span>
            </span>
          </div>
        </div>

        {/* 6. Two-Column Facilities Overview: Savings Account & Credit Card */}
        <div className="hdfc-cards-row">
          {/* Savings Account Card */}
          <div className="hdfc-card-tile">
            <div className="tile-header">
              <div className="tile-title-group">
                <Landmark size={18} className="text-blue" />
                <h4 className="tile-title">Savings Advantage Account</h4>
              </div>
              <span className="tile-badge savings">Active • Salary Prime</span>
            </div>

            <div className="tile-body">
              <div className="account-number-row">
                <span className="acc-type-text">HDFC SuperSaver Corporate</span>
                <span className="acc-number-digits">
                  A/C: {showSavingsNumber ? '5010 0492 8190 1024' : '•••• •••• •••• 1024'}
                  <button
                    className="btn-eye-toggle"
                    onClick={() => setShowSavingsNumber(!showSavingsNumber)}
                    title="Toggle Account Number"
                  >
                    {showSavingsNumber ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </span>
              </div>

              <div className="balance-metric-display">
                <span className="balance-sub-label">Total Available Balance</span>
                <span className="balance-large-val font-mono">
                  ${(14250.80).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="balance-limits-row">
                <div className="limit-cell">
                  <span className="limit-lbl">Sweep-in FD Balance</span>
                  <span className="limit-val font-mono">$35,000.00</span>
                </div>
                <div className="limit-cell">
                  <span className="limit-lbl">Monthly Interest Earned</span>
                  <span className="limit-val text-green font-mono">+$84.20</span>
                </div>
              </div>
            </div>

            <div className="tile-actions-footer">
              <button
                className="tile-btn-link"
                onClick={() => alert('E-statement download initiated for last 6 months.')}
              >
                <FileText size={14} />
                <span>View Detailed Statement</span>
              </button>
              <button
                className="tile-btn-primary"
                onClick={() => alert('Quick Transfer modal opened.')}
              >
                <Send size={14} />
                <span>Send Money (IMPS)</span>
              </button>
            </div>
          </div>

          {/* Credit Card Facility (Titanium Prime) */}
          <div className="hdfc-card-tile">
            <div className="tile-header">
              <div className="tile-title-group">
                <CreditCard size={18} className="text-red" />
                <h4 className="tile-title">Apex Titanium Credit Facility</h4>
              </div>
              <span className="tile-badge credit">{isFrozen ? 'Card Frozen' : 'Active • Prime'}</span>
            </div>

            <div className="tile-body">
              {/* Credit Card Visual Strip */}
              <div className="credit-card-preview-strip">
                <div className="card-strip-info">
                  <span className="card-strip-name">APEX TITANIUM REGALIA</span>
                  <span className="card-strip-number">•••• •••• •••• {cardLast4}</span>
                </div>
                <span className="card-strip-badge">
                  {isFrozen ? 'FROZEN' : 'ACTIVE'}
                </span>
              </div>

              <div className="balance-metric-display">
                <span className="balance-sub-label">Current Outstanding Balance</span>
                <span className="balance-large-val font-mono">
                  ${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="balance-limits-row">
                <div className="limit-cell">
                  <span className="limit-lbl">Available Credit Limit</span>
                  <span className="limit-val text-green font-mono">
                    ${availableCredit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="limit-cell">
                  <span className="limit-lbl">Total Credit Limit</span>
                  <span className="limit-val font-mono">
                    ${creditLimit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>

            <div className="tile-actions-footer">
              <button
                className="tile-btn-link"
                onClick={() => onOpenAgent('Can you raise my credit limit?')}
                title="Request credit limit increase with autonomous policy evaluation"
              >
                <Zap size={14} />
                <span>Request Limit Increase (AI)</span>
              </button>
              <button
                className="tile-btn-primary"
                onClick={() => onOpenAgent()}
                title="Open card servicing copilot"
              >
                <Bot size={14} />
                <span>Card Servicing Agent</span>
              </button>
            </div>
          </div>
        </div>

        {/* 7. Quick Banking Services Grid */}
        <div className="hdfc-quick-actions-bar">
          <div className="section-headline-row">
            <h4 className="section-headline">
              <Zap size={16} className="text-blue" />
              <span>Instant NetBanking Services &amp; Autonomous AI Tools</span>
            </h4>
            <span className="text-muted text-xs">Direct API Execution</span>
          </div>

          <div className="quick-services-grid">
            <button className="quick-service-btn" onClick={() => alert('Instant Fund Transfer via UPI / IMPS selected.')}>
              <div className="quick-icon-wrap">
                <Repeat size={18} />
              </div>
              <span className="quick-btn-label">Quick Transfer</span>
            </button>

            <button className="quick-service-btn" onClick={() => alert('Credit Card Bill Pay portal opened.')}>
              <div className="quick-icon-wrap">
                <CreditCard size={18} />
              </div>
              <span className="quick-btn-label">Pay Card Bill</span>
            </button>

            <button
              className="quick-service-btn special-ai"
              onClick={() => onOpenAgent('Please waive my annual membership fee.')}
              title="Waive annual or late fees instantly via Autonomous Policy Gate"
            >
              <div className="quick-icon-wrap">
                <Sparkles size={18} />
              </div>
              <span className="quick-btn-label">Waive Fees (AI)</span>
            </button>

            <button
              className="quick-service-btn special-ai"
              onClick={() => onOpenAgent('I would like to request a credit limit increase to $14,000.')}
              title="Request credit limit enhancement"
            >
              <div className="quick-icon-wrap">
                <Zap size={18} />
              </div>
              <span className="quick-btn-label">Raise Limit (AI)</span>
            </button>

            <button
              className="quick-service-btn special-ai"
              onClick={() => onOpenAgent('I noticed an unauthorized charge of $850.00 from Delta Air Lines. Please dispute this charge under policy guardrails.')}
              title="Dispute unauthorized charges with statutory escalation"
            >
              <div className="quick-icon-wrap">
                <AlertTriangle size={18} />
              </div>
              <span className="quick-btn-label">Dispute Charge</span>
            </button>

            <button
              className="quick-service-btn"
              onClick={() => onOpenAgent('My card was lost or stolen. Please issue a replacement card immediately.')}
              title="Request physical or virtual card replacement"
            >
              <div className="quick-icon-wrap">
                <ShieldCheck size={18} />
              </div>
              <span className="quick-btn-label">Replace Card</span>
            </button>
          </div>
        </div>

        {/* 8. Recent Transactions & Statement Table with Inline AI Dispute */}
        <div className="hdfc-statement-card">
          <div className="statement-header">
            <div className="statement-title-group">
              <FileText size={18} className="text-blue" />
              <h4 className="statement-title">Recent Cardholder Transactions &amp; Activity Log</h4>
            </div>
            <div className="statement-filters">
              <span className="statement-filter-pill active">All Records</span>
              <span className="statement-filter-pill" onClick={() => onOpenAgent()}>Filter via AI</span>
            </div>
          </div>

          <table className="statement-table">
            <thead>
              <tr>
                <th>Date &amp; Time</th>
                <th>Merchant &amp; Narration</th>
                <th>Reference No</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Autonomous Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Today, 10:14 AM</td>
                <td className="tx-merchant-cell">
                  <span className="tx-merchant-name">Delta Air Lines</span>
                  <span className="tx-merchant-ref">Direct Flight Booking SFO • Merchant ID: 884192</span>
                </td>
                <td className="font-mono">TXN-904128</td>
                <td className="tx-amount-debit">-$850.00</td>
                <td><span className="text-xs text-muted">Settled POS</span></td>
                <td>
                  <button
                    className="btn-dispute-ai-table"
                    onClick={() => handleDisputeClick('Delta Air Lines', 850.00)}
                    title="Dispute this unauthorized transaction using Apex Copilot"
                  >
                    <span>Dispute with AI</span>
                    <ArrowUpRight size={11} />
                  </button>
                </td>
              </tr>
              <tr>
                <td>Yesterday, 08:40 PM</td>
                <td className="tx-merchant-cell">
                  <span className="tx-merchant-name">Electronics Depot NY</span>
                  <span className="tx-merchant-ref">POS Terminal 402 NYC</span>
                </td>
                <td className="font-mono">TXN-882144</td>
                <td className="tx-amount-debit">-$349.00</td>
                <td>
                  <span className="badge-disputed-table">
                    <CheckCircle2 size={11} />
                    <span>Disputed • $349 Credited</span>
                  </span>
                </td>
                <td>
                  <span className="text-xs text-muted">Docket #DSP-8821</span>
                </td>
              </tr>
              <tr>
                <td>Oct 01, 09:12 AM</td>
                <td className="tx-merchant-cell">
                  <span className="tx-merchant-name">AWS Cloud Services</span>
                  <span className="tx-merchant-ref">Infrastructure Recurring Compute</span>
                </td>
                <td className="font-mono">TXN-791820</td>
                <td className="tx-amount-debit">-$1,420.50</td>
                <td><span className="text-xs text-muted">Auto-Debit</span></td>
                <td><span className="text-xs text-muted">Verified</span></td>
              </tr>
              <tr>
                <td>Sep 30, 08:15 AM</td>
                <td className="tx-merchant-cell">
                  <span className="tx-merchant-name">Starbucks Coffee</span>
                  <span className="tx-merchant-ref">Contactless EMV Merchant</span>
                </td>
                <td className="font-mono">TXN-761290</td>
                <td className="tx-amount-debit">-$8.40</td>
                <td><span className="text-xs text-muted">Settled</span></td>
                <td><span className="text-xs text-muted">Verified</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>

      {/* 9. Floating EVA / Apex AI Copilot Capsule */}
      <div className="hdfc-floating-copilot">
        <button
          className="btn-floating-copilot"
          onClick={() => onOpenAgent()}
          title="Open Apex Autonomous AI Copilot"
        >
          <div className="floating-icon-wrap">
            <Bot size={18} className="text-white" />
            <div className="floating-pulse"></div>
          </div>
          <div className="floating-text-group">
            <span className="floating-title">Apex AI Servicing Copilot</span>
            <span className="floating-subtitle">Instant Fee Waiver • Limit • Disputes</span>
          </div>
          <Sparkles size={16} className="text-amber" />
        </button>
      </div>

      {/* 10. HDFC Footer */}
      <footer className="hdfc-footer">
        <div className="hdfc-footer-inner">
          <div className="footer-disclaimer">
            <p>&copy; 2026 HDFC Bank Ltd. All rights reserved. Regulated by Reserve Bank of India.</p>
            <p>
              Integrated with Apex Autonomous Servicing Copilot for academic examination demonstration.
              All operations are protected under statutory zero-liability banking frameworks and multi-signature ledger verification.
            </p>
          </div>
          <div className="footer-security-links">
            <span>Security FAQs</span>
            <span>Privacy Policy</span>
            <span>Customer Care: 1800-202-6161</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
