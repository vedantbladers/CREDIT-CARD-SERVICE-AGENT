import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import TitaniumCard from './components/TitaniumCard';
import SpendAnalytics from './components/SpendAnalytics';
import TransactionsLedger from './components/TransactionsLedger';
import SystemTelemetry from './components/SystemTelemetry';
import ChatMessages from './components/ChatMessages';
import Suggestions from './components/Suggestions';
import ChatInput from './components/ChatInput';
import { getTestToken, sendChatMessage, getAccounts } from './services/api';
import HdfcNetBanking from './components/HdfcNetBanking';
import { Bot, Sparkles, Terminal } from 'lucide-react';
import './App.css';

const DEFAULT_ACCOUNTS = [
  {
    id: 'ACC-1001',
    name: 'Alice Johnson',
    tier: 'Tier 1 Prime',
    balance: 3450.20,
    credit_limit: 10000.00,
    is_frozen: false,
    card_last4: '4289',
    card_full: '4532 8901 4289 4289',
    cvv: '842',
    exp: '09/29',
    status: '0 waivers • 18mo • $10k limit',
  },
  {
    id: 'ACC-1002',
    name: 'Bob Smith',
    tier: 'Standard Active',
    balance: 1840.50,
    credit_limit: 5000.00,
    is_frozen: false,
    card_last4: '5612',
    card_full: '4111 2304 7819 5612',
    cvv: '319',
    exp: '11/27',
    status: '1 waiver • 3mo • $5k limit',
  },
  {
    id: 'ACC-1003',
    name: 'Charlie Brown',
    tier: 'Suspended Facility',
    balance: 14200.00,
    credit_limit: 15000.00,
    is_frozen: true,
    card_last4: '8831',
    card_full: '5425 9012 3456 8831',
    cvv: '402',
    exp: '04/26',
    status: '2 waivers • 24mo • Suspended',
  },
  {
    id: 'ACC-1004',
    name: 'Dana Scully',
    tier: 'Security Review',
    balance: 420.00,
    credit_limit: 7500.00,
    is_frozen: false,
    card_last4: '9012',
    card_full: '3782 8210 9901 9012',
    cvv: '718',
    exp: '08/28',
    status: '0 waivers • 14mo • Fraud Alert',
  },
];

