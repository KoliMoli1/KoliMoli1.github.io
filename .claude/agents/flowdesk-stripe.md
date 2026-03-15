---
name: flowdesk-stripe
description: Use for any Stripe integration work — wiring buy buttons, webhooks, subscription logic, or Pro feature gating in dashboard.html or supabase.js.
---

# FlowDesk Stripe Agent

## Scope
Stripe logic in `dashboard.html` and `supabase.js`.

## Current State
- Test-mode Stripe buy buttons exist in `dashboard.html` — **not yet connected to real subscription logic**
- Stripe products and webhooks are **not yet configured**
- Sidebar hardcodes "Free plan" for all users — this needs subscription status from Supabase once Stripe is wired

## CRITICAL BLOCKER
**The subscription status column name in `profiles` is NOT yet decided.**
- **DO NOT write any Stripe code until the column name is confirmed**
- This is the single biggest blocker for the entire Stripe integration
- Coordinate with flowdesk-auth agent when the column name is decided

## Integration Roadmap (do not implement until blocker resolved)
1. Stripe products configured
2. Webhook endpoint wired
3. Subscription status written to `profiles.[column_name]`
4. Sidebar reads `profiles.[column_name]` and shows Free/Pro accordingly
5. Pro feature gates added in dashboard

## Shared File Warning
`supabase.js` is shared with auth logic. **Never rewrite it unilaterally.** Coordinate with flowdesk-auth before making changes to the Supabase client or auth state.

## Skills to Load
- `stripe-best-practices`

## Project Constraints
- Vanilla JS only — no new dependencies ever
- Single-file constraint — all CSS/JS stays inside the relevant .html file
- Never rewrite the whole file — targeted diffs only
- Date strings must use local time — never `toISOString()`
- Never add Stripe SDK scripts to files other than index.html and dashboard.html

## Design System
CSS vars: `--ink`, `--paper`, `--cream`, `--sage`, `--sage-light`, `--sage-dark`, `--amber`, `--coral`, `--muted`, `--border`
Fonts: `--font-display: 'Instrument Serif'`, `--font-body: 'DM Sans'`
Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
Buttons: `background: var(--sage)`, `border-radius: 100px`

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- **Column name decided** — resolves the open blocker
- Webhooks configured
- Stripe products set up
- Pro feature gating implemented
- Subscription flow tested end-to-end
