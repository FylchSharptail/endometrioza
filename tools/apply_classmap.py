#!/usr/bin/env -S /Users/ext.grzegorz.grabarz/.venv/css2tw/bin/python3
"""Apply Tailwind utility chains from classmap.json to index.html.

Usage: apply_classmap.py [--dry] SELECTOR...
  SELECTOR is a base selector key from classmap.json (e.g. '.card', '.ts', 'sup.ref').

For each base selector:
  - find matching elements via CSS selector in index.html
  - merge classmap['classes'] into their class="" attr (dedupe)
  - strip the selector's source CSS rules from the <style> block

Preserves file formatting outside of edited class attrs and the <style> block.
"""
import sys, re, json, pathlib, argparse
import cssutils
from bs4 import BeautifulSoup
cssutils.log.setLevel('FATAL')

ROOT = pathlib.Path('/opt/personal/git/endometrioza')
HTML_PATH = ROOT / 'index.html'
MAP_PATH = ROOT / 'tools' / 'classmap.json'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('selectors', nargs='+')
    args = ap.parse_args()

    cm = json.loads(MAP_PATH.read_text())
    html = HTML_PATH.read_text()

    soup = BeautifulSoup(html, 'html.parser')
    summary = []
    # For each touched element, collect (tag, original_class_attr_value_or_None, new_class_str)
    # then perform surgical regex replacement in the original HTML text to preserve formatting.
    touched = []  # list of dicts: {id, tag, old_class, new_class}

    for sel in args.selectors:
        if sel not in cm['selectors']:
            print(f'SKIP: {sel} not in classmap', file=sys.stderr); continue
        entry = cm['selectors'][sel]
        util_chain = entry['classes']
        try:
            matches = soup.select(sel)
        except Exception as e:
            print(f'SKIP: {sel} bs4 error: {e}', file=sys.stderr); continue
        summary.append(f'  {sel}: {len(matches)} elements, +{len(util_chain.split())} utils')
        for el in matches:
            existing = el.get('class') or []
            if isinstance(existing, str): existing = existing.split()
            new_utils = util_chain.split()
            merged = list(existing)
            seen = set(merged)
            for c in new_utils:
                if c not in seen: merged.append(c); seen.add(c)
            if merged == list(existing): continue
            touched.append({'tag': el.name, 'old': ' '.join(existing), 'new': ' '.join(merged), 'el': el})
            el['class'] = merged

    # Surgical patch: for each touched element, find its original start-tag in raw HTML
    # and replace class="..." in place. Match on tag + attribute signature (stable enough:
    # if same tag+attrs appears N times, bs4 visits in document order; we consume matches sequentially).
    new_html = html
    cursor = 0
    for t in touched:
        tag, old_cls, new_cls = t['tag'], t['old'], t['new']
        # Build regex that finds <tag ... class="OLD" ...> OR <tag ...> (when old_cls empty)
        if old_cls:
            pat = re.compile(r'<' + re.escape(tag) + r'\b([^>]*?)\bclass\s*=\s*\"' + re.escape(old_cls) + r'\"([^>]*?)>', re.S)
            def repl(m, new_cls=new_cls):
                return f'<{tag}{m.group(1)}class="{new_cls}"{m.group(2)}>'
        else:
            # no existing class attr: insert class="..." right after tag name
            pat = re.compile(r'<' + re.escape(tag) + r'(\s[^>]*)?>', re.S)
            def repl(m, new_cls=new_cls):
                attrs = m.group(1) or ''
                return f'<{tag} class="{new_cls}"{attrs}>'
        m = pat.search(new_html, cursor)
        if not m:
            m = pat.search(new_html)
            if not m:
                print(f'WARN: could not locate <{tag} class="{old_cls}"> in HTML', file=sys.stderr); continue
        new_html = new_html[:m.start()] + repl(m) + new_html[m.end():]
        cursor = m.start() + len(repl(m))

    # Strip CSS rules for processed selectors (surgical text walk)
    m = re.search(r'(<style[^>]*>)(.+?)(</style>)', new_html, re.S)
    if m:
        css_body = m.group(2); style_start = m.start(2)
        targets = set(args.selectors)
        new_css, removed_ct = strip_rules(css_body, targets)
        new_html = new_html[:style_start] + new_css + new_html[style_start + len(css_body):]
        summary.append(f'  stripped {removed_ct} CSS rules from <style>')

    print('APPLY SUMMARY:')
    for line in summary: print(line)
    if args.dry:
        print('DRY RUN (no write)')
    else:
        HTML_PATH.write_text(new_html)
        print(f'WROTE {HTML_PATH}')

# Mirror of converter's compound-base peel logic (so strip-match aligns with apply-match)
def classify_base(sel):
    sel = sel.strip(); tokens = sel.split()
    tok = tokens[0]
    m = re.match(r'(\*|#[\w-]+|\.[\w-]+|[a-zA-Z][\w-]*)', tok)
    if not m: return sel
    base = m.group(1); rest = tok[m.end():]
    while rest:
        m2 = re.match(r'(\.[\w-]+|\[[^\]]+\]|:not\([^)]+\))', rest)
        if not m2: break
        base += m2.group(1); rest = rest[m2.end():]
    return base

def strip_rules(css, targets):
    """Surgical CSS rule strip: walk char-by-char, remove top-level rules whose ALL
    comma-separated selectors classify to a target base. Preserves original whitespace
    and comments elsewhere. Skips @media blocks (left as-is for later cleanup)."""
    out = []; i = 0; n = len(css); removed = 0
    while i < n:
        ch = css[i]
        # pass through comments
        if css[i:i+2] == '/*':
            j = css.find('*/', i+2); j = n if j < 0 else j + 2
            out.append(css[i:j]); i = j; continue
        # at-rules: pass entire block through untouched
        if ch == '@':
            # find selector/prelude end at either ; or { matching
            j = i
            while j < n and css[j] not in ';{': j += 1
            if j < n and css[j] == ';':
                out.append(css[i:j+1]); i = j+1; continue
            # brace block: find matching close
            depth = 0; k = j
            while k < n:
                if css[k] == '{': depth += 1
                elif css[k] == '}':
                    depth -= 1
                    if depth == 0: k += 1; break
                k += 1
            out.append(css[i:k]); i = k; continue
        # whitespace
        if ch.isspace():
            out.append(ch); i += 1; continue
        # regular rule: capture selector up to '{'
        sel_start = i
        while i < n and css[i] != '{':
            if css[i:i+2] == '/*':
                j = css.find('*/', i+2); i = n if j < 0 else j + 2; continue
            i += 1
        if i >= n: out.append(css[sel_start:]); break
        sel_text = css[sel_start:i]
        brace_start = i
        depth = 1; i += 1
        while i < n and depth > 0:
            if css[i] == '{': depth += 1
            elif css[i] == '}': depth -= 1
            i += 1
        rule_end = i  # position after closing }
        # classify: all selectors must be targets to strip
        sels = [s.strip() for s in sel_text.split(',') if s.strip()]
        all_target = sels and all(classify_base(s) in targets for s in sels)
        if all_target:
            # also swallow trailing newline if present to avoid leaving blank lines
            if rule_end < n and css[rule_end] == '\n': rule_end += 1
            removed += 1
        else:
            out.append(css[sel_start:rule_end])
        i = rule_end
    return ''.join(out), removed

if __name__ == '__main__':
    main()
