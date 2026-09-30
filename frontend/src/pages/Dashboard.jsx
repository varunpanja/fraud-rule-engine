import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import DashboardStats from '../components/DashboardStats';
import TransactionTable from '../components/TransactionTable';
import ReviewModal from '../components/ReviewModal';
import NewTransactionModal from '../components/NewTransactionModal';
import api from '../services/api';

export const Dashboard = () => {
  const [stats, setStats] = useState({
    total_transactions: 0,
    flagged_transactions: 0,
    high_risk_count: 0,
    medium_risk_count: 0,
    low_risk_count: 0,
    pending_review_count: 0,
    reviewed_count: 0,
    cleared_count: 0,
  });

  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFlag, setSelectedFlag] = useState(null);
  const [showNewTxModal, setShowNewTxModal] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [submittingTx, setSubmittingTx] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [notificationMsg, setNotificationMsg] = useState(null);

  const showToast = (msg, type = 'info') => {
    setNotificationMsg({ msg, type });
    setTimeout(() => {
      setNotificationMsg(null);
    }, 4000);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, flagsData] = await Promise.all([
        api.getDashboardStats(),
        api.getFraudFlags(),
      ]);
      setStats(statsData);
      setFlags(flagsData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      showToast('Error connecting to backend API', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleReview = async (id, notes = '') => {
    try {
      setActionLoadingId(id);
      await api.reviewFraudFlag(id, notes);
      showToast(`Flag #${id} marked as REVIEWED`, 'success');
      if (selectedFlag && selectedFlag.id === id) {
        setSelectedFlag(null);
      }
      await loadData();
    } catch (err) {
      console.error('Review failed:', err);
      showToast('Failed to review transaction', 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleClear = async (id, notes = '') => {
    try {
      setActionLoadingId(id);
      await api.clearFraudFlag(id, notes);
      showToast(`Flag #${id} CLEARED (Legitimate)`, 'success');
      if (selectedFlag && selectedFlag.id === id) {
        setSelectedFlag(null);
      }
      await loadData();
    } catch (err) {
      console.error('Clear failed:', err);
      showToast('Failed to clear transaction', 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleSeed = async () => {
    try {
      setSeeding(true);
      const res = await api.seedDemo();
      showToast(res.message || 'Demo data loaded successfully!', 'success');
      await loadData();
    } catch (err) {
      console.error('Seeding failed:', err);
      showToast('Failed to seed demo data', 'error');
    } finally {
      setSeeding(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset all transactions and flags in the database?')) {
      return;
    }
    try {
      setResetting(true);
      await api.resetDemo();
      showToast('Database reset successfully', 'info');
      await loadData();
    } catch (err) {
      console.error('Reset failed:', err);
      showToast('Failed to reset database', 'error');
    } finally {
      setResetting(false);
    }
  };

  const handleCreateTransaction = async (formData) => {
    try {
      setSubmittingTx(true);
      const res = await api.createTransaction(formData);
      if (res.fraud_evaluation?.is_flagged) {
        showToast(
          `Transaction #${res.id} flagged! Risk: ${res.fraud_evaluation.risk_level} (${res.fraud_evaluation.risk_score} pts)`,
          res.fraud_evaluation.risk_level === 'HIGH' ? 'error' : 'warning'
        );
      } else {
        showToast(`Transaction #${res.id} processed: Normal (No Fraud)`, 'success');
      }
      await loadData();
      return res;
    } catch (err) {
      console.error('Transaction creation failed:', err);
      showToast('Failed to process transaction', 'error');
      throw err;
    } finally {
      setSubmittingTx(false);
    }
  };

  return (
    <div className="app-container">
      <Header
        onSeed={handleSeed}
        onReset={handleReset}
        onOpenNewTx={() => setShowNewTxModal(true)}
        seeding={seeding}
        resetting={resetting}
      />

      {/* Floating Toast Notification */}
      {notificationMsg && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            zIndex: 100,
            background: notificationMsg.type === 'error' ? '#ef4444' : notificationMsg.type === 'warning' ? '#f59e0b' : '#10b981',
            color: '#ffffff',
            padding: '0.75rem 1.25rem',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.875rem',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            animation: 'fadeIn 0.2s ease-in-out',
          }}
        >
          <span>{notificationMsg.msg}</span>
        </div>
      )}

      <main className="main-content">
        <DashboardStats stats={stats} loading={loading} />

        <TransactionTable
          flags={flags}
          loading={loading}
          onInspect={(flag) => setSelectedFlag(flag)}
          onReview={handleReview}
          onClear={handleClear}
          actionLoadingId={actionLoadingId}
        />
      </main>

      {/* Inspection & Review Modal */}
      {selectedFlag && (
        <ReviewModal
          flag={selectedFlag}
          onClose={() => setSelectedFlag(null)}
          onReview={handleReview}
          onClear={handleClear}
          loading={actionLoadingId === selectedFlag.id}
        />
      )}

      {/* Ingestion & Simulation Modal */}
      {showNewTxModal && (
        <NewTransactionModal
          onClose={() => setShowNewTxModal(false)}
          onSubmit={handleCreateTransaction}
          submitting={submittingTx}
        />
      )}
    </div>
  );
};

export default Dashboard;
