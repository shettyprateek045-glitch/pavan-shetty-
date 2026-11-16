import React, { useState } from 'react';
import { 
  Lock, 
  Mail, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  ShieldCheck, 
  AlertCircle, 
  Loader2, 
  Info,
  X
} from 'lucide-react';
import { loginApi } from '../api';

interface LoginProps {
  onLoginSuccess: (user: { name: string; email: string; role: string }) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  // Saved email from 'Remember me'
  const savedEmail = localStorage.getItem('talentrank_remembered_email') || '';
  const [email, setEmail] = useState(savedEmail);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(Boolean(savedEmail));

  // Validation & Submission States
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [generalError, setGeneralError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Password recovery is not configured by the demo backend.
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  const validate = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');
    setGeneralError('');

    const emailTrimmed = email.trim();
    if (!emailTrimmed) {
      setEmailError('Email address is required.');
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailTrimmed)) {
      setEmailError('Please enter a valid work email address (e.g. name@company.com).');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required.');
      isValid = false;
    } else if (password.length < 6) {
      setPasswordError('Password must contain at least 6 characters.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setGeneralError('');

    try {
      // The configured API provides demo validation, not production identity.
      const res = await loginApi({ email: email.trim(), password, remember_me: rememberMe });

      // Check remember me persistence
      if (rememberMe) {
        localStorage.setItem('talentrank_remembered_email', email.trim());
      } else {
        localStorage.removeItem('talentrank_remembered_email');
      }

      // Store in session storage
      sessionStorage.setItem('talentrank_auth_session', JSON.stringify({
        authenticated: true,
        user: res.user,
        timestamp: new Date().toISOString()
      }));

      onLoginSuccess(res.user);
    } catch (err) {
      setGeneralError(err instanceof Error ? err.message : 'Unable to reach the demo sign-in service. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-between py-8 px-4 sm:px-6 lg:px-8 selection:bg-accent/15 selection:text-accent font-sans">
      {/* Top Header Logo */}
      <div className="flex items-center justify-between max-w-5xl mx-auto w-full">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-navy-900 border border-navy-800 flex items-center justify-center text-white font-bold text-xs tracking-wider shadow-subtle">
            TR
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm tracking-tight text-primary leading-tight flex items-center gap-1.5">
              TALENTRANK <span className="text-[10px] uppercase font-bold text-accent bg-accent/10 px-1.5 py-0.5 rounded border border-accent/20">AI</span>
            </span>
            <span className="text-[11px] text-secondary">Recruitment Intelligence Platform</span>
          </div>
        </div>

        <span className="rounded-full border border-accent-border bg-accent-light px-3 py-1.5 text-[11px] font-medium text-accent-navy">DEMO WORKSPACE</span>
      </div>

      {/* Main Centered Login Card */}
      <div className="max-w-5xl w-full mx-auto my-8">
        <div className="grid overflow-hidden rounded-xl border border-border bg-card shadow-elevated md:grid-cols-[0.92fr_1.08fr]">
          <section className="relative hidden min-h-[510px] flex-col justify-between overflow-hidden bg-[#eff6ff] p-9 md:flex lg:p-12">
            <div className="absolute -right-20 top-24 h-72 w-72 rounded-full border border-blue-200/80" aria-hidden="true" />
            <div className="absolute -right-8 top-36 h-48 w-48 rounded-full border border-blue-300/70" aria-hidden="true" />
            <div className="absolute right-20 top-52 h-3 w-3 rounded-full bg-blue-600 shadow-[0_0_0_8px_rgba(37,99,235,0.10)]" aria-hidden="true" />
            <div className="relative z-10">
              <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white/80 px-3 py-1.5 text-[10px] font-medium uppercase tracking-[0.14em] text-blue-800"><span className="h-1.5 w-1.5 rounded-full bg-blue-600"/>Talent intelligence</div>
              <h2 className="max-w-sm text-3xl font-semibold leading-tight tracking-[-0.04em] text-slate-900 lg:text-4xl">A clearer view of <span className="text-blue-700">every possibility.</span></h2>
              <p className="mt-4 max-w-sm text-sm leading-6 text-slate-600">Bring role requirements, candidate evidence, and responsible screening into one focused workspace.</p>
            </div>
            <div className="relative z-10 mt-12 max-w-sm rounded-lg border border-blue-200/80 bg-white/85 p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between text-[10px] font-medium uppercase tracking-wider text-slate-500"><span>Pipeline signal</span><span className="text-blue-700">LIVE VIEW</span></div>
              <div className="flex items-end gap-2" aria-hidden="true">{[38,55,47,72,63,88,76,100,83,94,70,86].map((height,index)=><span key={index} className="flex-1 rounded-t-sm bg-blue-200" style={{height:`${height}px`,opacity:index>8?.55:1}}/> )}</div>
              <div className="mt-3 flex justify-between border-t border-blue-100 pt-3 text-[10px] text-slate-500"><span>Evidence-led ranking</span><span>Role alignment</span></div>
            </div>
            <div className="absolute bottom-12 right-12 h-2 w-2 rounded-full bg-sky-500" aria-hidden="true" />
          </section>
          <div className="p-6 sm:p-8 lg:p-12">
          <div className="mx-auto max-w-md space-y-6">
          {/* Card Heading */}
          <div className="space-y-1.5 text-center sm:text-left">
            <h1 className="text-xl sm:text-2xl font-semibold text-primary tracking-tight">
              Sign in to your workspace
            </h1>
            <p className="text-xs text-secondary leading-relaxed">
              Sign in to review screening activity, candidate pipelines, and fairness reports.
            </p>
          </div>

          {/* General Error Banner */}
          {generalError && (
            <div className="p-3 bg-danger-light border border-danger-border rounded-lg flex items-start gap-2.5 text-xs text-danger animate-in fade-in duration-150">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{generalError}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {/* Work Email */}
            <div className="space-y-1.5">
              <label 
                htmlFor="email" 
                className="block text-xs font-medium text-primary"
              >
                Work Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) setEmailError('');
                  }}
                  placeholder="name@company.com"
                  aria-invalid={Boolean(emailError)}
                  aria-describedby={emailError ? 'email-error' : undefined}
                  className={`w-full text-xs bg-white border rounded-lg pl-9 pr-3 py-2.5 text-primary placeholder:text-secondary-muted transition-colors ${
                    emailError
                      ? 'border-danger focus:border-danger focus:ring-danger/20'
                      : 'border-border focus:border-accent focus:ring-accent/15'
                  }`}
                />
              </div>
              {emailError && (
                <p id="email-error" role="alert" className="text-[11px] text-danger flex items-center gap-1 mt-1">
                  <AlertCircle className="w-3 h-3 shrink-0" />
                  <span>{emailError}</span>
                </p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label 
                  htmlFor="password" 
                  className="block text-xs font-medium text-primary"
                >
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(true);
                  }}
                  className="text-xs text-accent hover:text-accent-hover font-medium hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (passwordError) setPasswordError('');
                  }}
                  placeholder="••••••••••••"
                  aria-invalid={Boolean(passwordError)}
                  aria-describedby={passwordError ? 'password-error' : undefined}
                  className={`w-full text-xs bg-white border rounded-lg pl-9 pr-10 py-2.5 text-primary placeholder:text-secondary-muted transition-colors ${
                    passwordError
                      ? 'border-danger focus:border-danger focus:ring-danger/20'
                      : 'border-border focus:border-accent focus:ring-accent/15'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors p-0.5 rounded"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {passwordError && (
                <p id="password-error" role="alert" className="text-[11px] text-danger flex items-center gap-1 mt-1">
                  <AlertCircle className="w-3 h-3 shrink-0" />
                  <span>{passwordError}</span>
                </p>
              )}
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-border text-accent focus:ring-accent/20 cursor-pointer"
                />
                <span className="text-xs text-secondary font-medium">Remember my work email</span>
              </label>

              <span className="text-[10px] text-secondary font-mono">Demo access</span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 px-4 bg-accent hover:bg-accent-hover active:bg-accent-active disabled:opacity-60 text-white rounded-lg text-xs font-medium transition-colors shadow-subtle flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying credentials...</span>
                </>
              ) : (
                <>
                  <span>Sign in to Dashboard</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          <div className="rounded-lg border border-accent-border bg-accent-light/70 p-3 text-[11px] leading-relaxed text-secondary" role="note">
            Demo authentication only. The current API checks email format and a six-character minimum; it does not verify an account or password. Configure a real identity provider before using this app for protected data.
          </div>
          </div>
          </div>
        </div>
      </div>

      {/* Footer Governance & Security */}
      <div className="max-w-md mx-auto w-full text-center space-y-2 text-xs text-secondary">
        <div className="flex items-center justify-center gap-1.5 text-[11px]">
          <ShieldCheck className="w-3.5 h-3.5 text-success" />
          <span>EEOC & NYC Local Law 144 Audited • Zero Protected Attribute Evaluation</span>
        </div>
        <p className="text-[10px] text-secondary-muted">
          © 2026 TalentRank AI • Demo authentication; no account recovery configured.
        </p>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div 
          className="fixed inset-0 z-50 bg-navy-950/40 backdrop-blur-[2px] flex items-center justify-center p-4 animate-in fade-in duration-150"
          role="dialog"
          aria-modal="true"
          aria-labelledby="recovery-title"
        >
          <div className="bg-card border border-border rounded-xl shadow-elevated max-w-sm w-full p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <h2 id="recovery-title" className="text-sm font-semibold text-primary">Reset your password</h2>
                <p className="text-xs text-secondary leading-relaxed">
                  Password recovery is not connected in this demo. Ask your workspace administrator to configure an identity provider.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowForgotPassword(false)}
                className="text-secondary hover:text-primary p-1 rounded-md transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="rounded-md border border-accent-border bg-accent-light p-3 text-xs leading-relaxed text-accent-navy flex gap-2"><Info className="w-4 h-4 shrink-0"/>No reset email was sent. Password recovery must be enabled by the application administrator.</div>
            <button type="button" onClick={() => setShowForgotPassword(false)} className="w-full rounded-md bg-accent px-4 py-2 text-xs font-medium text-white hover:bg-accent-hover">Return to sign in</button>
          </div>
        </div>
      )}
    </div>
  );
};
