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
        <strong>Phase 3 Deterministic Policy Engine Active:</strong> Request ➔ Go Gateway (Chi) ➔
        FastAPI LangGraph (<code>classify_intent</code> ➔ <code>extract_slots</code> ➔ <code>route_decision</code>) ➔
        <strong> Policy Engine (Safety Guardrails)</strong>.
        <br />
        Inspect intent classification, extracted slots, and rule-based policy determinations (APPROVED / REJECTED / NEEDS_ESCALATION) below.
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
