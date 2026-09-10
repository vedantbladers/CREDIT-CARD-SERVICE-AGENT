import React from 'react';

const SUGGESTIONS = [
  {
    label: 'Fee Waiver: "Can you please waive my $95 annual fee?"',
    text: 'Can you please waive my $95 annual fee?',
  },
  {
    label: 'Limit Increase: "Raise my credit limit to $15,000"',
    text: 'I would like to raise my credit limit to $15,000 please',
  },
  {
    label: 'Missing Slot: "Send me a replacement card"',
    text: 'Can you please send me a replacement card to my address?',
  },
  {
    label: 'Out-of-Scope: "Can you help me apply for a car loan?"',
    text: 'Can you help me apply for a used car loan?',
  },
];

export default function Suggestions({ onSelect, disabled }) {
  return (
    <div className="suggestions">
      {SUGGESTIONS.map((item, idx) => (
        <button
          key={idx}
          className="chip"
          disabled={disabled}
          onClick={() => onSelect(item.text)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
