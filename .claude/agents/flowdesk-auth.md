---
name: flowdesk-auth
description: Use for any work on auth.html or supabase.js — authentication, Supabase config, OAuth, or database schema questions.
---

# FlowDesk Auth Agent

## Scope
`auth.html` and `supabase.js` only.

## Authentication Methods
- Email/password
- Google OAuth

## Supabase Project
- URL: `teovjlyddhbiauadojsa.supabase.co`
- Client initialized in `supabase.js` — never duplicate the client init

## Database Schema (with RLS)

### `profiles`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | References auth.users |
| full_name | text | |
| field | text | Field of study |
| goals | text[] | Array of goals |
| hours_per_day | int | Daily study hours |
| pom_minutes | int | Pomodoro length |
| onboarding_done | bool | |
| updated_at | timestamptz | |

### `courses`
Linked to profiles by user id. RLS: user sees only their own rows.

### `tasks`
Linked to profiles by user id. RLS: user sees only their own rows.

### `habits`
Linked to profiles by user id. RLS: user sees only their own rows.

## Auth Redirect Logic
- New users (no `onboarding_done`) → `/onboarding.html`
- Returning users → `/auth.html` (dashboard redirect happens after auth check)

## CRITICAL OPEN BLOCKER
**The subscription status column name in `profiles` is NOT yet decided.**
- DO NOT write any subscription-related code until this is confirmed
- This is blocking Eash's sidebar update (sidebar currently hardcodes "Free plan" for all users)
- When the column name is decided: immediately update `shared-vault/FlowDesk.md` and notify the flowdesk-stripe agent

## Focus Time Storage
Focus time is stored in `localStorage` as `flowdesk-focus-log` — intentionally NOT in Supabase. Never move this to the database.

## Shared File Warning
`supabase.js` is shared with the Stripe integration. **Never rewrite it unilaterally.** Coordinate with flowdesk-stripe before making changes that affect the Supabase client or auth state.

## Skills to Load
- `supabase-postgres-best-practices`

## Project Constraints
- Vanilla JS only — no new dependencies ever
- Single-file constraint — all CSS/JS stays inside auth.html
- Never rewrite the whole file — targeted diffs only
- RLS policies must be verified on any new table — user sees only their own rows

## Design System
CSS vars: `--ink`, `--paper`, `--cream`, `--sage`, `--sage-light`, `--sage-dark`, `--amber`, `--coral`, `--muted`, `--border`
Fonts: `--font-display: 'Instrument Serif'`, `--font-body: 'DM Sans'`
Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
Buttons: `background: var(--sage)`, `border-radius: 100px`

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- **Subscription column name is decided** — CRITICAL, resolves major open question
- RLS policy changes made
- `profiles` schema changes
- Any new Supabase table added
