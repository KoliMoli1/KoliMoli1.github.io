---
name: flowdesk-dashboard
description: Use for any work on dashboard.html — tasks, pomodoro, habits, planner, analytics, customize views, or JS/CSS inside the dashboard.
---

# FlowDesk Dashboard Agent

## Scope
`dashboard.html` only. Never touch other files.

## Views
- `view-dashboard` — overview stats
- `view-tasks` — task list
- `view-pomodoro` — timer
- `view-habits` — habit tracker
- `view-planner` — weekly planner
- `view-analytics` — focus analytics
- `view-customize` — theme/appearance settings

## Key Functions
- `switchView(viewId)` — handles all view transitions
- `renderTasks()` — rebuilds the task list from `tasks[]`
- `renderPlanner()` — rebuilds weekly planner; MUST be called after any `tasks[]` mutation
- `renderHabits()` — rebuilds habit grid
- `updateDashStats()` — refreshes dashboard overview counts
- `insertTask(task)`, `toggleTask(id)`, `deleteTask(id)` — task mutations
- `togglePom()`, `setPomMode(mode)` — pomodoro controls
- `restoreCustomize()` — restores theme settings from localStorage

## Global State
- `currentUser` — Supabase auth user object
- `profile` — row from `profiles` table
- `courses[]` — from `courses` table
- `tasks[]` — from `tasks` table; always call `renderPlanner()` after mutating
- `habits[]` — from `habits` table
- `focusSecondsToday` — accumulated from `flowdesk-focus-log` in localStorage

## localStorage Keys
| Key | Purpose |
|-----|---------|
| `flowdesk-theme` | light/dark |
| `flowdesk-color` | color scheme |
| `flowdesk-font` | font choice |
| `flowdesk-density` | compact/comfortable |
| `flowdesk-particles` | particles on/off |
| `flowdesk-animations` | animations on/off |
| `flowdesk-focus-log` | focus session log (local only, never in Supabase) |

## Project Constraints
- Vanilla JS only — no new dependencies ever
- Single-file constraint — all CSS/JS stays inside dashboard.html
- Never rewrite the whole file — targeted diffs only
- Return 4 labeled blocks when adding a full feature: **CSS**, **HTML**, **Nav item**, **JS**
- Date strings must use local time — never `toISOString()`
- Always call `renderPlanner()` after mutating `tasks[]`
- Always escape user content with `escapeHtml()` in innerHTML

## Design System
CSS vars: `--ink`, `--paper`, `--cream`, `--sage`, `--sage-light`, `--sage-dark`, `--amber`, `--coral`, `--muted`, `--border`, `--sidebar-w: 240px`
Fonts: `--font-display: 'Instrument Serif'`, `--font-body: 'DM Sans'`
Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
Buttons: `background: var(--sage)`, `border-radius: 100px`
Nav active: `background: var(--sage-light)` + 3px left bar via `::before`
Themes: `data-theme`, `data-color`, `data-font`, `data-density` on `<html>`

## UX Minimums
- 4.5:1 contrast ratio minimum
- 44×44px touch targets
- 8px minimum spacing
- Visible focus rings on all interactive elements
- No emoji as icons
- Animation duration 150–300ms only

## Known Issues
- Nav active state previously fixed — if it reappears, it's a view routing issue in `switchView()`

## Skills to Load
- `full-output-enforcement`
- `design-taste-frontend`

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- Structural bugs found/fixed
- New patterns established
- localStorage keys added or changed
- Nav/view routing changes made
