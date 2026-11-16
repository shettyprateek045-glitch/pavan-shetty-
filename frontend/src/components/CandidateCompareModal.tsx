import React from 'react';
import { X, Check, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Candidate, Job } from '../types';

interface CandidateCompareModalProps {
  candidates: Candidate[];
  activeJob: Job;
  onClose: () => void;
  blindScreening: boolean;
}

export const CandidateCompareModal: React.FC<CandidateCompareModalProps> = ({
  candidates,
  activeJob,
  onClose,
  blindScreening
}) => {
  if (candidates.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-primary/25 backdrop-blur-[2px] flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-xl shadow-dropdown w-full max-w-5xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border bg-[#FAFBFD] flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-primary tracking-tight">
              Candidate Head-to-Head Comparison
            </h2>
            <p className="text-xs text-secondary mt-0.5">
              Side-by-side evaluation against <strong className="text-primary">{activeJob.title}</strong>
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-md border border-border flex items-center justify-center text-secondary hover:text-primary hover:bg-[#F2F4F7] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Table */}
        <div className="p-6 overflow-y-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {candidates.map((cand, idx) => {
              const name = blindScreening ? `Candidate #${cand.rank || idx + 1}` : cand.name;
              return (
                <div key={cand.id} className="border border-border rounded-lg p-4 bg-[#FAFBFD] flex flex-col justify-between space-y-4">
                  {/* Candidate Header */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono font-bold px-2 py-0.5 bg-primary text-white rounded">
                        #{cand.rank || idx + 1}
                      </span>
                      <span className="text-xs font-mono font-bold text-success text-base">
                        {cand.overall_score}%
                      </span>
                    </div>
                    <div className="font-semibold text-sm text-primary">{name}</div>
                    <div className="text-xs text-secondary mt-0.5">{cand.title}</div>
                    <div className="text-[11px] text-secondary mt-0.5 font-mono">{cand.experience_years} Years Experience</div>
                  </div>

                  {/* Score breakdown metrics */}
                  <div className="space-y-1.5 bg-white p-3 rounded border border-border/80 text-xs">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-secondary">Semantic Similarity:</span>
                      <span className="font-mono font-semibold text-accent">{cand.semantic_score}%</span>
                    </div>
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-secondary">Keyword Match:</span>
                      <span className="font-mono font-semibold text-primary">{cand.keyword_score}%</span>
                    </div>
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-secondary">Seniority Fit:</span>
                      <span className="font-mono font-semibold text-primary">{cand.experience_score}%</span>
                    </div>
                  </div>

                  {/* Skills match */}
                  <div>
                    <div className="text-[11px] font-semibold text-secondary uppercase tracking-wider mb-1.5">
                      Matched Skills ({cand.matched_skills.length})
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {cand.matched_skills.map((s) => (
                        <span key={s} className="text-[10px] bg-success-light text-success border border-success-border px-1.5 py-0.2 rounded font-mono">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Gaps */}
                  <div>
                    <div className="text-[11px] font-semibold text-secondary uppercase tracking-wider mb-1.5">
                      Missing Requirements ({cand.missing_skills.length})
                    </div>
                    {cand.missing_skills.length === 0 ? (
                      <span className="text-[11px] text-success font-medium">None (100% Coverage)</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {cand.missing_skills.map((s) => (
                          <span key={s} className="text-[10px] bg-warning-light text-warning border border-warning-border px-1.5 py-0.2 rounded font-mono">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Recommendation Summary */}
                  <div className="text-[11px] text-secondary border-t border-border/60 pt-2 leading-relaxed">
                    {cand.explanation.summary}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Skill Requirement Coverage Matrix */}
          <div className="border border-border rounded-lg overflow-hidden">
            <div className="bg-[#FAFBFD] px-4 py-2.5 border-b border-border text-xs font-semibold text-primary">
              Requirement-by-Requirement Coverage Matrix
            </div>
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-slate-50 text-[11px] text-secondary">
                  <th className="py-2 px-4">Required Skill / Standard</th>
                  {candidates.map((c, idx) => (
                    <th key={c.id} className="py-2 px-4 font-medium text-primary">
                      {blindScreening ? `Candidate #${c.rank || idx + 1}` : c.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {activeJob.required_skills.map((skill) => (
                  <tr key={skill} className="hover:bg-[#F9FAFB]">
                    <td className="py-2 px-4 font-mono font-medium text-primary text-[11px]">
                      {skill}
                    </td>
                    {candidates.map((c) => {
                      const hasSkill = c.matched_skills.includes(skill);
                      return (
                        <td key={c.id} className="py-2 px-4">
                          {hasSkill ? (
                            <span className="inline-flex items-center gap-1 text-[11px] text-success font-medium">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Verified</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[11px] text-secondary line-through">
                              <span>Missing</span>
                            </span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-border bg-[#FAFBFD] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary text-white rounded-md text-xs font-medium hover:bg-black transition-colors"
          >
            Done Comparing
          </button>
        </div>
      </div>
    </div>
  );
};
