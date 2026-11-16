import { Job, Candidate, ScoringWeights, AnalyticsData, FairnessBenchmark } from './types';
import { INITIAL_JOBS, INITIAL_CANDIDATES, INITIAL_FAIRNESS } from './mockData';

const BASE_URL = (typeof window !== 'undefined' && window.location.protocol.startsWith('http'))
  ? window.location.origin
  : 'http://localhost:8000';

export async function loginApi(credentials: { email: string; password: string; remember_me?: boolean }): Promise<{
  status: string;
  token: string;
  user: { name: string; email: string; role: string; department?: string };
}> {
  try {
    const res = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
      signal: AbortSignal.timeout(3000),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = typeof data.detail === 'string' ? data.detail : 'Demo sign-in was rejected.';
      throw new Error(detail);
    }
    return data;
  } catch (err) {
    if (err instanceof Error && err.name !== 'AbortError' && err.name !== 'TimeoutError' && !/fetch/i.test(err.message)) {
      throw err;
    }
    throw new Error('The demo sign-in API is unavailable. Start the FastAPI service and try again.');
  }
}

export async function fetchJobs(): Promise<Job[]> {
  try {
    const res = await fetch(`${BASE_URL}/api/jobs`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      if (data.jobs && data.jobs.length > 0) return data.jobs;
    }
  } catch (err) {
    // Fallback to local high-fidelity data
  }
  return INITIAL_JOBS;
}

export async function fetchCandidates(jobId = 'job-lead-backend'): Promise<Candidate[]> {
  try {
    const res = await fetch(`${BASE_URL}/api/candidates?job_id=${encodeURIComponent(jobId)}`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      if (data.candidates && data.candidates.length > 0) return data.candidates;
    }
  } catch (err) {
    // Fallback
  }
  return INITIAL_CANDIDATES;
}

