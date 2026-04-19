#!/usr/bin/env -S /Users/ext.grzegorz.grabarz/.venv/css2tw/bin/python3
"""CSS -> Tailwind utilities + classmap.json. v3.

v3 fixes:
 - Token reverse-map from tailwind.config in index.html (colors, shadows,
   durations, easings, animations, screens) -> prefer named utils when value matches
 - @media mapping: print -> print:, (max-width:640px) -> max-sm:, (min-width:1100px) -> ep:,
   (hover:none|hover) stay as arbitrary
 - font-size length values -> text-[val] (not [font-size:val])
 - border:1px solid X -> border + border-[1px] + border-[X]
 - border:0 / border:none -> border-0
 - Preserve transform function casing (translateX, not translatex)
 - Preserve value token casing via source-text capture (cssutils normalizes values)
"""
import re, cssutils, json, sys, pathlib
from collections import defaultdict
cssutils.log.setLevel('FATAL')

HTML = pathlib.Path('/opt/personal/git/endometrioza/index.html').read_text()

# ---------- tailwind.config token reverse-map ----------
def _grab(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags); return m.group(1) if m else ''
def _parse_kv_block(body):
    out = {}
    for m in re.finditer(r"['\"]?([\w-]+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", body):
        out[m.group(1)] = m.group(2).strip()
    return out

cfg = _grab(r'tailwind\.config\s*=\s*\{(.*?)\n\}\s*</script>', HTML)
screens = _parse_kv_block(_grab(r'screens:\s*\{([^}]*)\}', cfg))
colors  = _parse_kv_block(_grab(r'colors:\s*\{([^}]*)\}', cfg))
shadows = _parse_kv_block(_grab(r'boxShadow:\s*\{([^}]*)\}', cfg))
durations = _parse_kv_block(_grab(r'transitionDuration:\s*\{([^}]*)\}', cfg))
easings = _parse_kv_block(_grab(r'transitionTimingFunction:\s*\{([^}]*)\}', cfg))
animations = _parse_kv_block(_grab(r'animation:\s*\{([^}]*)\}', cfg))

def _norm_val(v): return re.sub(r'\s+', '', v.lower())
COLOR_REV = {_norm_val(v): k for k,v in colors.items()}
SHADOW_REV = {_norm_val(v): k for k,v in shadows.items()}
DUR_REV = {_norm_val(v): k for k,v in durations.items()}
EASE_REV = {_norm_val(v): k for k,v in easings.items()}
ANIM_REV = {_norm_val(v): k for k,v in animations.items()}
SCREENS = {k: v for k,v in screens.items()}  # e.g. {'ep':'1100px'}

def color_util(prefix, value):
    key = _norm_val(value)
    if key in COLOR_REV: return f'{prefix}-{COLOR_REV[key]}'
    return f'{prefix}-[{_s(value)}]'

def shadow_util(value):
    key = _norm_val(value)
    if key in SHADOW_REV: return f'shadow-{SHADOW_REV[key]}'
    return f'shadow-[{_s(value)}]'

def duration_util(value):
    key = _norm_val(value)
    if key in DUR_REV: return f'duration-{DUR_REV[key]}'
    return f'duration-[{_s(value)}]'

def ease_util(value):
    key = _norm_val(value)
    if key in EASE_REV: return f'ease-{EASE_REV[key]}'
    return f'ease-[{_s(value)}]'

# ---------- transform-case restoration ----------
TRANSFORM_FNS = ['translateX','translateY','translateZ','translate3d','translate',
                 'rotateX','rotateY','rotateZ','rotate3d','rotate',
                 'scaleX','scaleY','scaleZ','scale3d','scale',
                 'skewX','skewY','skew',
                 'matrix3d','matrix','perspective']
TRANSFORM_FIX = {fn.lower(): fn for fn in TRANSFORM_FNS}
def fix_transform_case(v):
    def repl(m):
        name = m.group(1).lower()
        return TRANSFORM_FIX.get(name, m.group(1))
    return re.sub(r'\b([A-Za-z]+3?d?)(?=\s*\()', repl, v)

# ---------- value fixups ----------
def _s(x):
    x = str(x)
    x = fix_transform_case(x)
    return x.replace(' ', '_')

