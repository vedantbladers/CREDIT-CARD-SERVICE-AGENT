import React, { useRef } from 'react';
import { Send, Paperclip, Mic, CornerDownLeft } from 'lucide-react';

export default function ChatInput({ value, onChange, onSend, disabled }) {
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!disabled && value.trim()) {
      onSend();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) {
        onSend();
      }
    }
  };

  return (
    <div className="bento-input-container">
      <form className="bento-input-form" onSubmit={handleSubmit}>
        <button
          type="button"
          className="btn-input-accessory"
          title="Attach statement or receipt document"
          disabled={disabled}
        >
          <Paperclip size={16} />
        </button>

        <textarea
          ref={inputRef}
          rows={1}
          className="bento-textarea"
          placeholder="Ask Apex Copilot or instruct autonomous action (e.g. 'Waive $95 fee', 'Raise limit to $12k')..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />

        <button
          type="button"
          className="btn-input-accessory"
          title="Voice dictation"
          disabled={disabled}
        >
          <Mic size={16} />
        </button>

        <button
          type="submit"
          className={`btn-bento-send ${value.trim() ? 'active' : ''}`}
          disabled={disabled || !value.trim()}
          title="Send directive (Enter)"
        >
          <Send size={15} />
        </button>
      </form>

      <div className="input-hint-row">
        <span>Fiduciary guardrails active &bull; Cryptographically signed ledger verification</span>
        <span className="font-mono">Press ↵ to send</span>
      </div>
    </div>
  );
}
