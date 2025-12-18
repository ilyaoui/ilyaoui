/**
 * Manual API Test Script
 *
 * Use this to test API endpoints directly
 */

import { chromium } from '@playwright/test';

async function testAPI() {
  const url = process.argv[2] || 'https://basketball.exposureevents.com/260605/2025-christmas-classic-rec-only/schedule';

  console.log('🔍 Analyzing network calls for:', url);

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  const apiCalls: any[] = [];

  // Intercept all requests
  page.on('request', (request) => {
    const url = request.url();
    const method = request.method();

    console.log(`📤 ${method} ${url}`);
  });

  // Intercept all responses
  page.on('response', async (response) => {
    const url = response.url();
    const status = response.status();
    const contentType = response.headers()['content-type'] || '';

    if (contentType.includes('application/json')) {
      try {
        const data = await response.json();
        console.log(`\n✅ API FOUND!`);
        console.log(`   URL: ${url}`);
        console.log(`   Status: ${status}`);
        console.log(`   Method: ${response.request().method()}`);
        console.log(`   Data keys: ${Object.keys(data).join(', ')}`);

        // Check if it looks like schedule data
        const jsonStr = JSON.stringify(data).toLowerCase();
        if (jsonStr.includes('game') || jsonStr.includes('match') ||
            jsonStr.includes('schedule') || jsonStr.includes('team')) {
          console.log(`   🎯 LOOKS LIKE SCHEDULE DATA!`);
          apiCalls.push({
            url,
            method: response.request().method(),
            status,
            dataKeys: Object.keys(data),
            sampleData: data,
          });
        }
      } catch {
        // Not JSON or parse error
      }
    }
  });

  // Navigate to page
  await page.goto(url, { waitUntil: 'networkidle' });

  console.log('\n⏳ Waiting for page to load...');
  await page.waitForTimeout(5000);

  // Try clicking schedule buttons
  console.log('\n🖱️ Looking for Schedule buttons...');
  const scheduleSelectors = [
    'a:has-text("Schedule")',
    'button:has-text("Schedule")',
    '[href*="schedule"]',
  ];

  for (const selector of scheduleSelectors) {
    try {
      const elements = await page.$$(selector);
      console.log(`   Found ${elements.length} elements: ${selector}`);

      if (elements.length > 0) {
        console.log(`   Clicking first element...`);
        await elements[0].click();
        await page.waitForTimeout(3000);
      }
    } catch (error) {
      console.log(`   Error: ${error}`);
    }
  }

  console.log('\n📊 Summary:');
  console.log(`   Total API calls found: ${apiCalls.length}`);

  if (apiCalls.length > 0) {
    console.log('\n🎯 API Endpoints to use:');
    apiCalls.forEach((call, i) => {
      console.log(`\n${i + 1}. ${call.method} ${call.url}`);
      console.log(`   Data structure: ${call.dataKeys.slice(0, 5).join(', ')}`);
    });
  } else {
    console.log('\n❌ No API endpoints found. Site might use HTML rendering.');
  }

  console.log('\nPress Ctrl+C to exit...');
  await new Promise(() => {}); // Keep browser open
}

testAPI().catch(console.error);
