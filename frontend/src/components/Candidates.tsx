import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  Download, 
  ChevronLeft, 
  ChevronRight, 
  SlidersHorizontal,
  CheckCircle2, 
  Clock, 
  AlertCircle,
  Eye,
  Layers,
  Scale
} from 'lucide-react';
import { Candidate, Job } from '../types';

interface CandidatesProps {
  candidates: Candidate[];
  activeJob: Job;
  onSelectCandidate: (candidate: Candidate) => void;
  onCompareCandidates: (candidates: Candidate[]) => void;
  blindScreening: boolean;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}

export const Candidates: React.FC<CandidatesProps> = ({
  candidates,
  activeJob,
  onSelectCandidate,
  onCompareCandidates,
  blindScreening,
  searchQuery,
  setSearchQuery
}) => {
  // Filter States
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [minScoreFilter, setMinScoreFilter] = useState<number>(0);
  const [expFilter, setExpFilter] = useState<number>(0);

  // Sorting State
  const [sortBy, setSortBy] = useState<'overall' | 'semantic' | 'keyword' | 'experience' | 'name'>('overall');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Multi-selection for comparison
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Pagination
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 8;

  // Toggle selection
  const handleToggleSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedIds.length === candidates.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(candidates.map(c => c.id));
    }
  };

  // Filter & Sort Logic
  const filteredAndSortedCandidates = useMemo(() => {
    return candidates
      .filter((cand) => {
        // Search text
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchesName = cand.name.toLowerCase().includes(q);
          const matchesTitle = cand.title.toLowerCase().includes(q);
          const matchesCompany = cand.current_company.toLowerCase().includes(q);
          const matchesSkill = cand.skills.some(s => s.toLowerCase().includes(q));
          if (!matchesName && !matchesTitle && !matchesCompany && !matchesSkill) return false;
        }

        // Status filter
        if (statusFilter !== 'All' && cand.status !== statusFilter) {
          return false;
        }

        // Min score
        if (cand.overall_score < minScoreFilter) {
          return false;
        }

        // Experience
        if (cand.experience_years < expFilter) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        let diff = 0;
        if (sortBy === 'overall') diff = a.overall_score - b.overall_score;
        else if (sortBy === 'semantic') diff = a.semantic_score - b.semantic_score;
        else if (sortBy === 'keyword') diff = a.keyword_score - b.keyword_score;
        else if (sortBy === 'experience') diff = a.experience_years - b.experience_years;
        else if (sortBy === 'name') diff = a.name.localeCompare(b.name);

        return sortDirection === 'desc' ? -diff : diff;
      });
  }, [candidates, searchQuery, statusFilter, minScoreFilter, expFilter, sortBy, sortDirection]);

  // Paginated slice
  const totalPages = Math.ceil(filteredAndSortedCandidates.length / pageSize) || 1;
  const paginatedCandidates = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSortedCandidates.slice(start, start + pageSize);
  }, [filteredAndSortedCandidates, currentPage, pageSize]);

  // Export CSV
  const handleExportCSV = () => {
    const headers = [
      'Rank',
      'Name',
      'Email',
      'Title',
      'Company',
      'Experience (Years)',
      'Overall Score (%)',
      'Semantic Score (%)',
      'Keyword Score (%)',
      'Status',
      'Matched Skills',
      'Missing Skills'
    ];

    const rows = filteredAndSortedCandidates.map((c, idx) => [
      c.rank || idx + 1,
      `"${c.name}"`,
      `"${c.email}"`,
      `"${c.title}"`,
      `"${c.current_company}"`,
      c.experience_years,
      c.overall_score,
      c.semantic_score,
      c.keyword_score,
      `"${c.status}"`,
      `"${c.matched_skills.join(', ')}"`,
      `"${c.missing_skills.join(', ')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `TalentRank_Candidates_${activeJob.id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Trigger compare modal
  const handleCompareClick = () => {
    const selected = candidates.filter(c => selectedIds.includes(c.id));
    onCompareCandidates(selected);
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto pb-12">
      {/* Header & Requisition Info */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold text-primary tracking-tight">
              Candidate Management
            </h1>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/10 text-primary font-medium">
              {filteredAndSortedCandidates.length} Evaluated
            </span>
          </div>
          <p className="text-xs text-secondary mt-1">
            Requisition: <strong className="text-primary">{activeJob.title}</strong> ({activeJob.experience_required}+ yrs required)
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Compare Button */}
          {selectedIds.length >= 2 && selectedIds.length <= 4 && (
            <button
              onClick={handleCompareClick}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-accent text-white rounded-md text-xs font-medium shadow-subtle hover:bg-accent-hover transition-colors"
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Compare Selected ({selectedIds.length})</span>
            </button>
          )}

          {/* Export CSV Button */}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-card border border-border text-primary rounded-md text-xs font-medium hover:bg-[#F2F4F7] transition-colors shadow-subtle"
          >
            <Download className="w-3.5 h-3.5 text-secondary" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Control Bar */}
      <div className="bg-card border border-border rounded-lg p-3 shadow-subtle flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative min-w-[240px] flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-secondary" />
          <input
            type="text"
            placeholder="Search by name, title, skill or company..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs bg-slate-50 border border-border rounded-md pl-8 pr-3 py-1.5 text-primary placeholder:text-secondary focus:bg-white focus:border-accent transition-colors"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-md border border-border/80">
            {['All', 'Shortlisted', 'Review', 'Under Review'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`text-[11px] font-medium px-2.5 py-1 rounded transition-colors ${
                  statusFilter === status
                    ? 'bg-card text-accent shadow-subtle font-semibold'
                    : 'text-secondary hover:text-primary'
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          {/* Min Score Dropdown */}
          <select
            value={minScoreFilter}
            onChange={(e) => setMinScoreFilter(Number(e.target.value))}
            className="text-xs bg-slate-50 border border-border rounded-md px-2.5 py-1.5 text-secondary hover:text-primary font-medium"
          >
            <option value="0">All Scores</option>
            <option value="80">≥ 80% (Qualified)</option>
            <option value="90">≥ 90% (Top Tier)</option>
          </select>

          {/* Experience Dropdown */}
          <select
            value={expFilter}
            onChange={(e) => setExpFilter(Number(e.target.value))}
            className="text-xs bg-slate-50 border border-border rounded-md px-2.5 py-1.5 text-secondary hover:text-primary font-medium"
          >
            <option value="0">All Seniority</option>
            <option value="5">≥ 5 Years Exp</option>
            <option value="7">≥ 7 Years Exp</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-card border border-border rounded-lg shadow-subtle overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-[#FAFBFD] text-[11px] font-medium text-secondary">
                <th className="py-3 px-3 w-8">
                  <input
                    type="checkbox"
                    checked={selectedIds.length === candidates.length && candidates.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-border text-accent focus:ring-accent w-3.5 h-3.5"
                  />
                </th>
                <th className="py-3 px-3">
                  <button 
                    onClick={() => {
                      if (sortBy === 'overall') setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                      else { setSortBy('overall'); setSortDirection('desc'); }
                    }}
                    className="flex items-center gap-1 hover:text-primary font-medium"
                  >
                    <span>Rank & Candidate</span>
                    <ArrowUpDown className="w-3 h-3 text-secondary" />
                  </button>
                </th>
                <th className="py-3 px-3">Skills Alignment</th>
                <th className="py-3 px-3">
                  <button 
                    onClick={() => {
                      if (sortBy === 'experience') setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                      else { setSortBy('experience'); setSortDirection('desc'); }
                    }}
                    className="flex items-center gap-1 hover:text-primary font-medium"
                  >
                    <span>Experience</span>
                    <ArrowUpDown className="w-3 h-3 text-secondary" />
                  </button>
                </th>
                <th className="py-3 px-3 text-right">
                  <button 
                    onClick={() => {
                      if (sortBy === 'keyword') setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                      else { setSortBy('keyword'); setSortDirection('desc'); }
                    }}
                    className="flex items-center gap-1 hover:text-primary font-medium ml-auto"
                  >
                    <span>Keyword (TF-IDF)</span>
                    <ArrowUpDown className="w-3 h-3 text-secondary" />
                  </button>
                </th>
                <th className="py-3 px-3 text-right">
                  <button 
                    onClick={() => {
                      if (sortBy === 'semantic') setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                      else { setSortBy('semantic'); setSortDirection('desc'); }
                    }}
                    className="flex items-center gap-1 hover:text-primary font-medium ml-auto"
                  >
                    <span>Semantic Sim</span>
                    <ArrowUpDown className="w-3 h-3 text-secondary" />
                  </button>
                </th>
                <th className="py-3 px-3 text-right font-medium">Overall Fit</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {paginatedCandidates.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-secondary">
                    No candidates matched the specified filter criteria.
                  </td>
                </tr>
              ) : (
                paginatedCandidates.map((cand, idx) => {
                  const isSelected = selectedIds.includes(cand.id);
                  const name = blindScreening ? `Candidate #${cand.rank || idx + 1}` : cand.name;
                  const company = blindScreening ? 'Enterprise Tech' : cand.current_company;

                  return (
                    <tr
                      key={cand.id}
                      onClick={() => onSelectCandidate(cand)}
                      className={`hover:bg-[#F9FAFB] cursor-pointer transition-colors ${
                        isSelected ? 'bg-accent/5' : ''
                      }`}
                    >
                      {/* Checkbox */}
                      <td className="py-3 px-3" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={(e) => handleToggleSelect(cand.id, e as any)}
                          className="rounded border-border text-accent focus:ring-accent w-3.5 h-3.5"
                        />
                      </td>

                      {/* Rank & Candidate */}
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-2.5">
                          <span className="w-5 h-5 rounded bg-[#F4F5F7] border border-border flex items-center justify-center font-mono text-[10px] font-bold text-primary shrink-0">
                            {cand.rank || idx + 1}
                          </span>
                          <div>
                            <span className="font-medium text-xs text-primary block leading-tight hover:text-accent">
                              {name}
                            </span>
                            <span className="text-[11px] text-secondary truncate block max-w-[170px]">
                              {cand.title} • {company}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Skills */}
                      <td className="py-3 px-3 max-w-[220px]">
                        <div className="flex flex-wrap gap-1">
                          {cand.matched_skills.slice(0, 3).map((skill) => (
                            <span
                              key={skill}
                              className="text-[10px] font-mono bg-[#F2F4F7] text-secondary px-1.5 py-0.2 rounded"
                            >
                              {skill}
                            </span>
                          ))}
                          {cand.matched_skills.length > 3 && (
                            <span className="text-[10px] font-mono text-secondary px-1 py-0.2">
                              +{cand.matched_skills.length - 3}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Experience */}
                      <td className="py-3 px-3">
                        <span className="font-mono text-xs text-primary font-medium">
                          {cand.experience_years} yrs
                        </span>
                      </td>

                      {/* Keyword Score */}
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-12 h-1 bg-[#E7E9EE] rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-primary" 
                              style={{ width: `${cand.keyword_score}%` }}
                            ></div>
                          </div>
                          <span className="font-mono text-[11px] text-primary w-8">
                            {cand.keyword_score}%
                          </span>
                        </div>
                      </td>

                      {/* Semantic Score */}
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-12 h-1 bg-[#E7E9EE] rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-accent" 
                              style={{ width: `${cand.semantic_score}%` }}
                            ></div>
                          </div>
                          <span className="font-mono text-[11px] text-accent font-medium w-8">
                            {cand.semantic_score}%
                          </span>
                        </div>
                      </td>

                      {/* Overall Fit */}
                      <td className="py-3 px-3 text-right font-mono font-bold">
                        <span className={
                          cand.overall_score >= 85 ? 'text-success' :
                          cand.overall_score >= 75 ? 'text-accent' : 'text-warning'
                        }>
                          {cand.overall_score}%
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-medium font-sans ${
                          cand.status === 'Shortlisted' ? 'bg-success-light text-success border border-success-border' :
                          cand.status === 'Review' ? 'bg-accent/10 text-accent border border-accent/20' :
                          'bg-[#F2F4F7] text-secondary'
                        }`}>
                          {cand.status}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCandidate(cand);
                          }}
                          className="p-1 rounded text-secondary hover:text-primary hover:bg-[#F2F4F7] transition-colors"
                          title="Inspect candidate analysis"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-4 py-3 border-t border-border bg-[#FAFBFD] flex items-center justify-between text-xs text-secondary">
          <div>
            Showing <strong className="text-primary font-mono">{paginatedCandidates.length}</strong> of{' '}
            <strong className="text-primary font-mono">{filteredAndSortedCandidates.length}</strong> candidates
          </div>

          <div className="flex items-center gap-1.5">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              className="px-2 py-1 border border-border rounded bg-card disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#F2F4F7] text-primary"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-xs text-primary px-2">
              {currentPage} / {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              className="px-2 py-1 border border-border rounded bg-card disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#F2F4F7] text-primary"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
