# E2E tests

```
cd /tmp/endo-tests     # or wherever @playwright/test is installed
node /opt/personal/git/endometrioza/tests/e2e.mjs
```

Screenshots land in `/tmp/endo-tests/shots/`. Measurements print to stdout and are saved to `/tmp/endo-tests/report.txt`.

Setup (once):
```
mkdir -p /tmp/endo-tests && cd /tmp/endo-tests
npm init -y && npm i -D @playwright/test
npx playwright install chromium
```
