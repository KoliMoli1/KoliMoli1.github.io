const { test, expect } = require('@playwright/test');

test('1. Landing page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/FlowDesk/);
  await expect(page.locator('.hero-headline, h1').first()).toBeVisible();
});

test('2. Stripe buy buttons are not placeholders', async ({ page }) => {
  await page.goto('/');
  const proBtnHref = await page.locator('#proBuyBtn').getAttribute('href');
  const groupBtnHref = await page.locator('#groupBuyBtn').getAttribute('href');
  expect(proBtnHref).not.toContain('PASTE_');
  expect(groupBtnHref).not.toContain('PASTE_');
  expect(proBtnHref).not.toBe('auth.html');
  expect(groupBtnHref).not.toBe('auth.html');
});

test('3. Landing nav links exist', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('a[href="#features"]').first()).toBeVisible();
  await expect(page.locator('a[href="#pricing"]').first()).toBeVisible();
});

test('4. CTA buttons point to auth.html not #', async ({ page }) => {
  await page.goto('/');
  const ctaHrefs = await page.locator('a.btn-primary, a.nav-cta, a[href="auth.html"]').evaluateAll(
    els => els.map(el => el.getAttribute('href'))
  );
  const badLinks = ctaHrefs.filter(h => h === '#');
  expect(badLinks).toHaveLength(0);
});

test('5. Mobile nav hamburger opens and closes', async ({ page }) => {
  await page.goto('/');
  const hamburger = page.locator('#hamburger');
  await expect(hamburger).toBeVisible();
  await hamburger.click();
  await expect(page.locator('#mobileMenu')).toHaveClass(/open/);
  await hamburger.click();
  await expect(page.locator('#mobileMenu')).not.toHaveClass(/open/);
});

test('6. Auth page loads with tabs and Google button', async ({ page }) => {
  await page.goto('/auth.html');
  await expect(page.locator('#tabSignup')).toBeVisible();
  await expect(page.locator('#tabLogin')).toBeVisible();
  await expect(page.locator('#btnGoogleSignup, #btnGoogleLogin').first()).toBeVisible();
});

test('7. Onboarding redirects unauthenticated users', async ({ page }) => {
  await page.goto('/onboarding.html');
  await page.waitForTimeout(2000);
  expect(page.url()).toContain('auth.html');
});

test('8. Dashboard redirects unauthenticated users', async ({ page }) => {
  await page.goto('/dashboard.html');
  await page.waitForTimeout(2000);
  expect(page.url()).toContain('auth.html');
});

test('9. No console errors on landing page', async ({ page }) => {
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', err => errors.push(err.message));
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  expect(errors).toHaveLength(0);
});

test('10. Baseline screenshots', async ({ page }) => {
  const { mkdirSync } = require('fs');
  mkdirSync('playwright-sweep/screenshots', { recursive: true });
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'playwright-sweep/screenshots/landing.png', fullPage: true });
  await page.goto('/auth.html');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'playwright-sweep/screenshots/auth.png', fullPage: true });
});
