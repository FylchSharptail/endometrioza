#!/usr/bin/env python3
"""Convert CSS rules -> Tailwind utilities + build classmap.json.

Upgrades over v1:
 - Inline CSS var(--x) values from :root blocks (all of them)
 - Split font-size -> [font-size:...] vs color -> text-[...]
 - Fold state-class selectors (.foo.state / #id.state) as [&.state]:util on parent
 - Fold pseudo-elements ::before / ::after as before:/after: variants
 - Fold :hover / :focus-visible / :active / :empty / :first-child / :not(...) as variants
 - Fold descendant chains .parent .child as [&_.child]:util on parent
"""
import re, cssutils, json, sys, pathlib
from collections import defaultdict
cssutils.log.setLevel('FATAL')

# ---------- value/decl translation ----------
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
CURSORS = {'pointer','grab','grabbing','text','default','not-allowed','move','help','wait','ew-resize','ns-resize','nwse-resize','nesw-resize','col-resize','row-resize','crosshair','zoom-in','zoom-out'}

# color-ish: hex, rgb(...), rgba(...), hsl(...), hsla(...), named (crude heuristic: single word, no unit/digit)
COLOR_RE = re.compile(r'^(#[0-9a-fA-F]{3,8}|rgba?\(.*\)|hsla?\(.*\)|var\(--[\w-]*(color|bg|text|surface|accent|muted|border|warn|purple)[\w-]*\)|transparent|currentColor|inherit|initial|unset|white|black|red|green|blue|yellow|orange|purple|pink|gray|grey|cyan|magenta|brown|silver|gold)$')
NAMED_COLOR_PREFIX = re.compile(r'^(rgb|rgba|hsl|hsla|#)')

def _s(x): return str(x).replace(' ', '_')

