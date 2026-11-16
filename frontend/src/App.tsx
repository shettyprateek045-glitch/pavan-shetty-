import React, { useState, useEffect } from 'react';
import { NavigationTab, Job, Candidate, AnalyticsData, FairnessBenchmark } from './types';
import { fetchJobs, fetchCandidates, fetchAnalyticsData, fetchFairnessAudit } from './api';
import { INITIAL_JOBS, INITIAL_CANDIDATES, INITIAL_FAIRNESS } from './mockData';

import { Login } from './components/Login';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { Overview } from './components/Overview';
import { Screening } from './components/Screening';
import { Candidates } from './components/Candidates';
import { CandidateDrawer } from './components/CandidateDrawer';
import { CandidateCompareModal } from './components/CandidateCompareModal';
import { AiAnalysis } from './components/AiAnalysis';
import { ThreeCanvasView } from './components/ThreeCanvasView';
import { FairnessAudit } from './components/FairnessAudit';
import { Analytics } from './components/Analytics';
import { Reports } from './components/Reports';
import { Settings } from './components/Settings';

export const App: React.FC = () => {
  // Authentication State (App opens directly to Login unless session exists)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    try {
      const session = sessionStorage.getItem('talentrank_auth_session');
      if (session) {
        const parsed = JSON.parse(session);
        return Boolean(parsed.authenticated);
      }
    } catch {
      // Ignore
    }
    return false;
  });

  const [currentUser, setCurrentUser] = useState<{ name: string; email: string; role: string }>(() => {
    try {
      const session = sessionStorage.getItem('talentrank_auth_session');
      if (session) {
        const parsed = JSON.parse(session);
        if (parsed.user) return parsed.user;
      }
    } catch {
      // Ignore
    }
    return {
      name: 'Jordan Davis',
      email: 'recruiter@talentrank.ai',
      role: 'Lead Technical Recruiter',
    };
  });

  // Mobile Navigation Drawer State
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Navigation & Active Context
  const [activeTab, setActiveTab] = useState<NavigationTab>('overview');
  const [jobs, setJobs] = useState<Job[]>(INITIAL_JOBS);
  const [activeJob, setActiveJob] = useState<Job>(INITIAL_JOBS[0]);
  const [candidates, setCandidates] = useState<Candidate[]>(INITIAL_CANDIDATES);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [fairnessData, setFairnessData] = useState<{ benchmark: FairnessBenchmark }>(INITIAL_FAIRNESS);

  // Modals & Panels
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [compareList, setCompareList] = useState<Candidate[]>([]);
  const [blindScreening, setBlindScreening] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Initial Load & Job Sync
  useEffect(() => {
    if (!isAuthenticated) return;
    async function loadInitial() {
      const loadedJobs = await fetchJobs();
      setJobs(loadedJobs);
      if (loadedJobs.length > 0 && !activeJob) {
        setActiveJob(loadedJobs[0]);
      }
      const loadedAnalytics = await fetchAnalyticsData(activeJob?.id || 'job-lead-backend');
      setAnalytics(loadedAnalytics);
      const loadedCandidates = await fetchCandidates(activeJob?.id || 'job-lead-backend');
      setCandidates(loadedCandidates);
      const loadedFairness = await fetchFairnessAudit();
      setFairnessData(loadedFairness);
    }
    loadInitial();
  }, [isAuthenticated]);

  // When activeJob changes, reload candidate list and analytics
  const handleSelectActiveJob = async (job: Job) => {
    setActiveJob(job);
    const updatedCandidates = await fetchCandidates(job.id);
    setCandidates(updatedCandidates);
    const updatedAnalytics = await fetchAnalyticsData(job.id);
    setAnalytics(updatedAnalytics);
  };

  // Update candidate status
  const handleUpdateCandidateStatus = (candidateId: string, newStatus: Candidate['status']) => {
    setCandidates((prev) =>
      prev.map((c) => (c.id === candidateId ? { ...c, status: newStatus } : c))
    );
    if (selectedCandidate && selectedCandidate.id === candidateId) {
      setSelectedCandidate((prev) => (prev ? { ...prev, status: newStatus } : null));
    }
  };

  // Screening complete callback
  const handleScreeningComplete = (results: {
    candidates: Candidate[];
    shortlisted_count: number;
    average_score: number;
  }) => {
    setCandidates(results.candidates);
  };

  // Handle successful login
  const handleLoginSuccess = (user: { name: string; email: string; role: string }) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  // Handle sign out
  const handleSignOut = () => {
    sessionStorage.removeItem('talentrank_auth_session');
    setIsAuthenticated(false);
  };

  // Direct login screen if unauthenticated
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Authenticated Recruitment Dashboard
  return (
    <div className="min-h-screen bg-background flex flex-row font-sans text-primary antialiased">
      {/* Left Sidebar (Desktop static, Mobile drawer) */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        candidateCount={candidates.length}
        isMobileOpen={isMobileSidebarOpen}
        onMobileClose={() => setIsMobileSidebarOpen(false)}
        onSignOut={handleSignOut}
        user={currentUser}
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Top Navigation */}
        <Navbar
          activeTab={activeTab}
          jobs={jobs}
          activeJob={activeJob}
          setActiveJob={handleSelectActiveJob}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          blindScreening={blindScreening}
          setBlindScreening={setBlindScreening}
          onMobileMenuToggle={() => setIsMobileSidebarOpen(true)}
          onSignOut={handleSignOut}
          user={currentUser}
        />

        {/* Tab Content Area */}
        <main className="flex-1 p-4 sm:p-6 md:p-8 overflow-y-auto">
          {activeTab === 'overview' && analytics && (
            <Overview
              analytics={analytics}
              candidates={candidates}
              setActiveTab={setActiveTab}
              onSelectCandidate={(cand) => setSelectedCandidate(cand)}
              blindScreening={blindScreening}
            />
          )}

          {activeTab === 'screening' && (
            <Screening
              activeJob={activeJob}
              setActiveJob={setActiveJob}
              jobs={jobs}
              onScreeningComplete={handleScreeningComplete}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'candidates' && (
            <Candidates
              candidates={candidates}
              activeJob={activeJob}
              onSelectCandidate={(cand) => setSelectedCandidate(cand)}
              onCompareCandidates={(cands) => setCompareList(cands)}
              blindScreening={blindScreening}
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
            />
          )}

          {activeTab === '3d-space' && (
            <div className="space-y-4 max-w-7xl mx-auto pb-12">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h1 className="text-xl font-semibold text-primary tracking-tight">
                    3D Talent Vector Space
                  </h1>
                  <p className="text-xs text-secondary mt-1">
                    Real-time WebGL spatial vector embedding constellation. Tilt and rotate camera with cursor motion.
                  </p>
                </div>
              </div>

              <ThreeCanvasView
                candidates={candidates}
                activeJob={activeJob}
                onSelectCandidate={(cand) => setSelectedCandidate(cand)}
                blindScreening={blindScreening}
              />
            </div>
          )}

          {activeTab === 'ai-analysis' && (
            <AiAnalysis
              candidates={candidates}
              activeJob={activeJob}
              onSelectCandidate={(cand) => setSelectedCandidate(cand)}
              blindScreening={blindScreening}
            />
          )}

          {activeTab === 'fairness' && (
            <FairnessAudit
              fairnessData={fairnessData}
              activeJob={activeJob}
            />
          )}

          {activeTab === 'analytics' && (
            <Analytics
              candidates={candidates}
              activeJob={activeJob}
            />
          )}

          {activeTab === 'reports' && (
            <Reports
              candidates={candidates}
              activeJob={activeJob}
              blindScreening={blindScreening}
            />
          )}

          {activeTab === 'settings' && (
            <Settings
              blindScreening={blindScreening}
              setBlindScreening={setBlindScreening}
            />
          )}
        </main>
      </div>

      {/* Candidate Profile Slide-over Drawer */}
      <CandidateDrawer
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        onUpdateStatus={handleUpdateCandidateStatus}
        blindScreening={blindScreening}
      />

      {/* Candidate Head-to-Head Compare Modal */}
      {compareList.length > 0 && (
        <CandidateCompareModal
          candidates={compareList}
          activeJob={activeJob}
          onClose={() => setCompareList([])}
          blindScreening={blindScreening}
        />
      )}
    </div>
  );
};

export default App;
