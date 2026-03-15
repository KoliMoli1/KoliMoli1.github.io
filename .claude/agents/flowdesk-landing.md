---
name: flowdesk-landing
description: Use for any work on index.html — hero, pricing, testimonials, GSAP animations, aurora background, or Stripe buy buttons on the landing page.
---

# FlowDesk Landing Page Agent

## Scope
`index.html` only. Never touch other files.

## What's on This Page
- Hero section with aurora WebGL background
- Custom cursor animation
- Features/benefits sections
- Testimonials
- Pricing section with Stripe buy buttons (test mode)
- GSAP ScrollTrigger animations throughout

## GSAP Policy
**GSAP 3.12.5 + ScrollTrigger are ALLOWED here and ONLY here.**
Do not add GSAP to any other file. When editing animations, keep the existing GSAP version — do not upgrade without explicit instruction.

## Hardcoded Marketing Stats
These are intentional — **never flag as bugs**:
- 42k+ students
- 2.1M tasks completed
- 98% satisfaction rate

These exist as marketing copy and will remain static until the team explicitly decides to wire them to real data.

## Stripe Buy Buttons
- Test mode only — not connected to real subscription logic
- Do not wire buy buttons to backend logic without explicit instruction
- Stripe products and webhooks are not yet configured

## Project Constraints
- Vanilla JS only — no new dependencies ever
- Single-file constraint — all CSS/JS stays inside index.html
- Never rewrite the whole file — targeted diffs only
- Return 4 labeled blocks when adding a full feature: **CSS**, **HTML**, **Nav item**, **JS**
- GSAP is the only allowed library here

## Design System
CSS vars: `--ink`, `--paper`, `--cream`, `--sage`, `--sage-light`, `--sage-dark`, `--amber`, `--coral`, `--muted`, `--border`
Fonts: `--font-display: 'Instrument Serif'`, `--font-body: 'DM Sans'`
Cards: `border-radius: 14px`, `background: var(--cream)`, `border: 1px solid var(--border)`
Buttons: `background: var(--sage)`, `border-radius: 100px`

## UX Minimums
- 4.5:1 contrast ratio minimum
- 44×44px touch targets
- 8px minimum spacing
- Visible focus rings on all interactive elements
- No emoji as icons
- Animation duration 150–300ms for UI transitions (GSAP scroll animations are exempt)

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- GSAP animation structure changes significantly
- New sections added to the page
- A decision is made on whether marketing stats become real data
- Stripe buy buttons are wired to real logic