def is_color(v):
    vv = v.strip().lower()
    if NAMED_COLOR_PREFIX.match(vv): return True
    if COLOR_RE.match(v.strip()): return True
    if vv.startswith('var(--') and any(k in vv for k in ('color','bg','text','surface','accent','muted','border','warn','purple')):
        return True
    return False

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
    if p in ('list-style','list-style-type') and v0 in LIST_STYLE: return [LIST_STYLE[v0]]
    if p == 'text-decoration' and v0 in TEXT_DEC: return [TEXT_DEC[v0]]
    if p == 'user-select' and v0 in USER_SEL: return [USER_SEL[v0]]
    if p == 'pointer-events' and v0 in POINTER: return [POINTER[v0]]
    if p == 'font-weight' and v0 in FONT_WEIGHT: return [FONT_WEIGHT[v0]]
    if p == 'font-style': return ['italic'] if v0=='italic' else (['not-italic'] if v0=='normal' else [])
    if p == 'font-size': return [f'[font-size:{_s(v0)}]']
    if p == 'line-height': return [f'leading-[{_s(v0)}]']
    if p == 'letter-spacing': return [f'tracking-[{_s(v0)}]']
    if p == 'color':
        return [f'text-[{_s(v0)}]'] if is_color(v0) else [f'[color:{_s(v0)}]']
    if p == 'background-color': return [f'bg-[{_s(v0)}]']
    if p == 'background': return [f'bg-[{_s(v0)}]']
    if p == 'opacity': return [f'opacity-[{_s(v0)}]']
    if p == 'cursor': return [f'cursor-{v0}'] if v0 in CURSORS else [f'[cursor:{_s(v0)}]']
    if p == 'z-index': return [f'z-[{_s(v0)}]']
    if p == 'width': return [f'w-[{_s(v0)}]']
    if p == 'height': return [f'h-[{_s(v0)}]']
    if p == 'min-width': return [f'min-w-[{_s(v0)}]']
    if p == 'max-width': return [f'max-w-[{_s(v0)}]']
    if p == 'min-height': return [f'min-h-[{_s(v0)}]']
    if p == 'max-height': return [f'max-h-[{_s(v0)}]']
    if p == 'top': return [f'top-[{_s(v0)}]']
    if p == 'right': return [f'right-[{_s(v0)}]']
    if p == 'bottom': return [f'bottom-[{_s(v0)}]']
    if p == 'left': return [f'left-[{_s(v0)}]']
    if p == 'inset': return [f'inset-[{_s(v0)}]']
    if p == 'gap': return [f'gap-[{_s(v0)}]']
    if p == 'margin':
        parts = v0.split()
        if len(parts)==1: return [f'm-[{_s(parts[0])}]']
        return [f'[margin:{_s(v0)}]']
    if p == 'padding':
        parts = v0.split()
        if len(parts)==1: return [f'p-[{_s(parts[0])}]']
        return [f'[padding:{_s(v0)}]']
    if p == 'margin-top': return [f'mt-[{_s(v0)}]']
    if p == 'margin-bottom': return [f'mb-[{_s(v0)}]']
    if p == 'margin-left': return [f'ml-[{_s(v0)}]']
    if p == 'margin-right': return [f'mr-[{_s(v0)}]']
    if p == 'padding-top': return [f'pt-[{_s(v0)}]']
    if p == 'padding-bottom': return [f'pb-[{_s(v0)}]']
    if p == 'padding-left': return [f'pl-[{_s(v0)}]']
    if p == 'padding-right': return [f'pr-[{_s(v0)}]']
    if p == 'border-radius': return [f'rounded-[{_s(v0)}]']
    if p == 'border':
        m = re.match(r'(\d+\w*)\s+(solid|dashed|dotted|double)?\s*(.*)', v0)
        if m and m.group(3): return [f'border-[{m.group(1)}]', f'border-[{_s(m.group(3))}]']
        return [f'[border:{_s(v0)}]']
    if p in ('border-top','border-bottom','border-left','border-right'): return [f'[{p}:{_s(v0)}]']
    if p == 'border-color': return [f'border-[{_s(v0)}]']
    if p == 'border-width': return [f'border-[{_s(v0)}]']
    if p == 'border-style': return [f'[border-style:{_s(v0)}]']
    if p == 'box-shadow': return [f'shadow-[{_s(v0)}]']
    if p == 'transition': return [f'[transition:{_s(v0)}]']
    if p == 'transform': return [f'[transform:{_s(v0)}]']
    if p == 'transform-origin': return [f'[transform-origin:{_s(v0)}]']
    if p == 'text-decoration-color': return [f'decoration-[{_s(v0)}]']
    if p == 'text-decoration-thickness': return [f'decoration-[{_s(v0)}]']
    if p == 'content': return [f'content-[{_s(v0)}]']
    if p == 'flex': return ['flex-1'] if v0=='1' else [f'flex-[{_s(v0)}]']
    if p == 'flex-shrink': return ['shrink-0'] if v0=='0' else [f'[flex-shrink:{v0}]']
    if p == 'flex-grow': return ['grow-0'] if v0=='0' else [f'[flex-grow:{v0}]']
    if p == 'flex-wrap' and v0 in ('wrap','nowrap','wrap-reverse'): return [f'flex-{v0}']
    if p == 'grid-template-columns': return [f'grid-cols-[{_s(v0)}]']
    if p == 'grid-template-rows': return [f'grid-rows-[{_s(v0)}]']
    if p == 'text-underline-offset': return [f'underline-offset-[{_s(v0)}]']
    if p == 'filter': return [f'[filter:{_s(v0)}]']
    if p == 'backdrop-filter': return [f'[backdrop-filter:{_s(v0)}]']
    if p == '-webkit-backdrop-filter': return []
    if p == 'font-family': return [f'[font-family:{_s(v0)}]']
    if p == 'font': return [f'[font:{_s(v0)}]']
    if p == 'font-variant-numeric': return [f'[font-variant-numeric:{_s(v0)}]']
    if p == 'place-items': return [f'place-items-{v0}']
    if p == 'border-collapse': return [f'border-{v0}']
    if p == 'outline': return [f'[outline:{_s(v0)}]']
    if p == 'outline-offset': return [f'[outline-offset:{_s(v0)}]']
    if p == 'box-sizing': return [f'[box-sizing:{v0}]']
    if p == 'text-rendering': return [f'[text-rendering:{v0}]']
    if p == '-webkit-font-smoothing': return ['antialiased'] if v0=='antialiased' else []
    if p == 'counter-reset': return [f'[counter-reset:{_s(v0)}]']
    if p == 'counter-increment': return [f'[counter-increment:{_s(v0)}]']
    if p == 'animation': return [f'[animation:{_s(v0)}]']
    if p == 'mix-blend-mode': return [f'mix-blend-{v0}']
    if p == 'vertical-align': return [f'align-{v0}'] if v0 in ('middle','top','bottom','baseline','super','sub') else [f'[vertical-align:{v0}]']
    if p == 'object-fit': return [f'object-{v0}']
    if p == 'word-break': return [f'break-{v0}']
    if p == 'text-overflow' and v0=='ellipsis': return ['text-ellipsis']
    if p == 'touch-action': return [f'[touch-action:{_s(v0)}]']
    if p == 'aspect-ratio': return [f'aspect-[{_s(v0)}]']
    if p == 'isolation': return [f'[isolation:{v0}]']
    if p == 'border-image': return [f'[border-image:{_s(v0)}]']
    if p == '-webkit-text-size-adjust': return []
    if p == 'text-size-adjust': return [f'[text-size-adjust:{v0}]']
    if p == 'backdrop-blur': return [f'backdrop-blur-[{_s(v0)}]']
    return [f'[{p}:{_s(v0)}]']

