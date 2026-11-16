import React, { useState } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  X, 
  AlertCircle, 
  Sliders, 
  Play, 
  Loader2, 
  Sparkles, 
  ShieldCheck,
  Plus,
  RefreshCw
} from 'lucide-react';
import { Job, ScoringWeights, Candidate, NavigationTab } from '../types';
import { runScreeningApi } from '../api';

interface ScreeningProps {
  activeJob: Job;
  setActiveJob: (job: Job) => void;
  jobs: Job[];
  onScreeningComplete: (results: {
    candidates: Candidate[];
    shortlisted_count: number;
    average_score: number;
  }) => void;
  setActiveTab: (tab: NavigationTab) => void;
}

interface UploadedFileItem {
  id: string;
  name: string;
  size: string;
  type: string;
  status: 'Ready' | 'Processing' | 'Parsed';
}

export const Screening: React.FC<ScreeningProps> = ({
  activeJob,
  setActiveJob,
  jobs,
  onScreeningComplete,
  setActiveTab
}) => {
  // Form State
  const [jobTitle, setJobTitle] = useState(activeJob.title);
  const [company, setCompany] = useState(activeJob.company);
  const [experienceRequired, setExperienceRequired] = useState(activeJob.experience_required);
  const [requiredSkills, setRequiredSkills] = useState<string[]>(activeJob.required_skills);
  const [newSkillInput, setNewSkillInput] = useState('');
  const [jobDescription, setJobDescription] = useState(activeJob.description);

  // Weights
  const [weights, setWeights] = useState<ScoringWeights>({
    keyword: 0.35,
    semantic: 0.45,
    experience: 0.20
  });

  // Uploaded Files State
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileItem[]>([
    { id: 'f-1', name: 'Elena_Rostova_Staff_Systems.pdf', size: '142 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-2', name: 'Marcus_Vance_Staff_Backend.pdf', size: '158 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-3', name: 'Zachary_Zhao_Platform_Architect.pdf', size: '180 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-4', name: 'Aisha_Kamara_Distributed_Systems.pdf', size: '135 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-5', name: 'Tariq_Mansoor_Senior_Backend.pdf', size: '124 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-6', name: 'Julian_Brooks_OpenSource_Systems.pdf', size: '112 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-7', name: 'Devin_Chen_Backend_Dev.docx', size: '98 KB', type: 'DOCX', status: 'Ready' },
    { id: 'f-8', name: 'Carlos_Mendez_Fintech_Backend.pdf', size: '118 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-9', name: 'Lucas_Weber_Systems_Engineer.pdf', size: '104 KB', type: 'PDF', status: 'Ready' },
    { id: 'f-10', name: 'Liam_OConnor_Backend_Developer.pdf', size: '95 KB', type: 'PDF', status: 'Ready' },
  ]);

  // Screening Stages & Execution State
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(-1);
  const [screeningResult, setScreeningResult] = useState<{
    shortlisted: number;
    avg: number;
    total: number;
  } | null>(null);

  const processingStages = [
    { name: 'Document Ingestion & Text Extraction', detail: 'Parsing text layers from PDF/DOCX multi-part streams' },
    { name: 'Entity Parsing & Technical Taxonomy Mapping', detail: 'Normalizing language tokens and synonym clusters' },
    { name: 'Dense Semantic Vectorization', detail: 'Evaluating contextual bi-encoder alignment with job criteria' },
    { name: 'Calibrated Ranking & Explainability Rationale', detail: 'Generating transparent strengths, gaps and composite scores' },
    { name: 'Responsible AI Demographic Pre-check', detail: 'Verifying blind evaluation & zero protected-attribute leakage' }
  ];

  // Add / Remove Skills
  const handleAddSkill = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    if (!newSkillInput.trim()) return;
    if (!requiredSkills.includes(newSkillInput.trim())) {
      setRequiredSkills([...requiredSkills, newSkillInput.trim()]);
    }
    setNewSkillInput('');
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setRequiredSkills(requiredSkills.filter(s => s !== skillToRemove));
  };

  // Drag & drop file handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    const newItems: UploadedFileItem[] = files.map((file, idx) => ({
      id: `up-${Date.now()}-${idx}`,
      name: file.name,
      size: `${(file.size / 1024).toFixed(0)} KB`,
      type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
      status: 'Ready'
    }));
    setUploadedFiles(prev => [...newItems, ...prev]);
  };

  const handleRemoveFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Preset Switcher
  const handleSelectJobPreset = (jobId: string) => {
    const found = jobs.find(j => j.id === jobId);
    if (found) {
      setActiveJob(found);
      setJobTitle(found.title);
      setCompany(found.company);
      setExperienceRequired(found.experience_required);
      setRequiredSkills(found.required_skills);
      setJobDescription(found.description);
    }
  };

  // Execute Screening
  const handleRunScreening = async () => {
    setIsProcessing(true);
    setCurrentStageIndex(0);
    setScreeningResult(null);

    // Subtle stage progression
    for (let i = 0; i < processingStages.length; i++) {
      setCurrentStageIndex(i);
      await new Promise(r => setTimeout(r, 450));
    }

    // Call API or calibrated local calculation
    const result = await runScreeningApi({
      job_id: activeJob.id,
      custom_job: {
        ...activeJob,
        title: jobTitle,
        company,
        experience_required: experienceRequired,
        required_skills: requiredSkills,
        description: jobDescription
      },
      weights
    });

    setIsProcessing(false);
    setCurrentStageIndex(-1);
    setScreeningResult({
      shortlisted: result.shortlisted_count,
      avg: result.average_score,
      total: result.total_screened
    });

    onScreeningComplete({
      candidates: result.candidates,
      shortlisted_count: result.shortlisted_count,
      average_score: result.average_score
    });
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-primary tracking-tight">
            Screening Workspace
          </h1>
          <p className="text-xs text-secondary mt-1">
            Configure job specifications, upload candidate resumes, and run multi-layer semantic matching.
          </p>
        </div>

        {/* Requisition Preset Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-secondary font-medium">Requisition Preset:</span>
          <select
            value={activeJob.id}
            onChange={(e) => handleSelectJobPreset(e.target.value)}
            className="text-xs bg-card border border-border rounded-md px-3 py-1.5 font-medium text-primary shadow-subtle focus:border-accent"
          >
            {jobs.map(j => (
              <option key={j.id} value={j.id}>{j.title}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Job Description Editor */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div>
                <h2 className="text-sm font-semibold text-primary tracking-tight">
                  Job Description & Criteria
                </h2>
                <p className="text-[11px] text-secondary mt-0.5">
                  Define technical requisites and role expectations
                </p>
              </div>
              <span className="text-[11px] font-medium text-success bg-success-light px-2 py-0.5 rounded border border-success-border flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                Linguistic Scan: Balanced
              </span>
            </div>

            {/* Title & Company */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-medium text-secondary mb-1">
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-border rounded-md px-3 py-2 text-primary focus:bg-white focus:border-accent transition-colors"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-secondary mb-1">
                  Company / Organization
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-border rounded-md px-3 py-2 text-primary focus:bg-white focus:border-accent transition-colors"
                />
              </div>
            </div>

            {/* Experience Requirements Slider */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-medium text-secondary">
                  Minimum Experience Threshold
                </label>
                <span className="font-mono text-xs font-semibold text-primary">
                  {experienceRequired} Years Required
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="12"
                step="1"
                value={experienceRequired}
                onChange={(e) => setExperienceRequired(Number(e.target.value))}
                className="w-full h-1.5 bg-[#E2E8F0] rounded-lg appearance-none cursor-pointer accent-accent"
              />
            </div>

            {/* Required Skills Tag Editor */}
            <div>
              <label className="block text-[11px] font-medium text-secondary mb-1.5">
                Required Technical Skills (Click tag to remove)
              </label>
              <div className="flex flex-wrap gap-1.5 p-2 bg-slate-50 border border-border rounded-md min-h-[44px]">
                {requiredSkills.map((skill) => (
                  <span
                    key={skill}
                    onClick={() => handleRemoveSkill(skill)}
                    className="inline-flex items-center gap-1 text-[11px] font-medium bg-card border border-border px-2 py-0.5 rounded text-primary hover:border-danger hover:text-danger cursor-pointer transition-colors"
                  >
                    <span>{skill}</span>
                    <X className="w-2.5 h-2.5" />
                  </span>
                ))}
                <div className="flex items-center gap-1 inline-flex">
                  <input
                    type="text"
                    placeholder="Add skill..."
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    onKeyDown={handleAddSkill}
                    className="text-[11px] bg-transparent outline-none border-none py-0.5 px-1 w-24 text-primary placeholder:text-secondary"
                  />
                  <button
                    onClick={handleAddSkill}
                    className="w-4 h-4 rounded-full bg-border/80 flex items-center justify-center text-secondary hover:text-primary"
                  >
                    <Plus className="w-2.5 h-2.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Full Job Description Textarea */}
            <div>
              <label className="block text-[11px] font-medium text-secondary mb-1">
                Full Job Description & Role Responsibilities
              </label>
              <textarea
                rows={7}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-border rounded-md p-3 text-primary focus:bg-white focus:border-accent transition-colors font-sans leading-relaxed resize-none"
              />
            </div>

            {/* Weight Allocation Control */}
            <div className="p-3 bg-[#FAFBFD] border border-border/80 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-semibold text-primary flex items-center gap-1.5">
                  <Sliders className="w-3.5 h-3.5 text-accent" />
                  Scoring Weight Distribution
                </span>
                <span className="text-[10px] text-secondary font-mono">100% Calibrated</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-white border border-border/80 p-2 rounded">
                  <div className="text-[10px] text-secondary">Semantic Weight</div>
                  <div className="font-mono font-semibold text-accent mt-0.5">{(weights.semantic * 100).toFixed(0)}%</div>
                </div>
                <div className="bg-white border border-border/80 p-2 rounded">
                  <div className="text-[10px] text-secondary">Keyword (TF-IDF)</div>
                  <div className="font-mono font-semibold text-primary mt-0.5">{(weights.keyword * 100).toFixed(0)}%</div>
                </div>
                <div className="bg-white border border-border/80 p-2 rounded">
                  <div className="text-[10px] text-secondary">Seniority Fit</div>
                  <div className="font-mono font-semibold text-primary mt-0.5">{(weights.experience * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Resume Upload & Pipeline Panel */}
        <div className="bg-card border border-border rounded-lg p-5 shadow-subtle flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <div>
                <h2 className="text-sm font-semibold text-primary tracking-tight">
                  Resume Batch Upload
                </h2>
                <p className="text-[11px] text-secondary mt-0.5">
                  Accepts PDF, DOCX, and TXT resumes for parsing
                </p>
              </div>
              <span className="text-xs font-mono font-medium text-secondary">
                {uploadedFiles.length} In Queue
              </span>
            </div>

            {/* Drag & Drop Dropzone */}
            <label className="border-2 border-dashed border-border hover:border-accent/60 bg-[#FAFBFD] hover:bg-[#F5F7FB] transition-all rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer group">
              <div className="w-10 h-10 rounded-full bg-white border border-border shadow-subtle flex items-center justify-center text-secondary group-hover:text-accent mb-2">
                <UploadCloud className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-primary group-hover:text-accent">
                Click to upload or drag resumes here
              </span>
              <span className="text-[11px] text-secondary mt-0.5">
                PDF, DOCX, or TXT (up to 25MB per file)
              </span>
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {/* Uploaded File List */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-medium text-secondary uppercase tracking-wider">
                  Indexed Resumes in Pipeline ({uploadedFiles.length})
                </span>
                <button
                  onClick={() => setUploadedFiles([
                    { id: 'f-1', name: 'Elena_Rostova_Staff_Systems.pdf', size: '142 KB', type: 'PDF', status: 'Ready' },
                    { id: 'f-2', name: 'Marcus_Vance_Staff_Backend.pdf', size: '158 KB', type: 'PDF', status: 'Ready' },
                    { id: 'f-3', name: 'Zachary_Zhao_Platform_Architect.pdf', size: '180 KB', type: 'PDF', status: 'Ready' },
                    { id: 'f-4', name: 'Aisha_Kamara_Distributed_Systems.pdf', size: '135 KB', type: 'PDF', status: 'Ready' },
                    { id: 'f-5', name: 'Tariq_Mansoor_Senior_Backend.pdf', size: '124 KB', type: 'PDF', status: 'Ready' },
                  ])}
                  className="text-[11px] text-secondary hover:text-primary flex items-center gap-1"
                >
                  <RefreshCw className="w-2.5 h-2.5" />
                  <span>Reset Synthetic Pool</span>
                </button>
              </div>

              <div className="max-h-60 overflow-y-auto space-y-1.5 pr-1">
                {uploadedFiles.map((f) => (
                  <div
                    key={f.id}
                    className="p-2 rounded-md border border-border/80 bg-[#FAFBFD] flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <div className="w-6 h-6 rounded bg-card border border-border flex items-center justify-center text-primary font-mono text-[10px] font-semibold shrink-0">
                        {f.type}
                      </div>
                      <div className="truncate">
                        <span className="font-medium text-primary text-xs truncate block">{f.name}</span>
                        <span className="text-[10px] text-secondary font-mono">{f.size}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-[10px] font-medium text-secondary bg-card border border-border px-1.5 py-0.2 rounded font-mono">
                        {f.status}
                      </span>
                      <button
                        onClick={() => handleRemoveFile(f.id)}
                        className="text-secondary hover:text-danger p-0.5 rounded transition-colors"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Primary Action Section */}
          <div className="pt-3 border-t border-border/80">
            {isProcessing ? (
              <div className="space-y-3 bg-[#FAFBFD] p-4 rounded-lg border border-border">
                <div className="flex items-center justify-between text-xs font-medium text-primary">
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-accent" />
                    <span>Processing Stage {currentStageIndex + 1} of {processingStages.length}</span>
                  </span>
                  <span className="text-[11px] font-mono text-secondary">
                    {Math.round(((currentStageIndex + 1) / processingStages.length) * 100)}%
                  </span>
                </div>

                {/* Subtle progress bar */}
                <div className="w-full h-1.5 bg-[#E7E9EE] rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-accent transition-all duration-300"
                    style={{ width: `${((currentStageIndex + 1) / processingStages.length) * 100}%` }}
                  ></div>
                </div>

                <div className="text-xs text-primary font-medium">
                  {processingStages[currentStageIndex]?.name}
                </div>
                <div className="text-[11px] text-secondary">
                  {processingStages[currentStageIndex]?.detail}
                </div>
              </div>
            ) : screeningResult ? (
              <div className="p-4 bg-success-light border border-success-border rounded-lg space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-success">
                    <CheckCircle className="w-4 h-4" />
                    <span>Screening Completed Successfully</span>
                  </div>
                  <span className="text-[11px] text-secondary font-mono">{screeningResult.total} Resumes Scored</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white/80 p-2 rounded border border-success-border/60">
                    <span className="text-[10px] text-secondary">Shortlisted (≥80%)</span>
                    <div className="font-mono font-bold text-success text-sm">{screeningResult.shortlisted} Candidates</div>
                  </div>
                  <div className="bg-white/80 p-2 rounded border border-success-border/60">
                    <span className="text-[10px] text-secondary">Pool Average Relevance</span>
                    <div className="font-mono font-bold text-primary text-sm">{screeningResult.avg}%</div>
                  </div>
                </div>

                <button
                  onClick={() => setActiveTab('candidates')}
                  className="w-full py-2 bg-success text-white rounded-md text-xs font-medium hover:bg-emerald-700 transition-colors shadow-subtle flex items-center justify-center gap-1.5"
                >
                  <span>Review Ranked Candidates</span>
                </button>
              </div>
            ) : (
              <button
                onClick={handleRunScreening}
                className="w-full py-2.5 bg-accent hover:bg-accent-hover text-white rounded-md text-xs font-medium transition-colors shadow-subtle flex items-center justify-center gap-2"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Run Screening ({uploadedFiles.length} Resumes)</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
