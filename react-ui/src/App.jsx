import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import AuthBar from './components/AuthBar';
import ChatMessages from './components/ChatMessages';
import Suggestions from './components/Suggestions';
import ChatInput from './components/ChatInput';
import { getTestToken, sendChatMessage } from './services/api';
import './App.css';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: 'Welcome! I am your AI Credit Card Servicing Platform with Phase 4 MCP Server & ACID Execution active. Requests are classified via LangGraph, validated by deterministic policy rules, and executed directly against PostgreSQL via Model Context Protocol (MCP) with full ACID transaction guarantees.',
      intent: 'system',
      status: 'ready',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState('');
  const [accountId, setAccountId] = useState('ACC-1001');
  const [errorBanner, setErrorBanner] = useState('');
  const messagesEndRef = useRef(null);

  const fetchToken = async (targetAccountId = accountId) => {
    try {
      setErrorBanner('');
      const data = await getTestToken(targetAccountId);
      setToken(data.token);
      setAccountId(data.account_id || targetAccountId);
    } catch (err) {
      console.warn('Could not auto-fetch test token:', err);
      setErrorBanner(
        'Go Gateway (Chi) is currently unreachable. Start your docker containers or verify port 8080.'
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
  }, [messages]);

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
          text: `[Gateway Error]: ${errMsg}`,
          intent: 'error',
          status: 'failed',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <AuthBar
        accountId={accountId}
        token={token}
        onSelectAccount={handleAccountChange}
        onRefreshToken={fetchToken}
        onClearToken={() => setToken('')}
      />
      {errorBanner && <div className="error-banner">{errorBanner}</div>}
      <main className="chat-window">
        <ChatMessages messages={messages} loading={loading} messagesEndRef={messagesEndRef} />
        <Suggestions onSelect={handleSend} disabled={loading} />
        <ChatInput
          value={inputText}
          onChange={setInputText}
          onSend={() => handleSend()}
          disabled={loading}
        />
      </main>
    </div>
  );
}
