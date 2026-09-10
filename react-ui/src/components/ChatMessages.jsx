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
        <strong>LangGraph Reasoning Active:</strong> Request ➔ Go Gateway (Chi) ➔
        FastAPI State Graph (<code>classify_intent</code> ➔ <code>extract_slots</code> ➔ <code>route_decision</code>).
        <br />
        Inspect extracted slots, confidence scores, and clarification triggers below.
      </div>

      {messages.map((m) => (
        <div key={m.id} className={`message-item ${m.sender}`}>
          <div className="message-bubble">
            {m.text}

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
            {m.status && <span>({m.status})</span>}
          </div>
        </div>
      ))}

      {loading && (
        <div className="message-item agent">
          <div className="message-bubble">
            LangGraph orchestrator reasoning &amp; extracting parameters...
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
