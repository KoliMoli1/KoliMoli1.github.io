# FlowDesk — Project Context for Claude Code

> Auto-maintained by Claude. Last updated: 2026-03-12

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
- Google OAuth currently in "Testing" mode — needs publishing before public launch
- Email confirmation currently OFF (for development)

---

## Dashboard Views (dashboard.html)

| View ID | Nav label | Description |
|---------|-----------|-------------|
| `view-dashboard` | Dashboard | Stat cards + today's tasks + quick pomodoro |
| `view-tasks` | Tasks | Full task list with filters + add form |
| `view-pomodoro` | Pomodoro | SVG ring timer, modes, session dots |
| `view-habits` | Habits | Weekly grid, streaks |
| `view-planner` | Planner | 7-column weekly grid, quick-add per day |
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
- [x] Dashboard with all 6 views
- [x] Full task CRUD with Supabase
- [x] Pomodoro timer with SVG ring, modes, session dots, audio cue
- [x] Habits with weekly grid + streak tracking
- [x] Weekly Planner (7-column grid, quick-add per day)
- [x] Customize panel (theme, color, font, density, effects toggles)
- [x] Dark mode + 6 color themes + font themes + density
- [x] Sidebar particles canvas animation
- [x] Fluid animations: view transitions, task slide-in, check pop, habit day pop, pomodoro ring glow

## Not Yet Built
- [ ] Focus analytics / stats view
- [ ] Focus mode (distraction-free fullscreen)
- [ ] Study Group plan features
- [ ] Stripe payment integration (test links exist in index.html, not wired)
- [ ] Weekly planner: drag-to-reschedule tasks
- [ ] Course management UI (courses created during onboarding only)

---

## How to Start a Claude Code Session
Always launch Claude Code from inside the repo root:
```bash
cd kolimoli1.github.io   # or wherever you cloned it
claude
```
Claude Code will auto-read this CLAUDE.md and have full project context. Never run it from outside the repo folder.

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
- **ui-styling** — Load for shadcn/ui components, Tailwind customization, or canvas design system work.
- **design** — Load for logo, icon, or slide design tasks.
- **design-system** — Load for design tokens, component specs, or token architecture decisions.
- **brand** — Load for brand consistency checks or guideline work.
