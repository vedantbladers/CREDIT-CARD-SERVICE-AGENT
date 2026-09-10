import React from 'react';

export default function ChatInput({ value, onChange, onSend, disabled }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!disabled && value.trim()) {
      onSend();
    }
  };

  return (
    <div className="input-area">
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="text-input"
          placeholder="Type your credit card request here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
        />
        <button type="submit" className="btn-send" disabled={disabled || !value.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
