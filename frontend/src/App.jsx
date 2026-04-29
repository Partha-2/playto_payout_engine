import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wallet, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Plus,
  RefreshCcw,
  ArrowRight
} from 'lucide-react';

// Get API base URL from environment or use relative path
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : `${window.location.protocol}//${window.location.host}/api/v1`);

export default function App() {
  const [merchant, setMerchant] = useState(null);
  const [payouts, setPayouts] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorState, setErrorState] = useState(null);
  const [merchantId, setMerchantId] = useState(1); // Default to first seeded merchant
  const [showPayoutForm, setShowPayoutForm] = useState(false);

    try {
      const [mRes, pRes, hRes] = await Promise.all([
        axios.get(`${API_BASE}/merchants/${merchantId}/`),
        axios.get(`${API_BASE}/payouts?merchant_id=${merchantId}`),
        axios.get(`${API_BASE}/merchants/${merchantId}/history`)
      ]);
      setMerchant(mRes.data);
      setPayouts(pRes.data);
      setHistory(hRes.data);
      setErrorState(null);
    } catch (err) {
      console.error("Error fetching data", err);
      setErrorState(err.message || "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Polling for live updates
    return () => clearInterval(interval);
  }, [merchantId]);

  if (loading && !merchant) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <motion.div 
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
      >
        <RefreshCcw className="text-primary w-8 h-8" />
      </motion.div>
    </div>
  );

  if (errorState && !merchant) return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center text-white p-4">
      <AlertCircle className="text-rose-500 w-16 h-16 mb-4" />
      <h2 className="text-2xl font-bold">Connection Error</h2>
      <p className="text-zinc-400 mt-2 text-center">Could not connect to the API at <br/><span className="text-white font-mono bg-white/10 px-2 py-1 rounded text-sm">{API_BASE}</span></p>
      <div className="bg-white/5 p-4 rounded-xl mt-6 max-w-md text-sm text-zinc-400 border border-white/10">
        <p className="mb-2"><strong className="text-white">If running locally:</strong> Make sure your Django backend is running on port 8000.</p>
        <p><strong className="text-white">If deployed:</strong> Ensure the <code className="text-primary bg-primary/10 px-1 rounded">VITE_API_URL</code> environment variable is set to your Render backend URL.</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Playto <span className="text-primary">Pay</span></h1>
            <p className="text-zinc-500 text-sm">Payout Engine Dashboard</p>
          </div>
          <div className="flex items-center gap-3 bg-card p-1 rounded-full border border-white/5">
            {[1, 2, 3].map(id => (
              <button 
                key={id}
                onClick={() => setMerchantId(id)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${merchantId === id ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-zinc-400 hover:text-white'}`}
              >
                M-{id}
              </button>
            ))}
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 rounded-3xl relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <Wallet size={80} className="text-primary" />
            </div>
            <p className="text-zinc-400 text-sm font-medium uppercase tracking-wider">Available Balance</p>
            <h2 className="text-4xl font-bold mt-2">
              ₹{(merchant.balance_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </h2>
            <div className="mt-4 flex items-center gap-2 text-emerald-500 text-xs font-semibold">
              <ArrowUpRight size={14} />
              <span>Real-time Settlement</span>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6 rounded-3xl"
          >
            <p className="text-zinc-400 text-sm font-medium uppercase tracking-wider">Held Funds</p>
            <h2 className="text-4xl font-bold mt-2">
              ₹{(payouts.filter(p => p.status === 'PENDING' || p.status === 'PROCESSING').reduce((acc, p) => acc + p.amount_paise, 0) / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </h2>
            <div className="mt-4 flex items-center gap-2 text-amber-500 text-xs font-semibold">
              <Clock size={14} />
              <span>Awaiting Bank Settlement</span>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-primary p-6 rounded-3xl shadow-2xl shadow-primary/20 flex flex-col justify-between"
          >
            <div>
              <h3 className="text-white font-bold text-lg">Send Payout</h3>
              <p className="text-primary-foreground/70 text-sm">Withdraw to your linked bank account</p>
            </div>
            <button 
              onClick={() => setShowPayoutForm(true)}
              className="mt-4 bg-white text-primary px-6 py-3 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-zinc-100 transition-colors"
            >
              <Plus size={20} />
              New Payout
            </button>
          </motion.div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Payout History */}
          <div className="space-y-4">
            <div className="flex justify-between items-center px-2">
              <h3 className="text-lg font-bold">Recent Payouts</h3>
              <button onClick={fetchData} className="text-zinc-400 hover:text-white transition-colors">
                <RefreshCcw size={16} />
              </button>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {payouts.slice(0, 5).map((payout) => (
                  <motion.div 
                    key={payout.id}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="glass-card p-4 rounded-2xl flex items-center justify-between group hover:border-white/20 transition-all"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-xl ${
                        payout.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-500' :
                        payout.status === 'FAILED' ? 'bg-rose-500/10 text-rose-500' :
                        'bg-amber-500/10 text-amber-500 animate-pulse'
                      }`}>
                        {payout.status === 'COMPLETED' ? <CheckCircle2 size={20} /> :
                         payout.status === 'FAILED' ? <XCircle size={20} /> :
                         <Clock size={20} />}
                      </div>
                      <div>
                        <p className="font-bold">₹{(payout.amount_paise / 100).toLocaleString('en-IN')}</p>
                        <p className="text-xs text-zinc-500">Bank: {payout.bank_account_id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-[10px] uppercase tracking-widest font-black px-2 py-1 rounded-md ${
                        payout.status === 'COMPLETED' ? 'text-emerald-500 bg-emerald-500/5' :
                        payout.status === 'FAILED' ? 'text-rose-500 bg-rose-500/5' :
                        'text-amber-500 bg-amber-500/5'
                      }`}>
                        {payout.status}
                      </span>
                      <p className="text-[10px] text-zinc-600 mt-1">{new Date(payout.created_at).toLocaleTimeString()}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Ledger History */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold px-2">Ledger Activity</h3>
            <div className="glass-card rounded-3xl overflow-hidden border border-white/5">
              <table className="w-full text-sm text-left">
                <thead className="text-[10px] text-zinc-500 uppercase tracking-widest bg-zinc-900/50">
                  <tr>
                    <th className="px-6 py-4 font-black">Type</th>
                    <th className="px-6 py-4 font-black">Description</th>
                    <th className="px-6 py-4 font-black text-right">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {history.slice(0, 8).map((entry) => (
                    <tr key={entry.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4">
                        <span className={`flex items-center gap-2 ${entry.amount_paise > 0 ? 'text-emerald-500' : 'text-zinc-400'}`}>
                          {entry.amount_paise > 0 ? <ArrowDownLeft size={14} /> : <ArrowUpRight size={14} />}
                          {entry.entry_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-zinc-400 font-medium">{entry.description}</td>
                      <td className={`px-6 py-4 text-right font-bold ${entry.amount_paise > 0 ? 'text-emerald-400' : 'text-white'}`}>
                        {entry.amount_paise > 0 ? '+' : ''}{(entry.amount_paise / 100).toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Payout Modal */}
      <AnimatePresence>
        {showPayoutForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowPayoutForm(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="glass-card w-full max-w-md p-8 rounded-[40px] relative z-10"
            >
              <h2 className="text-2xl font-bold mb-2 text-center">Request Payout</h2>
              <p className="text-zinc-500 text-center text-sm mb-8">Funds will be debited from your balance immediately.</p>
              
              <PayoutForm 
                merchantId={merchantId} 
                onSuccess={() => {
                  setShowPayoutForm(false);
                  fetchData();
                }} 
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function PayoutForm({ merchantId, onSuccess }) {
  const [amount, setAmount] = useState('');
  const [bankId, setBankId] = useState('BANK-IND-9921');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    
    try {
      const idempotencyKey = uuidv4();
      await axios.post(`${API_BASE}/payouts`, {
        merchant_id: merchantId,
        amount_paise: parseInt(amount) * 100,
        bank_account_id: bankId
      }, {
        headers: { 'Idempotency-Key': idempotencyKey }
      });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label className="text-xs font-black uppercase tracking-widest text-zinc-500 ml-1">Amount (INR)</label>
        <input 
          type="number"
          required
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00"
          className="w-full bg-zinc-900 border border-white/10 rounded-2xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-primary/50 text-xl font-bold"
        />
      </div>

      <div className="space-y-2">
        <label className="text-xs font-black uppercase tracking-widest text-zinc-500 ml-1">Bank Account</label>
        <div className="w-full bg-zinc-900 border border-white/10 rounded-2xl px-5 py-4 flex items-center justify-between">
          <span className="font-medium text-zinc-300">{bankId}</span>
          <CheckCircle2 size={18} className="text-primary" />
        </div>
      </div>

      {error && (
        <motion.div 
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-rose-500/10 border border-rose-500/20 text-rose-500 p-4 rounded-2xl flex items-center gap-3 text-sm"
        >
          <AlertCircle size={18} />
          {error}
        </motion.div>
      )}

      <button 
        type="submit"
        disabled={submitting}
        className="w-full bg-primary py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:opacity-90 disabled:opacity-50 transition-all shadow-xl shadow-primary/20"
      >
        {submitting ? <RefreshCcw className="animate-spin" /> : <>Confirm Payout <ArrowRight size={20} /></>}
      </button>
    </form>
  );
}

// Simple UUID generator for simulation
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
