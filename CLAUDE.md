# FlowDesk — Project Context for Claude Code

> Auto-maintained by Claude. Last updated: 2026-03-16

---

## Project Overview
FlowDesk is a student productivity SaaS — single-file HTML/CSS/JS pages, no build tools, no frameworks. Live at **https://kolimoli1.github.io**.

---

## Stack
- **Frontend:** Vanilla HTML/CSS/JS, single-file pages
- **Auth + DB:** Supabase (`https://teovjlyddhbiauadojsa.supabase.co`)
- **Hosting:** GitHub Pages (repo: `kolimoli1/kolimoli1.github.io`, branch: `main`, root `/`)
- **Fonts:** Instrument Serif (display), DM Sans (body) via Google Fonts
- **Animations:** GSAP 3.12.5 + ScrollTrigger (landing page only), vanilla CSS keyframes + JS elsewhere

---

## File Structure
| File | Purpose |
|------|---------|
| `index.html` | Landing/marketing page |
| `auth.html` | Sign up / log in |
| `onboarding.html` | 4-step new user onboarding |
| `dashboard.html` | Main app (1500+ lines) |
| `supabase.js` | Supabase client init (imported by all pages) |
| `privacy.html` | Privacy policy |
| `terms.html` | Terms of service |
| `google1e931fac63162d50.html` | DO NOT DELETE — Google Search Console verification |
| `CLAUDE.md` | This file |

**Page flow:** `index.html` → `auth.html` → `onboarding.html` (new users) → `dashboard.html`

---

## Design System (CSS custom properties)

```css
--ink        /* primary text */
--paper      /* page background */
--cream      /* card/sidebar background */
--sage       /* primary accent (green) */
--sage-light /* accent tint background */
--sage-dark  /* accent dark (hover states) */
--amber      /* warning/due dates */
--amber-light
--coral      /* danger/overdue */
--muted      /* secondary text */
--border     /* rgba border color */
--sidebar-w: 240px
--font-display: 'Instrument Serif', Georgia, serif
--font-body:    'DM Sans', sans-serif
```

### Themes
- **Dark mode:** `data-theme="dark"` on `<html>`
- **Color themes:** `data-color="forest|ocean|lavender|rose|amber|mono"` on `<html>`
- **Font themes:** `data-font="serif|sans|mono"` on `<html>`
- **Density:** `data-density="compact|spacious"` on `<html>`
- All preferences persisted to `localStorage` with keys: `flowdesk-theme`, `flowdesk-color`, `flowdesk-font`, `flowdesk-density`, `flowdesk-particles`, `flowdesk-animations`

### Key UI Patterns
- Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
- Buttons (primary): `background: var(--sage)`, `border-radius: 100px`
- Nav active state: `background: var(--sage-light)` + 3px left accent bar via `::before`
- View transitions: `animation: viewIn 0.4s cubic-bezier(0.16,1,0.3,1)`
- Task rows slide in from left: `taskSlideIn` keyframe
- Check buttons: spring pop `checkPop` keyframe on done
- Habit days: `dayPop` spring rotation keyframe

---

## Supabase

**Project URL:** `https://teovjlyddhbiauadojsa.supabase.co`  
**Anon key:** in `supabase.js`

### Database Tables (all with RLS — users see only their own rows)
```sql
profiles   (id, full_name, field, goals[], hours_per_day, pom_minutes, onboarding_done, updated_at)
courses    (id, user_id, name, color, created_at)
tasks      (id, user_id, title, done, due_date, course_id, notes, created_at, updated_at)
habits     (id, user_id, name, emoji, completions[], created_at, updated_at)
```

### Auth
- Email/password + Google OAuth
- Redirect URLs: `https://kolimoli1.github.io/onboarding.html`, `https://kolimoli1.github.io/auth.html`
- Google OAuth: branding verified, publishing in progress
- Email confirmation currently OFF (for development)

**Legal:** Privacy policy at `/privacy.html`, Terms of Service at `/terms.html`

---

## Dashboard Views (dashboard.html)

| View ID | Nav label | Description |
|---------|-----------|-------------|
| `view-dashboard` | Dashboard | Stat cards + today's tasks + quick pomodoro |
| `view-tasks` | Tasks | Full task list with filters + add form |
| `view-pomodoro` | Pomodoro | SVG ring timer, modes, session dots |
| `view-habits` | Habits | Weekly grid, streaks |
| `view-planner` | Planner | 7-column weekly grid, quick-add per day |
| `view-analytics` | Analytics | Focus stats, streak counts, best-streak card |
| `view-customize` | Customize | Theme/color/font/density/effects |

### Key JS Functions
```js
switchView(v)              // switches active view, updates nav + header title
renderTasks(container?)    // renders task list; always call renderPlanner() after
renderPlanner()            // renders 7-day weekly grid from tasks array
renderHabits()             // renders habit list with weekly completion dots
updateDashStats()          // updates stat cards on dashboard view
insertTask(title, due, courseId)  // inserts to Supabase + updates local tasks[]
toggleTask(id)             // toggles done, animates, re-renders
deleteTask(id)             // removes from Supabase + re-renders
togglePom() / setPomMode() // pomodoro controls
setMode/setColor/setFont/setDensity()  // customize panel
restoreCustomize()         // reads localStorage and applies all saved prefs
```

### Global State
```js
currentUser   // Supabase user object
profile       // profiles row
courses[]     // user's courses
tasks[]       // all user tasks (in-memory, source of truth for renders)
habits[]      // all user habits
focusSecondsToday  // accumulated pomodoro focus time
```

