const { test, expect } = require('@playwright/test');

test.use({ channel: 'chrome', viewport: { width: 390, height: 844 } });

test('complete primary prototype flow without browser errors', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });

  await page.goto('http://127.0.0.1:8765/medicare-ai-mobile-app-prototype.html');
  await expect(page.locator('#overlay-splash')).toHaveClass(/active/);
  await page.locator('#splashContinueBtn').click();
  await expect(page.locator('#onbContinueBtn')).toBeDisabled();
  await page.locator('#consentRow').click();
  await expect(page.locator('#onbContinueBtn')).toBeEnabled();
  await page.locator('#onbContinueBtn').click();

  await page.locator('#homeCtaCard').click();
  await expect(page.locator('#overlay-wizard')).toHaveClass(/active/);
  await page.locator('#wizardNextBtn').click();
  await page.locator('[data-symptom="fever"]').click();
  await page.locator('[data-symptom="chest_pain"]').click();
  await page.locator('#wizardNextBtn').click();
  await page.locator('[data-group="bp"] button[data-val="high"]').click();
  await page.locator('#wizardNextBtn').click();

  await expect(page.locator('#overlay-results')).toHaveClass(/active/, { timeout: 4000 });
  await expect(page.locator('#resultDisease')).not.toHaveText('');
  await expect(page.locator('#diffList .diff-row')).toHaveCount(5);
  await expect(page.locator('#resultsFindCareBtn')).toBeVisible();
  await page.locator('#viewMedsBtn').click();
  await expect(page.locator('#medsList .med-card')).not.toHaveCount(0);
  await page.locator('#medsBackToResultsBtn').click();
  await page.locator('#resultsCloseBtn').click();
  await expect(page.locator('#historyTimeline .history-row')).toHaveCount(1);

  await page.locator('.nav-item[data-tab="care"]').click();
  await page.locator('#clinicsList .clinic-row').first().click();
  await page.locator('#openBookModalBtn').click();
  await page.locator('#bookDaySegmented button[data-val="tomorrow"]').click();
  await page.locator('#bookSlotsGrid .slot-btn').nth(1).click();
  await page.locator('#confirmBookingBtn').click();
  await expect(page.locator('#appointmentsCard')).toBeVisible();
  await page.locator('#cancelApptBtn').click();
  await expect(page.locator('#appointmentsCard')).toBeHidden();

  console.log(await page.evaluate(() => JSON.stringify((() => {
    const nav = document.querySelector('.nav-item[data-tab="settings"]');
    const rect = nav.getBoundingClientRect();
    return {
      overlays: [...document.querySelectorAll('.overlay')].map(el => ({ id: el.id, className: el.className, rect: el.getBoundingClientRect().toJSON() })),
      navRect: rect.toJSON(),
      hitStack: document.elementsFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2).map(el => `${el.id || el.className || el.tagName}`)
    };
  })())));
  await page.locator('.nav-item[data-tab="settings"]').click();
  await page.locator('#darkToggle').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

  expect(errors).toEqual([]);
});

test('survives malformed saved browser data', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('http://127.0.0.1:8765/medicare-ai-mobile-app-prototype.html');
  await page.evaluate(() => {
    localStorage.setItem('medicare_history', '{}');
    localStorage.setItem('medicare_appointments', 'null');
  });
  await page.reload();
  expect(errors).toEqual([]);
});
