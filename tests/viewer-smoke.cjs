const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2] || 'http://127.0.0.1:8000');
 await page.waitForSelector('.board');

 assert.match(await page.locator('#status').innerText(),/Recorded neural inference/);
 await page.selectOption('#compare','astra-v2-seed-73.json');await page.waitForSelector('.paired .board');
 assert.equal(await page.locator('.board').count(),2);
 assert.match(await page.locator('#status').innerText(),/% of weights changed/);
 await page.click('[data-mode="features"]');assert.match(await page.locator('#detail').innerText(),/Candidates by score/);
 await page.click('[data-mode="weights"]');assert.match(await page.locator('#detail').innerText(),/W3/);
 await page.click('#next');assert.match(await page.locator('#counter').innerText(),/^2 /);
 await page.selectOption('#speed','4');await page.click('#play');await page.waitForTimeout(900);await page.click('#play');
 assert.ok(parseInt(await page.locator('#counter').innerText())>2);
 await page.selectOption('#compare','');await page.selectOption('#recording','heuristic-baseline.json');
 await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('baseline gameplay'));
 await page.click('[data-mode="network"]');await page.fill('#seek','47');assert.match(await page.locator('#counter').innerText(),/48 \/ 48/);
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 if(!process.argv.includes('--published')){
   const files=page.locator('#file');
   await files.setInputFiles(require('node:path').join(__dirname,'../viewer/data/fixture-b.json'));
   await page.waitForFunction(()=>document.querySelector('#recording').value.startsWith('local:'));
   assert.match(await page.locator('#readout').innerText(),/Fixture B/);
   await page.selectOption('#compare','fixture-a.json');
   await page.waitForSelector('.paired .board');
   await files.setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{}')});
   await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('Import failed'));
   assert.equal(await page.locator('#recording option').count(),6);
   await page.click('#next');
   assert.match(await page.locator('#counter').innerText(),/^2 /);
 }
 assert.deepEqual(errors,[]);await browser.close();console.log('Browser smoke passed: playback, seek, speed, paired boards, inspection, baseline, mobile, no page errors.');
})().catch(e=>{console.error(e);process.exit(1)});
