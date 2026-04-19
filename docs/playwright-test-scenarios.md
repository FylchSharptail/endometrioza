# Playwright Regression Scenarios

Exhaustive manipulation matrix for the endo site. Each scenario has an ID `NN.mm`, a target profile set, and a pass criterion. The sweep script in `/tmp/endo-sweep/sweep.mjs` references these IDs.

## Profiles

| ID | Name | Viewport | DPR | isMobile | hasTouch | Notes |
|----|------|----------|-----|----------|----------|-------|
| P1 | desktop-1920 | 1920x1080 | 1 | no | no | wide desktop |
| P2 | desktop-1280 | 1280x800 | 1 | no | no | default desktop |
| P3 | laptop-1100 | 1100x700 | 1 | no | no | mobile-CSS breakpoint boundary |
| P4 | ipad-768 | 768x1024 | 2 | yes | yes | tablet portrait (preset) |
| P5 | ipad-landscape | 1024x768 | 2 | yes | yes | tablet landscape |
| P6 | iphone12 | 390x844 | 3 | yes | yes | preset |
| P7 | huawei-mate20 | 360x780 | 3 | yes | yes | custom, EMUI UA |
| P8 | small-phone-320 | 320x640 | 2 | yes | yes | narrowest supported |

## Convention

- **pass** = condition must hold for the scenario to be green
- **deform check** = all `#sn > button:not(#sn-grip):not(#sn-rst)` share identical width & height (within 0.5px), each is square (within 0.5px)
- **no-shift check** = main nav buttons remain at identical x,y (within 1px) before/after the interaction
- **no-hscroll** = `window.scrollTo(9999,0)` leaves `scrollX===0` and no element's `getBoundingClientRect().right > innerWidth + 1`

---

## 1. Load & initial render

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 1.1 | all | Navigate to `/?v=<stamp>`, wait networkidle | no page errors, no console errors except known YT iframe noise |
| 1.2 | all | `#sn` exists and visible | bounding box, opacity >= 0.5 |
| 1.3 | all | `#yt-box` exists | visible on desktop; mobile: fixed-bottom |
| 1.4 | all | No horizontal scrollability | no-hscroll after `scrollTo(9999,0)` |
| 1.5 | all | Deform check at rest | pass |
| 1.6 | P1-P3 | Nav pill top-centered within 2px of `innerWidth/2` | pass |
| 1.7 | P1-P3 | Nav pill top distance between 3 and 15px | pass |
| 1.8 | all | `html` has `text-size-adjust:100%` | computed style check |
| 1.9 | all | `body` has `overflow-x:hidden` | pass |
| 1.10 | all | Page title non-empty, Polish `lang="pl"` | pass |
| 1.11 | all | First `.ts` badge has `::before` content "play-triangle" (U+25B8) | pass |

## 2. Nav pill - hover / open / peek

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 2.1 | P1-P3 | Hover `#sn` | grip opacity >= 0.8 after 500ms |
| 2.2 | P1-P3 | Hover `#sn` | grip right edge <= pill left + 10px (grip flush-left, outside pill) |
| 2.3 | P1-P3 | Hover reveals grip | no-shift check on main buttons |
| 2.4 | P1-P3 | Hover reveals grip | deform check |
| 2.5 | P1-P3 | Unhover (move mouse away 500ms) | grip opacity returns to 0 |
| 2.6 | P4-P8 | On-touch default state | grip opacity >= 0.7 (hover:none) |
| 2.7 | all | Click `#sn-menu` | `#sn-list` opacity >= 0.9, pointer-events enabled |
| 2.8 | all | Menu open with pill near top | `#sn-list` below pill, list.y >= pill.bottom - 5 |
| 2.9 | all | Menu list fits viewport | list.x >= 0 and list.x+list.width <= innerWidth |
| 2.10 | all | Click first `#sn-list a` | menu closes (opacity < 0.1), URL hash changes, active marker updates |
| 2.11 | all | Menu open then click outside list | menu closes |
| 2.12 | all | Menu open then press `Escape` | menu closes (if keyboard handler exists), else note |
| 2.13 | all | Click `#sn-top` | window scrolled to y~=0 |
| 2.14 | all | Click `#sn-prev` / `#sn-next` | active section marker `.on` shifts by one |