LENGTH_RE = re.compile(r'^-?\d*\.?\d+(px|rem|em|%|vh|vw|pt|ch|ex|vmin|vmax)$|^(smaller|larger|xx-small|x-small|small|medium|large|x-large|xx-large)$', re.I)
COLOR_RE = re.compile(r'^(#[0-9a-fA-F]{3,8}|rgba?\(.*\)|hsla?\(.*\)|transparent|currentColor|inherit|initial|unset|white|black|red|green|blue|yellow|orange|purple|pink|gray|grey|cyan|magenta|brown|silver|gold)$', re.I)

def is_length(v): return bool(LENGTH_RE.match(v.strip()))
def is_color(v):
    vv = v.strip()
    if COLOR_RE.match(vv): return True
    if vv.lower().startswith('var(--') and any(k in vv.lower() for k in ('color','bg','text','surface','accent','muted','border','warn','purple','ink')):
        return True
    return False

# ---------- CSS var inlining ----------
def collect_vars(css_text):
    vars_map = {}
    for block in re.finditer(r':root\s*\{([^}]*)\}', css_text):
        for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+?)(?=;|$)', block.group(1)):
            vars_map[m.group(1).strip()] = m.group(2).strip()
    return vars_map

def inline_vars(value, vars_map, depth=0):
    if depth > 5 or 'var(' not in value: return value
    def repl(m):
        name = m.group(1).strip(); default = m.group(2)
        if name in vars_map: return vars_map[name]
        return default.strip() if default else m.group(0)
    new = re.sub(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)', repl, value)
    return inline_vars(new, vars_map, depth+1) if new != value else new

# ---------- decl translation ----------
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

