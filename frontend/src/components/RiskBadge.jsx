import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';

export const RiskBadge = ({ level = 'LOW', score = null, showIcon = true }) => {
  const normLevel = (level || 'LOW').toUpperCase();

  if (normLevel === 'HIGH') {
    return (
      <span className="badge badge-high" title={`Risk Score: ${score ?? 'High'}`}>
        {showIcon && <AlertCircle size={13} className="pulse" />}
        <span>HIGH</span>
        {score !== null && <span className="mono font-bold">({score})</span>}
      </span>
    );
  }

  if (normLevel === 'MEDIUM') {
    return (
      <span className="badge badge-med" title={`Risk Score: ${score ?? 'Medium'}`}>
        {showIcon && <AlertTriangle size={13} />}
        <span>MEDIUM</span>
        {score !== null && <span className="mono font-bold">({score})</span>}
      </span>
    );
  }

  return (
    <span className="badge badge-low" title={`Risk Score: ${score ?? 'Low'}`}>
      {showIcon && <CheckCircle2 size={13} />}
      <span>LOW</span>
      {score !== null && <span className="mono font-bold">({score})</span>}
    </span>
  );
};

export default RiskBadge;
