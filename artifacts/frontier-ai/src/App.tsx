import { type ReactNode, useState } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ClerkProvider, SignIn, SignUp, useClerk, useUser } from '@clerk/react';
import { publishableKeyFromHost } from '@clerk/react/internal';
import { shadcn } from '@clerk/themes';
import {
  Activity, ArrowUpRight, BookOpen, BrainCircuit, Check, ChevronRight, CircleAlert,
  Clock3, Database, FlaskConical, Gauge, GitBranch, Info, Menu, Play, Plus,
  RefreshCw, SlidersHorizontal, Sparkles, Terminal, X, Zap,
} from 'lucide-react';
import {
  getGetResearchOverviewQueryKey, getListExperimentsQueryKey, getListTrainingRunsQueryKey, getListTrainingRunsQueryOptions,
  useCreateExperiment, useGetResearchOverview, useListDatasets, useListEvaluations,
  useListExperiments, useListModels, useListTrainingRuns, useRunInference,
  useStartTrainingRun,
} from '@workspace/api-client-react';
import type {
  Dataset, Evaluation, Experiment, InferenceResult, Model, ResearchOverview, TrainingRun,
} from '@workspace/api-client-react';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Link, Route, Switch, useLocation, Router as WouterRouter } from 'wouter';

const queryClient = new QueryClient();
const basePath = import.meta.env.BASE_URL.replace(/\/$/, '');
const clerkPubKey = publishableKeyFromHost(
  window.location.hostname,
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
);
const clerkProxyUrl = import.meta.env.VITE_CLERK_PROXY_URL;

function stripBase(path: string) {
  return basePath && path.startsWith(basePath)
    ? path.slice(basePath.length) || '/'
    : path;
}

const nav = [
  { href: '/overview', label: 'Overview', icon: Activity },
  { href: '/models', label: 'Model registry', icon: BrainCircuit },
  { href: '/datasets', label: 'Datasets', icon: Database },
  { href: '/experiments', label: 'Experiments', icon: FlaskConical },
  { href: '/training', label: 'Training runs', icon: Zap },
  { href: '/evaluations', label: 'Evaluations', icon: Gauge },
  { href: '/playground', label: 'Playground', icon: Terminal },
];