def rule_to_tw(rule):
    utils = []
    for d in rule.style:
        if not d.name or not d.value: continue
        utils.extend(decl_to_tw(d.name, d.value))
    return utils

# ---------- CSS var inlining ----------
def collect_vars(css_text):
    """Collect all --x:y; declarations from :root { ... } blocks."""
    vars_map = {}
    for block in re.finditer(r':root\s*\{([^}]*)\}', css_text):
        body = block.group(1)
        for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+?)(?=;|$)', body):
            vars_map[m.group(1).strip()] = m.group(2).strip()
    return vars_map

def inline_vars(value, vars_map, depth=0):
    if depth > 5 or 'var(' not in value: return value
    def repl(m):
        name = m.group(1).strip()
        default = m.group(2)
        if name in vars_map: return vars_map[name]
        return default.strip() if default else m.group(0)
    # matches var(--name) or var(--name, fallback)
    new = re.sub(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)', repl, value)
    if new != value: return inline_vars(new, vars_map, depth+1)
    return new

# ---------- selector analysis ----------
PSEUDO_VARIANT_MAP = {
    ':hover': 'hover',
    ':focus': 'focus',
    ':focus-visible': 'focus-visible',
    ':focus-within': 'focus-within',
    ':active': 'active',
    ':disabled': 'disabled',
    ':checked': 'checked',
    ':empty': 'empty',
    ':first-child': 'first',
    ':last-child': 'last',
    '::before': 'before',
    '::after': 'after',
    '::placeholder': 'placeholder',
    '::first-letter': 'first-letter',
    '::first-line': 'first-line',
    '::marker': 'marker',
    '::selection': 'selection',
}

ID_RE = r'#[\w-]+'
CLASS_RE = r'\.[\w-]+'
TAG_RE = r'[a-zA-Z][\w-]*'

def split_first_token(tokens):
    """For descendant sel '.a .b .c' -> returns ('.a', '.b .c')."""
    if len(tokens) == 1: return tokens[0], ''
    return tokens[0], ' '.join(tokens[1:])

def parse_base_and_tail(tok):
    """Given a single compound selector like '#yt-box.audio:not(.dragged):hover::before',
    return (base, tail) where base is the first #id / .class / tag, and tail is the remainder.
    """
    m = re.match(r'(\*|' + ID_RE + '|' + CLASS_RE + '|' + TAG_RE + ')', tok)
    if not m: return tok, ''
    return m.group(1), tok[m.end():]

def tail_to_variant(tail):
    """Convert selector tail (.state, :hover, ::before, :not(.x), [attr], combos) -> variant prefix or None.
    Returns (variant_string, remaining_tail) where variant is like 'hover:' or '[&.state]:' or '' if tail is empty.
    If conversion fails, returns (None, tail).
    """
    if not tail: return '', ''
    variants = []
    rest = tail
    # peel known pseudos first
    while rest:
        matched = False
        for pseudo, var in sorted(PSEUDO_VARIANT_MAP.items(), key=lambda x: -len(x[0])):
            if rest.startswith(pseudo):
                # must be terminal or followed by another recognizable segment
                nxt = rest[len(pseudo)]  if len(rest) > len(pseudo) else ''
                if nxt in ('', ':', '.', '[', ' '):
                    variants.append(var)
                    rest = rest[len(pseudo):]
                    matched = True
                    break
        if matched: continue
        # :not(...)
        m = re.match(r':not\(([^)]+)\)', rest)
        if m:
            variants.append(f'[&:not({m.group(1)})]')
            rest = rest[m.end():]
            continue
        # .state -> [&.state]
        m = re.match(r'(\.[\w-]+)', rest)
        if m:
            variants.append(f'[&{m.group(1)}]')
            rest = rest[m.end():]
            continue
        # [attr]
        m = re.match(r'(\[[^\]]+\])', rest)
        if m:
            variants.append(f'[&{m.group(1)}]')
            rest = rest[m.end():]
            continue
        # id suffix? (rare, compound like #a#b) -> bail
        return None, tail
    return ':'.join(variants) + ':' if variants else '', ''