## 3. Nav pill - drag & reset

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 3.1 | P1-P3 | Mouse-drag grip to (100,300) | pill gets `.moved` class |
| 3.2 | P1-P3 | After drag | pill x < 200 (moved leftward) |
| 3.3 | P1-P3 | After drag | pill no longer has `transform:translateX(-50%)` |
| 3.4 | P1-P3 | After drag hover | `#sn-rst` opacity >= 0.7 |
| 3.5 | P1-P3 | Click `#sn-rst` | pill returns to center (within 2px), `.moved` cleared |
| 3.6 | P4-P8 | Touch-drag grip | same as 3.1 via touch events |
| 3.7 | P1-P3 | Drag pill to bottom-center, open menu | `#sn-list` has `.above` class (auto-flip) |
| 3.8 | P1-P3 | Drag pill to bottom, open menu | list.y < pill.y (visually above) |
| 3.9 | all | Drag during `.dragging` state | no layout shift of main section content |
| 3.10 | P1-P3 | Multiple rapid reset clicks | no crash, pill stays centered |
| 3.11 | P1-P3 | Drag pill off-screen (negative coords) | pill clamped within viewport (x >= 0, y >= 0) |
| 3.12 | P1-P3 | Drag pill past viewport right | pill clamped (x + width <= innerWidth) |

## 4. Video player - hide / show / pulse / tooltip

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 4.1 | P1-P3 | Hover `#yt-box` | `.bars` class added, top bar visible (height > 20px) |
| 4.2 | P4-P8 | Touch any area of `#yt-box` | bars become visible |
| 4.3 | all | Click `#yt-hide` | after 600ms, `#yt-box` has `.hidden` class |
| 4.4 | all | After hide | `#yt-show` visible, has `.on` class |
| 4.5 | all | Immediately after hide | `#yt-show` has `.pulse` class |
| 4.6 | all | Immediately after hide | tooltip text contains "przywroc" visible near `#yt-show` |
| 4.7 | all | 3.2s after hide | `.pulse` cleared; tooltip hidden |
| 4.8 | all | Click `#yt-show` | `#yt-box` loses `.hidden`, `#yt-show` loses `.on` |
| 4.9 | all | Hide then show twice rapidly | no stuck state, no leftover inline transform on `#yt-box` |
| 4.10 | P1-P3 | During hide animation | translate target within 50px of `#yt-show` center |
| 4.11 | all | Double-click `#yt-hide` | single hide, no error |
| 4.12 | P1-P3 | After hide, mouse over `#yt-rztr` location | resize handle not clickable (box hidden); no pointer-events leak |
| 4.13 | **regression** | `#yt-hide` z-index | `#yt-hide` clickable on desktop; NOT overlaid by `#yt-rztr` |

## 5. Video player - resize

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 5.1 | P1-P3 | Drag `#yt-rz` (BR) by (+100,+100) | box width & height both increase by ~100 |
| 5.2 | P1-P3 | Drag `#yt-rzl` (BL) by (-100,+100) | width increases, left decreases |
| 5.3 | P1-P3 | Drag `#yt-rztl` (TL) | width increases, top decreases |
| 5.4 | P1-P3 | Drag `#yt-rztr` (TR) | width increases, top decreases |
| 5.5 | P1-P3 | Drag `#yt-rn` (N edge) by (0,-50) | height increases by ~50 |
| 5.6 | P1-P3 | Drag `#yt-rs` (S edge) by (0,+50) | height increases by ~50 |
| 5.7 | P1-P3 | Drag `#yt-re` (E edge) by (+50,0) | width increases by ~50 |
| 5.8 | P1-P3 | Drag `#yt-rw` (W edge) by (-50,0) | width increases by ~50 |
| 5.9 | P1-P3 | Resize below min-width (200) | box width clamped >= 200 |
| 5.10 | P1-P3 | Resize below min-height (e.g. 120) | box height clamped |
| 5.11 | P1-P3 | Resize beyond viewport | box stays within viewport |
| 5.12 | P1-P3 | Handle hover | opacity 0 to 1 per `#yt-box:hover .yt-rz{opacity:1}` |
| 5.13 | P4-P8 | Handles on touch | `.yt-rz` opacity ~0.35 (always visible) |

