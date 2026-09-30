import React, { useState } from 'react';
import { X, Send, Zap, DollarSign, Plane, AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react';
import RiskBadge from './RiskBadge';

export const NewTransactionModal = ({ onClose, onSubmit, submitting }) => {
  const [formData, setFormData] = useState({
    account_id: 'ACC' + Math.floor(1000 + Math.random() * 9000),
    amount: 15000,
    currency: 'INR',
    timestamp: new Date().toISOString().slice(0, 19),
    latitude: 17.3850,
    longitude: 78.4867,
    location: 'Hyderabad, India',
    transaction_type: 'TRANSFER',
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' || name === 'latitude' || name === 'longitude' ? Number(value) : value,
    }));
  };

  // Preset Handlers for Judges / Instant Testing
  const applyPreset = (presetType) => {
    const now = new Date().toISOString().slice(0, 19);

    if (presetType === 'VELOCITY') {
      setFormData({
        account_id: 'ACC-VELOCITY',
        amount: 3500,
        currency: 'INR',
        timestamp: now,
        latitude: 17.3850,
        longitude: 78.4867,
        location: 'Hyderabad, India',
        transaction_type: 'TRANSFER',
      });
    } else if (presetType === 'AMOUNT') {
      setFormData({
        account_id: 'ACC-AMOUNT-TEST',
        amount: 250000,
        currency: 'INR',
        timestamp: now,
        latitude: 19.0760,
        longitude: 72.8777,
        location: 'Mumbai, India',
        transaction_type: 'TRANSFER',
      });
    } else if (presetType === 'GEO') {
      setFormData({
        account_id: 'ACC-TRAVEL',
        amount: 12000,
        currency: 'INR',
        timestamp: now,
        latitude: 51.5074,
        longitude: -0.1278,
        location: 'London, UK',
        transaction_type: 'PURCHASE',
      });
    } else if (presetType === 'HIGH_RISK') {
      setFormData({
        account_id: 'ACC-CRITICAL',
        amount: 350000,
        currency: 'INR',
        timestamp: now,
        latitude: 40.7128,
        longitude: -74.0060,
        location: 'New York, USA',
        transaction_type: 'TRANSFER',
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await onSubmit(formData);
      setResult(response);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Zap size={22} color="#6366f1" />
            <h3 className="modal-title">Live Transaction Ingestion & Simulator</h3>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onClose} style={{ padding: '0.25rem 0.5rem' }}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {/* Quick Presets for Judges */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label className="form-label" style={{ color: '#a5b4fc' }}>
              ⚡ Quick Rule Presets (1-Click Judge Demos)
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => applyPreset('VELOCITY')}
                style={{ justifyContent: 'flex-start', fontSize: '0.75rem' }}
              >
                <Zap size={13} color="#f59e0b" />
                Trigger Velocity Rule (+30)
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => applyPreset('AMOUNT')}
                style={{ justifyContent: 'flex-start', fontSize: '0.75rem' }}
              >
                <DollarSign size={13} color="#f59e0b" />
                Trigger Unusual Amount (+30)
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => applyPreset('GEO')}
                style={{ justifyContent: 'flex-start', fontSize: '0.75rem' }}
              >
                <Plane size={13} color="#f59e0b" />
                Trigger Impossible Travel (+40)
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => applyPreset('HIGH_RISK')}
                style={{ justifyContent: 'flex-start', fontSize: '0.75rem', borderColor: '#ef4444' }}
              >
                <AlertOctagon size={13} color="#ef4444" />
                Trigger High Risk & SNS (70+)
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label className="form-label">Account ID</label>
                <input
                  type="text"
                  name="account_id"
                  className="form-input mono"
                  value={formData.account_id}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Amount (₹)</label>
                <input
                  type="number"
                  name="amount"
                  className="form-input mono"
                  value={formData.amount}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location Name</label>
                <input
                  type="text"
                  name="location"
                  className="form-input"
                  value={formData.location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Transaction Type</label>
                <select
                  name="transaction_type"
                  className="form-select"
                  value={formData.transaction_type}
                  onChange={handleChange}
                >
                  <option value="TRANSFER">TRANSFER</option>
                  <option value="PURCHASE">PURCHASE</option>
                  <option value="WITHDRAWAL">WITHDRAWAL</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Latitude</label>
                <input
                  type="number"
                  step="any"
                  name="latitude"
                  className="form-input mono"
                  value={formData.latitude}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Longitude</label>
                <input
                  type="number"
                  step="any"
                  name="longitude"
                  className="form-input mono"
                  value={formData.longitude}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Timestamp (ISO 8601)</label>
              <input
                type="datetime-local"
                name="timestamp"
                className="form-input mono"
                value={formData.timestamp.slice(0, 16)}
                onChange={(e) => setFormData((prev) => ({ ...prev, timestamp: e.target.value + ':00' }))}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}
              disabled={submitting}
            >
              <Send size={15} />
              {submitting ? 'Evaluating Rules...' : 'Submit & Evaluate Transaction'}
            </button>
          </form>

          {/* Real-time Rule Evaluation Output */}
          {result && (
            <div style={{ marginTop: '1.5rem', background: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ fontWeight: 700, fontSize: '0.9rem' }}>Evaluation Result</h4>
                <RiskBadge
                  level={result.fraud_evaluation?.risk_level}
                  score={result.fraud_evaluation?.risk_score}
                />
              </div>

              <div style={{ fontSize: '0.825rem', marginBottom: '0.5rem' }}>
                <strong>Status:</strong>{' '}
                {result.fraud_evaluation?.is_flagged ? (
                  <span style={{ color: '#f87171' }}>FLAGGED FOR REVIEW</span>
                ) : (
                  <span style={{ color: '#34d399' }}>PASSED - NO FRAUD DETECTED</span>
                )}
              </div>

              <div style={{ fontSize: '0.825rem', marginBottom: '0.5rem' }}>
                <strong>AWS Notification:</strong>{' '}
                <span style={{ color: result.fraud_evaluation?.notification_sent ? '#4ade80' : 'var(--text-muted)' }}>
                  {result.fraud_evaluation?.notification_status}
                </span>
              </div>

              {result.fraud_evaluation?.triggered_rules?.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Triggered Rules:
                  </div>
                  {result.fraud_evaluation.triggered_rules.map((r, idx) => (
                    <div key={idx} className="rule-breakdown-card" style={{ marginTop: '0.4rem' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#f87171' }}>
                        {r.rule_name} (+{r.score_contribution} pts)
                      </div>
                      <div style={{ fontSize: '0.775rem', color: '#cbd5e1' }}>{r.reason}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewTransactionModal;
