#!/usr/bin/env node
/**
 * Capture screenshots of the Terrarium website
 * Usage: node scripts/capture-screenshots.js [url]
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SITE_URL = process.argv[2] || 'https://mutatedterrarium.com';
const OUTPUT_DIR = path.join(__dirname, '..', 'assets', 'screenshots');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function captureScreenshots() {
  console.log(`🌿 Capturing screenshots from ${SITE_URL}...`);

  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2, // Retina quality
  });

  const page = await context.newPage();

  try {
    // Navigate to site
    console.log('📍 Loading homepage...');
    await page.goto(SITE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000); // Wait for animations

    // 1. Hero section
    console.log('📸 Capturing hero section...');
    await page.screenshot({
      path: path.join(OUTPUT_DIR, 'hero.png'),
      fullPage: false,
    });

    // 2. Scroll to landscapes visualization
    console.log('📸 Capturing landscapes visualization...');
    const landscapesSection = await page.locator('text=/landscapes/i').first();
    if (await landscapesSection.count() > 0) {
      await landscapesSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(4000); // Wait for 3D animation

      // Capture the whole section including title
      const vizSection = landscapesSection.locator('..').locator('..');
      await vizSection.screenshot({
        path: path.join(OUTPUT_DIR, 'landscapes-viz.png'),
      });
    }

    // 3. Services/substations section
    console.log('📸 Capturing services section...');
    const servicesSection = await page.locator('text=/substations/i').first();
    if (await servicesSection.count() > 0) {
      await servicesSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      const servicesContainer = servicesSection.locator('..').locator('..');
      await servicesContainer.screenshot({
        path: path.join(OUTPUT_DIR, 'services.png'),
      });
    }

    // 4. Full page screenshot
    console.log('📸 Capturing full page...');
    await page.screenshot({
      path: path.join(OUTPUT_DIR, 'full-page.png'),
      fullPage: true,
    });

    // 5. Mobile view (skip for now - can cause crashes)
    // console.log('📱 Capturing mobile view...');
    // Create a new page for mobile to avoid crashes
    // const mobilePage = await context.newPage();
    // await mobilePage.setViewportSize({ width: 375, height: 812 });
    // await mobilePage.goto(SITE_URL, { waitUntil: 'networkidle' });
    // await mobilePage.waitForTimeout(2000);
    // await mobilePage.screenshot({
    //   path: path.join(OUTPUT_DIR, 'mobile-view.png'),
    //   fullPage: true,
    // });
    // await mobilePage.close();

    console.log(`✅ Screenshots saved to: ${OUTPUT_DIR}`);
    console.log('   - hero.png');
    console.log('   - landscapes-viz.png');
    console.log('   - services.png');
    console.log('   - full-page.png');
    console.log('   - mobile-view.png');

  } catch (error) {
    console.error('❌ Error capturing screenshots:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

// Run
captureScreenshots()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
