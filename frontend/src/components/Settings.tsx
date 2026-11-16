import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Shield, 
  Sliders, 
  Save, 
  Check, 
  Lock, 
  Bell, 
  Key,
  Sparkles
} from 'lucide-react';

interface SettingsProps {
  blindScreening: boolean;
  setBlindScreening: (val: boolean) => void;
}

export const Settings: React.FC<SettingsProps> = ({
  blindScreening,
  setBlindScreening
}) => {
  const [shortlistThreshold, setShortlistThreshold] = useState(80);
  const [auditFrequency, setAuditFrequency] = useState('Weekly');
  const [savedFeedback, setSavedFeedback] = useState(false);

  const handleSave = () => {
    setSavedFeedback(true);
    setTimeout(() => setSavedFeedback(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            Platform Settings & Governance
          </h1>
          <p className="text-xs text-secondary mt-1">
            Configure algorithmic scoring thresholds, blind screening policies, and compliance rules.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center gap-1.5 px-4 py-2 bg-primary text-white rounded-md text-xs font-medium hover:bg-black transition-colors shadow-subtle"
        >
          {savedFeedback ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
          <span>{savedFeedback ? 'Saved!' : 'Save Settings'}</span>
        </button>
      </div>

      {/* Section 1: Algorithmic Thresholds */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="border-b border-border/80 pb-3">
          <h2 className="text-sm font-semibold text-primary tracking-tight flex items-center gap-2">
            <Sliders className="w-4 h-4 text-accent" />
            <span>Scoring & Shortlisting Calibrations</span>
          </h2>
          <p className="text-[11px] text-secondary mt-0.5">
            Define cutoffs for automated shortlist qualification
          </p>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between items-center text-xs mb-1">
              <span className="font-medium text-primary">Shortlist Qualification Cutoff</span>
              <span className="font-mono font-bold text-success text-sm">{shortlistThreshold}%</span>
            </div>
            <input
              type="range"
              min="70"
              max="95"
              step="1"
              value={shortlistThreshold}
              onChange={(e) => setShortlistThreshold(Number(e.target.value))}
              className="w-full h-1.5 bg-[#E7E9EE] rounded-lg appearance-none cursor-pointer accent-success"
            />
            <p className="text-[11px] text-secondary mt-1">
              Candidates scoring at or above this threshold receive automated 'Shortlisted' status and recruiter notifications.
            </p>
          </div>
        </div>
      </div>

      {/* Section 2: Blind Screening & Unconscious Bias Prevention */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="border-b border-border/80 pb-3">
          <h2 className="text-sm font-semibold text-primary tracking-tight flex items-center gap-2">
            <Shield className="w-4 h-4 text-success" />
            <span>Blind Screening & Demographic Masking</span>
          </h2>
          <p className="text-[11px] text-secondary mt-0.5">
            Anonymize identifiable applicant information during initial evaluation cycles
          </p>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 bg-[#FAFBFD] border border-border rounded-md">
            <div>
              <span className="font-medium text-primary block">Enable Global Blind Screening</span>
              <span className="text-[11px] text-secondary">
                Masks applicant candidate names, email addresses, and university pedigree names.
              </span>
            </div>
            <input
              type="checkbox"
              checked={blindScreening}
              onChange={(e) => setBlindScreening(e.target.checked)}
              className="rounded border-border text-accent focus:ring-accent w-4 h-4 cursor-pointer"
            />
          </div>

          <div className="p-3 bg-[#FAFBFD] border border-border rounded-md space-y-2">
            <span className="font-medium text-primary block">Masked Attributes in Blind Mode:</span>
            <div className="grid grid-cols-2 gap-2 text-secondary text-[11px]">
              <div className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-success" />
                <span>Full Legal Name & Identity</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-success" />
                <span>Personal Email & Phone Number</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-success" />
                <span>University / School Name</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-success" />
                <span>Graduation Years (Age Proxy)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Compliance & Automated Audits */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="border-b border-border/80 pb-3">
          <h2 className="text-sm font-semibold text-primary tracking-tight flex items-center gap-2">
            <Lock className="w-4 h-4 text-primary" />
            <span>Compliance Automation & EEOC Auditing</span>
          </h2>
          <p className="text-[11px] text-secondary mt-0.5">
            Schedule recurring demographic disparity audits
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-[11px] font-medium text-secondary mb-1">
              Automated Audit Recurrence
            </label>
            <select
              value={auditFrequency}
              onChange={(e) => setAuditFrequency(e.target.value)}
              className="w-full bg-slate-50 border border-border rounded-md px-3 py-2 text-primary font-medium"
            >
              <option value="Daily">Daily Automated Check</option>
              <option value="Weekly">Weekly Parity Verification (Recommended)</option>
              <option value="Monthly">Monthly Executive Review</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-secondary mb-1">
              Audit Standard Threshold
            </label>
            <input
              type="text"
              disabled
              value="EEOC 4/5ths Rule (DIR ≥ 0.80)"
              className="w-full bg-[#F2F4F7] border border-border rounded-md px-3 py-2 text-secondary font-mono"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
