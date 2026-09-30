import React, { useState } from 'react';
import { Search, Eye, CheckCircle, ShieldX, Filter, AlertTriangle } from 'lucide-react';
import RiskBadge from './RiskBadge';
import StatusBadge from './StatusBadge';

export const TransactionTable = ({
  flags = [],
  loading = false,
  onInspect,
  onReview,
  onClear,
  actionLoadingId = null,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  // Filter flags client-side for immediate responsiveness
  const filteredFlags = flags.filter((f) => {
    const matchesSearch =
      !searchTerm ||
      (f.account_id && f.account_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (f.location && f.location.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (f.transaction_id && f.transaction_id.toString().includes(searchTerm)) ||
      (Array.isArray(f.triggered_rules) &&
        f.triggered_rules.some((r) =>
          (r.rule_name || r).toLowerCase().includes(searchTerm.toLowerCase())
        ));

    const matchesStatus =
      statusFilter === 'ALL' || (f.status || '').toUpperCase() === statusFilter;

    const matchesRisk =
      riskFilter === 'ALL' || (f.risk_level || '').toUpperCase() === riskFilter;

    return matchesSearch && matchesStatus && matchesRisk;
  });

  const formatCurrency = (amt, curr = 'INR') => {
    if (amt === undefined || amt === null) return 'N/A';
    const symbol = curr === 'INR' ? '₹' : `${curr} `;
    return `${symbol}${Number(amt).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="card-section">
      <div className="section-header">
        <h2 className="section-title">
          <AlertTriangle size={20} color="#f59e0b" />
          Flagged Transactions Queue
          <span className="mono text-muted text-sm font-normal">
            ({filteredFlags.length} {filteredFlags.length === 1 ? 'item' : 'items'})
          </span>
        </h2>

        <div className="controls-bar">
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search account, location, rule..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            className="select-filter"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="ALL">All Risk Levels</option>
            <option value="HIGH">High Risk (70-100)</option>
            <option value="MEDIUM">Medium Risk (30-69)</option>
            <option value="LOW">Low Risk (0-29)</option>
          </select>

          <select
            className="select-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="CLEARED">Cleared</option>
          </select>
        </div>
      </div>

      <div className="table-responsive">
        <table className="custom-table">
          <thead>
            <tr>
              <th>TX ID</th>
              <th>Account</th>
              <th>Amount</th>
              <th>Location & Time</th>
              <th>Risk Level</th>
              <th>Triggered Rules</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '3rem' }}>
                  <div style={{ color: 'var(--text-secondary)' }}>Loading flagged transactions...</div>
                </td>
              </tr>
            ) : filteredFlags.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '3.5rem' }}>
                  <div style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
                    No flagged transactions match the criteria.
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.825rem' }}>
                    Try adjusting filters, creating a new suspicious transaction, or clicking "Seed Demo Data".
                  </div>
                </td>
              </tr>
            ) : (
              filteredFlags.map((flag) => {
                const isOperating = actionLoadingId === flag.id;
                const rules = Array.isArray(flag.triggered_rules) ? flag.triggered_rules : [];

                return (
                  <tr key={flag.id}>
                    <td className="mono font-bold">#{flag.transaction_id}</td>
                    <td>
                      <span className="mono" style={{ color: '#a5b4fc', fontWeight: 600 }}>
                        {flag.account_id || 'N/A'}
                      </span>
                    </td>
                    <td className="mono font-bold">
                      {formatCurrency(flag.amount, flag.currency)}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{flag.location || 'Unknown'}</div>
                      <div className="mono text-muted text-xs">{formatDate(flag.timestamp)}</div>
                    </td>
                    <td>
                      <RiskBadge level={flag.risk_level} score={flag.risk_score} />
                    </td>
                    <td>
                      <div style={{ maxWidth: '240px' }}>
                        {rules.map((r, i) => {
                          const rName = typeof r === 'string' ? r : r.rule_name;
                          return (
                            <span key={i} className="rule-chip">
                              {rName}
                            </span>
                          );
                        })}
                      </div>
                    </td>
                    <td>
                      <StatusBadge status={flag.status} />
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => onInspect(flag)}
                          title="Inspect full transaction details & rule reasons"
                        >
                          <Eye size={13} />
                          Inspect
                        </button>

                        {flag.status === 'PENDING' && (
                          <>
                            <button
                              className="btn btn-primary btn-sm"
                              onClick={() => onReview(flag.id)}
                              disabled={isOperating}
                              title="Mark as Reviewed (Confirmed Suspicious)"
                            >
                              <CheckCircle size={13} />
                              Review
                            </button>
                            <button
                              className="btn btn-success btn-sm"
                              onClick={() => onClear(flag.id)}
                              disabled={isOperating}
                              title="Mark as Cleared (False Positive)"
                            >
                              <ShieldX size={13} />
                              Clear
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionTable;