def decl_to_tw(prop, val, imp=False):
    p = prop.lower().strip(); v0 = val.strip()
    bang = '!' if imp else ''
    def out(u): return [bang + u] if u else []
    if p == 'display' and v0 in DISPLAY: return out(DISPLAY[v0])
    if p == 'position' and v0 in POSITION: return out(POSITION[v0])
    if p == 'text-align' and v0 in TEXT_ALIGN: return out(TEXT_ALIGN[v0])
    if p == 'text-transform' and v0 in TEXT_TRANSFORM: return out(TEXT_TRANSFORM[v0])
    if p == 'flex-direction' and v0 in FLEX_DIR: return out(FLEX_DIR[v0])
    if p == 'justify-content' and v0 in JUSTIFY: return out(JUSTIFY[v0])
    if p == 'align-items' and v0 in ALIGN: return out(ALIGN[v0])
    if p == 'overflow' and v0 in OVERFLOW: return out(OVERFLOW[v0])
    if p == 'overflow-x' and v0 in OVERFLOW: return out(OVERFLOW[v0].replace('overflow-','overflow-x-'))
    if p == 'overflow-y' and v0 in OVERFLOW: return out(OVERFLOW[v0].replace('overflow-','overflow-y-'))
    if p == 'white-space' and v0 in WHITESPACE: return out(WHITESPACE[v0])
    if p in ('list-style','list-style-type') and v0 in LIST_STYLE: return out(LIST_STYLE[v0])
    if p == 'text-decoration':
        if v0 in TEXT_DEC: return out(TEXT_DEC[v0])
        return [bang + f'[text-decoration:{_s(v0)}]']
    if p == 'user-select' and v0 in USER_SEL: return out(USER_SEL[v0])
    if p == 'pointer-events' and v0 in POINTER: return out(POINTER[v0])
    if p == 'font-weight' and v0 in FONT_WEIGHT: return out(FONT_WEIGHT[v0])
    if p == 'font-style':
        if v0 == 'italic': return out('italic')
        if v0 == 'normal': return out('not-italic')
        return []
    if p == 'font-size':
        if is_length(v0): return out(f'text-[{_s(v0)}]')
        return out(f'[font-size:{_s(v0)}]')
    if p == 'line-height': return out(f'leading-[{_s(v0)}]')
    if p == 'letter-spacing': return out(f'tracking-[{_s(v0)}]')
    if p == 'color':
        return out(color_util('text', v0)) if is_color(v0) else out(f'[color:{_s(v0)}]')
    if p == 'background-color': return out(color_util('bg', v0))
    if p == 'background':
        # if pure color
        if is_color(v0): return out(color_util('bg', v0))
        return out(f'bg-[{_s(v0)}]')
    if p == 'opacity':
        m = re.match(r'^([0-9.]+)$', v0)
        if m:
            f = float(m.group(1))
            if 0 <= f <= 1: return out(f'opacity-[{v0}]')
        return out(f'opacity-[{_s(v0)}]')
    if p == 'cursor': return out(f'cursor-{v0}') if v0 in CURSORS else out(f'[cursor:{_s(v0)}]')
    if p == 'z-index': return out(f'z-[{_s(v0)}]')
    if p == 'width': return out(f'w-[{_s(v0)}]')
    if p == 'height': return out(f'h-[{_s(v0)}]')
    if p == 'min-width': return out(f'min-w-[{_s(v0)}]')
    if p == 'max-width': return out(f'max-w-[{_s(v0)}]')
    if p == 'min-height': return out(f'min-h-[{_s(v0)}]')
    if p == 'max-height': return out(f'max-h-[{_s(v0)}]')
    if p == 'top': return out(f'top-[{_s(v0)}]')
    if p == 'right': return out(f'right-[{_s(v0)}]')
    if p == 'bottom': return out(f'bottom-[{_s(v0)}]')
    if p == 'left': return out(f'left-[{_s(v0)}]')
    if p == 'inset': return out(f'inset-[{_s(v0)}]')
    if p == 'gap': return out(f'gap-[{_s(v0)}]')
    if p == 'margin':
        parts = v0.split()
        if len(parts)==1: return out(f'm-[{_s(parts[0])}]')
        return out(f'[margin:{_s(v0)}]')
    if p == 'padding':
        parts = v0.split()
        if len(parts)==1: return out(f'p-[{_s(parts[0])}]')
        return out(f'[padding:{_s(v0)}]')
    if p == 'margin-top': return out(f'mt-[{_s(v0)}]')
    if p == 'margin-bottom': return out(f'mb-[{_s(v0)}]')
    if p == 'margin-left': return out(f'ml-[{_s(v0)}]')
    if p == 'margin-right': return out(f'mr-[{_s(v0)}]')
    if p == 'padding-top': return out(f'pt-[{_s(v0)}]')
    if p == 'padding-bottom': return out(f'pb-[{_s(v0)}]')
    if p == 'padding-left': return out(f'pl-[{_s(v0)}]')
    if p == 'padding-right': return out(f'pr-[{_s(v0)}]')
    if p == 'border-radius': return out(f'rounded-[{_s(v0)}]')
    if p == 'border':
        if v0 in ('0','none'): return out('border-0')
        m = re.match(r'(\d+\w*)\s+(solid|dashed|dotted|double)\s+(.+)', v0)
        if m:
            w, st, col = m.groups()
            utils = [f'border-[{w}]']
            if st != 'solid': utils.append(f'border-{st}')
            utils.append(color_util('border', col))
            return [bang + u for u in utils]
        return [bang + f'[border:{_s(v0)}]']
    if p in ('border-top','border-bottom','border-left','border-right'):
        side = p.split('-')[1][0]  # t b l r
        if v0 in ('0','none'): return out(f'border-{side}-0')
        m = re.match(r'(\d+\w*)\s+(solid|dashed|dotted|double)\s+(.+)', v0)
        if m:
            w, st, col = m.groups()
            utils = [f'border-{side}-[{w}]']
            if st != 'solid': utils.append(f'border-{st}')
            utils.append(color_util(f'border-{side}', col))
            return [bang + u for u in utils]
        return [bang + f'[{p}:{_s(v0)}]']
    if p == 'border-color': return out(color_util('border', v0))
    if p == 'border-width': return out(f'border-[{_s(v0)}]')
    if p == 'border-style': return out(f'border-{v0}') if v0 in ('solid','dashed','dotted','double','none') else out(f'[border-style:{v0}]')
    if p == 'border-left-width': return out(f'border-l-[{_s(v0)}]')
    if p == 'border-right-width': return out(f'border-r-[{_s(v0)}]')
    if p == 'border-top-width': return out(f'border-t-[{_s(v0)}]')
    if p == 'border-bottom-width': return out(f'border-b-[{_s(v0)}]')
    if p == 'border-left-color': return out(color_util('border-l', v0))
    if p == 'border-right-color': return out(color_util('border-r', v0))
    if p == 'border-top-color': return out(color_util('border-t', v0))
    if p == 'border-bottom-color': return out(color_util('border-b', v0))
    if p == 'box-shadow': return out(shadow_util(v0))
    if p == 'transition':
        if ',' not in v0:
            m = re.match(r'^([\w-]+|all)\s+([\d.]+m?s)\s+(\S.*)$', v0)
            if m:
                tprop, tdur, tease = m.groups()
                props_map = {'opacity':'transition-opacity','transform':'transition-transform','background':'transition-colors','background-color':'transition-colors','color':'transition-colors','all':'transition-all'}
                pu = props_map.get(tprop, f'[transition-property:{tprop}]')
                return [bang + pu, bang + duration_util(tdur), bang + ease_util(tease)]
        return [bang + f'[transition:{_s(v0)}]']
    if p == 'transition-duration': return out(duration_util(v0))
    if p == 'transition-timing-function': return out(ease_util(v0))
    if p == 'transition-property': return out(f'[transition-property:{_s(v0)}]')
    if p == 'transition-delay': return out(f'delay-[{_s(v0)}]')
    if p == 'transform': return out(f'[transform:{_s(v0)}]')
    if p == 'transform-origin': return out(f'[transform-origin:{_s(v0)}]')
    if p == 'text-decoration-color': return out(f'decoration-[{_s(v0)}]')
    if p == 'text-decoration-thickness': return out(f'decoration-[{_s(v0)}]')
    if p == 'content': return out(f'content-[{_s(v0)}]')
    if p == 'flex':
        if v0 == '1' or v0 == '1 1 0%': return out('flex-1')
        return out(f'flex-[{_s(v0)}]')
    if p == 'flex-shrink': return out('shrink-0') if v0=='0' else out(f'[flex-shrink:{v0}]')
    if p == 'flex-grow': return out('grow-0') if v0=='0' else out(f'[flex-grow:{v0}]')
    if p == 'flex-wrap' and v0 in ('wrap','nowrap','wrap-reverse'): return out(f'flex-{v0}')
    if p == 'grid-template-columns': return out(f'grid-cols-[{_s(v0)}]')
    if p == 'grid-template-rows': return out(f'grid-rows-[{_s(v0)}]')
    if p == 'text-underline-offset': return out(f'underline-offset-[{_s(v0)}]')
    if p == 'filter': return out(f'[filter:{_s(v0)}]')
    if p == 'backdrop-filter':
        mbb = re.match(r'^blur\(([\w.]+)\)', v0)
        if mbb: return out(f'backdrop-blur-[{mbb.group(1)}]')
        return out(f'[backdrop-filter:{_s(v0)}]')
    if p == '-webkit-backdrop-filter': return []
    if p == 'font-family': return out(f'[font-family:{_s(v0)}]')
    if p == 'font': return out(f'[font:{_s(v0)}]')
    if p == 'font-variant-numeric': return out(f'[font-variant-numeric:{_s(v0)}]')
    if p == 'place-items': return out(f'place-items-{v0}')
    if p == 'border-collapse': return out(f'border-{v0}')
    if p == 'outline':
        if v0 == 'none' or v0 == '0': return out('outline-none')
        m = re.match(r'(\d+\w*)\s+(solid|dashed|dotted|double)\s+(.+)', v0)
        if m:
            w, st, col = m.groups()
            utils = [f'outline-[{w}]', color_util('outline', col)]
            if st != 'solid': utils.append(f'outline-{st}')
            return [bang + u for u in utils]
        return [bang + f'[outline:{_s(v0)}]']
    if p == 'outline-offset': return out(f'outline-offset-[{_s(v0)}]')
    if p == 'box-sizing': return out(f'[box-sizing:{v0}]')
    if p == 'text-rendering': return out(f'[text-rendering:{v0}]')
    if p == '-webkit-font-smoothing': return out('antialiased') if v0=='antialiased' else []
    if p == 'counter-reset': return out(f'[counter-reset:{_s(v0)}]')
    if p == 'counter-increment': return out(f'[counter-increment:{_s(v0)}]')
    if p == 'animation':
        key = _norm_val(v0)
        if key in ANIM_REV: return out(f'animate-{ANIM_REV[key]}')
        return out(f'[animation:{_s(v0)}]')
    if p == 'mix-blend-mode': return out(f'mix-blend-{v0}')
    if p == 'vertical-align':
        if v0 in ('middle','top','bottom','baseline','super','sub'): return out(f'align-{v0}')
        return out(f'[vertical-align:{v0}]')
    if p == 'object-fit': return out(f'object-{v0}')
    if p == 'word-break': return out(f'break-{v0}')
    if p == 'text-overflow' and v0 == 'ellipsis': return out('text-ellipsis')
    if p == 'touch-action': return out(f'[touch-action:{_s(v0)}]')
    if p == 'aspect-ratio': return out(f'aspect-[{_s(v0)}]')
    if p == 'isolation': return out(f'[isolation:{v0}]')
    if p == 'border-image':
        if v0 == 'initial': return []  # no-op
        return out(f'[border-image:{_s(v0)}]')
    if p == '-webkit-text-size-adjust': return []
    if p == 'text-size-adjust': return out(f'[text-size-adjust:{v0}]')
    if p == 'print-color-adjust': return out(f'[print-color-adjust:{v0}]')
    if p == 'will-change': return out(f'[will-change:{_s(v0)}]')
    return [bang + f'[{p}:{_s(v0)}]']

