import { chromium, devices } from '@playwright/test';
import { createServer } from 'http';
import { readFileSync, statSync } from 'fs';
import { resolve, extname, join } from 'path';
import { mkdirSync } from 'fs';

const ROOT = '/opt/personal/git/endometrioza';
const PORT = 5599;
const OUT = '/tmp/endo-tests/shots';
mkdirSync(OUT, { recursive: true });

const MIME = { '.html':'text/html', '.js':'application/javascript', '.css':'text/css', '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg' };
const srv = createServer((req,res)=>{
  let p = req.url.split('?')[0]; if(p==='/')p='/index.html';
  const f = resolve(join(ROOT, p));
  if(!f.startsWith(ROOT)){ res.writeHead(403); return res.end(); }
  try { const b = readFileSync(f); res.writeHead(200,{'Content-Type':MIME[extname(f)]||'text/plain'}); res.end(b); }
  catch(e){ res.writeHead(404); res.end('nf'); }
}).listen(PORT);

const log = [];
function L(msg){ console.log(msg); log.push(msg); }

async function shot(page, name){
  const p = `${OUT}/${name}.png`;
  await page.screenshot({ path: p, fullPage: false });
  L(`  [shot] ${name}.png`);
}

async function measure(page, label){
  const m = await page.evaluate(()=>{
    const box = document.getElementById('yt-box');
    const br = box.getBoundingClientRect();
    const iframe = document.getElementById('yt-player');
    const ir = iframe.getBoundingClientRect();
    const ctrl = document.getElementById('yt-audio-ctrl');
    const cr = ctrl.getBoundingClientRect();
    const acBtns = document.querySelector('.ac-btns');
    const ar = acBtns.getBoundingClientRect();
    const sn = document.getElementById('sn');
    const sr = sn.getBoundingClientRect();
    const acPlay = document.getElementById('ac-play');
    const pr = acPlay.getBoundingClientRect();
    const visible = (r)=> r.width>0 && r.height>0 && r.bottom>0 && r.top<innerHeight && r.right>0 && r.left<innerWidth;
    return {
      vp: {w: innerWidth, h: innerHeight},
      box: {top:br.top, bottom:br.bottom, w:br.width, h:br.height, vis:visible(br)},
      iframe: {top:ir.top, bottom:ir.bottom, w:ir.width, h:ir.height, vis:visible(ir), ratio: ir.width>0 ? (ir.height/ir.width).toFixed(3) : 'n/a'},
      ctrl: {top:cr.top, bottom:cr.bottom, h:cr.height, vis:visible(cr)},
      acBtns: {top:ar.top, bottom:ar.bottom, h:ar.height, vis:visible(ar)},
      acPlay: {top:pr.top, bottom:pr.bottom, w:pr.width, h:pr.height, vis:visible(pr)},
      pill: {top:sr.top, right:sr.right, left:sr.left, w:sr.width, h:sr.height, vis:visible(sr)}
    };
  });
  L(`[${label}] vp=${m.vp.w}x${m.vp.h}`);
  L(`  box: ${Math.round(m.box.w)}x${Math.round(m.box.h)} @y=${Math.round(m.box.top)}-${Math.round(m.box.bottom)} vis=${m.box.vis}`);
  L(`  iframe: ${Math.round(m.iframe.w)}x${Math.round(m.iframe.h)} ratio=${m.iframe.ratio} vis=${m.iframe.vis}`);
  L(`  audio-ctrl: h=${Math.round(m.ctrl.h)} y=${Math.round(m.ctrl.top)}-${Math.round(m.ctrl.bottom)} vis=${m.ctrl.vis}`);
  L(`  ac-btns: h=${Math.round(m.acBtns.h)} vis=${m.acBtns.vis}`);
  L(`  ac-play: ${Math.round(m.acPlay.w)}x${Math.round(m.acPlay.h)} vis=${m.acPlay.vis}`);
  L(`  pill: @y=${Math.round(m.pill.top)} right=${Math.round(m.pill.right)} vis=${m.pill.vis}`);
  return m;
}

const browser = await chromium.launch();

async function zcheck(page, label){
  const z = await page.evaluate(()=>{
    const sn = document.getElementById('sn');
    const box = document.getElementById('yt-box');
    const sr = sn.getBoundingClientRect();
    const br = box.getBoundingClientRect();
    // Does pill overlap box?
    const overlap = !(sr.right<=br.left||sr.left>=br.right||sr.bottom<=br.top||sr.top>=br.bottom);
    // Which is on top at pill center?
    const cx = sr.left+sr.width/2, cy = sr.top+sr.height/2;
    const top = document.elementFromPoint(cx, cy);
    return { overlap, topId: top ? (top.id||top.className||top.tagName) : null, snZ: getComputedStyle(sn).zIndex, boxZ: getComputedStyle(box).zIndex };
  });
  L(`[${label}] overlap=${z.overlap} elemAtPillCenter=${z.topId} snZ=${z.snZ} boxZ=${z.boxZ}`);
}

