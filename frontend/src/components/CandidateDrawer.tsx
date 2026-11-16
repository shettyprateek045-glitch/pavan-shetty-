import React, { useState } from 'react';
import { 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  Briefcase, 
  GraduationCap, 
  MapPin, 
  Mail, 
  FileText, 
  ExternalLink,
  Calendar,
  Layers,
  Sparkles
} from 'lucide-react';
import { Candidate } from '../types';

interface CandidateDrawerProps {
  candidate: Candidate | null;
  onClose: () => void;
  onUpdateStatus: (candidateId: string, newStatus: Candidate['status']) => void;
  blindScreening: boolean;
}

export const CandidateDrawer: React.FC<CandidateDrawerProps> = ({
  candidate,
  onClose,
  onUpdateStatus,
  blindScreening
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'resume'>('profile');

  if (!candidate) return null;

  const displayName = blindScreening ? `Candidate #${candidate.rank || '1'}` : candidate.name;
  const displayEmail = blindScreening ? 'masked-identity@applicant.internal' : candidate.email;
  const displayCompany = blindScreening ? 'Enterprise Tech Provider' : candidate.current_company;
  const displayLocation = blindScreening ? 'Region: US Remote' : candidate.location;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-primary/20 backdrop-blur-[1px] flex justify-end">
      <div 
        className="w-full max-w-xl bg-card border-l border-border h-full shadow-drawer flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200"
      >
        {/* Top Header */}
        <div className="p-5 border-b border-border bg-[#FAFBFD] sticky top-0 z-10">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 border border-border flex items-center justify-center font-bold text-sm text-primary">
                {blindScreening ? `#${candidate.rank || '1'}` : candidate.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-semibold text-primary">{displayName}</h2>
                  <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-border/60 text-secondary">
                    {candidate.experience_years}y Exp
                  </span>
                </div>
                <div className="text-xs text-secondary mt-0.5 flex items-center gap-2">
                  <span>{candidate.title}</span>
                  <span>•</span>
                  <span>{displayCompany}</span>
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-7 h-7 rounded-md border border-border flex items-center justify-center text-secondary hover:text-primary hover:bg-[#F2F4F7] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Contact & Metadata */}
          <div className="flex items-center gap-4 mt-3 text-xs text-secondary">
            <div className="flex items-center gap-1.5 truncate">
              <Mail className="w-3.5 h-3.5" />
              <span className="truncate">{displayEmail}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5" />
              <span>{displayLocation}</span>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex items-center gap-2 mt-4 pt-2 border-t border-border/60">
            <button
              onClick={() => setActiveTab('profile')}
              className={`text-xs font-medium px-3 py-1 rounded-md transition-colors ${
                activeTab === 'profile'
                  ? 'bg-primary text-white shadow-subtle'
                  : 'text-secondary hover:text-primary hover:bg-[#F2F4F7]'
              }`}
            >
              Analysis & Profile
            </button>
            <button
              onClick={() => setActiveTab('resume')}
              className={`text-xs font-medium px-3 py-1 rounded-md transition-colors ${
                activeTab === 'resume'
                  ? 'bg-primary text-white shadow-subtle'
                  : 'text-secondary hover:text-primary hover:bg-[#F2F4F7]'
              }`}
            >
              Original Parsed Resume
            </button>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-5 space-y-6 flex-1">
          {activeTab === 'profile' ? (
            <>
              {/* Score Breakdown Grid */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-primary tracking-tight uppercase tracking-wider text-[11px]">
                    Relevance Score Breakdown
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-secondary">Status:</span>
                    <select
                      value={candidate.status}
                      onChange={(e) => onUpdateStatus(candidate.id, e.target.value as Candidate['status'])}
                      className="text-xs bg-white border border-border rounded px-2 py-0.5 font-medium text-primary shadow-subtle"
                    >
                      <option value="Shortlisted">Shortlisted</option>
                      <option value="Review">Review</option>
                      <option value="Under Review">Under Review</option>
                      <option value="Interview">Interview</option>
                      <option value="Rejected">Rejected</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-2">
                  <div className="bg-[#FAFBFD] border border-border rounded-lg p-2.5 text-center">
                    <div className="text-[10px] text-secondary font-medium">Overall Fit</div>
                    <div className="text-lg font-bold font-mono text-success mt-1">
                      {candidate.overall_score}%
                    </div>
                  </div>
                  <div className="bg-[#FAFBFD] border border-border rounded-lg p-2.5 text-center">
                    <div className="text-[10px] text-secondary font-medium">Semantic Sim</div>
                    <div className="text-lg font-bold font-mono text-accent mt-1">
                      {candidate.semantic_score}%
                    </div>
                  </div>
                  <div className="bg-[#FAFBFD] border border-border rounded-lg p-2.5 text-center">
                    <div className="text-[10px] text-secondary font-medium">Keyword TF-IDF</div>
                    <div className="text-lg font-bold font-mono text-primary mt-1">
                      {candidate.keyword_score}%
                    </div>
                  </div>
                  <div className="bg-[#FAFBFD] border border-border rounded-lg p-2.5 text-center">
                    <div className="text-[10px] text-secondary font-medium">Experience Fit</div>
                    <div className="text-lg font-bold font-mono text-primary mt-1">
                      {candidate.experience_score}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Match Explanation & Natural Language Summary */}
              <div className="bg-[#FAFBFD] border border-border rounded-lg p-4 space-y-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-primary">
                  <Sparkles className="w-3.5 h-3.5 text-accent" />
                  <span>Explainability & Ranking Rationale</span>
                </div>
                <p className="text-xs text-primary leading-relaxed font-sans">
                  {candidate.explanation.summary}
                </p>

                {/* Strengths */}
                {candidate.explanation.strengths.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-border/60">
                    <div className="text-[11px] font-semibold text-success uppercase tracking-wider">
                      Verified Strengths
                    </div>
                    {candidate.explanation.strengths.map((s, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-primary">
                        <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                        <span>{s}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Missing Criteria / Gaps */}
                {candidate.missing_skills.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-border/60">
                    <div className="text-[11px] font-semibold text-warning uppercase tracking-wider">
                      Identified Gaps & Missing Skills
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {candidate.missing_skills.map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center gap-1 text-[11px] bg-warning-light text-warning border border-warning-border px-2 py-0.5 rounded font-mono font-medium"
                        >
                          <AlertTriangle className="w-3 h-3" />
                          <span>{skill}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Technical Skills Verification */}
              <div>
                <div className="text-xs font-semibold text-primary uppercase tracking-wider text-[11px] mb-2">
                  Skills Matrix ({candidate.matched_skills.length} Matched / {candidate.missing_skills.length} Missing)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {candidate.matched_skills.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 text-[11px] bg-success-light text-success border border-success-border px-2 py-0.5 rounded font-mono"
                    >
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      <span>{skill}</span>
                    </span>
                  ))}
                  {candidate.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 text-[11px] bg-[#F2F4F7] text-secondary border border-border px-2 py-0.5 rounded font-mono line-through"
                    >
                      <span>{skill}</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* Education & Experience Details */}
              <div className="space-y-3 pt-2 border-t border-border/80">
                <div className="flex items-center gap-2 text-xs text-primary font-medium">
                  <GraduationCap className="w-4 h-4 text-secondary" />
                  <span>{blindScreening ? 'Accredited Higher Education' : candidate.education}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-primary font-medium">
                  <Briefcase className="w-4 h-4 text-secondary" />
                  <span>{candidate.experience_years} years documented engineering track record</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-secondary">
                  <Calendar className="w-4 h-4 text-secondary" />
                  <span>Applied on {candidate.applied_date}</span>
                </div>
              </div>
            </>
          ) : (
            /* Original Parsed Resume Tab */
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-secondary">
                <span>Text Layer Extraction (Source Resume)</span>
                <span className="font-mono text-[10px]">Indexed UTF-8</span>
              </div>
              <pre className="bg-[#FAFBFD] border border-border rounded-lg p-4 text-xs font-mono text-primary whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-[500px]">
                {candidate.resume_text}
              </pre>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-border bg-[#FAFBFD] flex items-center justify-between sticky bottom-0">
          <button
            onClick={() => onUpdateStatus(candidate.id, 'Shortlisted')}
            className="px-4 py-2 bg-success text-white rounded-md text-xs font-medium hover:bg-emerald-700 transition-colors shadow-subtle"
          >
            Shortlist Candidate
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 bg-card border border-border rounded-md text-xs font-medium text-primary hover:bg-[#F2F4F7] transition-colors"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
};