---

## Sidebar Particles
Canvas-based floating dot animation inside `<aside class="sidebar">`. Togglable via Customize panel. Uses `requestAnimationFrame`, theme-aware green color.

---

## What's Been Built
- [x] Landing page (index.html) with GSAP animations, aurora WebGL background, pricing tiers, testimonials
- [x] Auth page (email + Google OAuth)
- [x] Onboarding (4 steps, saves to `profiles` + `courses`)
- [x] Dashboard with all 7 views (including Analytics)
- [x] Full task CRUD with Supabase
- [x] Pomodoro timer with SVG ring, modes, session dots, audio cue
- [x] Habits with weekly grid + streak tracking
- [x] Weekly Planner (7-column grid, quick-add per day)
- [x] Customize panel (theme, color, font, density, effects toggles)
- [x] Dark mode + 6 color themes + font themes + density
- [x] Sidebar particles canvas animation
- [x] Fluid animations: view transitions, task slide-in, check pop, habit day pop, pomodoro ring glow
- [x] Privacy policy (privacy.html)
- [x] Terms of Service (terms.html)
- [x] Google Search Console verification
- [x] Google OAuth branding submitted

## Not Yet Built
- [ ] Focus mode (distraction-free fullscreen) — **Eash**
- [ ] Stripe payment integration (wire to actual Pro status) — **kolimoli1**
- [ ] Study Group plan features — **kolimoli1**
- [ ] Course management UI — **kolimoli1**
- [ ] Weekly planner: drag-to-reschedule tasks — **unassigned**

---

## Ownership Split

| Area | Owner | GitHub |
|------|-------|--------|
| Focus analytics view | Eash | eashman-design |
| Focus mode (distraction-free) | Eash | eashman-design |
| Stripe integration + billing | kolimoli1 | kolimoli1 |
| Course management UI | kolimoli1 | kolimoli1 |
| Shared (CLAUDE.md, supabase.js, design system) | Both | — |

## Branch Convention
- Eash: `eash/feature-name`
- kolimoli1: `koli/feature-name`
- Never commit directly to main
- Always pull from main before starting a new branch
- Open a PR when a feature is done — other person reviews before merging

---

## Known Bugs
- `user-plan` in sidebar hardcodes "Free plan" for all users — needs to check actual Supabase subscription status once Stripe is wired
- Stripe buy buttons in index.html use test-mode links and aren't connected to real subscription logic
- Stat numbers on landing page (42k+ students, 2.1M tasks) are hardcoded placeholders
- `focusSecondsToday` is in-memory only — resets to 0 on page reload; needs persistence once analytics view is fully wired

---

## How to Start a Claude Code Session
Always launch Claude Code from inside the repo root:
```bash
cd kolimoli1.github.io   # or wherever you cloned it
claude
```
Claude Code will auto-read this CLAUDE.md and have full project context. Never run it from outside the repo folder.

## Session Start — Required First Step

**Before doing anything else in a new session**, invoke the `branch-manager` agent to report git status:
- Current branch and any uncommitted changes
- Branches that have unmerged commits
- Branches that are merged and can be cleaned up
- Whether local `main` is in sync with `origin/main`

This gives both developer and Claude a shared picture of repo state before any work begins.

---

## Rules for Claude Code
1. **Never rewrite the whole file** — return targeted diffs/additions only
2. **No new dependencies** — vanilla JS only for dashboard; GSAP only on index.html
3. **Match the design system** — use CSS vars, same border-radius, same animation style
4. **Single-file constraint** — all CSS/JS stays inside the relevant `.html` file
5. **Always call `renderPlanner()`** after any function that mutates `tasks[]`
6. **Escape user content** with `escapeHtml()` when injecting into innerHTML
7. **Date strings** must use local time (not `toISOString()`) to avoid UTC offset bugs — see `renderPlanner()` for the correct pattern
8. **Return 4 labeled blocks** when adding a full feature: CSS, HTML, Nav item, JS

---

## Active Skills

The following skills are installed in `.claude/skills/` and should be loaded when relevant:

- **ui-ux-pro-max** — Load for any UI design, styling, component work, or visual decisions. Contains 50+ styles, 161 color palettes, 57 font pairings, and 99 UX guidelines.
- **ui-styling** — Load for canvas design system work or accessible component patterns (note: project uses vanilla CSS, not Tailwind/shadcn).
- **design** — Load for logo, icon, or slide design tasks.
- **design-system** — Load for design tokens, component specs, or token architecture decisions.
- **brand** — Load for brand consistency checks or guideline work.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **kolimoli1.github.io** (23 symbols, 12 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run a GitNexus query at the start of any investigation or bug fix** — before reading files or grepping. The repo contains files not listed in CLAUDE.md (e.g. `supabase/functions/`). Use `gitnexus_query({query: "<concept or symptom>"})` to surface the full picture first.
- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/kolimoli1.github.io/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/kolimoli1.github.io/context` | Codebase overview, check index freshness |
| `gitnexus://repo/kolimoli1.github.io/clusters` | All functional areas |
| `gitnexus://repo/kolimoli1.github.io/processes` | All execution flows |
| `gitnexus://repo/kolimoli1.github.io/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## CLI

- Re-index: `npx gitnexus analyze`
- Check freshness: `npx gitnexus status`
- Generate docs: `npx gitnexus wiki`

<!-- gitnexus:end -->