async function touchLongPress(page, selector){
  // Trigger tooltip via real touch events; verify ripple + tip-portal show
  const info = await page.evaluate((sel)=>{
    const el = document.querySelector(sel);
    const r = el.getBoundingClientRect();
    return { x: r.left+r.width/2, y: r.top+r.height/2 };
  }, selector);
  const client = await page.context().newCDPSession(page);
  await client.send('Input.dispatchTouchEvent', { type:'touchStart', touchPoints:[{x:info.x,y:info.y}] });
  // Sample ripple class at 200ms
  await page.waitForTimeout(200);
  const mid = await page.evaluate((sel)=>document.querySelector(sel).classList.contains('ripping'), selector);
  await page.waitForTimeout(400); // total ~600ms
  const tipShown = await page.evaluate(()=>{
    const tp = document.querySelector('.tip-portal');
    return tp ? tp.classList.contains('show') : false;
  });
  await client.send('Input.dispatchTouchEvent', { type:'touchEnd', touchPoints:[] });
  await page.waitForTimeout(100);
  L(`  touch long-press ${selector}: ripple@200ms=${mid}, tipShown@600ms=${tipShown}`);
}

// ===== MOBILE iPhone 12 =====
L('\n===== MOBILE (iPhone 12, 390x844) =====');
{
  const ctx = await browser.newContext({ ...devices['iPhone 12'] });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);
  await measure(page, 'mobile initial');
  await zcheck(page, 'mobile z-index');
  await shot(page, 'mobile-1-initial');
  // Touch long-press: ripple + tooltip
  await touchLongPress(page, '#sn-menu');
  await shot(page, 'mobile-1b-touch-tip');
  
  // Tap the pill to open menu
  await page.tap('#sn-menu').catch(()=>{});
  await page.waitForTimeout(400);
  await measure(page, 'mobile menu open');
  await shot(page, 'mobile-2-menu');
  await page.tap('#sn-menu').catch(()=>{});
  await page.waitForTimeout(300);
  
  // Tap top bar to force bars, then tap audio toggle
  await page.evaluate(()=>document.getElementById('yt-box').classList.add('bars'));
  await page.waitForTimeout(400);
  await shot(page, 'mobile-3-bars');
  await page.tap('#yt-audio').catch(()=>{});
  await page.waitForTimeout(600);
  await measure(page, 'mobile audio mode');
  await shot(page, 'mobile-4-audio');
  
  // Back to video
  await page.tap('#yt-audio').catch(()=>{});
  await page.waitForTimeout(600);
  await measure(page, 'mobile back to video');
  await shot(page, 'mobile-5-video-again');
  
  // Scroll down to see if pill stays put
  await page.evaluate(()=>scrollTo(0,800));
  await page.waitForTimeout(400);
  await shot(page, 'mobile-6-scrolled');
  await page.evaluate(()=>scrollTo(0,0));
  await page.waitForTimeout(200);
  
  // Touch drag the pill on mobile + menu follows
  await page.tap('#sn-menu');
  await page.waitForTimeout(300);
  const grip2 = await page.locator('#sn-grip').boundingBox();
  const client = await page.context().newCDPSession(page);
  await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:grip2.x+grip2.width/2,y:grip2.y+grip2.height/2}]});
  for(const [x,y] of [[300,250],[180,300],[60,350]]){
    await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y}]});
    await page.waitForTimeout(100);
  }
  await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await page.waitForTimeout(300);
  await menuSideCheck(page, 'mobile after touch-drag to left');
  await shot(page, 'mobile-7-touch-drag-menu-follows');
  
  await ctx.close();
}

async function menuSideCheck(page, label){
  const m = await page.evaluate(()=>{
    const sn = document.getElementById('sn');
    const sl = document.getElementById('sn-list');
    if(!sl.classList.contains('open')) return { open:false };
    const sr = sn.getBoundingClientRect();
    const lr = sl.getBoundingClientRect();
    const pillCx = sr.left + sr.width/2;
    const listCx = lr.left + lr.width/2;
    const side = listCx < pillCx ? 'left' : 'right';
    // Check menu is touching pill (adjacent within 30px gap)
    const gap = side==='left' ? (sr.left - lr.right) : (lr.left - sr.right);
    return { open:true, side, gap: Math.round(gap), listX: Math.round(lr.left), pillX: Math.round(sr.left), pillW: Math.round(sr.width), vw: innerWidth };
  });
  L(`  [${label}] menu ${m.open?`side=${m.side} gap=${m.gap}px listX=${m.listX} pillX=${m.pillX}`:'(closed)'}`);
  return m;
}

