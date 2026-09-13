import React from 'react';

export default function ChatMessages({ messages, loading, messagesEndRef }) {
  const getIntentClass = (intent) => {
    switch (intent) {
      case 'fee_waiver':
        return 'intent-waiver';
      case 'credit_limit_increase':
        return 'intent-limit';
      case 'card_replacement':
        return 'intent-card';
      case 'unclear':
        return 'intent-unclear';
      case 'error':
        return 'intent-error';
      default:
        return '';
    }
  };

  return (
    <div className="messages-list">
      <div className="system-banner">
        <strong>Phase 4 End-to-End Pipeline Active:</strong> Request ➔ Go Gateway (Chi) ➔
        FastAPI LangGraph (<code>classify_intent</code> ➔ <code>extract_slots</code>) ➔
        Deterministic Policy Engine ➔
        <strong> MCP Server (PostgreSQL ACID Transactions &amp; Audit Ledger)</strong>.
        <br />
        Policy approval triggers real-time Model Context Protocol database tools with verifiable before/after balance state.
      </div>

      {messages.map((m) => (
        <div key={m.id} className={`message-item ${m.sender}`}>
          <div className="message-bubble">
            <div className="message-text-content">{m.text}</div>

            {/* Extracted Slots Breakdown */}
            {m.slots && Object.keys(m.slots).length > 0 && (
              <div className="slots-container">
                <span className="slots-title">Extracted Slots:</span>
                <div className="slots-grid">
                  {Object.entries(m.slots).map(([key, val]) => (
                    <span key={key} className="slot-pill">
                      <strong>{key}:</strong> {val !== null && val !== undefined ? String(val) : <em>missing</em>}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Phase 3 Deterministic Policy Engine Verdict Card */}
            {m.policy_decision && (
              <div className={`policy-card policy-${m.policy_decision.toLowerCase()}`}>
                <div className="policy-header">
                  <span className={`policy-badge badge-${m.policy_decision.toLowerCase()}`}>
                    {m.policy_decision === 'APPROVED' && '✅ POLICY APPROVED'}
                    {m.policy_decision === 'REJECTED' && '❌ POLICY REJECTED'}
                    {m.policy_decision === 'NEEDS_ESCALATION' && '⚠️ NEEDS ESCALATION'}
                  </span>
                  {m.policy_rule && <span className="policy-rule-tag">{m.policy_rule}</span>}
                </div>
                {m.policy_reason && <div className="policy-reason">{m.policy_reason}</div>}
                {m.policy_details && Object.keys(m.policy_details).length > 0 && (
                  <div className="policy-details-grid">
                    {Object.entries(m.policy_details).map(([k, v]) => (
                      <span key={k} className="policy-metric">
                        <em>{k.replace(/_/g, ' ')}:</em> <strong>{String(v)}</strong>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Phase 4 MCP Database Execution Result Card */}
            {m.execution_result && (
              <div className="execution-card">
                {m.execution_result.status === 'SUCCESS' && (
                  <>
                    <div className="execution-header">
                      <span className="badge-acid">⚡ MCP TOOL EXECUTED (ACID COMMITTED)</span>
                      <span className="tx-id-tag">Tx #{m.execution_result.transaction_id}</span>
                    </div>
                    <div className="execution-tool-info">
                      <strong>Tool:</strong> <code>{m.execution_result.tool}</code> &bull;{' '}
                      <strong>Guaranteed:</strong> <span className="acid-status">ACID Atomicity</span>
                    </div>
                    {m.execution_result.database_state && (
                      <div className="db-delta-grid">
                        {m.execution_result.database_state.balance && (
                          <div className="delta-item">
                            <span className="delta-label">Account Balance:</span>
                            <span className="delta-change">
                              ${m.execution_result.database_state.balance.before.toFixed(2)} ➔{' '}
                              <strong>${m.execution_result.database_state.balance.after.toFixed(2)}</strong>
                            </span>
                          </div>
                        )}
                        {m.execution_result.database_state.fees_waived_this_quarter && (
                          <div className="delta-item">
                            <span className="delta-label">Quarterly Waivers:</span>
                            <span className="delta-change">
                              {m.execution_result.database_state.fees_waived_this_quarter.before} ➔{' '}
                              <strong>{m.execution_result.database_state.fees_waived_this_quarter.after}</strong>
                            </span>
                          </div>
                        )}
                        {m.execution_result.database_state.credit_limit && (
                          <div className="delta-item">
                            <span className="delta-label">Credit Limit:</span>
                            <span className="delta-change">
                              ${m.execution_result.database_state.credit_limit.before.toFixed(2)} ➔{' '}
                              <strong>${m.execution_result.database_state.credit_limit.after.toFixed(2)}</strong>
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                    {m.execution_result.replacement_id && (
                      <div className="db-delta-grid">
                        <div className="delta-item">
                          <span className="delta-label">Card Dispatch Order:</span>
                          <span className="delta-change">
                            #{m.execution_result.replacement_id} ({m.execution_result.delivery_type})
                          </span>
                        </div>
                        <div className="delta-item">
                          <span className="delta-label">Estimated Delivery:</span>
                          <span className="delta-change">
                            {m.execution_result.estimated_delivery_days} business days
                          </span>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {m.execution_result.status === 'BLOCKED_BY_POLICY' && (
                  <div className="execution-blocked">
                    <span className="badge-blocked">🛡️ MCP EXECUTION BLOCKED</span>
                    <p>Defense-in-depth: database mutation prevented because policy rejected the request.</p>
                  </div>
                )}

                {m.execution_result.status === 'ESCALATED_MANUAL_REVIEW' && (
                  <div className="execution-escalated">
                    <span className="badge-paused">⏸️ MCP EXECUTION HELD</span>
                    <p>Automated tool call suspended. Request placed in manual review queue for underwriter authorization.</p>
                  </div>
                )}
              </div>
            )}

            {/* Clarification Alert */}
            {m.needs_clarification && (
              <div className="clarify-box">
                ⚠️ <strong>Clarification Required:</strong> Action paused until missing slot or intent is confirmed.
              </div>
            )}
          </div>

          <div className="message-meta">
            <span>{m.time}</span>
            {m.intent && (
              <span className={`meta-tag ${getIntentClass(m.intent)}`}>
                intent: {m.intent}
              </span>
            )}
            {m.confidence_score !== undefined && m.confidence_score !== null && (
              <span className="confidence-pill">
                {(m.confidence_score * 100).toFixed(0)}% confidence
              </span>
            )}
            {m.policy_decision && (
              <span className={`policy-pill-tag tag-${m.policy_decision.toLowerCase()}`}>
                {m.policy_decision}
              </span>
            )}
            {m.status && <span>({m.status})</span>}
          </div>
        </div>
      ))}

      {loading && (
        <div className="message-item agent">
          <div className="message-bubble">
            LangGraph orchestrating &amp; Deterministic Policy Engine evaluating rules...
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
