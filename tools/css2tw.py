#!/usr/bin/env python3
"""Convert simple CSS rules -> Tailwind utility string; apply to HTML via bs4."""
import re, cssutils, json, sys, pathlib
from bs4 import BeautifulSoup
cssutils.log.setLevel('FATAL')

FONT_WEIGHT = {'400':'font-normal','500':'font-medium','600':'font-semibold','700':'font-bold','800':'font-extrabold','900':'font-black','bold':'font-bold','normal':'font-normal'}
DISPLAY = {'block':'block','inline':'inline','inline-block':'inline-block','flex':'flex','grid':'grid','none':'hidden','inline-flex':'inline-flex','inline-grid':'inline-grid'}
TEXT_ALIGN = {'left':'text-left','center':'text-center','right':'text-right','justify':'text-justify'}
POSITION = {'static':'static','relative':'relative','absolute':'absolute','fixed':'fixed','sticky':'sticky'}
FLEX_DIR = {'row':'flex-row','row-reverse':'flex-row-reverse','column':'flex-col','column-reverse':'flex-col-reverse'}
JUSTIFY = {'flex-start':'justify-start','flex-end':'justify-end','center':'justify-center','space-between':'justify-between','space-around':'justify-around','space-evenly':'justify-evenly'}
ALIGN = {'flex-start':'items-start','flex-end':'items-end','center':'items-center','baseline':'items-baseline','stretch':'items-stretch'}
OVERFLOW = {'hidden':'overflow-hidden','visible':'overflow-visible','auto':'overflow-auto','scroll':'overflow-scroll'}
TEXT_TRANSFORM = {'uppercase':'uppercase','lowercase':'lowercase','capitalize':'capitalize','none':'normal-case'}
WHITESPACE = {'nowrap':'whitespace-nowrap','pre':'whitespace-pre','pre-wrap':'whitespace-pre-wrap','normal':'whitespace-normal'}
LIST_STYLE = {'none':'list-none','decimal':'list-decimal','disc':'list-disc'}
TEXT_DEC = {'none':'no-underline','underline':'underline'}
USER_SEL = {'none':'select-none','auto':'select-auto','text':'select-text'}
POINTER = {'none':'pointer-events-none','auto':'pointer-events-auto'}

def v(x):
    # return arbitrary-value-safe string (spaces -> _)
    return str(x).replace(' ', '_')