## 6. Audio mode

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 6.1 | all | Click `#yt-audio` | `#yt-box` gains `.audio` class |
| 6.2 | all | In audio mode | bottom edge of `#yt-box` matches pre-toggle bottom (within 4px) |
| 6.3 | all | In audio mode | `#yt-audio-ctrl` visible, controls laid out |
| 6.4 | all | In audio mode | `#ac-prev`, `#ac-next`, `#ac-back10`, `#ac-fwd10`, `#ac-play` all present |
| 6.5 | all | Click `#ac-back10` | currentTime decreases by ~10s (or clamps to 0) |
| 6.6 | all | Click `#ac-fwd10` | currentTime increases by ~10s |
| 6.7 | all | Click `#ac-prev` | jumps to previous chapter timestamp |
| 6.8 | all | Click `#ac-next` | jumps to next chapter timestamp |
| 6.9 | all | Click `#ac-play` | toggles play/pause state |
| 6.10 | all | Toggle audio then video then audio | no translate accumulation; bottom stays anchored |
| 6.11 | all | In audio mode, chapter label | current chapter title rendered in ctrl panel |
| 6.12 | all | Progress bar scrub (click in track) | seeks to that fraction |
| 6.13 | P1-P3 | Audio + drag | player still draggable by top bar |
| 6.14 | P1-P3 | Audio + resize | resize still works in audio layout |

## 7. TS badges

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 7.1 | all | Each `.ts` renders play-triangle via `::before` | pass |
| 7.2 | all | Hover `.ts` | background darkens, `::before` scales/translates |
| 7.3 | P1-P3 | Click `.ts` | YT iframe `seekTo` called, player active state updates |
| 7.4 | P4-P8 | Tap `.ts` visible above player | seeks |
| 7.5 | P4-P8 | Tap `.ts` during scroll | player shrunk, `.ts` tap reaches handler |
| 7.6 | all | Focus `.ts` via Tab | focus ring visible (outline 2px accent) |
| 7.7 | all | `.ts` enter key | same as click |

## 8. Mobile-specific: scroll-shrink

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 8.1 | P4-P8 | Begin scrolling body | `#yt-box` gains `.scrolling` within 100ms |
| 8.2 | P4-P8 | During `.scrolling` | player translated down by ~(height - 6px); opacity ~= 0.55 |
| 8.3 | P4-P8 | During `.scrolling` | `pointer-events: none` on box; `.ts` behind it tappable |
| 8.4 | P4-P8 | Stop scrolling 700ms | `.scrolling` cleared, box restored (transform empty, opacity 1) |
| 8.5 | P4-P8 | Hide player then scroll | `.scrolling` never applied while `.hidden` |
| 8.6 | P4-P8 | Scroll during `.hiding` animation | `.scrolling` not added (exclusion in selector) |
| 8.7 | P4-P8 | Tiny scroll (<4px delta) | no `.scrolling` added |
| 8.8 | P4-P8 | Fast scroll to bottom then to top | never stuck in `.scrolling` state for > 1s after stop |
| 8.9 | P1-P3 | Desktop scroll | `.scrolling` never applied (desktop ignored) |

## 9. Orientation & resize

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 9.1 | P4 | Rotate to landscape | pill re-centers, no overflow |
| 9.2 | P5 | Rotate to portrait | pill re-centers |
| 9.3 | all | Continuous window resize 320<->1920 | no console errors, no stuck `.moved`/`.above` states |
| 9.4 | all | After resize past 1099 breakpoint | mobile styles swap correctly; no-hscroll |

## 10. Accessibility & keyboard

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 10.1 | P2 | Tab from top | skip-link focuses first, visible when focused |
| 10.2 | P2 | Press Enter on skip-link | focus moves to `#main-content` |
| 10.3 | P2 | Tab through page | all interactive nav/pill/player controls reachable |
| 10.4 | P2 | Focus `#sn-menu` then Enter | menu opens |
| 10.5 | P2 | In menu, Arrow keys (if implemented) | navigate items, else note |
| 10.6 | P2 | ESC while menu open | menu closes (if implemented) |
| 10.7 | all | Every button has accessible name | `aria-label` or text content non-empty |
| 10.8 | all | All images have `alt` | pass |
| 10.9 | all | Heading hierarchy | h1 then h2 then h3 nesting valid |
| 10.10 | all | `lang="pl"` on `<html>` | pass |