def classify_selector(sel):
    """Return (base_key, variant_prefix) for a selector.
    base_key is the root element selector (#id, .class, or tag) under which we attach the rule.
    variant_prefix is '' for direct rules, or 'hover:', '[&.state]:', 'before:hover:', or '[&_.child]:' for nested.
    Returns (None, None) if not classifiable (multi-root, complex combinators, etc.).
    """
    sel = sel.strip()
    tokens = sel.split()
    # Single compound (no descendant combinator)
    if len(tokens) == 1:
        base, tail = parse_base_and_tail(tokens[0])
        if not base: return None, None
        var, leftover = tail_to_variant(tail)
        if var is None: return None, None
        return base, var
    # Descendant chain: root + rest
    first = tokens[0]
    rest_toks = tokens[1:]
    base, base_tail = parse_base_and_tail(first)
    if not base: return None, None
    base_var, leftover = tail_to_variant(base_tail)
    if base_var is None: return None, None
    # For descendant rest: emit [&_.child]:util (use _ combinator for descendant)
    rest_sel = ' '.join(rest_toks)
    # Tailwind arbitrary variant uses _ for space; tolerate '>' by passing through
    rest_esc = rest_sel.replace(' ', '_')
    return base, f'{base_var}[&_{rest_esc}]:'

# ---------- main ----------
html_path = pathlib.Path('/opt/personal/git/endometrioza/index.html')
html = html_path.read_text()
m = re.search(r'<style[^>]*>(.+?)</style>', html, re.S)
if not m:
    print('no <style> block'); sys.exit(1)
css_text = m.group(1)

vars_map = collect_vars(css_text)
print(f'CSS vars collected: {len(vars_map)}')
for k,v in vars_map.items(): print(f'  {k} = {v}')

# Inline vars in the whole css text BEFORE parsing (quick+dirty pass on values).
# Safer: walk declarations and inline, so we keep selectors intact. Use cssutils.
sheet = cssutils.parseString(css_text)

# classmap[base_selector] = list of (variant_prefix, util_list)
classmap = defaultdict(list)
unclassified = []  # rules we couldn't fold

def walk_rules(rule_list):
    for rule in rule_list:
        t = rule.typeString
        if t == 'STYLE_RULE':
            for sel in [s.strip() for s in rule.selectorText.split(',')]:
                # pre-inline vars in each decl value
                utils = []
                for d in rule.style:
                    if not d.name or not d.value: continue
                    val = inline_vars(d.value, vars_map)
                    utils.extend(decl_to_tw(d.name, val))
                if not utils: continue
                base, variant = classify_selector(sel)
                if base is None:
                    unclassified.append((sel, utils))
                    continue
                classmap[base].append((variant, utils, sel))
        elif t == 'MEDIA_RULE':
            # stash under @media prefix via arbitrary variant (not applied, just recorded)
            mq = rule.media.mediaText
            # Tailwind arbitrary media: [@media(...)]:util (approximate)
            mq_prefix = f'[@media{mq.replace(" ", "")}]:'
            for inner in rule.cssRules:
                if inner.typeString != 'STYLE_RULE': continue
                for sel in [s.strip() for s in inner.selectorText.split(',')]:
                    utils = []
                    for d in inner.style:
                        if not d.name or not d.value: continue
                        val = inline_vars(d.value, vars_map)
                        utils.extend(decl_to_tw(d.name, val))
                    if not utils: continue
                    base, variant = classify_selector(sel)
                    if base is None:
                        unclassified.append((f'@media {mq} {sel}', utils))
                        continue
                    classmap[base].append((mq_prefix + variant, utils, f'@media {mq} {sel}'))
        elif t == 'KEYFRAMES_RULE':
            pass  # tailwind.config already owns keyframes
        elif t == 'FONT_FACE_RULE':
            pass

walk_rules(sheet)

# Build output: per base selector, dict of variant->utils (dedup)
out = {}
for base, entries in sorted(classmap.items()):
    merged = defaultdict(list)
    provenance = []
    for var, utils, original in entries:
        merged[var].extend(utils)
        provenance.append({'variant': var, 'utils': ' '.join(utils), 'from': original})
    # dedup per variant preserving order
    merged_clean = {}
    for var, utils in merged.items():
        seen = set(); keep = []
        for u in utils:
            if u not in seen: seen.add(u); keep.append(u)
        # prefix utils with variant
        if var:
            merged_clean[var] = ' '.join(f'{var}{u}' for u in keep)
        else:
            merged_clean[var] = ' '.join(keep)
    # flatten: one big class string for this selector = concatenation of all variant groups
    classes_all = ' '.join(merged_clean.values())
    out[base] = {'classes': classes_all, 'by_variant': merged_clean, 'provenance': provenance}

payload = {
    'vars': vars_map,
    'selectors': out,
    'unclassified': [{'selector': s, 'utils': ' '.join(u)} for s,u in unclassified],
}
pathlib.Path('/opt/personal/git/endometrioza/tools/classmap.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(f'Selectors folded: {len(out)}')
print(f'Unclassified: {len(unclassified)}')
for u in unclassified[:20]: print('  UNC:', u[0])
print('wrote tools/classmap.json')