# ---------- @media -> variant ----------
PRINT_MQ = re.compile(r'^\s*print\s*$')
MAXW_MQ = re.compile(r'^\(\s*max-width\s*:\s*(\d+)px\s*\)\s*$')
MINW_MQ = re.compile(r'^\(\s*min-width\s*:\s*(\d+)px\s*\)\s*$')

SM_BREAKPOINTS = {'640':'sm','768':'md','1024':'lg','1280':'xl','1536':'2xl'}

def mq_to_variant(mq):
    mq = mq.strip().lower().replace('only ','').replace('screen and ','').replace('screen ','').strip()
    if PRINT_MQ.match(mq): return 'print:'
    m = MAXW_MQ.match(mq)
    if m:
        px = m.group(1)
        # max-width:X => max-{bp} where X = bp-1 ? tailwind max-sm is < 640
        # we treat max-width:640 as max-sm:, max-width:1099 as max-ep:
        for bp_px, bp_name in SM_BREAKPOINTS.items():
            if str(int(bp_px)) == px: return f'max-{bp_name}:'
        # custom breakpoint? ep=1100 -> max-ep means <1100; css max-width:1099 -> max-ep-1:? approximate
        for name, val in SCREENS.items():
            if val.replace('px','') == str(int(px)+1): return f'max-{name}:'
            if val.replace('px','') == px: return f'max-{name}:'
        return f'[@media(max-width:{px}px)]:'
    m = MINW_MQ.match(mq)
    if m:
        px = m.group(1)
        for bp_px, bp_name in SM_BREAKPOINTS.items():
            if bp_px == px: return f'{bp_name}:'
        for name, val in SCREENS.items():
            if val.replace('px','') == px: return f'{name}:'
        return f'[@media(min-width:{px}px)]:'
    # compound like (hover:none) etc
    return f'[@media{mq.replace(" ", "")}]:'

