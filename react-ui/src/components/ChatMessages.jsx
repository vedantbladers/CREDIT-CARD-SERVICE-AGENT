import React from 'react';
import {
  Shield,
  Bot,
  User,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Zap,
  ArrowRight,
  Database,
  Truck,
  Sparkles,
  Info,
} from 'lucide-react';

export default function ChatMessages({ messages, loading, messagesEndRef }) {
  const getIntentBadgeClass = (intent) => {
    switch (intent) {
      case 'fee_waiver':
        return 'intent-waiver';
      case 'credit_limit_increase':
        return 'intent-limit';
      case 'card_replacement':
        return 'intent-card';
      case 'dispute_charge':
        return 'intent-dispute';
      case 'unclear':
        return 'intent-unclear';
      case 'error':
        return 'intent-error';
      default:
        return 'intent-default';
    }
  };

  return (
    <div className="messages-stream">
      {/* Intro Platform Banner */}
      <div className="platform-intro-card">
        <div className="intro-icon-wrap">
          <Sparkles className="intro-sparkle" size={18} />
        </div>
        <div className="intro-text">
          <div className="intro-title">Apex Autonomous Financial Copilot &bull; Fiduciary Guardrail v4.2</div>
          <div className="intro-desc">
            All cardholder adjustments, limit requests, fee waivers, and card replacements are classified via LangGraph,
            verified against deterministic rule policies, and executed directly via PostgreSQL MCP with ACID transaction guarantees.
          </div>
        </div>
      </div>

      {messages.map((m) => {
        const isAgent = m.sender === 'agent';
        return (
          <div key={m.id} className={`message-row ${m.sender}`}>
            <div className="message-avatar">
              {isAgent ? <Bot size={16} /> : <User size={16} />}
            </div>

            <div className="message-bubble-wrapper">
              <div className="message-meta-header">
                <span className="sender-name">{isAgent ? 'Apex Agent Core' : 'Authenticated Cardholder'}</span>
                <span className="message-time font-mono">{m.time}</span>
                {m.intent && m.intent !== 'system' && (
                  <span className={`intent-badge ${getIntentBadgeClass(m.intent)}`}>
                    intent: {m.intent}
                  </span>
                )}
                {m.confidence_score !== undefined && m.confidence_score !== null && (
                  <span className="confidence-pill font-mono">
                    {(m.confidence_score * 100).toFixed(0)}% conf
                  </span>
                )}
              </div>

              <div className="message-text">{m.text}</div>

              {/* Extracted Slots Breakdown */}
              {m.slots && Object.keys(m.slots).length > 0 && (
                <div className="slots-panel">
                  <div className="slots-header">
                    <Info size={12} className="text-indigo" />
                    <span>Extracted Entities &amp; Slots</span>
                  </div>
                  <div className="slots-tags-container">
                    {Object.entries(m.slots).map(([key, val]) => (
                      <span key={key} className="slot-tag">
                        <span className="slot-key">{key}:</span>
                        <span className="slot-val font-mono">
                          {val !== null && val !== undefined ? String(val) : 'missing'}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Policy Engine Verdict Card */}
              {m.policy_decision && (
                <div className={`bento-policy-card policy-${m.policy_decision.toLowerCase()}`}>
                  <div className="policy-card-top">
                    <div className="policy-badge-container">
                      {m.policy_decision === 'APPROVED' && (
                        <span className="policy-status-pill approved">
                          <CheckCircle2 size={13} />
                          POLICY APPROVED
                        </span>
                      )}
                      {m.policy_decision === 'REJECTED' && (
                        <span className="policy-status-pill rejected">
                          <XCircle size={13} />
                          POLICY REJECTED
                        </span>
                      )}
                      {m.policy_decision === 'NEEDS_ESCALATION' && (
                        <span className="policy-status-pill escalation">
                          <AlertTriangle size={13} />
                          NEEDS ESCALATION
                        </span>
                      )}
                    </div>
                    {m.policy_rule && (
                      <span className="policy-rule-code font-mono">{m.policy_rule}</span>
                    )}
                  </div>

                  {m.policy_reason && (
                    <div className="policy-reason-text">{m.policy_reason}</div>
                  )}

                  {m.policy_details && Object.keys(m.policy_details).length > 0 && (
                    <div className="policy-metrics-grid">
                      {Object.entries(m.policy_details).map(([k, v]) => (
                        <div key={k} className="policy-metric-item">
                          <span className="metric-k">{k.replace(/_/g, ' ')}:</span>
                          <span className="metric-v font-mono">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* MCP ACID Database Execution Receipt */}
              {m.execution_result && (
                <div className="bento-execution-card">
                  {m.execution_result.status === 'SUCCESS' && (
                    <>
                      <div className="execution-card-header">
                        <div className="execution-title-group">
                          <Zap size={14} className="text-amber animate-pulse" />
                          <span className="execution-title">PostgreSQL ACID Commit Confirmed</span>
                        </div>
                        <span className="tx-badge font-mono">
                          Tx #{m.execution_result.transaction_id}
                        </span>
                      </div>

                      <div className="execution-subline">
                        <span>Tool: <code>{m.execution_result.tool}</code></span>
                        <span className="subline-dot">&bull;</span>
                        <span className="text-emerald font-mono">Guaranteed ACID Atomicity</span>
                      </div>

                      {m.execution_result.database_state && (
                        <div className="db-diff-container">
                          {m.execution_result.database_state.balance && (
                            <div className="diff-item">
                              <span className="diff-label">Account Balance Diff:</span>
                              <div className="diff-values font-mono">
                                <span className="diff-before">${m.execution_result.database_state.balance.before.toFixed(2)}</span>
                                <ArrowRight size={12} className="diff-arrow" />
                                <span className="diff-after text-emerald font-semibold">
                                  ${m.execution_result.database_state.balance.after.toFixed(2)}
                                </span>
                              </div>
                            </div>
                          )}

                          {m.execution_result.database_state.fees_waived_this_quarter && (
                            <div className="diff-item">
                              <span className="diff-label">Quarterly Waivers:</span>
                              <div className="diff-values font-mono">
                                <span className="diff-before">{m.execution_result.database_state.fees_waived_this_quarter.before}</span>
                                <ArrowRight size={12} className="diff-arrow" />
                                <span className="diff-after text-emerald font-semibold">
                                  {m.execution_result.database_state.fees_waived_this_quarter.after}
                                </span>
                              </div>
                            </div>
                          )}

                          {m.execution_result.database_state.credit_limit && (
                            <div className="diff-item">
                              <span className="diff-label">Credit Limit Adjusted:</span>
                              <div className="diff-values font-mono">
                                <span className="diff-before">${m.execution_result.database_state.credit_limit.before.toFixed(2)}</span>
                                <ArrowRight size={12} className="diff-arrow" />
                                <span className="diff-after text-emerald font-semibold">
                                  ${m.execution_result.database_state.credit_limit.after.toFixed(2)}
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {m.execution_result.replacement_id && (
                        <div className="dispatch-badge-card">
                          <Truck size={14} className="text-blue" />
                          <div className="dispatch-info">
                            <span className="dispatch-code font-mono">
                              Dispatch Order #{m.execution_result.replacement_id} ({m.execution_result.delivery_type})
                            </span>
                            <span className="dispatch-est">
                              Estimated Delivery: {m.execution_result.estimated_delivery_days} business days
                            </span>
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {m.execution_result.status === 'BLOCKED_BY_POLICY' && (
                    <div className="execution-status-blocked">
                      <Shield size={14} className="text-rose" />
                      <div>
                        <strong>MCP Execution Prevented by Policy Gate:</strong> Database mutation cancelled to preserve ledger integrity.
                      </div>
                    </div>
                  )}

                  {m.execution_result.status === 'ESCALATED_MANUAL_REVIEW' && (
                    <div className="execution-status-escalated">
                      <AlertTriangle size={14} className="text-amber" />
                      <div>
                        <strong>MCP Execution Held for Senior Underwriter:</strong> Dispatched to manual escalation queue.
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Clarification Box */}
              {m.needs_clarification && (
                <div className="clarify-alert-pill">
                  <AlertTriangle size={13} className="text-amber" />
                  <span>Clarification Required: Autonomous action paused until ambiguous details are confirmed.</span>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {loading && (
        <div className="message-row agent">
          <div className="message-avatar">
            <Bot size={16} />
          </div>
          <div className="message-bubble-wrapper">
            <div className="loading-state-card">
              <span className="loading-spinner"></span>
              <span className="loading-text">
                LangGraph routing &bull; Evaluating deterministic policy rules &bull; MCP Server preparing ACID transaction...
              </span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
