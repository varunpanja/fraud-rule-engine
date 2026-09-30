import React from 'react';
import { Clock, CheckCheck, ShieldCheck, HelpCircle } from 'lucide-react';

export const StatusBadge = ({ status = 'PENDING', showIcon = true }) => {
  const normStatus = (status || 'PENDING').toUpperCase();

  if (normStatus === 'PENDING') {
    return (
      <span className="badge badge-pending">
        {showIcon && <Clock size={12} />}
        <span>PENDING</span>
      </span>
    );
  }

  if (normStatus === 'REVIEWED') {
    return (
      <span className="badge badge-reviewed">
        {showIcon && <CheckCheck size={12} />}
        <span>REVIEWED</span>
      </span>
    );
  }

  if (normStatus === 'CLEARED') {
    return (
      <span className="badge badge-cleared">
        {showIcon && <ShieldCheck size={12} />}
        <span>CLEARED</span>
      </span>
    );
  }

  return (
    <span className="badge" style={{ background: '#334155', color: '#cbd5e1' }}>
      {showIcon && <HelpCircle size={12} />}
      <span>{normStatus}</span>
    </span>
  );
};

export default StatusBadge;
