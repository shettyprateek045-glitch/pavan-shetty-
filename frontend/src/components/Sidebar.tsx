import React from 'react';
import { 
  LayoutDashboard, 
  SlidersHorizontal, 
  Users, 
  Cpu, 
  ShieldCheck, 
  BarChart2, 
  FileText, 
  Settings,
  Sparkles,
  ExternalLink,
  Box,
  LogOut,
  X
} from 'lucide-react';
import { NavigationTab } from '../types';

interface SidebarProps {
  activeTab: NavigationTab;
  setActiveTab: (tab: NavigationTab) => void;
  candidateCount: number;
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
  onSignOut?: () => void;
  user?: { name: string; email: string; role: string };
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  setActiveTab,
  candidateCount,
  isMobileOpen = false,
  onMobileClose,
  onSignOut,
  user
}) => {
  const navItems = [
    { id: 'overview' as NavigationTab, label: 'Overview', icon: LayoutDashboard },
    { id: 'screening' as NavigationTab, label: 'Screening', icon: SlidersHorizontal },
    { id: 'candidates' as NavigationTab, label: 'Candidates', icon: Users, badge: candidateCount },
    { id: '3d-space' as NavigationTab, label: '3D Talent Space', icon: Box, is3D: true },
    { id: 'ai-analysis' as NavigationTab, label: 'AI Analysis', icon: Cpu },
    { id: 'fairness' as NavigationTab, label: 'Fairness Audit', icon: ShieldCheck, isAudit: true },
    { id: 'analytics' as NavigationTab, label: 'Analytics', icon: BarChart2 },
    { id: 'reports' as NavigationTab, label: 'Reports', icon: FileText },
    { id: 'settings' as NavigationTab, label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div 
          onClick={onMobileClose}
          className="fixed inset-0 bg-navy-950/40 backdrop-blur-xs z-40 lg:hidden animate-in fade-in duration-150"
          aria-hidden="true"
        />
      )}

      {/* Main Sidebar (Drawer on mobile, fixed left on desktop) */}
      <aside 
        className={`w-64 bg-sidebar border-r border-border h-screen flex flex-col justify-between select-none shrink-0 z-50 transition-transform duration-200 ease-in-out fixed inset-y-0 left-0 lg:static lg:translate-x-0 ${
          isMobileOpen ? 'translate-x-0 shadow-drawer' : '-translate-x-full'
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="h-16 px-5 flex items-center justify-between border-b border-border">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-md bg-navy-900 border border-navy-800 flex items-center justify-center text-white font-semibold text-xs tracking-wider shadow-subtle">
                TR
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-sm tracking-tight text-primary leading-tight flex items-center gap-1.5">
                  TALENTRANK <span className="text-[10px] uppercase font-bold text-accent bg-accent/10 px-1 py-0.2 rounded border border-accent/20">AI</span>
                </span>
                <span className="text-[11px] text-secondary">Recruitment Intelligence</span>
              </div>
            </div>

            {/* Mobile Close Button */}
            {onMobileClose && (
              <button
                onClick={onMobileClose}
                className="lg:hidden text-secondary hover:text-primary p-1 rounded-md"
                aria-label="Close sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Navigation Section */}
          <div className="px-3 py-4">
            <div className="text-[11px] font-medium text-secondary uppercase tracking-wider px-3 mb-2">
              Workspace Navigation
            </div>
            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveTab(item.id);
                      if (onMobileClose) onMobileClose();
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 text-[13px] font-medium rounded-md transition-colors duration-150 ${
                      isActive
                        ? 'bg-accent text-white shadow-subtle'
                        : 'text-primary hover:bg-slate-50 hover:text-accent'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-secondary'}`} />
                      <span>{item.label}</span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      {item.badge !== undefined && (
                        <span className={`text-[11px] px-1.5 py-0.5 rounded font-mono ${
                          isActive ? 'bg-white/20 text-white' : 'bg-slate-100 text-secondary'
                        }`}>
                          {item.badge}
                        </span>
                      )}

                      {item.is3D && (
                        <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase tracking-wider font-mono ${
                          isActive ? 'bg-white text-accent' : 'bg-accent/10 text-accent border border-accent/20'
                        }`}>
                          3D
                        </span>
                      )}

                      {item.isAudit && !isActive && (
                        <span className="w-1.5 h-1.5 rounded-full bg-success"></span>
                      )}
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Bottom Section: Compliance + User Sign Out */}
        <div className="p-3 border-t border-border space-y-2">
          {/* Responsible AI Compliance Card */}
          <div className="bg-slate-50 border border-border rounded-lg p-3">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-success" />
                <span className="text-xs font-medium text-primary">EEOC / NYC LL144</span>
              </div>
              <span className="text-[10px] font-semibold text-success bg-success-light px-1.5 py-0.5 rounded border border-success-border">
                Certified
              </span>
            </div>
            <p className="text-[11px] text-secondary leading-snug mb-2">
              Disparate impact ratio: <strong className="text-primary font-mono">1.05</strong> (4/5ths compliant).
            </p>
            <button 
              onClick={() => {
                setActiveTab('fairness');
                if (onMobileClose) onMobileClose();
              }}
              className="text-[11px] text-accent font-medium hover:underline flex items-center gap-1"
            >
              Review audit certificates
              <ExternalLink className="w-2.5 h-2.5" />
            </button>
          </div>

          {/* User Sign Out Button */}
          {onSignOut && (
            <button
              onClick={onSignOut}
              className="w-full flex items-center justify-between px-3 py-2 text-xs font-medium text-secondary hover:text-danger hover:bg-danger-light rounded-md border border-border transition-colors"
            >
              <div className="flex items-center gap-2 truncate">
                <div className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                  {user?.name ? user.name.split(' ').map(n => n[0]).join('') : 'JD'}
                </div>
                <span className="truncate">{user?.name || 'Jordan Davis'}</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] shrink-0">
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </div>
            </button>
          )}
        </div>
      </aside>
    </>
  );
};