def decl_to_tw(prop, val):
    p = prop.lower().strip()
    v0 = val.strip()
    if p == 'display' and v0 in DISPLAY: return [DISPLAY[v0]]
    if p == 'position' and v0 in POSITION: return [POSITION[v0]]
    if p == 'text-align' and v0 in TEXT_ALIGN: return [TEXT_ALIGN[v0]]
    if p == 'text-transform' and v0 in TEXT_TRANSFORM: return [TEXT_TRANSFORM[v0]]
    if p == 'flex-direction' and v0 in FLEX_DIR: return [FLEX_DIR[v0]]
    if p == 'justify-content' and v0 in JUSTIFY: return [JUSTIFY[v0]]
    if p == 'align-items' and v0 in ALIGN: return [ALIGN[v0]]
    if p == 'overflow' and v0 in OVERFLOW: return [OVERFLOW[v0]]
    if p == 'overflow-x' and v0 in OVERFLOW: return [OVERFLOW[v0].replace('overflow-','overflow-x-')]
    if p == 'overflow-y' and v0 in OVERFLOW: return [OVERFLOW[v0].replace('overflow-','overflow-y-')]
    if p == 'white-space' and v0 in WHITESPACE: return [WHITESPACE[v0]]
    if p == 'list-style' and v0 in LIST_STYLE: return [LIST_STYLE[v0]]
    if p == 'list-style-type' and v0 in LIST_STYLE: return [LIST_STYLE[v0]]
    if p == 'text-decoration' and v0 in TEXT_DEC: return [TEXT_DEC[v0]]
    if p == 'user-select' and v0 in USER_SEL: return [USER_SEL[v0]]
    if p == 'pointer-events' and v0 in POINTER: return [POINTER[v0]]
    if p == 'font-weight' and v0 in FONT_WEIGHT: return [FONT_WEIGHT[v0]]
    if p == 'font-style' and v0 == 'italic': return ['italic']
    if p == 'font-style' and v0 == 'normal': return ['not-italic']
    if p == 'font-size': return [f'text-[{v(v0)}]']
    if p == 'line-height': return [f'leading-[{v(v0)}]']
    if p == 'letter-spacing': return [f'tracking-[{v(v0)}]']
    if p == 'color': return [f'text-[{v(v0)}]']
    if p == 'background-color': return [f'bg-[{v(v0)}]']
    if p == 'background': return [f'bg-[{v(v0)}]']
    if p == 'opacity': return [f'opacity-[{v(v0)}]']
    if p == 'cursor': return [f'cursor-{v0}'] if v0 in ('pointer','grab','grabbing','text','default','not-allowed','move','help','wait') else [f'[cursor:{v(v0)}]']
    if p == 'z-index': return [f'z-[{v(v0)}]']
    if p == 'width': return [f'w-[{v(v0)}]']
    if p == 'height': return [f'h-[{v(v0)}]']
    if p == 'min-width': return [f'min-w-[{v(v0)}]']
    if p == 'max-width': return [f'max-w-[{v(v0)}]']
    if p == 'min-height': return [f'min-h-[{v(v0)}]']
    if p == 'max-height': return [f'max-h-[{v(v0)}]']
    if p == 'top': return [f'top-[{v(v0)}]']
    if p == 'right': return [f'right-[{v(v0)}]']
    if p == 'bottom': return [f'bottom-[{v(v0)}]']
    if p == 'left': return [f'left-[{v(v0)}]']
    if p == 'inset': return [f'inset-[{v(v0)}]']
    if p == 'gap': return [f'gap-[{v(v0)}]']
    if p == 'margin':
        parts = v0.split()
        if len(parts)==1: return [f'm-[{v(parts[0])}]']
        return [f'[margin:{v(v0)}]']
    if p == 'padding':
        parts = v0.split()
        if len(parts)==1: return [f'p-[{v(parts[0])}]']
        return [f'[padding:{v(v0)}]']
    if p == 'margin-top': return [f'mt-[{v(v0)}]']
    if p == 'margin-bottom': return [f'mb-[{v(v0)}]']
    if p == 'margin-left': return [f'ml-[{v(v0)}]']
    if p == 'margin-right': return [f'mr-[{v(v0)}]']
    if p == 'padding-top': return [f'pt-[{v(v0)}]']
    if p == 'padding-bottom': return [f'pb-[{v(v0)}]']
    if p == 'padding-left': return [f'pl-[{v(v0)}]']
    if p == 'padding-right': return [f'pr-[{v(v0)}]']
    if p == 'border-radius': return [f'rounded-[{v(v0)}]']
    if p == 'border':
        # border: 1px solid #xxx
        m = re.match(r'(\d+\w*)\s+(solid|dashed|dotted|double)?\s*(.*)', v0)
        if m and m.group(3): return [f'border-[{m.group(1)}]', f'border-[{v(m.group(3))}]']
        return [f'[border:{v(v0)}]']
    if p == 'border-top': return [f'[border-top:{v(v0)}]']
    if p == 'border-bottom': return [f'[border-bottom:{v(v0)}]']
    if p == 'border-left': return [f'[border-left:{v(v0)}]']
    if p == 'border-right': return [f'[border-right:{v(v0)}]']
    if p == 'border-color': return [f'border-[{v(v0)}]']
    if p == 'border-width': return [f'border-[{v(v0)}]']
    if p == 'border-style': return [f'[border-style:{v(v0)}]']
    if p == 'box-shadow': return [f'shadow-[{v(v0)}]']
    if p == 'transition': return [f'[transition:{v(v0)}]']
    if p == 'transform': return [f'[transform:{v(v0)}]']
    if p == 'text-decoration-color': return [f'decoration-[{v(v0)}]']
    if p == 'content': return [f'content-[{v(v0)}]']
    if p == 'flex': return [f'flex-[{v(v0)}]'] if v0!='1' else ['flex-1']
    if p == 'flex-shrink': return ['shrink-0'] if v0=='0' else [f'[flex-shrink:{v0}]']
    if p == 'flex-grow': return ['grow-0'] if v0=='0' else [f'[flex-grow:{v0}]']
    if p == 'flex-wrap': return [f'flex-{v0}'] if v0 in ('wrap','nowrap','wrap-reverse') else []
    if p == 'grid-template-columns': return [f'grid-cols-[{v(v0)}]']
    if p == 'grid-template-rows': return [f'grid-rows-[{v(v0)}]']
    if p == 'text-underline-offset': return [f'underline-offset-[{v(v0)}]']
    if p == 'filter': return [f'[filter:{v(v0)}]']
    if p == 'backdrop-filter': return [f'[backdrop-filter:{v(v0)}]']
    if p == '-webkit-backdrop-filter': return []  # covered by backdrop-filter
    if p == 'font-family': return [f'[font-family:{v(v0)}]']
    if p == 'place-items': return [f'place-items-{v0}']
    if p == 'border-collapse': return [f'border-{v0}']
    if p == 'outline': return [f'[outline:{v(v0)}]']
    if p == 'outline-offset': return [f'[outline-offset:{v(v0)}]']
    if p == 'box-sizing': return [f'[box-sizing:{v0}]']
    if p == 'text-rendering': return [f'[text-rendering:{v0}]']
    if p == '-webkit-font-smoothing': return ['antialiased'] if v0=='antialiased' else []
    if p == 'counter-reset': return [f'[counter-reset:{v(v0)}]']
    if p == 'counter-increment': return [f'[counter-increment:{v(v0)}]']
    if p == 'animation': return [f'[animation:{v(v0)}]']
    if p == 'mix-blend-mode': return [f'mix-blend-{v0}']
    if p == 'vertical-align': return [f'align-{v0}'] if v0 in ('middle','top','bottom','baseline','super','sub') else [f'[vertical-align:{v0}]']
    if p == 'object-fit': return [f'object-{v0}']
    if p == 'word-break': return [f'break-{v0}']
    if p == 'text-overflow': return [f'text-{v0}'] if v0=='ellipsis' else []
    # fallthrough
    return [f'[{p}:{v(v0)}]']

