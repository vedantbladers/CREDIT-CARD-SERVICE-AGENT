import React from 'react';
import { Sparkles, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

const SUGGESTIONS = [
  {
    label: 'Fee Waiver ($95)',
    type: 'approve',
    text: 'Can you please waive my $95 annual membership fee?',
    hint: 'Approves under POL-FEES-001',
  },
  {
    label: 'Fee Waiver ($250)',
    type: 'escalate',
    text: 'Please waive my $250 late fee that was charged yesterday',
    hint: 'Escalates: amount > $150 cap',
  },
  {
    label: 'Limit +20% ($12k)',
    type: 'approve',
    text: 'I would like to raise my credit limit to $12,000 please',
    hint: 'Approves under POL-CR-001',
  },
  {
    label: 'Limit +40% ($14k)',
    type: 'escalate',
    text: 'Please increase my credit limit to $14,000 for travel',
    hint: 'Escalates: requested bump > 25%',
  },
  {
    label: 'Limit +80% ($18k)',
    type: 'reject',
    text: 'Can you increase my credit limit to $18,000?',
    hint: 'Rejects: exceeds account ceiling',
  },
  {
    label: 'Replace Stolen Card',
    type: 'approve',
    text: 'My credit card was stolen in the subway, I need a replacement right away',
    hint: 'Approves & dispatches courier',
  },
  {
    label: 'Ambiguous Reason',
    type: 'clarify',
    text: 'Can you please send me a replacement card to my address?',
    hint: 'Triggers clarification prompt',
  },
];

export default function Suggestions({ onSelect, disabled }) {
  const getIcon = (type) => {
    switch (type) {
      case 'approve':
        return <CheckCircle2 size={12} className="text-emerald" />;
      case 'escalate':
        return <AlertTriangle size={12} className="text-amber" />;
      case 'reject':
        return <XCircle size={12} className="text-rose" />;
      case 'clarify':
        return <HelpCircle size={12} className="text-indigo" />;
      default:
        return <Sparkles size={12} className="text-indigo" />;
    }
  };

  return (
    <div className="bento-suggestions-row">
      <div className="suggestions-label">
        <Sparkles size={13} className="text-indigo" />
        <span>Quick Scenario Scaffolds:</span>
      </div>
      <div className="suggestions-scroll-container">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            className={`bento-suggestion-chip chip-${item.type}`}
            disabled={disabled}
            onClick={() => onSelect(item.text)}
            title={`${item.hint} • Click to send`}
          >
            {getIcon(item.type)}
            <span className="chip-text">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
