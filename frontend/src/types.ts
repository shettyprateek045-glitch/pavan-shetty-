export type NavigationTab = 
  | 'overview' 
  | 'screening' 
  | 'candidates' 
  | '3d-space'
  | 'ai-analysis' 
  | 'fairness' 
  | 'analytics' 
  | 'reports' 
  | 'settings';

export interface Job {
  id: string;
  title: string;
  company: string;
  department: string;
  location: string;
  experience_required: number;
  salary_range: string;
  type: string;
  status: string;
  required_skills: string[];
  nice_to_have_skills?: string[];
  description: string;
}

export interface CandidateExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  metrics?: {
    keyword_match_pct: number;
    semantic_similarity_pct: number;
    experience_fit_pct: number;
    skills_matched_count: number;
    skills_missing_count: number;
  };
}

export interface Candidate {
  id: string;
  rank?: number;
  candidate_id?: string;
  name: string;
  email: string;
  title: string;
  location: string;
  experience_years: number;
  current_company: string;
  education: string;
  skills: string[];
  status: 'Shortlisted' | 'Review' | 'Under Review' | 'Rejected' | 'Interview';
  applied_date: string;
  keyword_score: number;
  semantic_score: number;
  experience_score: number;
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: CandidateExplanation;
  resume_text: string;
  gender_proxy?: string;
  edu_tier?: string;
}

export interface ScoringWeights {
  keyword: number;
  semantic: number;
  experience: number;
}

export interface DemographicGroup {
  name: string;
  evaluated: number;
  selected: number;
  selection_rate: number;
  disparate_impact_ratio: number;
  parity_difference: number;
  status: string;
}

export interface ProtectedCategory {
  category: string;
  groups: DemographicGroup[];
}

export interface AuditHistoryItem {
  id: string;
  timestamp: string;
  job_title: string;
  sample_size: number;
  demographic_parity_diff: number;
  equal_opportunity_diff: number;
  status: string;
  auditor: string;
}

export interface FairnessBenchmark {
  total_evaluated: number;
  total_selected: number;
  selection_rate_overall: number;
  protected_groups: ProtectedCategory[];
  disparate_impact_threshold: number;
  nyc_local_law_144: {
    status: string;
    last_independent_audit_date: string;
    compliance_score: number;
    adverse_impact_flag: boolean;
  };
  audit_history: AuditHistoryItem[];
}

export interface KPIItem {
  value: string | number;
  change: string;
  is_positive: boolean;
  label: string;
}

export interface AnalyticsData {
  kpis: {
    resumes_analyzed: KPIItem;
    shortlisted_candidates: KPIItem;
    avg_relevance_score: KPIItem;
    active_jds: KPIItem;
  };
  screening_timeline: Array<{
    date: string;
    screened: number;
    shortlisted: number;
    avgScore: number;
  }>;
  match_distribution: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  top_candidates: Array<{
    rank: number;
    id: string;
    name: string;
    title: string;
    overall_score: number;
    keyword_score: number;
    semantic_score: number;
    matched_skills: string[];
    experience_years: number;
  }>;
  recent_activity: Array<{
    id: string;
    job_title: string;
    candidate_name: string;
    score: number;
    status: string;
    time: string;
  }>;
}

export interface ScreeningStage {
  id: string;
  name: string;
  detail: string;
  status: 'pending' | 'running' | 'completed';
}
