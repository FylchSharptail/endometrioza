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

    # Strip CSS rules for processed selectors from <style>
    m = re.search(r'(<style[^>]*>)(.+?)(</style>)', new_html, re.S)
    if m:
        style_open, css_body, style_close = m.group(1), m.group(2), m.group(3)
        sheet = cssutils.parseString(css_body)
        targets = set(args.selectors)
        # Also add selectors that are comma-siblings to targets (e.g. .note,.warn rule).
        kept = []
        removed_ct = 0
        for rule in sheet:
            t = rule.typeString
            if t == 'STYLE_RULE':
                keep_sels = []
                for s in [x.strip() for x in rule.selectorText.split(',')]:
                    base = classify_base(s)
                    if base not in targets: keep_sels.append(s)
                if keep_sels:
                    rule.selectorText = ', '.join(keep_sels)
                    kept.append(rule.cssText)
                else:
                    removed_ct += 1
            elif t == 'MEDIA_RULE':
                inner_kept = []
                for inner in rule.cssRules:
                    if inner.typeString == 'STYLE_RULE':
                        keep_sels = []
                        for s in [x.strip() for x in inner.selectorText.split(',')]:
                            base = classify_base(s)
                            if base not in targets: keep_sels.append(s)
                        if keep_sels:
                            inner.selectorText = ', '.join(keep_sels)
                            inner_kept.append(inner.cssText)
                        else:
                            removed_ct += 1
                    else:
                        inner_kept.append(inner.cssText)
                if inner_kept:
                    kept.append(f'@media {rule.media.mediaText} {{\n' + '\n'.join(inner_kept) + '\n}')
            else:
                kept.append(rule.cssText)
        new_css = '\n'.join(kept)
        new_html = new_html[:m.start()] + style_open + new_css + style_close + new_html[m.end():]
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

if __name__ == '__main__':
    main()