## 11. Content

| ID | Scenario | Pass |
|----|----------|------|
| 11.1 | Polish diacritics present | pass |
| 11.2 | No mojibake (garbled UTF-8 triplets) anywhere in DOM text | pass |
| 11.3 | No placeholder strings (TODO, lorem, FIXME, XXX) | pass |
| 11.4 | All `.ts` data-t correspond to chapter times | pass |
| 11.5 | All anchor links target existing IDs | pass |
| 11.6 | External links have `rel="noopener"` | pass |
| 11.7 | Every `<a>` with `target="_blank"` has `rel` | pass |
| 11.8 | Cite sources present for medical claims (sample check) | pass |

## 12. Performance & resilience

| ID | Profile | Scenario | Pass |
|----|---------|----------|------|
| 12.1 | all | Block YouTube iframe domain | page still renders, no UI crash |
| 12.2 | all | Slow 3G emulation | page readable < 5s; iframe can lazy-load |
| 12.3 | all | Offline after load | drag/hide/menu still work |
| 12.4 | all | Rapid 50x hide+show | no memory leak, no accumulated listeners (<100 extra) |
| 12.5 | all | Rapid 50x drag + reset | pill returns cleanly each time |
| 12.6 | all | Open-close menu 30x | no opacity stuck between 0 and 1 |
| 12.7 | all | Time-travel by seeking 100x | no stale UI state |

## 13. Regression guards (bugs previously caught)

| ID | Origin | Scenario | Pass |
|----|--------|----------|------|
| R.1 | v34 | `#yt-hide` clickable while `#yt-rztr` present | hide fires on first click |
| R.2 | v33 | Nav pill grip does NOT shift main buttons on hover | no-shift check |
| R.3 | v33 | Nav pill `top = 5px` (not 10) | `getBoundingClientRect().y` <= 15 |
| R.4 | v32 | plus/minus 10s seek handlers bound | `#ac-back10` click changes currentTime |
| R.5 | v32 | `#yt-show` pulse auto-clears at 3s | `.pulse` gone after 3.2s |
| R.6 | v32 | `.ts::before` renders play glyph | `content` is play-triangle |
| R.7 | v31 | Menu is CSS-only absolute positioned | `#sn-list.open` uses `opacity/transform`, not `display` |
| R.8 | v30 | `text-size-adjust:100%` on `html` | computed style |
| R.9 | v35 | Scroll-shrink excludes `.hidden` and `.hiding` | scenario 8.5, 8.6 |
| R.10 | v33 | Tooltip for `#yt-show` says Polish message including "przywroc" | pass |
| R.11 | v29 | "Nawracajace objawy zapalenia pecherza" present | pass |
| R.12 | v29 | "Prawidlowe stezenie testosteronu" present (not "Normalne testosteron") | pass |
| R.13 | v29 | "perimenopauze" present (not "perimenopause") | pass |

## 14. Deform guard (run after EACH interaction in scenarios 2-6)

After every click/drag/hover/scroll/resize:
- All `#sn` main buttons same width & height (within 0.5px); each is square
- `#yt-hide`, `#yt-audio`, `#yt-reset`, `#ac-play`, `#ac-prev`, `#ac-next`, `#ac-back10`, `#ac-fwd10` are square (within 1px)
- No element has `transform: matrix(...)` with non-uniform scaling
- No element has `zoom` property != 1

---

## Known non-bugs (test should classify, not fail on)

1. Chromium mobile emulation reports `document.scrollWidth` = `innerWidth` + ~8px on iPhone 12 preset due to visual/layout viewport mismatch. Real devices don't have this.
2. YouTube iframe logs permission-policy violations for `compute-pressure`, `private-aggregation`, etc. Upstream YT probing, harmless.
3. Skip-link at `x:-9999` by design (visible only on focus).

## Execution notes

- Run against `https://fylchsharptail.github.io/endometrioza/?v=<timestamp>` to bypass GH Pages cache.
- Wait `networkidle` + 800ms after nav to allow YT iframe `onReady` before interacting with player.
- Use `{force: true}` sparingly - only for 5.x handle drags where Playwright's pointer cover-check falsely reports handle obscured.
- Each profile runs every applicable scenario. Budget: ~3-5 min per profile, ~30 min total.
