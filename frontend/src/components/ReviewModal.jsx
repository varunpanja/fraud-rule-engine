import React, { useState } from 'react';
import { X, AlertTriangle, ShieldCheck, CheckCircle2, ShieldAlert } from 'lucide-react';
import RiskBadge from './RiskBadge';
import StatusBadge from './StatusBadge';

export const ReviewModal = ({
  flag,
  onClose,
  onReview,
  onClear,
  loading = false,
}) => {
  if (!flag) return null;

  const [notes, setNotes] = useState(flag.reviewer_notes || '');

  const rules = Array.isArray(flag.triggered_rules) ? flag.triggered_rules : [];

  const handleReview = () => {
    onReview(flag.id, notes);
  };

  const handleClear = () => {
    onClear(flag.id, notes);
  };

  const formatCurrency = (amt, curr = 'INR') => {
    if (amt === undefined || amt === null) return 'N/A';
    const symbol = curr === 'INR' ? '₹' : `${curr} `;
    return `${symbol}${Number(amt).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <ShieldAlert size={22} color="#ef4444" />
            <h3 className="modal-title">Transaction Investigation #{flag.transaction_id}</h3>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={onClose}
            style={{ padding: '0.25rem 0.5rem' }}
          >
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {/* Key transaction parameters */}
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-k">Account ID</span>
              <span className="detail-v mono" style={{ color: '#a5b4fc' }}>
                {flag.account_id || 'N/A'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-k">Transaction Amount</span>
              <span className="detail-v mono" style={{ color: '#34d399' }}>
                {formatCurrency(flag.amount, flag.currency)}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-k">Location & Coordinates</span>
              <span className="detail-v" style={{ fontSize: '0.85rem' }}>
                {flag.location || 'N/A'} ({flag.latitude ?? 0}, {flag.longitude ?? 0})
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-k">Timestamp</span>
              <span className="detail-v mono" style={{ fontSize: '0.825rem' }}>
                {flag.timestamp ? new Date(flag.timestamp).toLocaleString('en-IN') : 'N/A'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-k">Current Status</span>
              <div>
                <StatusBadge status={flag.status} />
              </div>
            </div>

            <div className="detail-item">
              <span className="detail-k">Calculated Risk</span>
              <div>
                <RiskBadge level={flag.risk_level} score={flag.risk_score} />
              </div>
            </div>
          </div>

          {/* Triggered Rules Detailed Breakdown */}
          <div style={{ marginBottom: '1.25rem' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '0.6rem', color: '#e2e8f0' }}>
              Triggered Fraud Rules ({rules.length})
            </h4>

            {rules.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No active rule flags recorded.
              </div>
            ) : (
              rules.map((rule, idx) => {
                const name = typeof rule === 'string' ? rule : rule.rule_name;
                const reason = typeof rule === 'object' ? rule.reason : 'Condition triggered.';
                const score = typeof rule === 'object' ? rule.score_contribution : 0;

                return (
                  <div key={idx} className="rule-breakdown-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                        {name}
                      </span>
                      {score > 0 && (
                        <span className="mono text-xs" style={{ background: '#ef4444', color: '#fff', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 700 }}>
                          +{score} pts
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.825rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                      {reason}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Reviewer Note Input / Audit Trail */}
          <div className="form-group">
            <label className="form-label">Reviewer Notes & Justification</label>
            <textarea
              rows={3}
              className="form-textarea"
              placeholder="Enter audit rationale (e.g. 'Verified with customer by phone', 'Authorized high value transfer')..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={loading}
            />
          </div>

          {flag.reviewed_at && (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Last updated: {new Date(flag.reviewed_at).toLocaleString('en-IN')}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Close
          </button>

          <button
            className="btn btn-success"
            onClick={handleClear}
            disabled={loading}
            title="Mark as CLEARED (False positive)"
          >
            <ShieldCheck size={16} />
            {loading ? 'Processing...' : 'Mark Cleared (Legitimate)'}
          </button>

          <button
            className="btn btn-primary"
            onClick={handleReview}
            disabled={loading}
            title="Mark as REVIEWED (Confirmed Suspicious)"
          >
            <CheckCircle2 size={16} />
            {loading ? 'Processing...' : 'Mark Reviewed (Suspicious)'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewModal;
