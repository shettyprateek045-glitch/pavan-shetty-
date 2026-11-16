import React from 'react';
import { 
  BarChart2, 
  TrendingUp, 
  Users, 
  Clock, 
  Target, 
  CheckCircle2, 
  Zap,
  ArrowUpRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell, 
  AreaChart, 
  Area 
} from 'recharts';
import { Candidate, Job } from '../types';

interface AnalyticsProps {
  candidates: Candidate[];
  activeJob: Job;
}

export const Analytics: React.FC<AnalyticsProps> = ({
  candidates,
  activeJob
}) => {
  // Score histogram data
  const scoreBands = [
    { band: '60-69%', count: candidates.filter(c => c.overall_score >= 60 && c.overall_score < 70).length, label: 'Low Fit' },
    { band: '70-79%', count: candidates.filter(c => c.overall_score >= 70 && c.overall_score < 80).length, label: 'Moderate' },
    { band: '80-89%', count: candidates.filter(c => c.overall_score >= 80 && c.overall_score < 90).length, label: 'Strong' },
    { band: '90-100%', count: candidates.filter(c => c.overall_score >= 90).length, label: 'Exceptional' },
  ];

  // Pipeline funnel data
  const funnelStages = [
    { stage: 'Ingested Resumes', count: 142, rate: '100%' },
    { stage: 'Scored & Normalized', count: 142, rate: '100%' },
    { stage: 'Shortlisted (≥80%)', count: 38, rate: '26.8%' },
    { stage: 'Recruiter Outreach', count: 18, rate: '12.6%' },
    { stage: 'Technical Interviews', count: 8, rate: '5.6%' },
    { stage: 'Final Offers Made', count: 2, rate: '1.4%' },
  ];

  // Skill demand vs supply data
  const skillMarketData = [
    { skill: 'Go', candidateSupply: 85, requirementDemand: 95 },
    { skill: 'Kafka', candidateSupply: 62, requirementDemand: 90 },
    { skill: 'PostgreSQL', candidateSupply: 90, requirementDemand: 85 },
    { skill: 'Kubernetes', candidateSupply: 70, requirementDemand: 80 },
    { skill: 'gRPC', candidateSupply: 48, requirementDemand: 75 },
    { skill: 'Redis', candidateSupply: 88, requirementDemand: 80 },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            Recruitment Intelligence & Talent Analytics
          </h1>
          <p className="text-xs text-secondary mt-1">
            Pipeline conversion velocity, score distribution histograms, and skill gap metrics.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono bg-card border border-border px-3 py-1.5 rounded-md shadow-subtle">
          <Clock className="w-3.5 h-3.5 text-secondary" />
          <span>Avg Screening Latency: <strong className="text-primary font-bold">140ms</strong></span>
        </div>
      </div>

      {/* Top Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle">
          <span className="text-xs font-medium text-secondary">Time-to-Screen</span>
          <div className="text-2xl font-bold font-mono text-primary mt-1">1.8 Days</div>
          <span className="text-[11px] text-success font-medium mt-1 block">↓ 68% vs traditional manual review</span>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle">
          <span className="text-xs font-medium text-secondary">Recruiter Throughput</span>
          <div className="text-2xl font-bold font-mono text-primary mt-1">45 Resumes/hr</div>
          <span className="text-[11px] text-success font-medium mt-1 block">↑ 4.2x efficiency boost</span>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle">
          <span className="text-xs font-medium text-secondary">Interview Pass Rate</span>
          <div className="text-2xl font-bold font-mono text-primary mt-1">82.4%</div>
          <span className="text-[11px] text-success font-medium mt-1 block">Predictive technical precision</span>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 shadow-subtle">
          <span className="text-xs font-medium text-secondary">Candidate Satisfaction</span>
          <div className="text-2xl font-bold font-mono text-primary mt-1">4.9 / 5.0</div>
          <span className="text-[11px] text-secondary mt-1 block">Transparent explainability feedback</span>
        </div>
      </div>

      {/* Middle Row: Score Distribution (Left) & Pipeline Funnel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution Histogram */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Relevance Score Histogram
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Calibrated distribution across the indexed candidate pool
            </p>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreBands} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="band" 
                  stroke="#9CA3AF" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <YAxis 
                  stroke="#9CA3AF" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <Tooltip
                  formatter={(val: any, name: string) => [val, 'Candidates in Band']}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E7E9EE',
                    borderRadius: '8px',
                    fontSize: '11px'
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {scoreBands.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={index === 3 ? '#16845B' : index === 2 ? '#4F46E5' : '#C58A29'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-[11px] text-secondary pt-3 border-t border-border/60">
            <span>Peak concentration between 80-89%</span>
            <span>Target shortlist benchmark: ≥ 80%</span>
          </div>
        </div>

        {/* Pipeline Funnel */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Recruitment Pipeline Velocity Funnel
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Progression from raw inbound applications to verified hiring offers
            </p>

            <div className="space-y-2 mt-4">
              {funnelStages.map((stage, idx) => (
                <div key={stage.stage} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-primary">{stage.stage}</span>
                    <span className="font-mono text-secondary">
                      <strong className="text-primary">{stage.count}</strong> ({stage.rate})
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-[#E7E9EE] rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${idx < 3 ? 'bg-primary' : 'bg-success'}`}
                      style={{ width: stage.rate }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-border/60 text-[11px] text-secondary flex items-center justify-between">
            <span>Overall Ingestion to Offer: 1.4%</span>
            <span className="text-success font-medium">Industry Benchmark: 0.8%</span>
          </div>
        </div>
      </div>

      {/* Skill Market Supply vs Requirement Demand */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="border-b border-border/80 pb-3">
          <h2 className="text-sm font-semibold text-primary tracking-tight">
            Skill Market Supply vs. Requisition Demand
          </h2>
          <p className="text-[11px] text-secondary mt-0.5">
            Identify talent scarcity areas in the active requisition pool
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {skillMarketData.map((s) => {
            const gap = s.requirementDemand - s.candidateSupply;
            return (
              <div key={s.skill} className="bg-[#FAFBFD] border border-border rounded-lg p-3 text-center space-y-1">
                <span className="font-mono font-semibold text-xs text-primary block">{s.skill}</span>
                <div className="text-[10px] text-secondary font-mono">
                  Supply: {s.candidateSupply}%
                </div>
                <div className="text-[10px] text-secondary font-mono">
                  Demand: {s.requirementDemand}%
                </div>
                <div className={`text-[10px] font-bold font-mono pt-1 ${gap > 20 ? 'text-danger' : gap > 0 ? 'text-warning' : 'text-success'}`}>
                  {gap > 0 ? `-${gap}% Gap` : 'Equilibrium'}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
