import React from 'react';

const SUGGESTIONS = [
  {
    label: '🟢 Fee Waiver (Approve): "Please waive my $95 annual fee"',
    text: 'Can you please waive my $95 annual membership fee?',
    accountHint: 'ACC-1001',
  },
  {
    label: '⚠️ Fee Waiver (Escalate >$150): "Waive my $250 late fee"',
    text: 'Please waive my $250 late fee that was charged yesterday',
    accountHint: 'ACC-1001',
  },
  {
    label: '🟢 Limit +20% (Approve): "Raise my credit limit to $12,000"',
    text: 'I would like to raise my credit limit to $12,000 please',
    accountHint: 'ACC-1001',
  },
  {
    label: '⚠️ Limit +40% (Escalate): "Raise my credit limit to $14,000"',
    text: 'Please increase my credit limit to $14,000 for travel',
    accountHint: 'ACC-1001',
  },
  {
    label: '🔴 Limit +80% (Reject Cap): "Raise limit to $18,000"',
    text: 'Can you increase my credit limit to $18,000?',
    accountHint: 'ACC-1001',
  },
  {
    label: '🟢 Replace Card (Approve): "My card was stolen, replace it"',
    text: 'My credit card was stolen in the subway, I need a replacement right away',
    accountHint: 'ACC-1001',
  },
  {
    label: '❓ Missing Slot (Clarify): "Send replacement card"',
    text: 'Can you please send me a replacement card to my address?',
    accountHint: 'ACC-1001',
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
