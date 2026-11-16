import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  ChevronDown, 
  Check, 
  Briefcase, 
  Sparkles, 
  Menu, 
  LogOut, 
  User as UserIcon,
  ShieldCheck
} from 'lucide-react';
import { NavigationTab, Job } from '../types';

interface NavbarProps {
  activeTab: NavigationTab;
  jobs: Job[];
  activeJob: Job;
  setActiveJob: (job: Job) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  blindScreening: boolean;
  setBlindScreening: (val: boolean) => void;
  onMobileMenuToggle?: () => void;
  onSignOut?: () => void;
  user?: { name: string; email: string; role: string };
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  jobs,
  activeJob,
  setActiveJob,
  searchQuery,
  setSearchQuery,
  blindScreening,
  setBlindScreening,
  onMobileMenuToggle,
  onSignOut,
  user
}) => {
  const [jobDropdownOpen, setJobDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  // Tab titles
  const tabTitles: Record<NavigationTab, { title: string; subtitle: string }> = {
    overview: { title: 'Hiring Overview', subtitle: 'Platform telemetry & recruitment performance' },
    screening: { title: 'Screening Workspace', subtitle: 'Resume ingestion, embedding & ranking' },
    candidates: { title: 'Candidate Management', subtitle: 'Ranked candidate pipeline & profiles' },
    '3d-space': { title: '3D Talent Vector Space', subtitle: 'Interactive WebGL spatial constellation with cursor motion' },
    'ai-analysis': { title: 'AI Explainability & Analysis', subtitle: 'Algorithmic transparency & weight simulation' },
    fairness: { title: 'Responsible AI & Fairness Audit', subtitle: 'Demographic parity & EEOC compliance' },
    analytics: { title: 'Talent Analytics', subtitle: 'Pipeline velocity & score distributions' },
    reports: { title: 'Executive Reports', subtitle: 'Audited hiring summaries & exportable dossiers' },
    settings: { title: 'Platform Settings', subtitle: 'Scoring calibrations, thresholding & API access' },
  };

  const currentTabInfo = tabTitles[activeTab] || tabTitles.overview;

  return (
    <header className="h-16 bg-card border-b border-border px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Mobile Hamburger & Page Title */}
      <div className="flex items-center gap-3">
        {onMobileMenuToggle && (
          <button
            onClick={onMobileMenuToggle}
            className="lg:hidden p-1.5 -ml-1.5 text-secondary hover:text-primary rounded-md hover:bg-slate-100 transition-colors"
            aria-label="Open mobile navigation"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="hidden sm:flex items-center text-xs text-secondary gap-1.5 font-medium">
          <span>TalentRank</span>
          <span>/</span>
          <span className="text-primary capitalize">{activeTab.replace('-', ' ')}</span>
        </div>
        <div className="hidden sm:block h-4 w-px bg-border mx-1"></div>
        <div className="text-sm font-semibold text-primary truncate max-w-[200px] sm:max-w-none">
          {currentTabInfo.title}
        </div>
      </div>

      {/* Center/Right Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Active Job Context Selector */}
        <div className="relative">
          <button
            onClick={() => {
              setJobDropdownOpen(!jobDropdownOpen);
              setNotificationsOpen(false);
              setProfileDropdownOpen(false);
            }}
            className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-primary bg-slate-50 hover:bg-slate-100 border border-border rounded-md transition-colors"
          >
            <Briefcase className="w-3.5 h-3.5 text-accent" />
            <span className="max-w-[120px] sm:max-w-[180px] truncate">{activeJob?.title || 'Select Role'}</span>
            <ChevronDown className="w-3 h-3 text-secondary shrink-0" />
          </button>

          {jobDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-72 bg-card border border-border rounded-lg shadow-dropdown p-1.5 z-30 animate-in fade-in duration-100">
              <div className="text-[10px] font-semibold text-secondary uppercase px-2 py-1">
                Active Job Requisition
              </div>
              <div className="space-y-0.5">
                {jobs.map((job) => {
                  const isSelected = job.id === activeJob?.id;
                  return (
                    <button
                      key={job.id}
                      onClick={() => {
                        setActiveJob(job);
                        setJobDropdownOpen(false);
                      }}
                      className={`w-full text-left px-2 py-1.5 rounded-md text-xs flex items-start justify-between ${
                        isSelected ? 'bg-accent/10 text-accent font-medium' : 'text-primary hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex flex-col pr-2">
                        <span className="truncate">{job.title}</span>
                        <span className="text-[10px] text-secondary">{job.department} • {job.experience_required}+ yrs</span>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-accent shrink-0 mt-0.5" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Global Search Bar (hidden on small mobile screens to prevent clutter) */}
        <div className="relative w-44 md:w-60 hidden md:block">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-secondary" />
          <input
            type="text"
            placeholder="Search candidates, skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-md pl-8 pr-3 py-1.5 text-xs text-primary placeholder:text-secondary focus:bg-white focus:border-accent transition-colors"
          />
        </div>

        {/* Blind Screening Toggle Pill */}
        <button
          onClick={() => setBlindScreening(!blindScreening)}
          title="Mask candidate names, universities, and photos to prevent unconscious bias"
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-md border transition-colors ${
            blindScreening
              ? 'bg-accent/10 border-accent/40 text-accent'
              : 'bg-card border-border text-secondary hover:text-primary hover:bg-slate-50'
          }`}
        >
          <Sparkles className="w-3 h-3 text-accent" />
          <span>Blind Mode {blindScreening ? 'On' : 'Off'}</span>
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => {
              setNotificationsOpen(!notificationsOpen);
              setJobDropdownOpen(false);
              setProfileDropdownOpen(false);
            }}
            className="w-8 h-8 rounded-md border border-border flex items-center justify-center text-secondary hover:text-primary hover:bg-slate-50 transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-accent ring-2 ring-card"></span>
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 mt-1.5 w-80 bg-card border border-border rounded-lg shadow-dropdown p-3 z-30 animate-in fade-in duration-100">
              <div className="flex items-center justify-between pb-2 border-b border-border mb-2">
                <span className="text-xs font-semibold text-primary">System Notifications</span>
                <span className="text-[10px] text-accent font-medium">3 unread</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-2 rounded bg-slate-50 border border-border/80">
                  <div className="font-medium text-primary text-[11px] flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-success" />
                    <span>Fairness Audit Passed</span>
                  </div>
                  <div className="text-[11px] text-secondary mt-0.5">Demographic parity confirmed across active cohort (DIR 1.05).</div>
                  <div className="text-[10px] text-secondary-muted mt-1">12 mins ago</div>
                </div>
                <div className="p-2 rounded hover:bg-slate-50 transition-colors">
                  <div className="font-medium text-primary text-[11px]">Qualified Candidate Match</div>
                  <div className="text-[11px] text-secondary mt-0.5">Elena Rostova scored 95.8% relevance fit for Staff Backend.</div>
                  <div className="text-[10px] text-secondary-muted mt-1">45 mins ago</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile & Logout Dropdown */}
        <div className="relative pl-1 sm:pl-2 border-l border-border">
          <button
            onClick={() => {
              setProfileDropdownOpen(!profileDropdownOpen);
              setJobDropdownOpen(false);
              setNotificationsOpen(false);
            }}
            className="flex items-center gap-2 p-1 rounded-md hover:bg-slate-50 transition-colors"
            aria-label="User profile menu"
          >
            <div className="w-7 h-7 rounded-full bg-accent/10 border border-accent/30 flex items-center justify-center text-accent font-semibold text-xs">
              {user?.name ? user.name.split(' ').map(n => n[0]).join('') : 'JD'}
            </div>
            <div className="hidden md:flex flex-col text-left">
              <span className="text-xs font-medium text-primary leading-tight">{user?.name || 'Jordan Davis'}</span>
              <span className="text-[10px] text-secondary leading-tight">{user?.role || 'Lead Recruiter'}</span>
            </div>
            <ChevronDown className="w-3 h-3 text-secondary hidden sm:block" />
          </button>

          {profileDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-56 bg-card border border-border rounded-lg shadow-dropdown p-1.5 z-30 animate-in fade-in duration-100">
              <div className="px-3 py-2 border-b border-border mb-1">
                <div className="text-xs font-semibold text-primary">{user?.name || 'Jordan Davis'}</div>
                <div className="text-[11px] text-secondary truncate">{user?.email || 'recruiter@talentrank.ai'}</div>
                <div className="text-[10px] text-accent font-medium mt-0.5">{user?.role || 'Lead Technical Recruiter'}</div>
              </div>

              <div className="space-y-0.5">
                <button
                  onClick={() => {
                    setBlindScreening(!blindScreening);
                    setProfileDropdownOpen(false);
                  }}
                  className="w-full text-left px-3 py-1.5 rounded-md text-xs text-primary hover:bg-slate-50 flex items-center justify-between"
                >
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-accent" />
                    <span>Blind Screening</span>
                  </span>
                  <span className="text-[10px] font-mono font-medium text-accent">
                    {blindScreening ? 'Active' : 'Off'}
                  </span>
                </button>

                {onSignOut && (
                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                      onSignOut();
                    }}
                    className="w-full text-left px-3 py-1.5 rounded-md text-xs text-danger hover:bg-danger-light flex items-center gap-2 transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
