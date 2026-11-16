import React, { useState, useMemo } from 'react';
import { 
  Cpu, 
  Sliders, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  ScatterChart as ScatterIcon,
  Layers,
  ArrowRight,
  Box
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  Tooltip, 
  Cell 
} from 'recharts';
import { Candidate, Job, ScoringWeights } from '../types';
import { ThreeCanvasView } from './ThreeCanvasView';

interface AiAnalysisProps {
  candidates: Candidate[];
  activeJob: Job;
  onSelectCandidate: (candidate: Candidate) => void;
  blindScreening: boolean;
}

export const AiAnalysis: React.FC<AiAnalysisProps> = ({
  candidates,
  activeJob,
  onSelectCandidate,
  blindScreening
}) => {
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');

  // Simulator Weights
  const [weights, setWeights] = useState<ScoringWeights>({
    semantic: 0.45,
    keyword: 0.35,
    experience: 0.20
  });

  // Dynamically re-score candidates based on live simulation weights
  const simulatedCandidates = useMemo(() => {
    const total = weights.semantic + weights.keyword + weights.experience;
    const wSem = weights.semantic / total;
    const wKw = weights.keyword / total;
    const wExp = weights.experience / total;

    const list = candidates.map((cand) => {
      const recalculated = Number(
        ((cand.semantic_score * wSem) + (cand.keyword_score * wKw) + (cand.experience_score * wExp)).toFixed(1)
      );
      return {
        ...cand,
        simulated_score: recalculated
      };
    });

    list.sort((a, b) => b.simulated_score - a.simulated_score);
    return list.map((c, idx) => ({ ...c, simulated_rank: idx + 1 }));
  }, [candidates, weights]);

  // Scatter chart data: X = Keyword Match, Y = Semantic Similarity, Z = Experience
  const scatterData = useMemo(() => {
    return simulatedCandidates.map((c) => ({
      name: blindScreening ? `Candidate #${c.simulated_rank}` : c.name,
      keyword: c.keyword_score,
      semantic: c.semantic_score,
      experience: c.experience_years,
      score: c.simulated_score,
      id: c.id
    }));
  }, [simulatedCandidates, blindScreening]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            AI Analysis & Explainability Workspace
          </h1>
          <p className="text-xs text-secondary mt-1">
            Algorithmic transparency, feature weight simulation, and cross-encoder semantic attribution.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* 3D vs 2D Toggle */}
          <div className="flex items-center gap-1 bg-[#F4F5F7] p-0.5 rounded-md border border-border">
            <button
              onClick={() => setViewMode('3d')}
              className={`text-xs font-medium px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 ${
                viewMode === '3d'
                  ? 'bg-primary text-white shadow-subtle'
                  : 'text-secondary hover:text-primary'
              }`}
            >
              <Box className="w-3.5 h-3.5" />
              <span>3D Spatial Mode</span>
            </button>
            <button
              onClick={() => setViewMode('2d')}
              className={`text-xs font-medium px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 ${
                viewMode === '2d'
                  ? 'bg-primary text-white shadow-subtle'
                  : 'text-secondary hover:text-primary'
              }`}
            >
              <ScatterIcon className="w-3.5 h-3.5" />
              <span>2D Projection</span>
            </button>
          </div>

          <span className="text-[11px] font-mono text-secondary bg-[#F4F5F7] px-2.5 py-1 rounded border border-border hidden sm:inline-block">
            Sentence-BERT + BM25 Lexical
          </span>
        </div>
      </div>

      {/* Feature Weight Simulator Section */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle space-y-4">
        <div className="flex items-center justify-between border-b border-border/80 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-accent" />
              <span>Interactive Model Weight Simulator</span>
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Adjust algorithm emphasis and observe real-time rank delta across candidate pool
            </p>
          </div>
          <button
            onClick={() => setWeights({ semantic: 0.45, keyword: 0.35, experience: 0.20 })}
            className="text-xs text-accent font-medium hover:underline"
          >
            Reset Default Weights
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-1">
          {/* Slider 1: Semantic */}
          <div className="bg-[#FAFBFD] p-3.5 rounded-lg border border-border/80 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-primary">Semantic Similarity Weight</span>
              <span className="font-mono font-bold text-accent">{(weights.semantic * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={weights.semantic}
              onChange={(e) => setWeights({ ...weights, semantic: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-[#E7E9EE] rounded-lg appearance-none cursor-pointer accent-accent"
            />
            <p className="text-[10px] text-secondary leading-tight">
              Captures architectural context, systems seniority, and latent synonyms.
            </p>
          </div>

          {/* Slider 2: Keyword */}
          <div className="bg-[#FAFBFD] p-3.5 rounded-lg border border-border/80 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-primary">Keyword TF-IDF / Lexical</span>
              <span className="font-mono font-bold text-primary">{(weights.keyword * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={weights.keyword}
              onChange={(e) => setWeights({ ...weights, keyword: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-[#E7E9EE] rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[10px] text-secondary leading-tight">
              Exact token presence, mandatory library tools, and taxonomy matching.
            </p>
          </div>

          {/* Slider 3: Experience */}
          <div className="bg-[#FAFBFD] p-3.5 rounded-lg border border-border/80 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-primary">Seniority / Experience Fit</span>
              <span className="font-mono font-bold text-primary">{(weights.experience * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={weights.experience}
              onChange={(e) => setWeights({ ...weights, experience: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-[#E7E9EE] rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[10px] text-secondary leading-tight">
              Years of verifiable engineering experience against role requirement.
            </p>
          </div>
        </div>
      </div>

      {/* Middle Row: Semantic vs Keyword 2D Space & Explainability Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* 3D WebGL Space vs 2D Scatter Mode */}
      {viewMode === '3d' ? (
        <ThreeCanvasView
          candidates={candidates}
          activeJob={activeJob}
          onSelectCandidate={onSelectCandidate}
          blindScreening={blindScreening}
        />
      ) : (
        /* 2D Scatter Space */
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Semantic vs. Lexical Alignment Space (2D Orthogonal Projection)
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              X-axis: Keyword Overlap • Y-axis: Semantic Similarity (High Y/Low X spots hidden talent)
            </p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: -10 }}>
                <XAxis 
                  type="number" 
                  dataKey="keyword" 
                  name="Keyword Match" 
                  unit="%" 
                  domain={[50, 100]}
                  fontSize={11}
                  stroke="#9CA3AF"
                  tickLine={false}
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <YAxis 
                  type="number" 
                  dataKey="semantic" 
                  name="Semantic Sim" 
                  unit="%" 
                  domain={[60, 100]}
                  fontSize={11}
                  stroke="#9CA3AF"
                  tickLine={false}
                  axisLine={{ stroke: '#E7E9EE' }}
                />
                <ZAxis type="number" dataKey="experience" range={[50, 160]} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-border rounded-lg p-2.5 shadow-dropdown text-xs">
                          <div className="font-semibold text-primary">{data.name}</div>
                          <div className="text-[11px] text-secondary mt-1">
                            Semantic: <strong className="text-accent">{data.semantic}%</strong> • Keyword: <strong className="text-primary">{data.keyword}%</strong>
                          </div>
                          <div className="text-[11px] text-secondary">
                            Experience: <strong>{data.experience} yrs</strong> • Score: <strong className="text-success">{data.score}%</strong>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={scatterData}>
                  {scatterData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.score >= 85 ? '#16845B' : entry.score >= 75 ? '#4F46E5' : '#C58A29'} 
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-[11px] text-secondary pt-3 border-t border-border/60">
            <span>Quadrant Top-Right: Ideal Alignment</span>
            <span>Bubble size indicates documented seniority</span>
          </div>
        </div>
      )}

        {/* Right: Technical Explanation & Mathematical Architecture */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Scoring Methodology & Transparency
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              How TalentRank AI computes unbiased relevance scores
            </p>

            <div className="space-y-3 mt-4 text-xs">
              <div className="p-3 bg-[#FAFBFD] border border-border/80 rounded-lg">
                <div className="font-medium text-primary flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
                  1. Dense Bi-Encoder Embeddings (Sentence Transformers)
                </div>
                <p className="text-[11px] text-secondary mt-1 leading-relaxed">
                  Both the job description criteria and resume work histories are projected into 384-dimensional cosine space. This ensures candidates with synonymous experience (e.g., <em>"Kafka message queuing"</em> matching <em>"event streaming"</em>) receive fair evaluation regardless of exact phrasing.
                </p>
              </div>

              <div className="p-3 bg-[#FAFBFD] border border-border/80 rounded-lg">
                <div className="font-medium text-primary flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                  2. Sublinear TF-IDF / BM25 Term Weighting
                </div>
                <p className="text-[11px] text-secondary mt-1 leading-relaxed">
                  Extracts verified hard technical requirements (e.g. <em>Go</em>, <em>PostgreSQL</em>, <em>Kubernetes</em>). Employs sublinear scaling (1 + ln(tf)) to prevent keyword stuffing.
                </p>
              </div>

              <div className="p-3 bg-[#FAFBFD] border border-border/80 rounded-lg">
                <div className="font-medium text-primary flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-success"></span>
                  3. Calibrated Explainability Rationale
                </div>
                <p className="text-[11px] text-secondary mt-1 leading-relaxed">
                  Every candidate score generates a decomposed checklist of verified competencies, detected seniority offsets, and specific unverified requirements in plain English.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-border/60 text-[11px] text-secondary flex items-center gap-1">
            <Info className="w-3.5 h-3.5 text-secondary shrink-0" />
            <span>Zero protected demographic features are indexed or utilized in model parameters.</span>
          </div>
        </div>
      </div>

      {/* Simulated Ranking Table */}
      <div className="bg-card border border-border rounded-lg p-5 shadow-subtle">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-primary tracking-tight">
              Calibrated Ranking Output (Live Simulated Ranks)
            </h2>
            <p className="text-[11px] text-secondary mt-0.5">
              Rank order dynamically recalculated from current weight parameters
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-[#FAFBFD] text-[11px] text-secondary font-medium">
                <th className="py-2.5 px-3">Live Rank</th>
                <th className="py-2.5 px-3">Candidate</th>
                <th className="py-2.5 px-3">Semantic Sim</th>
                <th className="py-2.5 px-3">Keyword Fit</th>
                <th className="py-2.5 px-3">Experience</th>
                <th className="py-2.5 px-3 text-right">Simulated Score</th>
                <th className="py-2.5 px-3">Top Strength</th>
                <th className="py-2.5 px-3 text-right">Profile</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {simulatedCandidates.map((cand) => (
                <tr key={cand.id} className="hover:bg-[#F9FAFB] transition-colors">
                  <td className="py-2.5 px-3 font-mono font-bold text-primary">
                    #{cand.simulated_rank}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="font-medium text-primary block">
                      {blindScreening ? `Candidate #${cand.simulated_rank}` : cand.name}
                    </span>
                    <span className="text-[10px] text-secondary">{cand.title}</span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-accent">
                    {cand.semantic_score}%
                  </td>
                  <td className="py-2.5 px-3 font-mono text-primary">
                    {cand.keyword_score}%
                  </td>
                  <td className="py-2.5 px-3 font-mono text-secondary">
                    {cand.experience_years} yrs
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-bold">
                    <span className={
                      cand.simulated_score >= 85 ? 'text-success' :
                      cand.simulated_score >= 75 ? 'text-accent' : 'text-warning'
                    }>
                      {cand.simulated_score}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-secondary text-[11px] truncate max-w-[260px]">
                    {cand.explanation.strengths[0] || 'Matches primary requisites.'}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => onSelectCandidate(cand)}
                      className="text-xs text-accent font-medium hover:underline"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