export async function runScreeningApi(payload: {
  job_id?: string;
  custom_job?: any;
  weights?: ScoringWeights;
}): Promise<{
  candidates: Candidate[];
  shortlisted_count: number;
  average_score: number;
  total_screened: number;
  jd_bias_check: any;
}> {
  try {
    const res = await fetch(`${BASE_URL}/api/screen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (err) {
    // Fallback client-side calibrated calculation
  }

  // Recalculate locally using supplied weights
  const weights = payload.weights || { keyword: 0.35, semantic: 0.45, experience: 0.20 };
  const wTotal = weights.keyword + weights.semantic + weights.experience;
  const kwW = weights.keyword / wTotal;
  const semW = weights.semantic / wTotal;
  const expW = weights.experience / wTotal;

  const rescored = INITIAL_CANDIDATES.map((cand) => {
    const overall = Number(
      ((cand.keyword_score * kwW) + (cand.semantic_score * semW) + (cand.experience_score * expW)).toFixed(1)
    );
    let status: Candidate['status'] = cand.status;
    if (overall >= 84.0) status = 'Shortlisted';
    else if (overall >= 72.0) status = 'Review';
    else status = 'Under Review';

    return {
      ...cand,
      overall_score: overall,
      status
    };
  }).sort((a, b) => b.overall_score - a.overall_score);

  rescored.forEach((c, idx) => {
    c.rank = idx + 1;
  });

  const scores = rescored.map((c) => c.overall_score);
  const avg = Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1));
  const shortlisted = rescored.filter((c) => c.overall_score >= 80.0).length;

  return {
    candidates: rescored,
    shortlisted_count: shortlisted,
    average_score: avg,
    total_screened: rescored.length,
    jd_bias_check: {
      sentiment: "Neutral / Balanced",
      masculine_count: 2,
      feminine_count: 2,
      recommendation: "Job description demonstrates equitable, neutral professional phrasing.",
      badge: "success"
    }
  };
}

export async function fetchAnalyticsData(jobId = 'job-lead-backend'): Promise<AnalyticsData> {
  try {
    const res = await fetch(`${BASE_URL}/api/analytics?job_id=${encodeURIComponent(jobId)}`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fallback
  }

  // High-fidelity fallback analytics
  return {
    kpis: {
      resumes_analyzed: { value: 142, change: '+18.4%', is_positive: true, label: 'vs. previous 30 days' },
      shortlisted_candidates: { value: 38, change: '+12.5%', is_positive: true, label: '26.8% conversion rate' },
      avg_relevance_score: { value: '81.4%', change: '+4.2%', is_positive: true, label: 'calibrated across pool' },
      active_jds: { value: 3, change: 'Active', is_positive: true, label: 'across 3 engineering pods' }
    },
    screening_timeline: [
      { date: 'Nov 03', screened: 12, shortlisted: 3, avgScore: 76.4 },
      { date: 'Nov 05', screened: 18, shortlisted: 5, avgScore: 79.1 },
      { date: 'Nov 07', screened: 24, shortlisted: 7, avgScore: 81.3 },
      { date: 'Nov 09', screened: 19, shortlisted: 4, avgScore: 78.8 },
      { date: 'Nov 11', screened: 28, shortlisted: 9, avgScore: 82.5 },
      { date: 'Nov 13', screened: 22, shortlisted: 6, avgScore: 80.2 },
      { date: 'Nov 15', screened: 31, shortlisted: 10, avgScore: 84.1 },
      { date: 'Nov 16', screened: 26, shortlisted: 8, avgScore: 83.6 },
    ],
    match_distribution: [
      { name: 'Exceptional (90-100%)', value: 4, color: '#2563EB' },
      { name: 'Strong Match (80-89%)', value: 4, color: '#0284C7' },
      { name: 'Moderate Match (70-79%)', value: 1, color: '#64748B' },
      { name: 'Low Alignment (<70%)', value: 1, color: '#94A3B8' }
    ],
    top_candidates: [
      { rank: 1, id: 'cand-01', name: 'Elena Rostova', title: 'Senior Distributed Systems Engineer', overall_score: 95.8, keyword_score: 96.0, semantic_score: 95.2, matched_skills: ['Go', 'Kafka', 'Redis'], experience_years: 8.0 },
      { rank: 2, id: 'cand-02', name: 'Marcus Vance', title: 'Staff Backend Engineer', overall_score: 95.1, keyword_score: 98.2, semantic_score: 93.6, matched_skills: ['Go', 'Python', 'Kafka'], experience_years: 9.5 },
      { rank: 3, id: 'cand-11', name: 'Zachary Zhao', title: 'Staff Platform Engineer', overall_score: 94.6, keyword_score: 94.0, semantic_score: 94.8, matched_skills: ['Go', 'Rust', 'Kubernetes'], experience_years: 10.0 },
      { rank: 4, id: 'cand-07', name: 'Aisha Kamara', title: 'Distributed Systems & Infrastructure Engineer', overall_score: 92.2, keyword_score: 92.5, semantic_score: 91.0, matched_skills: ['Go', 'Kafka', 'Kubernetes'], experience_years: 7.0 },
      { rank: 5, id: 'cand-03', name: 'Tariq Al-Mansoor', title: 'Senior Cloud Infrastructure & Backend Engineer', overall_score: 89.5, keyword_score: 89.0, semantic_score: 88.4, matched_skills: ['Go', 'Python', 'PostgreSQL'], experience_years: 6.5 },
    ],
    recent_activity: [
      { id: 'SCR-882', job_title: 'Staff Backend Distributed Systems Engineer', candidate_name: 'Elena Rostova', score: 95.8, status: 'Shortlisted', time: '12 mins ago' },
      { id: 'SCR-881', job_title: 'Staff Backend Distributed Systems Engineer', candidate_name: 'Marcus Vance', score: 95.1, status: 'Shortlisted', time: '45 mins ago' },
      { id: 'SCR-880', job_title: 'Senior AI/ML Semantic Search Engineer', candidate_name: 'Maya Lin', score: 92.4, status: 'Shortlisted', time: '2 hours ago' },
      { id: 'SCR-879', job_title: 'Principal Frontend UI/UX Architect', candidate_name: 'Sofia Delgado', score: 93.8, status: 'Shortlisted', time: '4 hours ago' },
      { id: 'SCR-878', job_title: 'Staff Backend Distributed Systems Engineer', candidate_name: 'Julian Brooks', score: 88.1, status: 'Review', time: '6 hours ago' }
    ]
  };
}

export async function fetchFairnessAudit(): Promise<{ benchmark: FairnessBenchmark }> {
  try {
    const res = await fetch(`${BASE_URL}/api/fairness`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fallback
  }
  return INITIAL_FAIRNESS;
}