export default function App() {
  const [currentView, setCurrentView] = useState('netbanking');
  const [theme, setTheme] = useState('dark');
  const [accounts, setAccounts] = useState(DEFAULT_ACCOUNTS);
  const [accountId, setAccountId] = useState('ACC-1001');
  const [token, setToken] = useState('');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorBanner, setErrorBanner] = useState('');
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: 'Good morning. Apex Autonomous Servicing Copilot initialized for session #SES-8821. Deterministic fiduciary policy engine is active with real-time PostgreSQL MCP ACID ledger integration. How can I assist with your credit facility today?',
      intent: 'system',
      status: 'ready',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  // Apply theme class to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const currentAccount = accounts.find((a) => a.id === accountId) || accounts[0];

  // Fetch token on account selection
  const fetchToken = async (targetAccountId = accountId) => {
    try {
      setErrorBanner('');
      const data = await getTestToken(targetAccountId);
      setToken(data.token);
      setAccountId(data.account_id || targetAccountId);
    } catch (err) {
      console.warn('Could not auto-fetch test token from Go Gateway:', err);
      setErrorBanner(
        'Go Gateway (:8080) is currently offline or unreachable. Please launch containers with "docker compose up -d".'
      );
    }
  };

  const handleAccountChange = async (newAccountId) => {
    setAccountId(newAccountId);
    await fetchToken(newAccountId);
  };

  useEffect(() => {
    fetchToken('ACC-1001');
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Handle card freeze toggle
  const handleToggleFreeze = () => {
    const willFreeze = !currentAccount.is_frozen;
    setAccounts((prev) =>
      prev.map((acc) =>
        acc.id === accountId ? { ...acc, is_frozen: willFreeze } : acc
      )
    );

    const actionText = willFreeze
      ? `Cryptographic hold engaged on card ${accountId}. POS and online merchants blocked.`
      : `Card ${accountId} reactivated. Contactless and merchant charges unlocked.`;

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: 'agent',
        text: actionText,
        intent: 'freeze_card',
        policy_decision: 'APPROVED',
        policy_rule: 'POL-SECURITY-FREEZE',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  // Generate virtual card
  const handleTriggerVirtualCard = () => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: 'agent',
        text: `Temporary virtual card issued for ${currentAccount.name}: 4532 •••• •••• 9812 (EXP: 10/26, CVV: 409). Single-use spend cap: $500.00. Ready for Apple Pay & Google Wallet.`,
        intent: 'virtual_card_generator',
        policy_decision: 'APPROVED',
        policy_rule: 'POL-VIRTUAL-TOKEN',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  // Chat message submission
  const handleSend = async (customMessage) => {
    const textToSend = (customMessage || inputText).trim();
    if (!textToSend || loading) return;

    setErrorBanner('');
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: 'user',
        text: textToSend,
        time: currentTime,
      },
    ]);
    setInputText('');
    setLoading(true);

    try {
      const data = await sendChatMessage(textToSend, token, accountId);

      // If MCP tool returned updated balances, update our local account state
      if (data.execution_result?.database_state) {
        const dbState = data.execution_result.database_state;
        setAccounts((prev) =>
          prev.map((acc) => {
            if (acc.id === accountId) {
              return {
                ...acc,
                balance: dbState.balance ? dbState.balance.after : acc.balance,
                credit_limit: dbState.credit_limit ? dbState.credit_limit.after : acc.credit_limit,
              };
            }
            return acc;
          })
        );
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'agent',
          text: data.message,
          intent: data.intent,
          confidence_score: data.confidence_score,
          slots: data.slots,
          needs_clarification: data.needs_clarification,
          policy_decision: data.policy_decision,
          policy_rule: data.policy_rule,
          policy_reason: data.policy_reason,
          policy_details: data.policy_details,
          execution_result: data.execution_result,
          status: data.status,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      const errMsg = err.message || 'Request failed';
      setErrorBanner(`Gateway Error (${err.status || 500}): ${errMsg}`);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'agent',
          text: `[Gateway Rejection / Error]: ${errMsg}`,
          intent: 'error',
          status: 'failed',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAgent = (presetPrompt) => {
    setCurrentView('agent');
    if (presetPrompt) {
      setTimeout(() => {
        handleSend(presetPrompt);
      }, 350);
    }
  };

  // 1. If currently in NetBanking portal view, render authentic HDFC customer dashboard
  if (currentView === 'netbanking') {
    return (
      <HdfcNetBanking
        account={currentAccount}
        accounts={accounts}
        onSelectAccount={handleAccountChange}
        onOpenAgent={handleOpenAgent}
      />
    );
  }

  // 2. Otherwise render Apex Autonomous Servicing Bento Console
  return (
    <div className="bento-app-container">
      {/* Top Header */}
      <Header
        accountId={accountId}
        accounts={accounts}
        onSelectAccount={handleAccountChange}
        token={token}
        onRefreshToken={fetchToken}
        onClearToken={() => setToken('')}
        theme={theme}
        onToggleTheme={toggleTheme}
        onBackToPortal={() => setCurrentView('netbanking')}
      />

      {errorBanner && (
        <div className="bento-error-banner">
          <span>{errorBanner}</span>
        </div>
      )}

      {/* 12-Column Bento Grid matching Stitch layout */}
      <main className="bento-grid">
        {/* Bento Box 1 (4 cols, row 1): Titanium Credit Card Visualizer */}
        <div className="bento-col-4">
          <TitaniumCard
            account={currentAccount}
            onToggleFreeze={handleToggleFreeze}
            onTriggerVirtualCard={handleTriggerVirtualCard}
          />
        </div>

        {/* Bento Box 2 (8 cols, row 1): Autonomous Servicing Copilot Console */}
        <div className="bento-col-8">
          <div className="bento-box bento-chat-box">
            <div className="bento-box-header">
              <div className="box-title-group">
                <Bot className="box-icon text-indigo" size={18} />
                <h2 className="box-title">Autonomous Servicing Copilot</h2>
              </div>
              <div className="chat-status-badges">
                <span className="badge-model font-mono">Claude 3.7 + MCP Tools</span>
                <span className="badge-guardrail font-mono">Policy Guardrail Active</span>
              </div>
            </div>

            <ChatMessages
              messages={messages}
              loading={loading}
              messagesEndRef={messagesEndRef}
            />

            <Suggestions onSelect={handleSend} disabled={loading} />

            <ChatInput
              value={inputText}
              onChange={setInputText}
              onSend={() => handleSend()}
              disabled={loading}
            />
          </div>
        </div>

        {/* Bento Box 3 (4 cols, row 2): Spend Analytics & Utilization Gauge */}
        <div className="bento-col-4">
          <SpendAnalytics account={currentAccount} />
        </div>

        {/* Bento Box 4 (5 cols, row 2): Transactions & Servicing Ledger */}
        <div className="bento-col-5">
          <TransactionsLedger onSelectPrompt={handleSend} />
        </div>

        {/* Bento Box 5 (3 cols, row 2): Live Telemetry & MCP Engine Traces */}
        <div className="bento-col-3">
          <SystemTelemetry />
        </div>
      </main>
    </div>
  );
}