function cx(...classes: Array<string | false | undefined>) { return classes.filter(Boolean).join(' '); }
function formatNumber(value: number | undefined | null) {
  if (value === undefined || value === null) return '—';
  return new Intl.NumberFormat('en-US', { notation: value > 9999 ? 'compact' : 'standard', maximumFractionDigits: 1 }).format(value);
}
function formatDate(value?: string | null) {
  if (!value) return 'Not recorded';
  return new Date(value).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function StatusPill({ status, measured = false }: { status?: string; measured?: boolean }) {
  const tone = status?.toLowerCase().includes('complete') || status?.toLowerCase().includes('pass') || status?.toLowerCase() === 'ready'
    ? 'success' : status?.toLowerCase().includes('active') || status?.toLowerCase().includes('running')
      ? 'active' : status?.toLowerCase().includes('fail') || status?.toLowerCase().includes('error') ? 'danger' : 'neutral';
  return (
    <span data-testid={`status-${status ?? 'unknown'}`} className={cx('inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[.12em]',
      tone === 'success' && 'border-teal-700/25 bg-teal-500/10 text-teal-700 dark:text-teal-300',
      tone === 'active' && 'border-amber-700/25 bg-amber-400/20 text-amber-800 dark:text-amber-200',
      tone === 'danger' && 'border-red-700/25 bg-red-500/10 text-red-700 dark:text-red-300',
      tone === 'neutral' && 'border-border bg-muted text-muted-foreground')}>
      {measured && <span className="h-1.5 w-1.5 rounded-full bg-teal-600" />}
      {status ?? 'unreported'}
    </span>
  );
}

function MetricCard({ label, value, detail, icon: Icon, accent = false }: { label: string; value: string | number; detail: string; icon: typeof Activity; accent?: boolean }) {
  return (
    <div data-testid={`metric-${label.toLowerCase().replaceAll(' ', '-')}`} className={cx('relative overflow-hidden rounded-lg border bg-card p-4 shadow-sm', accent && 'data-glow')}>
      <div className="flex items-start justify-between">
        <span className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">{label}</span>
        <Icon className={cx('h-4 w-4', accent ? 'text-primary' : 'text-muted-foreground')} />
      </div>
      <div className="mt-3 font-mono text-2xl font-medium tracking-tight">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{detail}</div>
      {accent && <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-accent/20 blur-2xl" />}
    </div>
  );
}

function PageTitle({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return (
    <div className="mb-7 flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-end">
      <div>
        <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[.2em] text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" /> {eyebrow}
        </div>
        <h1 className="font-display text-3xl font-extrabold tracking-[-.04em] md:text-4xl">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </div>
  );
}

function SkeletonBlock({ className = '' }: { className?: string }) {
  return <div className={cx('skeleton rounded-md', className)} aria-label="Loading" data-testid="loading-skeleton" />;
}

function QueryState({ loading, error, onRetry, children }: { loading?: boolean; error?: unknown; onRetry: () => void; children: ReactNode }) {
  if (loading) return <div className="space-y-3"><SkeletonBlock className="h-24 w-full" /><SkeletonBlock className="h-48 w-full" /></div>;
  if (error) return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-6" data-testid="error-query">
      <CircleAlert className="mb-3 h-5 w-5 text-destructive" />
      <h3 className="font-semibold">The evidence stream is unavailable</h3>
      <p className="mt-1 text-sm text-muted-foreground">The control plane did not return a response. No assumptions were filled in.</p>
      <button data-testid="button-retry" onClick={onRetry} className="mt-4 inline-flex items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm font-semibold hover:bg-muted"><RefreshCw className="h-3.5 w-3.5" /> Retry query</button>
    </div>
  );
  return <>{children}</>;
}

function Shell({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  return (
    <div className="min-h-[100dvh] bg-background text-foreground">
      <aside className={cx('fixed inset-y-0 left-0 z-30 w-[280px] border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-transform md:translate-x-0', mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex h-full flex-col px-4 py-5">
          <div className="mb-9 flex items-center justify-between px-2">
            <Link href="/" data-testid="link-brand" className="flex items-center gap-3">
              <img src={`${basePath}/denarixx-logo.png`} alt="Denarixx" className="h-10 w-10 rounded-md object-cover shadow-sm" />
              <span><span className="block text-sm font-extrabold tracking-tight">DENARIXX</span><span className="block whitespace-nowrap font-mono text-[9px] uppercase tracking-[.16em] text-sidebar-foreground/50">frontier / control plane</span></span>
            </Link>
            <button data-testid="button-close-menu" onClick={() => setMobileOpen(false)} className="rounded p-1 text-sidebar-foreground/50 hover:text-sidebar-foreground md:hidden"><X className="h-4 w-4" /></button>
          </div>
          <div className="mb-3 px-2 font-mono text-[9px] uppercase tracking-[.2em] text-sidebar-foreground/40">Research surface</div>
          <nav className="space-y-1">
            {nav.map(({ href, label, icon: Icon }) => (
              <Link key={href} href={href} data-testid={`link-nav-${label.toLowerCase().replaceAll(' ', '-')}`} onClick={() => setMobileOpen(false)}
                className={cx('group flex items-center justify-between rounded-md px-3 py-2.5 text-sm text-sidebar-foreground/65 hover:bg-sidebar-accent hover:text-sidebar-foreground', location === href && 'bg-sidebar-accent text-sidebar-foreground')}>
                <span className="flex min-w-0 items-center gap-3 whitespace-nowrap"><Icon className={cx('h-4 w-4 shrink-0', location === href ? 'text-sidebar-primary' : 'text-sidebar-foreground/45')} /><span>{label}</span></span>
                {location === href && <ChevronRight className="h-3.5 w-3.5 text-sidebar-primary" />}
              </Link>
            ))}
          </nav>
          <div className="mt-auto space-y-4">
            <div className="rounded-md border border-sidebar-border bg-sidebar-accent/40 p-3">
              <div className="mb-2 flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-teal-400" /><span className="font-mono text-[10px] uppercase tracking-[.16em]">System nominal</span></div>
              <p className="text-xs leading-relaxed text-sidebar-foreground/50">Evidence-first mode. Planned items are never mixed with measured results.</p>
            </div>
            <div className="flex items-center gap-3 border-t border-sidebar-border pt-4 px-2">
              <div className="grid h-7 w-7 place-items-center rounded-full bg-sidebar-primary font-mono text-[10px] text-sidebar-primary-foreground">DR</div>
              <div><div className="text-xs font-semibold">Denarixx Research</div><div className="font-mono text-[10px] text-sidebar-foreground/45">operator session</div></div>
            </div>
          </div>
        </div>
      </aside>
      <div className="md:pl-[280px]">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-border bg-background/90 px-4 backdrop-blur-md md:px-8">
          <button data-testid="button-open-menu" onClick={() => setMobileOpen(true)} className="rounded-md border border-border p-2 md:hidden"><Menu className="h-4 w-4" /></button>
          <div className="hidden items-center gap-2 font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground md:flex"><span className="text-foreground">D0 / experimental</span><span>/</span><span>research control plane</span></div>
            <div className="ml-auto flex items-center gap-3">
            <div className="hidden items-center gap-2 font-mono text-[10px] text-muted-foreground sm:flex"><span className="h-1.5 w-1.5 rounded-full bg-teal-500" /> API connected</div>
             {isSignedIn ? (
               <button type="button" onClick={() => signOut({ redirectUrl: basePath || '/' })} className="hidden rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-muted sm:block">
                 {user?.firstName ?? 'Researcher'} · Sign out
               </button>
             ) : (
               <Link href="/sign-in" className="rounded-md border border-accent/60 bg-accent/10 px-3 py-1.5 text-xs font-semibold text-accent-foreground hover:bg-accent/20">
                 Sign in to run
               </Link>
             )}
            <button data-testid="button-help" className="grid h-8 w-8 place-items-center rounded-md border border-border text-muted-foreground hover:bg-muted"><Info className="h-4 w-4" /></button>
          </div>
        </header>
        <main className="mx-auto max-w-[1440px] px-4 py-7 md:px-8 lg:px-10">{children}</main>
      </div>
    </div>
  );
}

function LandingPage() {
  return (
    <div className="landing-page min-h-[100dvh] overflow-hidden bg-[#101723] text-white">
      <header className="relative z-20 border-b border-white/10">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link href="/" className="flex items-center gap-3" data-testid="landing-brand">
            <img src={`${basePath}/denarixx-logo.png`} alt="Denarixx" className="h-11 w-11 rounded-lg object-cover shadow-[0_0_24px_rgba(247,210,62,.15)]" />
            <div>
              <div className="text-sm font-extrabold tracking-[.12em]">DENARIXX</div>
              <div className="font-mono text-[9px] uppercase tracking-[.2em] text-white/45">frontier intelligence</div>
            </div>
          </Link>
          <nav className="hidden items-center gap-8 text-sm text-white/60 md:flex">
            <a href="#platform" className="hover:text-white">Platform</a>
            <a href="#method" className="hover:text-white">Method</a>
            <a href="#evidence" className="hover:text-white">Evidence</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/sign-in" className="hidden text-sm font-semibold text-white/70 hover:text-white sm:block">Sign in</Link>
            <Link href="/overview" data-testid="landing-open-console" className="inline-flex items-center gap-2 rounded-md bg-[#f7d23e] px-4 py-2.5 text-sm font-bold text-[#101723] hover:bg-[#ffe36c]">
              Open console <ArrowUpRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative isolate">
          <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_72%_20%,rgba(247,210,62,.18),transparent_28%),radial-gradient(circle_at_20%_70%,rgba(45,212,191,.08),transparent_25%)]" />
          <div className="mx-auto grid min-h-[690px] max-w-7xl items-center gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[.86fr_1.14fr] lg:gap-10 lg:py-24">
            <div className="relative z-10 max-w-2xl">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#f7d23e]/30 bg-[#f7d23e]/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[.18em] text-[#f7d23e]">
                <span className="h-1.5 w-1.5 rounded-full bg-[#f7d23e] shadow-[0_0_10px_#f7d23e]" />
                D0 / experimental research system
              </div>
              <h1 className="max-w-3xl text-5xl font-extrabold leading-[.98] tracking-[-.06em] sm:text-6xl lg:text-[76px]">
                Build intelligence you can <span className="text-[#f7d23e]">measure.</span>
              </h1>
              <p className="mt-7 max-w-xl text-base leading-8 text-white/60 sm:text-lg">
                Denarixx Frontier AI is an evidence-first control plane for turning a raw corpus into a tested, inspectable model artifact — without hiding the work behind a chatbot demo.
              </p>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Link href="/overview" data-testid="landing-start-research" className="inline-flex items-center justify-center gap-2 rounded-md bg-[#f7d23e] px-5 py-3.5 text-sm font-bold text-[#101723] hover:bg-[#ffe36c]">
                  Start the research loop <ArrowUpRight className="h-4 w-4" />
                </Link>
                <a href="#method" className="inline-flex items-center justify-center gap-2 rounded-md border border-white/15 px-5 py-3.5 text-sm font-semibold text-white/80 hover:border-white/35 hover:bg-white/5">
                  See how it works <span className="text-[#f7d23e]">↓</span>
                </a>
              </div>
              <div className="mt-12 flex flex-wrap items-center gap-x-7 gap-y-3 border-t border-white/10 pt-5 font-mono text-[10px] uppercase tracking-[.14em] text-white/40">
                <span className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-teal-400" /> API connected</span>
                <span>OpenAPI-first</span>
                <span>CPU-compatible D0</span>
              </div>
            </div>

            <div className="relative lg:-mr-20">
              <div className="absolute -inset-10 -z-10 rounded-full bg-[#f7d23e]/10 blur-3xl" />
              <div className="landing-hero-frame relative overflow-hidden rounded-2xl border border-white/15 bg-[#182333] shadow-2xl shadow-black/40">
                <img src={`${basePath}/frontier-ai-hero.png`} alt="Abstract AI research infrastructure with glowing data layers" className="aspect-[4/3] h-full w-full object-cover opacity-90" />
                <div className="absolute inset-0 bg-gradient-to-tr from-[#101723]/75 via-transparent to-transparent" />
                <div className="absolute left-5 top-5 flex items-center gap-2 rounded-full border border-white/15 bg-[#101723]/75 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[.15em] text-white/70 backdrop-blur">
                  <span className="h-1.5 w-1.5 rounded-full bg-teal-400" /> live artifact surface
                </div>
                <div className="absolute bottom-5 left-5 right-5 grid gap-3 sm:grid-cols-3">
                  {[
                    ['01', 'Corpus', 'authored + versioned'],
                    ['02', 'D0 model', 'tiny transformer'],
                    ['03', 'Evidence', 'checkpoint-backed'],
                  ].map(([number, label, detail]) => (
                    <div key={number} className="rounded-lg border border-white/15 bg-[#101723]/80 p-3 backdrop-blur">
                      <div className="font-mono text-[9px] text-[#f7d23e]">{number}</div>
                      <div className="mt-1 text-xs font-bold">{label}</div>
                      <div className="mt-1 font-mono text-[9px] uppercase tracking-[.1em] text-white/40">{detail}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="absolute -bottom-7 -left-5 hidden w-48 rounded-lg border border-white/10 bg-[#151f2d]/95 p-4 shadow-xl backdrop-blur sm:block">
                <div className="flex items-center justify-between font-mono text-[9px] uppercase tracking-[.14em] text-white/45"><span>validation loss</span><span className="text-teal-300">↓ measured</span></div>
                <div className="mt-3 flex items-end gap-1">
                  {[38, 48, 35, 31, 26, 23, 18, 14, 11].map((height, index) => <span key={index} className="w-2 rounded-t-sm bg-[#f7d23e]" style={{ height }} />)}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="evidence" className="border-y border-white/10 bg-[#0d141f]">
          <div className="mx-auto grid max-w-7xl gap-px px-5 sm:grid-cols-3 sm:px-8">
            {[
              ['01', 'One traceable loop', 'Dataset → tokenizer → model → checkpoint → evaluation → inference.'],
              ['02', 'Measured by default', 'Loss, latency, throughput, and benchmark results stay attached to the artifact.'],
              ['03', 'Honest about unknowns', 'Planned milestones never masquerade as shipped capabilities.'],
            ].map(([number, title, description]) => (
              <div key={number} className="border-white/10 py-9 sm:border-r sm:px-8 sm:first:pl-0 sm:last:border-r-0 sm:last:pr-0">
                <div className="font-mono text-[10px] tracking-[.18em] text-[#f7d23e]">{number}</div>
                <h2 className="mt-3 text-base font-bold">{title}</h2>
                <p className="mt-2 max-w-xs text-sm leading-6 text-white/45">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="platform" className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <div className="max-w-2xl">
            <div className="font-mono text-[10px] uppercase tracking-[.2em] text-[#f7d23e]">The platform surface</div>
            <h2 className="mt-4 text-4xl font-extrabold tracking-[-.05em] sm:text-5xl">Less theater. More signal.</h2>
            <p className="mt-5 text-base leading-7 text-white/50">A focused research cockpit for teams who want to see exactly what happened, why it happened, and what to run next.</p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {[
              { icon: Database, label: 'Provenance', title: 'Start with the source.', body: 'Keep datasets, tokenizer choices, and experiment hypotheses visible before training begins.' },
              { icon: Gauge, label: 'Instrumentation', title: 'Make progress legible.', body: 'Surface real loss curves, gradient norms, throughput, checkpoints, and evaluation outcomes.' },
              { icon: BrainCircuit, label: 'Inference', title: 'Serve the exact artifact.', body: 'Probe the checkpoint that produced the result and carry latency and throughput into every sample.' },
            ].map(({ icon: Icon, label, title, body }) => (
              <article key={label} className="group rounded-xl border border-white/10 bg-white/[.03] p-6 transition hover:-translate-y-1 hover:border-[#f7d23e]/40 hover:bg-white/[.05]">
                <div className="flex items-center justify-between"><Icon className="h-5 w-5 text-[#f7d23e]" /><span className="font-mono text-[9px] uppercase tracking-[.16em] text-white/35">{label}</span></div>
                <h3 className="mt-10 text-xl font-bold">{title}</h3>
                <p className="mt-3 text-sm leading-7 text-white/45">{body}</p>
                <div className="mt-8 h-px w-10 bg-[#f7d23e] transition-all group-hover:w-full" />
              </article>
            ))}
          </div>
        </section>

        <section id="method" className="border-y border-white/10 bg-[#f7d23e] text-[#101723]">
          <div className="mx-auto grid max-w-7xl gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[.7fr_1.3fr] lg:items-center">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[.2em] text-[#101723]/60">Research method / D0</div>
              <h2 className="mt-4 text-4xl font-extrabold tracking-[-.05em] sm:text-5xl">Every claim has a trail.</h2>
              <p className="mt-5 max-w-md text-sm leading-7 text-[#101723]/65">The first vertical slice is intentionally small: a real CPU-compatible transformer, a reproducible corpus, a checkpoint, and an API that can be inspected.</p>
              <Link href="/overview" className="mt-8 inline-flex items-center gap-2 rounded-md bg-[#101723] px-5 py-3.5 text-sm font-bold text-[#f7d23e] hover:bg-[#1d2a3c]">Inspect the control plane <ArrowUpRight className="h-4 w-4" /></Link>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                ['01', 'Register', 'Record the model, dataset, and experiment intent.'],
                ['02', 'Train', 'Run the D0 loop with real metrics and checkpoints.'],
                ['03', 'Evaluate', 'Tie measured results to the exact artifact.'],
                ['04', 'Infer', 'Query the checkpoint and see the latency.'],
              ].map(([number, title, body]) => (
                <div key={number} className="rounded-lg border border-[#101723]/15 bg-white/20 p-5">
                  <div className="font-mono text-xs text-[#101723]/50">{number}</div>
                  <h3 className="mt-7 text-lg font-bold">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-[#101723]/60">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#182333] px-6 py-14 text-center sm:px-12">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(247,210,62,.2),transparent_55%)]" />
            <div className="relative">
              <Sparkles className="mx-auto h-6 w-6 text-[#f7d23e]" />
              <h2 className="mx-auto mt-5 max-w-2xl text-4xl font-extrabold tracking-[-.05em] sm:text-5xl">Make the next run count.</h2>
              <p className="mx-auto mt-4 max-w-lg text-sm leading-7 text-white/50">Open the research console and move from a hypothesis to a measured artifact.</p>
              <Link href="/overview" className="mt-8 inline-flex items-center gap-2 rounded-md bg-[#f7d23e] px-5 py-3.5 text-sm font-bold text-[#101723] hover:bg-[#ffe36c]">Enter Denarixx Frontier AI <ArrowUpRight className="h-4 w-4" /></Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-7 text-xs text-white/35 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span>© 2026 Denarixx Digital Solutions</span>
          <span className="font-mono uppercase tracking-[.14em]">Evidence-first intelligence</span>
        </div>
      </footer>
    </div>
  );
}

function OverviewPage() {
  const query = useGetResearchOverview();
  const overview = query.data as ResearchOverview | undefined;
  return (
    <PageFrame>
      <PageTitle eyebrow="Program / D0" title="Research overview" description="A measured view of the tiny experimental lifecycle — from raw corpus to inference." action={<Link href="/training" data-testid="link-open-training" className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-bold text-primary-foreground hover:opacity-90">Open training surface <ArrowUpRight className="h-4 w-4" /></Link>} />
      <QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}>
        <div className="mb-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <MetricCard label="Models" value={overview?.models ?? 0} detail="registered in control plane" icon={BrainCircuit} accent />
          <MetricCard label="Datasets" value={overview?.datasets ?? 0} detail="with provenance records" icon={Database} />
          <MetricCard label="Experiments" value={overview?.experiments ?? 0} detail="hypotheses logged" icon={FlaskConical} />
          <MetricCard label="Training runs" value={overview?.trainingRuns ?? 0} detail="CPU-compatible runs" icon={Zap} />
          <MetricCard label="Evaluations" value={overview?.evaluations ?? 0} detail="measured benchmarks" icon={Gauge} />
        </div>
        <div className="grid gap-5 xl:grid-cols-[1.3fr_.7fr]">
          <div className="rounded-lg border border-border bg-card p-5">
            <div className="mb-6 flex items-start justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">Lifecycle signal</div><h2 className="mt-1 text-lg font-bold">What has actually run</h2></div><StatusPill status={overview?.systemStatus ?? 'unknown'} /></div>
            <div className="space-y-0">
              {(overview?.milestones ?? []).map((milestone, index) => (
                <div key={milestone.id} data-testid={`milestone-${milestone.id}`} className="relative flex gap-4 pb-6 last:pb-0">
                  {index < (overview?.milestones.length ?? 0) - 1 && <div className="absolute left-[9px] top-5 h-full w-px bg-border" />}
                  <div className={cx('z-10 mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border', milestone.status === 'complete' ? 'border-teal-600 bg-teal-500/15 text-teal-700 dark:text-teal-300' : milestone.status === 'active' ? 'border-accent bg-accent text-accent-foreground' : 'border-border bg-muted text-muted-foreground')}>{milestone.status === 'complete' ? <Check className="h-3 w-3" /> : <span className="h-1.5 w-1.5 rounded-full bg-current" />}</div>
                  <div className="flex-1"><div className="flex flex-wrap items-center gap-2"><span className="text-sm font-semibold">{milestone.label}</span><StatusPill status={milestone.status} /></div><p className="mt-1 text-xs text-muted-foreground">{milestone.description}</p></div>
                </div>
              ))}
              {!overview?.milestones?.length && <EmptyState icon={GitBranch} title="No lifecycle milestones" description="The program has not published lifecycle markers yet." />}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-5">
            <div className="mb-5 flex items-start justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">Latest evidence</div><h2 className="mt-1 text-lg font-bold">Most recent run</h2></div><Link href="/training" data-testid="link-latest-run" className="text-muted-foreground hover:text-foreground"><ArrowUpRight className="h-4 w-4" /></Link></div>
            {overview?.latestRun ? <RunSummary run={overview.latestRun} /> : <EmptyState icon={Clock3} title="No run recorded" description="Start a tiny D0 run to create the first measurable artifact." action={<Link href="/training" data-testid="link-start-first-run" className="text-xs font-bold text-foreground underline decoration-accent decoration-2 underline-offset-4">Go to training</Link>} />}
          </div>
        </div>
        <div className="mt-5 rounded-lg border border-accent/40 bg-accent/10 p-4 text-sm"><div className="flex gap-3"><Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-accent-foreground" /><p><strong>Evidence boundary.</strong> D0 is experimental. A planned milestone indicates intent, not capability; measured cards carry a visible evidence marker and source.</p></div></div>
      </QueryState>
    </PageFrame>
  );
}

function RunSummary({ run }: { run: TrainingRun }) {
  const metric = run.metrics?.[run.metrics.length - 1];
  return <div className="space-y-5">
    <div className="flex items-center justify-between border-b border-border pb-4"><div><div className="font-mono text-xs">{run.id}</div><div className="mt-1 text-sm text-muted-foreground">{run.model} · {run.device}</div></div><StatusPill status={run.status} measured={run.measured} /></div>
    <div className="grid grid-cols-2 gap-3"><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Step</div><div className="mt-1 font-mono text-xl">{metric?.step ?? 0}<span className="text-xs text-muted-foreground"> / {run.maxSteps}</span></div></div><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Train loss</div><div className="mt-1 font-mono text-xl">{metric?.trainingLoss?.toFixed(3) ?? '—'}</div></div><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Tokens / sec</div><div className="mt-1 font-mono text-xl">{metric?.tokensPerSecond?.toFixed(1) ?? '—'}</div></div><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Checkpoint</div><div className="mt-1 truncate font-mono text-xs">{run.checkpointPath ?? 'pending'}</div></div></div>
    <div className="text-xs text-muted-foreground">Started {formatDate(run.startedAt)}</div>
  </div>;
}

function PageFrame({ children }: { children: ReactNode }) { return <Shell><div className="animate-in">{children}</div></Shell>; }

function EmptyState({ icon: Icon, title, description, action }: { icon: typeof Activity; title: string; description: string; action?: ReactNode }) {
  return <div className="grid min-h-36 place-items-center rounded-md border border-dashed border-border bg-muted/30 p-6 text-center"><Icon className="mb-2 h-5 w-5 text-muted-foreground" /><div className="text-sm font-semibold">{title}</div><p className="mt-1 max-w-sm text-xs text-muted-foreground">{description}</p>{action && <div className="mt-3">{action}</div>}</div>;
}

function ModelsPage() {
  const query = useListModels(); const models = query.data as Model[] | undefined;
  return <PageFrame><PageTitle eyebrow="Registry / Models" title="Model registry" description="Versioned model identities and architecture notes. D0 remains explicitly experimental." action={<span className="inline-flex items-center gap-2 rounded-md border border-accent/50 bg-accent/10 px-3 py-2 font-mono text-[10px] uppercase tracking-[.12em] text-accent-foreground"><BrainCircuit className="h-3.5 w-3.5" /> D0 surface</span>} />
    <QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{models?.map((model) => <ModelCard key={model.id} model={model} />)}{!models?.length && <EmptyState icon={BrainCircuit} title="No models registered" description="Model identities will appear here once the registry has evidence." />}</div></QueryState>
  </PageFrame>;
}
function ModelCard({ model }: { model: Model }) {
  return <article data-testid={`card-model-${model.id}`} className="group rounded-lg border border-border bg-card p-5 hover:border-accent/70">
    <div className="mb-7 flex items-start justify-between"><div className="grid h-10 w-10 place-items-center rounded-md bg-primary text-primary-foreground"><BrainCircuit className="h-5 w-5" /></div><StatusPill status={model.status} /></div>
    <h2 className="text-lg font-bold tracking-tight">{model.name}</h2><div className="mt-1 font-mono text-[10px] uppercase tracking-[.13em] text-muted-foreground">{model.family} · {model.id}</div>
    <div className="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-4"><div><div className="text-[10px] uppercase text-muted-foreground">Parameters</div><div className="mt-1 font-mono text-sm">{formatNumber(model.parameters)}</div></div><div><div className="text-[10px] uppercase text-muted-foreground">Context</div><div className="mt-1 font-mono text-sm">{formatNumber(model.contextLength)}</div></div><div className="col-span-2"><div className="text-[10px] uppercase text-muted-foreground">Architecture</div><div className="mt-1 font-mono text-xs">{model.architecture}</div></div></div>
    {model.note && <p className="mt-4 border-l-2 border-accent pl-3 text-xs leading-relaxed text-muted-foreground">{model.note}</p>}
  </article>;
}

function DatasetsPage() {
  const query = useListDatasets(); const datasets = query.data as Dataset[] | undefined;
  return <PageFrame><PageTitle eyebrow="Registry / Provenance" title="Dataset registry" description="Every training input has a name, version, source, and quality signal before it reaches a run." />
    <QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}><div className="overflow-hidden rounded-lg border border-border bg-card"><div className="grid grid-cols-[1.4fr_.7fr_.8fr_1fr_.7fr] gap-4 border-b border-border bg-muted/50 px-5 py-3 font-mono text-[10px] uppercase tracking-[.14em] text-muted-foreground max-md:hidden"><span>Dataset / version</span><span>Stage</span><span>Documents</span><span>Provenance</span><span>Quality</span></div>{datasets?.map((dataset) => <div key={dataset.id} data-testid={`row-dataset-${dataset.id}`} className="grid gap-3 border-b border-border px-5 py-4 last:border-0 md:grid-cols-[1.4fr_.7fr_.8fr_1fr_.7fr] md:items-center md:gap-4"><div><div className="text-sm font-bold">{dataset.name}</div><div className="mt-1 font-mono text-[10px] text-muted-foreground">{dataset.version} · {dataset.license}</div></div><div><StatusPill status={dataset.stage} /></div><div><div className="font-mono text-sm">{formatNumber(dataset.documents)}</div><div className="text-[10px] text-muted-foreground">{formatNumber(dataset.tokens)} tokens</div></div><div className="text-xs text-muted-foreground">{dataset.provenance}</div><div className="font-mono text-sm">{dataset.qualityScore != null ? `${dataset.qualityScore.toFixed(1)} / 10` : 'Not scored'}</div></div>)}{!datasets?.length && <div className="p-5"><EmptyState icon={Database} title="No datasets registered" description="Provenance records are intentionally required before training." /></div>}</div></QueryState>
  </PageFrame>;
}

function ExperimentsPage() {
  const query = useListExperiments(); const experiments = query.data as Experiment[] | undefined;
  const create = useCreateExperiment(); const client = useQueryClient(); const [open, setOpen] = useState(false); const [form, setForm] = useState({ name: '', hypothesis: '', baseline: '', variant: '', dataset: '' });
  const submit = () => { if (!Object.values(form).every(Boolean)) return; create.mutate({ data: form }, { onSuccess: () => { setOpen(false); setForm({ name: '', hypothesis: '', baseline: '', variant: '', dataset: '' }); client.invalidateQueries({ queryKey: getListExperimentsQueryKey() }); client.invalidateQueries({ queryKey: getGetResearchOverviewQueryKey() }); } }); };
  return <PageFrame><PageTitle eyebrow="Registry / Hypotheses" title="Experiments" description="A clean ledger of what we believed, what we compared, and what the evidence concluded." action={<button data-testid="button-new-experiment" onClick={() => setOpen(true)} className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-bold text-primary-foreground"><Plus className="h-4 w-4" /> Log experiment</button>} />
    <QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}><div className="space-y-3">{experiments?.map((experiment) => <ExperimentRow key={experiment.id} experiment={experiment} />)}{!experiments?.length && <EmptyState icon={FlaskConical} title="No hypotheses logged" description="Record the question before starting a run; this is how baselines stay legible." action={<button data-testid="button-empty-experiment" onClick={() => setOpen(true)} className="font-semibold underline decoration-accent decoration-2 underline-offset-4">Log the first experiment</button>} />}</div></QueryState>
    {open && <Modal title="Log a research experiment" onClose={() => setOpen(false)}><div className="space-y-4">{[['name', 'Experiment name', 'e.g. tokenizer-window-01'], ['hypothesis', 'Hypothesis', 'What do you expect to change?'], ['baseline', 'Baseline', 'Existing configuration or checkpoint'], ['variant', 'Variant', 'Single change under test'], ['dataset', 'Dataset', 'Dataset name and version']] .map(([key, label, placeholder]) => <label key={key} className="block"><span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[.12em] text-muted-foreground">{label}</span><input data-testid={`input-experiment-${key}`} value={form[key as keyof typeof form]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} placeholder={placeholder} className="w-full rounded-md border border-input bg-background px-3 py-2.5 text-sm outline-none focus:border-accent" /></label>)}<div className="flex justify-end gap-2 pt-2"><button data-testid="button-cancel-experiment" onClick={() => setOpen(false)} className="rounded-md border border-border px-3 py-2 text-sm">Cancel</button><button data-testid="button-save-experiment" disabled={create.isPending} onClick={submit} className="rounded-md bg-primary px-3 py-2 text-sm font-bold text-primary-foreground disabled:opacity-50">{create.isPending ? 'Saving…' : 'Save evidence record'}</button></div></div></Modal>}
  </PageFrame>;
}
function ExperimentRow({ experiment }: { experiment: Experiment }) {
  return <article data-testid={`row-experiment-${experiment.id}`} className="rounded-lg border border-border bg-card p-5"><div className="flex flex-col justify-between gap-3 md:flex-row md:items-start"><div><div className="flex flex-wrap items-center gap-2"><h2 className="font-bold">{experiment.name}</h2><StatusPill status={experiment.status} /></div><div className="mt-1 font-mono text-[10px] uppercase tracking-[.12em] text-muted-foreground">{experiment.id} · created {formatDate(experiment.createdAt)}</div></div><div className="font-mono text-[10px] text-muted-foreground">{experiment.dataset}</div></div><p className="mt-4 max-w-3xl text-sm leading-relaxed">{experiment.hypothesis}</p><div className="mt-5 grid gap-3 border-t border-border pt-4 md:grid-cols-2"><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Baseline</div><div className="mt-1 text-xs text-muted-foreground">{experiment.baseline}</div></div><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Variant</div><div className="mt-1 text-xs text-muted-foreground">{experiment.variant}</div></div></div>{experiment.conclusion && <div className="mt-4 rounded-md bg-muted/70 p-3 text-xs"><span className="font-bold">Conclusion · </span>{experiment.conclusion}</div>}</article>;
}

function TrainingPage() {
  const query = useQuery({ ...getListTrainingRunsQueryOptions(), refetchInterval: 2000 }); const runs = query.data as TrainingRun[] | undefined; const start = useStartTrainingRun(); const client = useQueryClient(); const [open, setOpen] = useState(false); const [maxSteps, setMaxSteps] = useState('40'); const [seed, setSeed] = useState('7'); const [resumeFromRunId, setResumeFromRunId] = useState('');
  const resumableRuns = runs?.filter((run) => run.status === 'complete' && Boolean(run.checkpointPath)) ?? [];
  const submit = () => start.mutate({ data: { maxSteps: Number(maxSteps), seed: Number(seed), resumeFromRunId: resumeFromRunId || null } }, { onSuccess: () => { setOpen(false); setResumeFromRunId(''); client.invalidateQueries({ queryKey: getListTrainingRunsQueryKey() }); client.invalidateQueries({ queryKey: getGetResearchOverviewQueryKey() }); } });
  return <PageFrame><PageTitle eyebrow="Lifecycle / Training" title="Training runs" description="Small, reproducible runs with metrics attached. Start a CPU-compatible D0 run, resume a checkpoint, and inspect the trace." action={<button data-testid="button-start-training" onClick={() => setOpen(true)} className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-bold text-primary-foreground"><Play className="h-4 w-4" /> Start tiny run</button>} />
    <div className="mb-5 flex items-center gap-2 border border-accent/40 bg-accent/10 px-4 py-3 text-xs"><Info className="h-4 w-4 text-accent-foreground" /><span><strong>Measured surface:</strong> only completed runs with <span className="font-mono">measured: true</span> should inform conclusions.</span></div>
    <QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}><div className="space-y-3">{runs?.map((run) => <TrainingRow key={run.id} run={run} />)}{!runs?.length && <EmptyState icon={Zap} title="No training runs yet" description="A tiny run creates the first checkpoint and metric trace." action={<button data-testid="button-empty-training" onClick={() => setOpen(true)} className="font-semibold underline decoration-accent decoration-2 underline-offset-4">Start a run</button>} />}</div></QueryState>
     {open && <Modal title="Start a tiny D0 run" onClose={() => setOpen(false)}><div className="mb-5 rounded-md border border-accent/40 bg-accent/10 p-3 text-xs leading-relaxed">The server chooses the registered D0 model and dataset. These controls set reproducibility parameters and can resume a completed checkpoint into a longer run.</div><label className="mb-4 block"><span className="mb-1.5 block font-mono text-[10px] uppercase text-muted-foreground">Max steps (1–200)</span><input data-testid="input-max-steps" type="number" min="1" max="200" value={maxSteps} onChange={(e) => setMaxSteps(e.target.value)} className="w-full rounded-md border border-input bg-background px-3 py-2.5 font-mono text-sm" /></label><label className="mb-4 block"><span className="mb-1.5 block font-mono text-[10px] uppercase text-muted-foreground">Seed</span><input data-testid="input-seed" type="number" min="0" value={seed} onChange={(e) => setSeed(e.target.value)} className="w-full rounded-md border border-input bg-background px-3 py-2.5 font-mono text-sm" /></label><label className="block"><span className="mb-1.5 block font-mono text-[10px] uppercase text-muted-foreground">Resume from checkpoint</span><select data-testid="select-resume-run" value={resumeFromRunId} onChange={(e) => { setResumeFromRunId(e.target.value); const source = resumableRuns.find((run) => run.id === e.target.value); if (source) setMaxSteps(String(Math.min(source.maxSteps + 20, 200))); }} className="w-full rounded-md border border-input bg-background px-3 py-2.5 text-sm"><option value="">Start from fresh initialization</option>{resumableRuns.map((run) => <option key={run.id} value={run.id}>{run.id} · step {run.maxSteps} · {run.device}</option>)}</select>{resumeFromRunId && <span className="mt-1.5 block text-[10px] text-muted-foreground">The next run will load model weights, optimizer state, scheduler state, tokenizer, and dataset references from this checkpoint.</span>}</label>{start.error && <div className="mt-4 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-xs text-destructive">Unable to start run. {((start.error as { data?: { error?: string } })?.data?.error) ?? 'Sign in and check the run parameters.'}</div>}<div className="mt-6 flex justify-end gap-2"><button data-testid="button-cancel-training" onClick={() => setOpen(false)} className="rounded-md border border-border px-3 py-2 text-sm">Cancel</button><button data-testid="button-confirm-training" disabled={start.isPending} onClick={submit} className="rounded-md bg-primary px-3 py-2 text-sm font-bold text-primary-foreground disabled:opacity-50">{start.isPending ? 'Starting…' : resumeFromRunId ? 'Resume run' : 'Start run'}</button></div></Modal>}
  </PageFrame>;
}
function TrainingRow({ run }: { run: TrainingRun }) {
  const metric = run.metrics?.[run.metrics.length - 1]; const first = run.metrics?.[0];
  return <article data-testid={`row-training-${run.id}`} className="rounded-lg border border-border bg-card p-5"><div className="flex flex-col justify-between gap-3 md:flex-row md:items-start"><div><div className="flex items-center gap-2"><h2 className="font-mono text-sm font-medium">{run.id}</h2><StatusPill status={run.status} measured={run.measured} /></div><div className="mt-2 text-xs text-muted-foreground">{run.model} · {run.dataset} · {run.device} · seed {run.seed}</div>{run.resumedFromRunId && <div className="mt-1 font-mono text-[10px] text-muted-foreground">resumed from {run.resumedFromRunId}</div>}</div><div className="font-mono text-[10px] text-muted-foreground">started {formatDate(run.startedAt)}</div></div><div className="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-4 sm:grid-cols-5"><TrainingMetric label="progress" value={`${metric?.step ?? 0} / ${run.maxSteps}`} /><TrainingMetric label="train loss" value={metric?.trainingLoss?.toFixed(4) ?? '—'} delta={first && metric ? (metric.trainingLoss - first.trainingLoss).toFixed(3) : undefined} /><TrainingMetric label="val loss" value={metric?.validationLoss?.toFixed(4) ?? '—'} /><TrainingMetric label="tok / sec" value={metric?.tokensPerSecond?.toFixed(1) ?? '—'} /><TrainingMetric label="checkpoint" value={run.checkpointPath ?? 'pending'} /></div>{run.error && <div className="mt-4 border-l-2 border-destructive bg-destructive/5 p-3 text-xs text-destructive">{run.error}</div>}</article>;
}
function TrainingMetric({ label, value, delta }: { label: string; value: string; delta?: string }) { return <div><div className="font-mono text-[9px] uppercase tracking-[.1em] text-muted-foreground">{label}</div><div className="mt-1 truncate font-mono text-sm">{value}</div>{delta && <div className="mt-0.5 text-[10px] text-teal-700 dark:text-teal-300">{delta} from first</div>}</div>; }

function EvaluationsPage() {
  const query = useListEvaluations(); const evaluations = query.data as Evaluation[] | undefined;
  return <PageFrame><PageTitle eyebrow="Evidence / Benchmarks" title="Evaluations" description="Measured benchmark outcomes, linked to the exact model and checkpoint that produced them." /><QueryState loading={query.isLoading} error={query.error} onRetry={() => query.refetch()}><div className="grid gap-4 lg:grid-cols-2">{evaluations?.map((evaluation) => <EvaluationCard key={evaluation.id} evaluation={evaluation} />)}{!evaluations?.length && <EmptyState icon={Gauge} title="No evaluations recorded" description="Evaluation results appear only after a checkpoint has been measured against a benchmark." />}</div></QueryState></PageFrame>;
}
function EvaluationCard({ evaluation }: { evaluation: Evaluation }) { return <article data-testid={`card-evaluation-${evaluation.id}`} className="rounded-lg border border-border bg-card p-5"><div className="flex items-start justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.14em] text-muted-foreground">{evaluation.benchmark} / {evaluation.benchmarkVersion}</div><h2 className="mt-2 text-lg font-bold">{evaluation.model}</h2></div><StatusPill status={evaluation.status} measured /></div><div className="mt-6 flex items-end justify-between border-t border-border pt-4"><div><div className="font-mono text-[10px] uppercase text-muted-foreground">Measured score</div><div className="mt-1 font-mono text-3xl font-medium">{evaluation.score != null ? evaluation.score.toFixed(3) : '—'}</div></div><div className="text-right text-xs text-muted-foreground"><div>{evaluation.checkpoint}</div><div className="mt-1">{formatDate(evaluation.evaluatedAt)}</div></div></div><div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground"><BookOpen className="h-3.5 w-3.5" /> Source: {evaluation.source}</div>{evaluation.rawResults && <details className="mt-4 rounded bg-muted/50 p-3 text-xs"><summary className="cursor-pointer font-semibold">Raw result payload</summary><pre className="mt-3 overflow-auto whitespace-pre-wrap font-mono text-[10px]">{evaluation.rawResults}</pre></details>}</article>; }

function PlaygroundPage() {
  const inference = useRunInference(); const [prompt, setPrompt] = useState('Explain what makes a measurement reproducible in one sentence.'); const [maxTokens, setMaxTokens] = useState('32'); const [temperature, setTemperature] = useState('0.7'); const [result, setResult] = useState<InferenceResult | null>(null);
  const run = () => inference.mutate({ data: { prompt, maxTokens: Number(maxTokens), temperature: Number(temperature) } }, { onSuccess: (data) => setResult(data) });
  return <PageFrame><PageTitle eyebrow="Inference / Measured sample" title="D0 playground" description="Probe the exact server-selected checkpoint. Latency and throughput are returned with every sample." action={<div className="inline-flex items-center gap-2 rounded-md border border-teal-700/25 bg-teal-500/10 px-3 py-2 font-mono text-[10px] uppercase tracking-[.12em] text-teal-700 dark:text-teal-300"><Terminal className="h-3.5 w-3.5" /> live inference</div>} />
    <div className="grid gap-5 xl:grid-cols-[.85fr_1.15fr]"><div className="rounded-lg border border-border bg-card p-5"><div className="mb-5 flex items-center justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">Input</div><h2 className="mt-1 text-lg font-bold">Prompt sample</h2></div><SlidersHorizontal className="h-4 w-4 text-muted-foreground" /></div><label className="block"><span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[.12em] text-muted-foreground">Prompt</span><textarea data-testid="textarea-inference-prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} maxLength={1000} rows={8} className="w-full resize-y rounded-md border border-input bg-background px-3 py-3 text-sm leading-relaxed outline-none focus:border-accent" /></label><div className="mt-4 grid grid-cols-2 gap-3"><label><span className="mb-1.5 block font-mono text-[10px] uppercase text-muted-foreground">Max tokens</span><input data-testid="input-inference-max-tokens" type="number" min="1" max="64" value={maxTokens} onChange={(e) => setMaxTokens(e.target.value)} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm" /></label><label><span className="mb-1.5 block font-mono text-[10px] uppercase text-muted-foreground">Temperature</span><input data-testid="input-inference-temperature" type="number" min=".1" max="2" step=".1" value={temperature} onChange={(e) => setTemperature(e.target.value)} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm" /></label></div><button data-testid="button-run-inference" disabled={!prompt.trim() || inference.isPending} onClick={run} className="mt-5 flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 text-sm font-bold text-primary-foreground disabled:opacity-50">{inference.isPending ? 'Running measured sample…' : 'Run inference'}<Play className="h-4 w-4" /></button>{inference.error && <div className="mt-3 text-xs text-destructive">Inference failed. Check the active checkpoint and retry.</div>}</div><div className="relative overflow-hidden rounded-lg border border-border bg-primary p-5 text-primary-foreground scanlines"><div className="relative z-10"><div className="mb-5 flex items-center justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.16em] text-primary-foreground/60">Output / measured</div><h2 className="mt-1 text-lg font-bold">Checkpoint response</h2></div>{result && <StatusPill status="measured" measured />}</div>{result ? <><div className="min-h-44 rounded-md border border-primary-foreground/15 bg-primary-foreground/5 p-4 text-sm leading-7">{result.output}</div><div className="mt-5 grid grid-cols-2 gap-3 border-t border-primary-foreground/15 pt-4 sm:grid-cols-4"><InferenceMetric label="model" value={result.model} /><InferenceMetric label="checkpoint" value={result.checkpoint} /><InferenceMetric label="latency" value={`${result.latencyMs.toFixed(1)} ms`} /><InferenceMetric label="throughput" value={`${result.tokensPerSecond.toFixed(1)} tok/s`} /></div></> : <div className="grid min-h-[330px] place-items-center rounded-md border border-dashed border-primary-foreground/20 text-center"><div><Terminal className="mx-auto mb-3 h-7 w-7 text-primary-foreground/50" /><div className="text-sm font-semibold">No sample yet</div><p className="mt-1 max-w-xs text-xs text-primary-foreground/60">Run the prompt to see the output plus its measured latency.</p></div></div>}</div></div></div>
  </PageFrame>;
}
function InferenceMetric({ label, value }: { label: string; value: string }) { return <div><div className="font-mono text-[9px] uppercase tracking-[.1em] text-primary-foreground/55">{label}</div><div className="mt-1 truncate font-mono text-xs">{value}</div></div>; }

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) { return <div className="fixed inset-0 z-50 grid place-items-center bg-foreground/35 p-4 backdrop-blur-sm" role="dialog" aria-modal="true"><div className="w-full max-w-lg rounded-lg border border-border bg-card p-6 shadow-2xl animate-in"><div className="mb-5 flex items-start justify-between"><div><div className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">Operator action</div><h2 className="mt-1 text-xl font-bold">{title}</h2></div><button data-testid="button-close-modal" onClick={onClose} className="rounded-md p-1.5 text-muted-foreground hover:bg-muted"><X className="h-4 w-4" /></button></div>{children}</div></div>; }

function SignInPage() {
  return <div className="flex min-h-[100dvh] items-center justify-center bg-background px-4"><SignIn routing="path" path={`${basePath}/sign-in`} signUpUrl={`${basePath}/sign-up`} /></div>;
}

function SignUpPage() {
  return <div className="flex min-h-[100dvh] items-center justify-center bg-background px-4"><SignUp routing="path" path={`${basePath}/sign-up`} signInUrl={`${basePath}/sign-in`} /></div>;
}

function Router() { return <RoutedErrorBoundary><Switch><Route path="/sign-in/*?" component={SignInPage} /><Route path="/sign-up/*?" component={SignUpPage} /><Route path="/" component={LandingPage} /><Route path="/overview" component={OverviewPage} /><Route path="/models" component={ModelsPage} /><Route path="/datasets" component={DatasetsPage} /><Route path="/experiments" component={ExperimentsPage} /><Route path="/training" component={TrainingPage} /><Route path="/evaluations" component={EvaluationsPage} /><Route path="/playground" component={PlaygroundPage} /><Route component={NotFound} /></Switch></RoutedErrorBoundary>; }
function RoutedErrorBoundary({ children }: { children: ReactNode }) { const [location] = useLocation(); return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>; }
function ClerkApp() {
  const [, setLocation] = useLocation();
  return <ClerkProvider
    publishableKey={clerkPubKey}
    proxyUrl={clerkProxyUrl}
    appearance={{
      theme: shadcn,
      cssLayerName: 'clerk',
      options: {
        logoPlacement: 'inside',
        logoLinkUrl: basePath || '/',
        logoImageUrl: `${window.location.origin}${basePath}/denarixx-logo.png`,
      },
      variables: {
        colorPrimary: '#f7d23e',
        colorForeground: '#1d2433',
        colorMutedForeground: '#6b7280',
        colorDanger: '#b42318',
        colorBackground: '#f8f9fb',
        colorInput: '#ffffff',
        colorInputForeground: '#1d2433',
        colorNeutral: '#d9dde5',
        fontFamily: 'Manrope, sans-serif',
        borderRadius: '0.5rem',
      },
      elements: {
        rootBox: 'w-full flex justify-center',
        cardBox: 'bg-[#f8f9fb] rounded-2xl w-[440px] max-w-full overflow-hidden',
        card: '!shadow-none !border-0 !bg-transparent !rounded-none',
        footer: '!shadow-none !border-0 !bg-transparent !rounded-none',
        headerTitle: 'text-[#1d2433] font-bold',
        headerSubtitle: 'text-[#6b7280]',
        socialButtonsBlockButtonText: 'text-[#1d2433]',
        formFieldLabel: 'text-[#1d2433]',
        footerActionLink: 'text-[#6d5c00] font-semibold',
        footerActionText: 'text-[#6b7280]',
        dividerText: 'text-[#6b7280]',
        formButtonPrimary: 'bg-[#1d2433] text-[#f7d23e] hover:bg-[#2b3446]',
        formFieldInput: 'bg-white text-[#1d2433] border-[#d9dde5]',
        socialButtonsBlockButton: 'bg-white border-[#d9dde5]',
        logoBox: 'h-10',
        logoImage: 'h-10',
        main: 'bg-transparent',
      },
    }}
    signInUrl={`${basePath}/sign-in`}
    signUpUrl={`${basePath}/sign-up`}
    routerPush={(to) => setLocation(stripBase(to))}
    routerReplace={(to) => setLocation(stripBase(to), { replace: true })}
  >
    <QueryClientProvider client={queryClient}>
      <TooltipProvider><Router /><Toaster /></TooltipProvider>
    </QueryClientProvider>
  </ClerkProvider>;
}
function App() { return <WouterRouter base={basePath}><ClerkApp /></WouterRouter>; }

export default App;