# ---------- selector parsing ----------
PSEUDO_VARIANT_MAP = {
    ':hover': 'hover',':focus': 'focus',':focus-visible': 'focus-visible',':focus-within': 'focus-within',
    ':active': 'active',':disabled': 'disabled',':checked': 'checked',':empty': 'empty',
    ':first-child': 'first',':last-child': 'last',
    '::before': 'before','::after': 'after','::placeholder': 'placeholder',
    '::first-letter': 'first-letter','::first-line': 'first-line','::marker': 'marker','::selection': 'selection',
}
ID_RE = r'#[\w-]+'; CLASS_RE = r'\.[\w-]+'; TAG_RE = r'[a-zA-Z][\w-]*'

def parse_base_and_tail(tok):
    m = re.match(r'(\*|' + ID_RE + '|' + CLASS_RE + '|' + TAG_RE + ')', tok)
    if not m: return tok, ''
    base = m.group(1); rest = tok[m.end():]
    # greedily absorb narrowing qualifiers (.class, [attr], :not(...)) into the base
    while rest:
        m2 = re.match(r'(\.[\w-]+|\[[^\]]+\]|:not\([^)]+\))', rest)
        if not m2: break
        base += m2.group(1); rest = rest[m2.end():]
    return base, rest

def tail_to_variant(tail):
    if not tail: return '', ''
    variants = []; rest = tail
    while rest:
        matched = False
        for pseudo, var in sorted(PSEUDO_VARIANT_MAP.items(), key=lambda x: -len(x[0])):
            if rest.startswith(pseudo):
                nxt = rest[len(pseudo)] if len(rest) > len(pseudo) else ''
                if nxt in ('', ':', '.', '[', ' ', '#'):
                    variants.append(var); rest = rest[len(pseudo):]; matched = True; break
        if matched: continue
        m = re.match(r':not\(([^)]+)\)', rest)
        if m: variants.append(f'[&:not({m.group(1)})]'); rest = rest[m.end():]; continue
        m = re.match(r'(\.[\w-]+)', rest)
        if m: variants.append(f'[&{m.group(1)}]'); rest = rest[m.end():]; continue
        m = re.match(r'(\[[^\]]+\])', rest)
        if m: variants.append(f'[&{m.group(1)}]'); rest = rest[m.end():]; continue
        return None, tail
    return ':'.join(variants) + ':' if variants else '', ''

