import React from 'react';
import { CreditCard, Flag, ShieldAlert, Clock, CheckCheck, ShieldCheck } from 'lucide-react';

export const DashboardStats = ({ stats, loading }) => {
  const cards = [
    {
      label: 'Total Transactions',
      value: stats.total_transactions ?? 0,
      icon: CreditCard,
      color: '#6366f1',
      bg: 'rgba(99, 102, 241, 0.15)',
    },
    {
      label: 'Flagged Transactions',
      value: stats.flagged_transactions ?? 0,
      icon: Flag,
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.15)',
    },
    {
      label: 'High Risk (Alerted)',
      value: stats.high_risk_count ?? 0,
      icon: ShieldAlert,
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
    },
    {
      label: 'Pending Review',
      value: stats.pending_review_count ?? 0,
      icon: Clock,
      color: '#eab308',
      bg: 'rgba(234, 179, 8, 0.15)',
    },
    {
      label: 'Reviewed',
      value: stats.reviewed_count ?? 0,
      icon: CheckCheck,
      color: '#a5b4fc',
      bg: 'rgba(99, 102, 241, 0.12)',
    },
    {
      label: 'Cleared',
      value: stats.cleared_count ?? 0,
      icon: ShieldCheck,
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.15)',
    },
  ];

  return (
    <div className="stats-grid">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div key={i} className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: c.bg, color: c.color }}>
              <Icon size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-label">{c.label}</span>
              <span className="stat-value mono">
                {loading ? '...' : c.value.toLocaleString()}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DashboardStats;
