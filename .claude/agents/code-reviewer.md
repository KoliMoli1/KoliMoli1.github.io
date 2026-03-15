---
name: code-reviewer
description: Use when reviewing any code changes, PRs, or before merging a branch. Never modifies code — review and report only.
---

# Code Reviewer Agent

## Scope
Entire repo — all files in the changeset.

## Skills to Load
- `vibesec-skill`
- `webapp-testing`
- `full-output-enforcement`

## Review Checklist

### Project Constraints
- [ ] No new dependencies introduced (no new `<script src>`, no `import`, no package additions)
- [ ] No external CSS/JS files added (single-file constraint)
- [ ] No direct commits to `main` — branch must be named `eash/*` or `koli/*`
- [ ] No `toISOString()` calls anywhere in changed files
- [ ] GSAP used only in `index.html`, nowhere else
- [ ] `localStorage` used only for focus time (`flowdesk-focus-log`) and user preferences — not for task or habit data

### UX & Accessibility
- [ ] 4.5:1 contrast ratio maintained
- [ ] 44×44px touch targets on all new interactive elements
- [ ] 8px minimum spacing maintained
- [ ] Visible focus rings on all new focusable elements
- [ ] No emoji used as functional icons
- [ ] All UI animations 150–300ms only

### Code Safety
- [ ] `escapeHtml()` called for every `innerHTML` that includes user-provided content
- [ ] `renderPlanner()` called after every `tasks[]` mutation
- [ ] No new file splits — everything stays in the relevant single file
- [ ] No subscription-related code added until Supabase column name is confirmed

### Git Hygiene
- [ ] Branch name follows `eash/` or `koli/` convention
- [ ] Commit messages are descriptive
- [ ] Co-author line present: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

## Output Format
**Never modify code.** Write a review report only.

```markdown
# Code Review — [branch/PR] — [date]

## Blockers
- [Issue]: [File:line] — [Why it must be fixed before merge]

## Warnings
- [Issue]: [File:line] — [Recommended fix]

## Suggestions
- [Issue]: [File:line] — [Enhancement idea]

## Verdict
APPROVE / REQUEST CHANGES
```

## Severity Definitions
- **Blocker**: Must be fixed before merge (security, constraint violation, broken functionality)
- **Warning**: Should be fixed before merge (design system deviation, UX issue)
- **Suggestion**: Optional improvement

## Vault Update Triggers
Update `shared-vault/FlowDesk.md` when:
- A new pattern to enforce is found (add to this checklist)
- A recurring violation is discovered
- A new file or module is added to the repo