def classify_selector(sel):
    sel = sel.strip(); tokens = sel.split()
    if len(tokens) == 1:
        base, tail = parse_base_and_tail(tokens[0])
        if not base: return None, None
        var, _ = tail_to_variant(tail)
        if var is None: return None, None
        return base, var
    first = tokens[0]; rest_toks = tokens[1:]
    base, base_tail = parse_base_and_tail(first)
    if not base: return None, None
    base_var, _ = tail_to_variant(base_tail)
    if base_var is None: return None, None
    rest_esc = ' '.join(rest_toks).replace(' ', '_')
    return base, f'{base_var}[&_{rest_esc}]:'

# ---------- main ----------
m = re.search(r'<style[^>]*>(.+?)</style>', HTML, re.S)
if not m: print('no <style>'); sys.exit(1)
css_text = m.group(1)
vars_map = collect_vars(css_text)
print(f'CSS vars collected: {len(vars_map)}')
print(f'Config tokens: colors={len(colors)} shadows={len(shadows)} durs={len(durations)} eases={len(easings)} anims={len(animations)} screens={len(screens)}')

sheet = cssutils.parseString(css_text)
classmap = defaultdict(list); unclassified = []

def style_decls(rule):
    """Yield (name, value, !important) preserving original value text."""
    for d in rule.style:
        if not d.name or not d.value: continue
        val = inline_vars(d.value, vars_map)
        yield d.name, val, d.priority == 'important'

def emit_rule(sel_text, decls, mq_prefix=''):
    for sel in [s.strip() for s in sel_text.split(',')]:
        utils = []
        for name, val, imp in decls:
            utils.extend(u for u in decl_to_tw(name, val, imp) if u and u not in ('!',))
        if not utils: continue
        base, variant = classify_selector(sel)
        if base is None:
            unclassified.append((f'{mq_prefix or ""}{sel}', utils)); continue
        classmap[base].append((mq_prefix + variant, utils, (mq_prefix or '') + sel))

for rule in sheet:
    t = rule.typeString
    if t == 'STYLE_RULE':
        emit_rule(rule.selectorText, list(style_decls(rule)))
    elif t == 'MEDIA_RULE':
        mqv = mq_to_variant(rule.media.mediaText)
        for inner in rule.cssRules:
            if inner.typeString == 'STYLE_RULE':
                emit_rule(inner.selectorText, list(style_decls(inner)), mq_prefix=mqv)

# ---------- build output ----------
out = {}
for base, entries in sorted(classmap.items()):
    by_variant = defaultdict(list); provenance = []
    for var, utils, orig in entries:
        by_variant[var].extend(utils)
        provenance.append({'variant': var, 'utils': ' '.join(utils), 'from': orig})
    variant_clean = {}
    for var, utils in by_variant.items():
        seen = set(); keep = []
        for u in utils:
            if u not in seen: seen.add(u); keep.append(u)
        variant_clean[var] = ' '.join(f'{var}{u}' for u in keep) if var else ' '.join(keep)
    out[base] = {
        'classes': ' '.join(variant_clean.values()),
        'by_variant': variant_clean,
        'provenance': provenance
    }

payload = {
    'vars': vars_map,
    'config_tokens': {'colors': colors, 'shadows': shadows, 'durations': durations, 'easings': easings, 'animations': animations, 'screens': screens},
    'selectors': out,
    'unclassified': [{'selector': s, 'utils': ' '.join(u)} for s,u in unclassified],
}
pathlib.Path('/opt/personal/git/endometrioza/tools/classmap.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(f'Base selectors: {len(out)}  Unclassified: {len(unclassified)}')
for u in unclassified[:20]: print('  UNC:', u[0])
print('wrote tools/classmap.json')