// ===== DESKTOP =====
L('\n===== DESKTOP (1440x900) =====');
{
  const ctx = await browser.newContext({ viewport: {width:1440, height:900} });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${PORT}/`);
  await page.waitForTimeout(1500);
  await measure(page, 'desktop initial');
  await zcheck(page, 'desktop z-index');
  await shot(page, 'desktop-1-initial');
  // Hover tip: ripple + tooltip
  await page.hover('#sn-menu');
  await page.waitForTimeout(200);
  const ripMid = await page.evaluate(()=>document.querySelector('#sn-menu').classList.contains('ripping'));
  await page.waitForTimeout(400);
  const tipOn = await page.evaluate(()=>{ const tp=document.querySelector('.tip-portal'); return tp?tp.classList.contains('show'):false; });
  L(`  hover #sn-menu: ripple@200ms=${ripMid}, tipShown@600ms=${tipOn}`);
  await shot(page, 'desktop-1b-hover-tip');
  await page.mouse.move(10, 10);
  await page.waitForTimeout(250);
  
  // Open pill menu via click
  await page.click('#sn-menu');
  await page.waitForTimeout(400);
  await measure(page, 'desktop menu open');
  await shot(page, 'desktop-2-menu');
  await page.click('#sn-menu');
  await page.waitForTimeout(300);
  
  // Hover pill to expand grip/reset
  await page.hover('#sn');
  await page.waitForTimeout(500);
  await shot(page, 'desktop-3-pill-hover');
  
  // Scenario A: open menu first, THEN drag pill — menu should FOLLOW
  await page.click('#sn-menu');
  await page.waitForTimeout(300);
  await menuSideCheck(page, 'before drag (right edge)');
  await page.hover('#sn');
  await page.waitForTimeout(200);
  let grip = await page.locator('#sn-grip').boundingBox();
  await page.mouse.move(grip.x + grip.width/2, grip.y + grip.height/2);
  await page.mouse.down();
  // Drag slowly toward LEFT edge — menu should flip to right side of pill
  for(const [x,y] of [[1000,300],[700,400],[400,450],[120,500]]){ await page.mouse.move(x,y,{steps:8}); await page.waitForTimeout(120); }
  await page.mouse.up();
  await page.waitForTimeout(350);
  await shot(page, 'desktop-4a-menu-follows-to-left');
  await menuSideCheck(page, 'after drag to left edge');
  // Drag back to right edge
  grip = await page.locator('#sn-grip').boundingBox();
  await page.mouse.move(grip.x + grip.width/2, grip.y + grip.height/2);
  await page.mouse.down();
  for(const [x,y] of [[500,500],[900,400],[1350,300]]){ await page.mouse.move(x,y,{steps:8}); await page.waitForTimeout(120); }
  await page.mouse.up();
  await page.waitForTimeout(350);
  await shot(page, 'desktop-4b-menu-flipped-back');
  await menuSideCheck(page, 'after drag back to right');
  await page.click('#sn-menu'); // close
  await page.waitForTimeout(200);
  
  // Scenario B: reset fade — drag player then check reset opacity
  const boxBox = await page.locator('#yt-box').boundingBox();
  const resetOpacityBefore = await page.evaluate(()=>getComputedStyle(document.getElementById('yt-reset')).opacity);
  L(`  reset opacity before drag: ${resetOpacityBefore}`);
  const drag = await page.locator('#yt-drag').boundingBox();
  await page.mouse.move(drag.x + drag.width/2, drag.y + drag.height/2);
  await page.mouse.down();
  await page.mouse.move(drag.x + 50, drag.y + 100, {steps: 8});
  await page.mouse.up();
  await page.waitForTimeout(400);
  const resetOpacityAfter = await page.evaluate(()=>getComputedStyle(document.getElementById('yt-reset')).opacity);
  L(`  reset opacity after drag: ${resetOpacityAfter}`);
  await shot(page, 'desktop-5-player-dragged-reset-visible');
  
  // Scenario C: resize player via SE corner
  const rz = await page.locator('#yt-rz').boundingBox();
  await page.mouse.move(rz.x + rz.width/2, rz.y + rz.height/2);
  await page.mouse.down();
  await page.mouse.move(rz.x + 200, rz.y + 150, {steps: 8});
  await page.mouse.up();
  await page.waitForTimeout(200);
  await shot(page, 'desktop-6-player-resized');
  
  await ctx.close();
}

// ===== NARROW MOBILE (iPhone SE, 375x667) =====
L('\n===== NARROW MOBILE (iPhone SE, 375x667) =====');
{
  const ctx = await browser.newContext({ ...devices['iPhone SE'] });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${PORT}/`);
  await page.waitForTimeout(1500);
  await measure(page, 'iphone-se initial');
  await shot(page, 'se-1-initial');
  await page.evaluate(()=>document.getElementById('yt-box').classList.add('bars'));
  await page.waitForTimeout(300);
  await page.tap('#yt-audio').catch(()=>{});
  await page.waitForTimeout(600);
  await measure(page, 'iphone-se audio');
  await shot(page, 'se-2-audio');
  await ctx.close();
}

await browser.close();
srv.close();
import('fs').then(fs=>fs.writeFileSync('/tmp/endo-tests/report.txt', log.join('\n')));
console.log('\nDONE. Screenshots in '+OUT);
