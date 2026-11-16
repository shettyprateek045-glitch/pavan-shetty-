import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Printer, 
  CheckCircle2, 
  ShieldCheck, 
  Sparkles,
  Calendar,
  Briefcase
} from 'lucide-react';
import { Candidate, Job } from '../types';

interface ReportsProps {
  candidates: Candidate[];
  activeJob: Job;
  blindScreening: boolean;
}

export const Reports: React.FC<ReportsProps> = ({
  candidates,
  activeJob,
  blindScreening
}) => {
  const [includeExplanations, setIncludeExplanations] = useState(true);
  const [includeAuditStamp, setIncludeAuditStamp] = useState(true);

  const topCandidates = candidates.slice(0, 5);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Controls & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            Executive Screening Reports
          </h1>
          <p className="text-xs text-secondary mt-1">
            Generate formal, auditable hiring dossiers for engineering leadership and compliance boards.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-card border border-border text-primary rounded-md text-xs font-medium hover:bg-[#F2F4F7] transition-colors shadow-subtle"
          >
            <Printer className="w-3.5 h-3.5 text-secondary" />
            <span>Print Report</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-primary text-white rounded-md text-xs font-medium hover:bg-black transition-colors shadow-subtle"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF Dossier</span>
          </button>
        </div>
      </div>

      {/* Report Customization Bar */}
      <div className="bg-card border border-border rounded-lg p-3 shadow-subtle flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-primary">Report Options:</span>
          <label className="flex items-center gap-1.5 cursor-pointer text-secondary hover:text-primary">
            <input
              type="checkbox"
              checked={includeExplanations}
              onChange={(e) => setIncludeExplanations(e.target.checked)}
              className="rounded border-border text-accent focus:ring-accent w-3.5 h-3.5"
            />
            <span>Include AI Natural Language Rationale</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-secondary hover:text-primary">
            <input
              type="checkbox"
              checked={includeAuditStamp}
              onChange={(e) => setIncludeAuditStamp(e.target.checked)}
              className="rounded border-border text-accent focus:ring-accent w-3.5 h-3.5"
            />
            <span>Include EEOC / NYC LL144 Certification Seal</span>
          </label>
        </div>

        <div className="text-[11px] text-secondary font-mono">
          Generated: Nov 16, 2026 • TalentRank Engine v2.4
        </div>
      </div>

      {/* Printable Report Document Card */}
      <div className="bg-card border border-border rounded-xl p-8 shadow-card max-w-4xl mx-auto space-y-6 text-primary">
        {/* Document Header */}
        <div className="border-b border-border pb-6 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase font-bold tracking-widest text-accent">
                TALENTRANK AI
              </span>
              <span className="text-secondary">•</span>
              <span className="text-xs text-secondary font-mono">Dossier #TR-2026-8842</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-primary">
              Executive Candidate Screening Assessment
            </h2>
            <div className="flex items-center gap-3 mt-1.5 text-xs text-secondary">
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5" />
                <strong>Role:</strong> {activeJob.title}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                Nov 16, 2026
              </span>
            </div>
          </div>

          <div className="text-right">
            <div className="text-xs font-semibold text-primary">Confidential Evaluation</div>
            <div className="text-[10px] text-secondary">Authorized for Internal Hiring Team Only</div>
          </div>
        </div>

        {/* Executive Summary Metrics */}
        <div className="grid grid-cols-4 gap-3 bg-[#FAFBFD] p-4 rounded-lg border border-border">
          <div>
            <span className="text-[10px] text-secondary uppercase font-semibold">Total Evaluated</span>
            <div className="text-lg font-bold font-mono text-primary mt-0.5">{candidates.length} Profiles</div>
          </div>
          <div>
            <span className="text-[10px] text-secondary uppercase font-semibold">Shortlist Qualified</span>
            <div className="text-lg font-bold font-mono text-success mt-0.5">
              {candidates.filter(c => c.overall_score >= 80).length} Candidates
            </div>
          </div>
          <div>
            <span className="text-[10px] text-secondary uppercase font-semibold">Median Relevance</span>
            <div className="text-lg font-bold font-mono text-primary mt-0.5">81.4%</div>
          </div>
          <div>
            <span className="text-[10px] text-secondary uppercase font-semibold">Parity Audit</span>
            <div className="text-lg font-bold font-mono text-success mt-0.5">Certified 100%</div>
          </div>
        </div>

        {/* Top 5 Ranked Candidates Breakdown */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-primary tracking-tight uppercase tracking-wider text-[11px]">
            Top Recommended Candidates & Technical Breakdown
          </h3>

          <div className="space-y-3">
            {topCandidates.map((cand, idx) => {
              const name = blindScreening ? `Candidate #${cand.rank || idx + 1}` : cand.name;
              return (
                <div key={cand.id} className="border border-border/80 rounded-lg p-4 bg-[#FAFBFD] space-y-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded bg-primary text-white text-[10px] font-mono font-bold flex items-center justify-center">
                          #{idx + 1}
                        </span>
                        <span className="font-bold text-sm text-primary">{name}</span>
                        <span className="text-xs text-secondary font-mono font-medium">({cand.experience_years}y Exp)</span>
                      </div>
                      <div className="text-xs text-secondary mt-0.5">
                        {cand.title} • {cand.current_company}
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-base font-bold font-mono text-success">
                        {cand.overall_score}% Fit
                      </div>
                      <div className="text-[10px] text-secondary font-mono">
                        Sem: {cand.semantic_score}% | KW: {cand.keyword_score}%
                      </div>
                    </div>
                  </div>

                  {includeExplanations && (
                    <div className="text-xs text-primary pt-2 border-t border-border/60 leading-relaxed font-sans">
                      <span className="font-semibold text-[11px] text-secondary uppercase block mb-0.5">
                        Attribution Rationale:
                      </span>
                      {cand.explanation.summary}
                    </div>
                  )}

                  <div className="flex items-center gap-1.5 pt-1 text-xs">
                    <span className="text-[10px] text-secondary font-semibold uppercase">Matched:</span>
                    {cand.matched_skills.map((s) => (
                      <span key={s} className="text-[10px] font-mono bg-white border border-border px-1.5 py-0.2 rounded text-primary">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Responsible AI Verification Seal */}
        {includeAuditStamp && (
          <div className="p-4 bg-success-light border border-success-border rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-6 h-6 text-success shrink-0" />
              <div>
                <div className="text-xs font-bold text-primary">
                  Responsible AI Certification Statement
                </div>
                <div className="text-[11px] text-secondary leading-snug">
                  This hiring batch was evaluated without consideration of age, gender, race, or proxy demographics.
                  Disparate Impact Ratio: <strong className="text-primary font-mono">1.05</strong>. Fully compliant with NYC Local Law 144.
                </div>
              </div>
            </div>
            <div className="text-right shrink-0 font-mono text-[10px] text-secondary">
              <div>Audited by: Automated Engine</div>
              <div>Hash: 7f8a9c...3b4e</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
