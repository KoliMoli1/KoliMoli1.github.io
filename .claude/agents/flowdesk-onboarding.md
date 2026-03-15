---
name: flowdesk-onboarding
description: Use for any work on onboarding.html — the 4-step new user flow, field/course/goals/pomodoro setup, or Supabase writes from onboarding.
---

# FlowDesk Onboarding Agent

## Scope
`onboarding.html` only.

## The 4-Step Flow
| Step | Content |
|------|---------|
| 1 | Field of study |
| 2 | Courses (up to 8) |
| 3 | Goals |
| 4 | Daily study hours + pomodoro length |

## Supabase Writes
- Step 1–4 results saved to `profiles` table
- Step 2 courses saved to `courses` table
- Uses auth state from `supabase.js` — **do not duplicate the client init**

## Critical Rules
- **Always use `escapeHtml()`** for any `renderCourses()` innerHTML — user input goes directly into the DOM here
- Auth guard: only logged-in users can see onboarding; unauthenticated users redirect to auth.html
- After successful onboarding, set `onboarding_done = true` on the profile and redirect to dashboard

## Project Constraints
- Vanilla JS only — no new dependencies ever
- Single-file constraint — all CSS/JS stays inside onboarding.html
- Never rewrite the whole file — targeted diffs only
- Return 4 labeled blocks when adding a full feature: **CSS**, **HTML**, **Nav item**, **JS**
- Date strings must use local time — never `toISOString()`

## Design System
CSS vars: `--ink`, `--paper`, `--cream`, `--sage`, `--sage-light`, `--sage-dark`, `--amber`, `--coral`, `--muted`, `--border`
Fonts: `--font-display: 'Instrument Serif'`, `--font-body: 'DM Sans'`
Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
Buttons: `background: var(--sage)`, `border-radius: 100px`
Themes: `data-theme`, `data-color`, `data-font`, `data-density` on `<html>`

## UX Minimums
- 4.5:1 contrast ratio minimum
- 44×44px touch targets
- 8px minimum spacing
- Visible focus rings on all interactive elements
- No emoji as icons
- Animation duration 150–300ms only

## Skills to Load
- `full-output-enforcement`
- `design-taste-frontend`

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- Onboarding flow changes significantly (steps added/removed/reordered)
- Any connection to Stripe or subscription status is added
- New fields added to the `profiles` or `courses` write
