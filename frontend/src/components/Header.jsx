import React, { useState } from 'react';
import { ShieldAlert, Database, PlusCircle, RotateCcw, Activity } from 'lucide-react';

export const Header = ({ onSeed, onReset, onOpenNewTx, seeding, resetting }) => {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand-section">
          <div className="brand-logo">
            <ShieldAlert size={22} color="#ffffff" />
          </div>
          <div>
            <h1 className="brand-title">Fraud Review Console</h1>
            <div className="brand-subtitle flex items-center gap-1">
              <span>SentinelGuard Engine v1.0</span>
              <span style={{ color: '#4ade80' }}>• Live</span>
            </div>
          </div>
        </div>

        <div className="nav-actions">
          <button 
            className="btn btn-secondary btn-sm"
            onClick={onReset}
            disabled={resetting || seeding}
            title="Reset demo database to clean state"
          >
            <RotateCcw size={14} className={resetting ? 'animate-spin' : ''} />
            {resetting ? 'Resetting...' : 'Reset Data'}
          </button>

          <button 
            className="btn btn-secondary btn-sm"
            onClick={onSeed}
            disabled={seeding || resetting}
            title="Load demo scenarios (Velocity, Amount, Geo breaches)"
          >
            <Database size={14} />
            {seeding ? 'Seeding Demo...' : 'Seed Demo Data'}
          </button>

          <button 
            className="btn btn-primary btn-sm"
            onClick={onOpenNewTx}
          >
            <PlusCircle size={15} />
            Ingest / Test Transaction
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