def rule_to_tw(rule):
    utils = []
    for d in rule.style:
        if not d.name or not d.value: continue
        tw = decl_to_tw(d.name, d.value)
        utils.extend(tw)
    return utils

# --- main ---
html_path = pathlib.Path('/opt/personal/git/endometrioza/index.html')
html = html_path.read_text()

# Extract <style> content
m = re.search(r'<style>(.+?)</style>', html, re.S)
if not m:
    print('no <style> block'); sys.exit(1)
css_text = m.group(1)
sheet = cssutils.parseString(css_text)

# Build map of SIMPLE selectors -> tw utility list
sel_map = {}  # e.g. '.card': [util,...], 'h2': [...], '.card b' (compound) collected separately as [&_b] variants on parent
nested = {}  # parent_selector -> list of (child_suffix, utils) using [&_sel] variant folding

for rule in sheet:
    if rule.typeString != 'STYLE_RULE': continue
    for sel in [s.strip() for s in rule.selectorText.split(',')]:
        utils = rule_to_tw(rule)
        if not utils: continue
        # Check if compound descendant selector like '.hero h1' or 'nav.toc ol' or '.card b'
        # Simple: single-token selectors go to sel_map. Multi-token to nested under first token.
        tokens = sel.split()
        if len(tokens) == 1 and '::' not in sel and ':' not in sel.replace(':not','').replace(':hover','').replace(':focus-visible','').replace(':empty','').replace(':first-child','').replace(':active','').replace(':focus',''):
            # pure single selector (may have pseudo-class)
            sel_map.setdefault(sel, []).extend(utils)
        else:
            # nested/pseudo: stash under first token as arbitrary variant
            parent = tokens[0]
            child = ' '.join(tokens[1:]) if len(tokens)>1 else sel[len(parent):]
            nested.setdefault(parent, []).append((child, sel, utils))

# Print summary for review
print('SIMPLE selectors:', len(sel_map))
for k in sorted(sel_map.keys())[:40]:
    print(f'  {k:30s} -> {" ".join(sel_map[k])[:120]}')
print('NESTED parents:', len(nested))
for k in sorted(nested.keys())[:20]:
    print(f'  {k}: {len(nested[k])} children')

# Emit mapping for human review
out = {'simple': {k: ' '.join(v) for k,v in sorted(sel_map.items())},
       'nested': {p: [{'child': c, 'full': full, 'utils': ' '.join(u)} for c,full,u in v] for p,v in sorted(nested.items())}}
pathlib.Path('/opt/personal/git/endometrioza/tools/classmap.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
print('wrote tools/classmap.json')
