import React, { useState } from 'react';
import { 
  TrendingUp, 
  Users, 
  CheckCircle2, 
  Target, 
  Briefcase, 
  ArrowUpRight, 
  ChevronRight,
  Eye,
  SlidersHorizontal,
  Box
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { AnalyticsData, Candidate, NavigationTab } from '../types';
import { TiltCard3D } from './TiltCard3D';

interface OverviewProps {
  analytics: AnalyticsData;
  candidates: Candidate[];
  setActiveTab: (tab: NavigationTab) => void;
  onSelectCandidate: (candidate: Candidate) => void;
  blindScreening: boolean;
}

export const Overview: React.FC<OverviewProps> = ({
  analytics,
  candidates,
  setActiveTab,
  onSelectCandidate,
  blindScreening
}) => {
  const [timelineRange, setTimelineRange] = useState<'7D' | '30D' | '90D'>('30D');

  const { kpis, screening_timeline, match_distribution, recent_activity } = analytics;
  const topCandidates = candidates.slice(0, 5);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            Good morning. Here's your hiring overview.
          </h1>
          <p className="text-xs text-secondary mt-1">
            Monitor candidate screening and recruitment insights.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setActiveTab('3d-space')}
            className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-primary bg-card hover:bg-[#F2F4F7] border border-border rounded-md shadow-subtle transition-colors"
          >
            <Box className="w-3.5 h-3.5 text-accent" />
            <span>Launch 3D Space</span>
          </button>

          <button
            onClick={() => setActiveTab('screening')}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-medium text-white bg-accent hover:bg-accent-hover rounded-md shadow-subtle transition-colors"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Run New Screening</span>
          </button>
        </div>
      </div>

      {/* 4 KPI Cards with 3D Tilt Motion */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <TiltCard3D className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Resumes Analyzed</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-primary">
              <Users className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary tracking-tight font-mono">
              {kpis.resumes_analyzed.value}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="inline-flex items-center font-medium text-success bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                <TrendingUp className="w-2.5 h-2.5 mr-0.5" />
                {kpis.resumes_analyzed.change}
              </span>
              <span className="text-secondary truncate">{kpis.resumes_analyzed.label}</span>
            </div>
          </div>
        </TiltCard3D>

        {/* KPI 2 */}
        <TiltCard3D className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Shortlisted Candidates</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-success">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary tracking-tight font-mono">
              {kpis.shortlisted_candidates.value}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="inline-flex items-center font-medium text-success bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                <TrendingUp className="w-2.5 h-2.5 mr-0.5" />
                {kpis.shortlisted_candidates.change}
              </span>
              <span className="text-secondary truncate">{kpis.shortlisted_candidates.label}</span>
            </div>
          </div>
        </TiltCard3D>

        {/* KPI 3 */}
        <TiltCard3D className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Average Relevance Score</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-accent">
              <Target className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary tracking-tight font-mono">
              {kpis.avg_relevance_score.value}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="inline-flex items-center font-medium text-success bg-success-light px-1.5 py-0.2 rounded border border-success-border font-mono">
                <TrendingUp className="w-2.5 h-2.5 mr-0.5" />
                {kpis.avg_relevance_score.change}
              </span>
              <span className="text-secondary truncate">{kpis.avg_relevance_score.label}</span>
            </div>
          </div>
        </TiltCard3D>

        {/* KPI 4 */}
        <TiltCard3D className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-xs font-medium">Active Job Descriptions</span>
            <div className="w-6 h-6 rounded bg-[#F4F5F7] flex items-center justify-center text-primary">
              <Briefcase className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-primary tracking-tight font-mono">
              {kpis.active_jds.value}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px]">
              <span className="inline-flex items-center font-medium text-primary bg-border/60 px-1.5 py-0.2 rounded font-mono">
                {kpis.active_jds.change}
              </span>
              <span className="text-secondary truncate">{kpis.active_jds.label}</span>
            </div>
          </div>
        </TiltCard3D>
      </div>

      {/* Middle Section: Screening Activity Chart (Left) & Match Distribution (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Section (2 cols): Interactive Line Chart */}
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-primary tracking-tight">
                Candidate Screening Activity
              </h2>
              <p className="text-[11px] text-secondary mt-0.5">
                Volumetric processing throughput and qualified shortlist trends
              </p>
            </div>

            <div className="flex items-center gap-1 bg-[#F4F5F7] p-0.5 rounded-md border border-border/80">
              {(['7D', '30D', '90D'] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => setTimelineRange(r)}
                  className={`text-[11px] font-medium px-2 py-0.5 rounded ${
                    timelineRange === r
                      ? 'bg-card text-primary shadow-subtle'
                      : 'text-secondary hover:text-primary'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={screening_timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="date" 
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
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E7E9EE',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
                    fontSize: '12px'
                  }}
                  formatter={(val: any, name: string) => [
                    val,
                    name === 'screened' ? 'Resumes Screened' : 'Qualified Shortlist'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="screened" 
                  stroke="#2563EB" 
                  strokeWidth={2} 
                  dot={{ r: 3, fill: '#2563EB' }} 
                  activeDot={{ r: 5 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="shortlisted" 
                  stroke="#059669" 
                  strokeWidth={2} 
                  dot={{ r: 3, fill: '#059669' }} 
                  activeDot={{ r: 5 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center gap-6 mt-4 pt-3 border-t border-border/60 text-xs text-secondary">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent"></span>
              <span>Screened Resumes</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-success"></span>
              <span>Qualified Shortlist (≥80%)</span>
            </div>
          </div>
        </div>

        {/* Right Section (1 col): Donut Chart */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div className="mb-2">
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Candidate Match Distribution
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Relevance calibration across active talent pool
            </p>
          </div>

          <div className="h-52 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={match_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={58}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {match_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E7E9EE',
                    borderRadius: '8px',
                    fontSize: '11px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-xl font-bold font-mono text-primary">81.4%</span>
              <span className="text-[10px] text-secondary uppercase tracking-wider">Median</span>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-border/60">
            {match_distribution.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-secondary text-[11px] truncate max-w-[150px]">{item.name}</span>
                </div>
                <span className="font-mono text-primary font-medium text-[11px]">{item.value} cands</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section: Recent Activity (Left) and Top Candidates (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left (2 cols): Recent Screening Activity Table */}
        <div className="lg:col-span-2 bg-card border border-border rounded-lg p-5 shadow-subtle">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-primary tracking-tight">
                Recent Screening Activity
              </h2>
              <p className="text-[11px] text-secondary mt-0.5">
                Real-time ingestion and automated scoring audit log
              </p>
            </div>
            <button
              onClick={() => setActiveTab('candidates')}
              className="text-xs text-accent font-medium hover:underline flex items-center gap-1"
            >
              <span>View all candidates</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-border text-[11px] font-medium text-secondary">
                  <th className="py-2.5 px-3">Batch ID</th>
                  <th className="py-2.5 px-3">Candidate</th>
                  <th className="py-2.5 px-3">Requisition</th>
                  <th className="py-2.5 px-3 text-right">Score</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {recent_activity.map((row) => (
                  <tr key={row.id} className="hover:bg-[#F9FAFB] transition-colors">
                    <td className="py-2.5 px-3 font-mono text-[11px] text-secondary">
                      {row.id}
                    </td>
                    <td className="py-2.5 px-3 font-medium text-primary">
                      {blindScreening ? 'Candidate ' + row.id.split('-')[1] : row.candidate_name}
                    </td>
                    <td className="py-2.5 px-3 text-secondary truncate max-w-[180px]">
                      {row.job_title}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      <span className={
                        row.score >= 85 ? 'text-success' :
                        row.score >= 75 ? 'text-accent' : 'text-warning'
                      }>
                        {row.score}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                        row.status === 'Shortlisted' 
                          ? 'bg-success-light text-success border border-success-border'
                          : 'bg-[#F2F4F7] text-secondary'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-secondary text-[11px]">
                      {row.time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right (1 col): Top Candidates Section */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-semibold text-primary tracking-tight">
                  Top Ranked Candidates
                </h2>
                <p className="text-[11px] text-secondary mt-0.5">
                  Highest semantic and technical alignment
                </p>
              </div>
              <button
                onClick={() => setActiveTab('candidates')}
                className="text-xs text-accent font-medium hover:underline flex items-center gap-0.5"
              >
                <span>Full List</span>
                <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-2.5">
              {topCandidates.map((cand, idx) => (
                <TiltCard3D
                  key={cand.id}
                  onClick={() => onSelectCandidate(cand)}
                  className="p-3 rounded-lg border border-border/80 hover:border-accent/40 bg-[#FAFBFD] transition-all cursor-pointer flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded bg-[#F4F5F7] border border-border flex items-center justify-center font-mono font-semibold text-xs text-primary">
                      #{idx + 1}
                    </div>
                    <div>
                      <div className="font-medium text-xs text-primary group-hover:text-accent transition-colors flex items-center gap-1.5">
                        <span>{blindScreening ? `Candidate #${cand.rank || idx + 1}` : cand.name}</span>
                        <span className="text-[10px] text-secondary">({cand.experience_years}y)</span>
                      </div>
                      <div className="flex items-center gap-1 mt-1">
                        {cand.matched_skills.slice(0, 3).map((skill) => (
                          <span
                            key={skill}
                            className="text-[10px] bg-[#F2F4F7] text-secondary px-1.5 py-0.2 rounded font-mono"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end">
                    <span className="text-xs font-bold font-mono text-success">
                      {cand.overall_score}%
                    </span>
                    <span className="text-[10px] text-secondary">Match</span>
                  </div>
                </TiltCard3D>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border/60">
            <button
              onClick={() => setActiveTab('candidates')}
              className="w-full py-2 text-xs font-medium text-primary bg-[#F4F5F7] hover:bg-[#EBEEF2] rounded-md transition-colors flex items-center justify-center gap-1.5"
            >
              <Eye className="w-3.5 h-3.5 text-secondary" />
              <span>Review Candidate Pipeline</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
