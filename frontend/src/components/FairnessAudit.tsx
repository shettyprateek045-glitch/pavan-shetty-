import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Scale, 
  AlertTriangle, 
  CheckCircle2, 
  FileCheck, 
  Download, 
  Info, 
  Sparkles,
  ExternalLink,
  History,
  X
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';
import { FairnessBenchmark, Job } from '../types';

interface FairnessAuditProps {
  fairnessData: { benchmark: FairnessBenchmark };
  activeJob: Job;
}

export const FairnessAudit: React.FC<FairnessAuditProps> = ({
  fairnessData,
  activeJob
}) => {
  const { benchmark } = fairnessData;
  const [selectedCohortIndex, setSelectedCohortIndex] = useState(0);
  const [showCertificateModal, setShowCertificateModal] = useState(false);

  const activeCohort = benchmark.protected_groups[selectedCohortIndex] || benchmark.protected_groups[0];

  const chartData = activeCohort.groups.map(g => ({
    name: g.name.split(' (')[0],
    rate: Math.round(g.selection_rate * 100),
    ratio: g.disparate_impact_ratio,
    status: g.status
  }));

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Banner: Strict Decoupling Notice */}
      <div className="bg-[#FAFBFD] border border-border rounded-lg p-4 flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-success-light border border-success-border flex items-center justify-center text-success shrink-0 mt-0.5">
          <ShieldCheck className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-semibold text-primary">
              Ethical Governance & Algorithmic Non-Discrimination Guardrails
            </h2>
            <span className="text-[10px] font-mono text-success bg-success-light px-1.5 py-0.2 rounded border border-success-border font-medium">
              EEOC & NYC Local Law 144 Compliant
            </span>
          </div>
          <p className="text-[11px] text-secondary mt-1 leading-relaxed">
            TalentRank AI strictly enforces zero protected-attribute leakage. Candidate scoring and ranking algorithms evaluate only verified technical skills and documented experience. Fairness audits are executed independently on aggregated cohorts to verify statistical parity.
          </p>
        </div>
        <button
          onClick={() => setShowCertificateModal(true)}
          className="shrink-0 flex items-center gap-1.5 text-xs text-primary font-medium bg-white border border-border rounded-md px-3 py-1.5 hover:bg-[#F2F4F7] transition-colors shadow-subtle"
        >
          <FileCheck className="w-3.5 h-3.5 text-success" />
          <span>View Audit Certificate</span>
        </button>
      </div>

      {/* 4 Responsible AI KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Disparate Impact Ratio */}
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Disparate Impact Ratio</span>
            <div className="w-6 h-6 rounded bg-success-light flex items-center justify-center text-success">
              <Scale className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary font-mono">
              1.05
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="text-success font-medium bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                Compliant (≥ 0.80)
              </span>
              <span className="text-secondary truncate">4/5ths Rule Pass</span>
            </div>
          </div>
        </div>

        {/* Metric 2: Demographic Parity Difference */}
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Demographic Parity Diff</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-primary">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary font-mono">
              0.018
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="text-success font-medium bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                Target (&lt; 0.10)
              </span>
              <span className="text-secondary truncate">Negligible Variance</span>
            </div>
          </div>
        </div>

        {/* Metric 3: Equal Opportunity Difference */}
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Equal Opportunity Diff</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-accent">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary font-mono">
              0.024
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="text-success font-medium bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                Target (&lt; 0.05)
              </span>
              <span className="text-secondary truncate">True Positive Parity</span>
            </div>
          </div>
        </div>

        {/* Metric 4: NYC LL144 Status */}
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">NYC LL144 Compliance</span>
            <div className="w-6 h-6 rounded bg-success-light flex items-center justify-center text-success">
              <ShieldCheck className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary font-mono">
              96.4%
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="text-success font-medium bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                Certified
              </span>
              <span className="text-secondary truncate">Audit Oct 18, 2026</span>
            </div>
          </div>
        </div>
      </div>

      {/* Group Selection Rates Bar Chart & Cohort Breakdown */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-border/80 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Cohort Selection Rates & Disparate Impact Evaluation
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Comparison of candidate advancement rates across synthetic demographic proxy categories
            </p>
          </div>

          {/* Cohort Category Switcher */}
          <div className="flex items-center gap-1 bg-[#F4F5F7] p-0.5 rounded-md border border-border/80">
            {benchmark.protected_groups.map((cat, idx) => (
              <button
                key={cat.category}
                onClick={() => setSelectedCohortIndex(idx)}
                className={`text-[11px] font-medium px-2.5 py-1 rounded transition-colors ${
                  selectedCohortIndex === idx
                    ? 'bg-card text-primary shadow-subtle'
                    : 'text-secondary hover:text-primary'
                }`}
              >
                {cat.category}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          {/* Bar Chart (2 cols) */}
          <div className="lg:col-span-2 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="name" 
                  stroke="#9CA3AF" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <YAxis 
                  unit="%" 
                  domain={[0, 40]}
                  stroke="#9CA3AF" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <Tooltip
                  formatter={(val: any) => [`${val}%`, 'Selection Rate']}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E7E9EE',
                    borderRadius: '8px',
                    fontSize: '11px'
                  }}
                />
                <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.ratio >= 0.80 ? '#16845B' : '#C58A29'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Cohort Metrics Table (1 col) */}
          <div className="space-y-2 border-l border-border/80 pl-4 flex flex-col justify-between">
            <div>
              <div className="text-xs font-semibold text-primary mb-2">
                {activeCohort.category} Metrics
              </div>
              <div className="space-y-2 text-xs">
                {activeCohort.groups.map((g) => (
                  <div key={g.name} className="p-2.5 bg-[#FAFBFD] border border-border/80 rounded-md">
                    <div className="flex justify-between items-start">
                      <span className="font-medium text-primary text-[11px] truncate max-w-[170px]">{g.name}</span>
                      <span className={`text-[10px] font-mono font-medium px-1.5 py-0.2 rounded ${
                        g.status === 'Compliant' || g.status === 'Benchmark'
                          ? 'bg-success-light text-success'
                          : 'bg-warning-light text-warning'
                      }`}>
                        {g.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-2 text-[10px] text-secondary font-mono">
                      <span>Rate: <strong className="text-primary">{Math.round(g.selection_rate * 100)}%</strong> ({g.selected}/{g.evaluated})</span>
                      <span>DI Ratio: <strong className="text-primary">{g.disparate_impact_ratio}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 text-[10px] text-secondary leading-tight">
              Federal 4/5ths standard requires selection rate of any protected cohort to be ≥ 80% of the benchmark rate.
            </div>
          </div>
        </div>
      </div>

      {/* JD Linguistic Scanner & Data Quality Warnings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Job Description Linguistic Bias Scanner */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-3">
          <div className="flex items-center justify-between border-b border-border/80 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-primary tracking-tight">
                Job Description Linguistic Parity Scanner
              </h2>
              <p className="text-[11px] text-secondary mt-0.5">
                Detects masculine- vs. feminine-coded phrasing in active job posting
              </p>
            </div>
            <span className="text-[10px] font-semibold text-success bg-success-light px-2 py-0.5 rounded border border-success-border">
              Balanced
            </span>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-2.5 bg-[#FAFBFD] border border-border rounded-md">
              <span className="text-secondary">Assertive / Agentic Terms Detected:</span>
              <span className="font-mono font-semibold text-primary">2 terms (lead, operate)</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-[#FAFBFD] border border-border rounded-md">
              <span className="text-secondary">Collaborative / Communal Terms Detected:</span>
              <span className="font-mono font-semibold text-primary">2 terms (mentor, support)</span>
            </div>
            <div className="p-3 bg-success-light border border-success-border rounded-md text-[11px] text-primary">
              <strong className="text-success font-medium">Linguistic Assessment: </strong>
              The active job specification demonstrates equitable linguistic neutrality. Phrasing attracts broad applicant demographics without unintentional gender-skewing friction.
            </div>
          </div>
        </div>

        {/* Right: Data Quality & Resume Ingestion Warnings */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-3">
          <div className="flex items-center justify-between border-b border-border/80 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-primary tracking-tight">
                Data Quality & Ingestion Health
              </h2>
              <p className="text-[11px] text-secondary mt-0.5">
                Monitoring parsing fidelity and non-standard resume formats
              </p>
            </div>
            <span className="text-[10px] font-mono text-secondary">100% Parsed</span>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-start gap-2.5 p-2.5 bg-[#FAFBFD] border border-border rounded-md">
              <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-primary">Zero OCR Text Layer Dropouts</span>
                <p className="text-[11px] text-secondary mt-0.5">
                  All 15 resumes processed with clean character encodings and full token fidelity.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2.5 bg-[#FAFBFD] border border-border rounded-md">
              <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-primary">Non-Traditional Resume Robustness</span>
                <p className="text-[11px] text-secondary mt-0.5">
                  Semantic engine successfully mapped open-source Github contributions and apprenticeships.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Audit History Log Table */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-3">
        <div className="flex items-center justify-between border-b border-border/80 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Historical Fairness & Parity Audits
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Cryptographically timestamped compliance evaluations
            </p>
          </div>
          <button 
            onClick={() => setShowCertificateModal(true)}
            className="text-xs text-accent font-medium hover:underline flex items-center gap-1"
          >
            <Download className="w-3 h-3" />
            <span>Download Official Audit Dossier</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-[#FAFBFD] text-[11px] text-secondary font-medium">
                <th className="py-2.5 px-3">Audit Reference</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Requisition</th>
                <th className="py-2.5 px-3 text-right">Sample Pool</th>
                <th className="py-2.5 px-3 text-right">Demographic Parity</th>
                <th className="py-2.5 px-3 text-right">Equal Opportunity</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Auditor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {benchmark.audit_history.map((item) => (
                <tr key={item.id} className="hover:bg-[#F9FAFB]">
                  <td className="py-2.5 px-3 font-mono text-[11px] text-primary font-semibold">
                    {item.id}
                  </td>
                  <td className="py-2.5 px-3 text-secondary text-[11px]">
                    {item.timestamp}
                  </td>
                  <td className="py-2.5 px-3 text-primary font-medium">
                    {item.job_title}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-secondary">
                    {item.sample_size} cands
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-success">
                    {item.demographic_parity_diff}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-success">
                    {item.equal_opportunity_diff}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="text-[10px] font-medium text-success bg-success-light px-2 py-0.5 rounded border border-success-border font-mono">
                      {item.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-secondary text-[11px]">
                    {item.auditor}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Compliance Certificate Modal */}
      {showCertificateModal && (
        <div className="fixed inset-0 z-50 bg-primary/30 backdrop-blur-[2px] flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-xl shadow-dropdown max-w-2xl w-full p-6 space-y-4">
            <div className="flex items-start justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-md bg-success-light border border-success-border flex items-center justify-center text-success">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-primary">
                    EEOC & NYC Local Law 144 Compliance Certificate
                  </h3>
                  <span className="text-[11px] text-secondary">Certificate ID: AEDT-2026-LL144-8842</span>
                </div>
              </div>
              <button
                onClick={() => setShowCertificateModal(false)}
                className="w-7 h-7 rounded-md border border-border flex items-center justify-center text-secondary hover:text-primary"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-primary leading-relaxed bg-[#FAFBFD] p-4 rounded-lg border border-border font-sans">
              <div className="font-semibold text-primary">
                Annual Independent Bias Audit Verification
              </div>
              <p className="text-secondary text-[11px]">
                This certifies that the automated employment decision tool (AEDT) deployed by <strong>TalentRank AI</strong> has undergone statistical bias auditing in compliance with NYC Administrative Code § 20-870 et seq. (Local Law 144).
              </p>
              <div className="grid grid-cols-2 gap-3 py-2 border-y border-border/80 font-mono text-[11px]">
                <div>
                  <span className="text-secondary block text-[10px]">Overall Selection Ratio:</span>
                  <span className="font-bold text-primary">1.05 (Passes 4/5ths Rule)</span>
                </div>
                <div>
                  <span className="text-secondary block text-[10px]">Demographic Parity Delta:</span>
                  <span className="font-bold text-success">0.018 (Variance &lt; 2%)</span>
                </div>
                <div>
                  <span className="text-secondary block text-[10px]">Protected Features in Scoring:</span>
                  <span className="font-bold text-success">Zero (Strictly Prohibited)</span>
                </div>
                <div>
                  <span className="text-secondary block text-[10px]">Audit Cycle:</span>
                  <span className="font-bold text-primary">Valid Through Nov 2027</span>
                </div>
              </div>
              <p className="text-[10px] text-secondary italic">
                Issued by Automated Systems Governance Board. Cryptographic SHA-256 Signature verified.
              </p>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowCertificateModal(false)}
                className="px-4 py-2 bg-primary text-white rounded-md text-xs font-medium hover:bg-black transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
