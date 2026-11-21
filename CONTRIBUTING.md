# Contributing Plugins to the Market

This guide defines the development rules, UI design requirements, packaging limits and submission workflow for plugins listed in [`index.json`](index.json) of the **SLAM & AutoNav console** (**Plugin Interface v1**, `api: 1`).

For the full runtime API reference, see `docs/plugins.md` and `docs/plugin-guidelines.md` in [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console).

---

## 1. Repository Layout & Manifest (`plugin.yaml`)

Each plugin built on an open-source project should live in a fork of that project under `robot_console_plugin/<id>/`, with its release zip attached to a GitHub Release of that repository.

```text
robot_console_plugin/
  package.py            # reproducible zip + entry.json generator
  <id>/                 # folder name MUST equal plugin.yaml id
    plugin.yaml         # required manifest
    backend.py          # optional backend module (or backend/__init__.py) with setup(ctx)
    worker.py           # recommended subprocess worker for heavy jobs / third-party packages
    ui/
      plugin.js         # pre-built IIFE frontend bundle (committed/packaged; users need no Node.js)
      plugin.css        # pre-built stylesheet
    web/                # optional frontend source (excluded from zip: node_modules, .vite, dist)
```

### Manifest Rules
`robot_console` validates `plugin.yaml` strictly before loading:

- `id`: **MUST** match `^[a-z][a-z0-9_]{1,39}$` and equal the plugin folder name.
- `api`: **MUST** be integer `1`.
- `version`: **MUST** be a non-empty string (<= 40 chars); SemVer (e.g. `0.1.0`) is recommended.
- `name` & `description`: **MUST** provide both Chinese and English (`{zh: ..., en: ...}`).
- `license`: **MUST** be declared; preserve the upstream project's licence terms.
- `upstream`: **MUST** be set (`https://...`) when wrapping an upstream open-source project.
- `homepage`: optional `http(s)://` URL.
- `backend.module`: **MUST** match `^[A-Za-z_][A-Za-z0-9_]*$` and expose `setup(ctx)`.
- `frontend`: `dir` (default `ui`), `script` (`plugin.js`), optional `style` (`plugin.css`). No absolute paths, `..`, or backslashes.
- `python.requirements`: optional, 1–40 entries. Each entry **MUST** be a plain PEP 508 name + optional extras + version specifiers (no URLs, local paths, environment markers, or pip flags such as `--index-url`).
- `settings`: optional. `key` matches `^[a-z][a-z0-9_]{0,39}$`; `type` is one of `string`, `text`, `number`, `integer`, `boolean`, `select`, `secret`. Do not set `default` on `secret`. Quote YAML 1.1 booleans (`on`, `off`, `yes`, `no`) if ever needed as values.

---

## 2. Security, Isolation & Backend Rules

1. **No internal imports**: Read and mutate console data **only** via `ctx.api` (the console's public REST API; `/api/plugins*` is blocked). Never import internal `robot_console.*` Python modules.
2. **Isolate third-party Python packages**: Declare packages in `python.requirements` and execute them **only** in child processes (`ctx.jobs` or `ctx.run_python`). Never import plugin-venv packages into the console process (keeps ROS/NumPy dependencies and copyleft licences isolated).
3. **Never block the event loop**: Any task taking more than ~200 ms (point cloud processing, registration, conversion, disk scans) **MUST** run as a background job via `ctx.jobs.submit(...)` or `await ctx.run_python(...)`.
4. **Worker protocol** (`ctx.python -E -s <plugin_dir>/<script> <job_dir>`):
   - Read `<job_dir>/input.json`.
   - Flush JSON progress lines to stdout: `{"progress": 0.42, "phase": "registering"}` (`0.0`–`1.0`); plain output goes to `log.txt`.
   - Write compact `result.json` on exit `0` (keep large binaries/images as separate files served via `/jobs/{job}/files/{name}`).
   - Write `error.json` (`{"code": "plugin.<id>.<code>", "params": {...}}`) on non-zero exit.
   - Write large artifacts atomically (temp file + rename) so cancelled jobs leave no corrupt output.
5. **Structured errors & live settings**: Raise `ctx.error(status, code, **params)` (translated via `errors.<code>`) or `ctx.console_error(...)`. Read `ctx.settings()` per request rather than caching once in `setup()`.
6. **No hardcoded secrets or machine paths**: Store user credentials in `type: secret` settings (never echo them in responses or logs). Store plugin data under `ctx.data_dir`.
7. **Non-destructive map outputs**: When generating a modified map, call `POST /api/maps/{name}/derive` to create a derived map version instead of overwriting an existing map.
8. **Clean shutdown**: Release threads/handles in `ctx.on_shutdown(fn)`.

---

## 3. Frontend & SDK Rules (`window.RobotConsole`)

1. **Pre-built IIFE bundle**: Build `ui/plugin.js` and `ui/plugin.css` (`cssCodeSplit: false`) with `vue` and `element-plus` externalized to `RobotConsole.vue` and `RobotConsole.ui`.
2. **Runtime-only Vue**: Use pre-compiled `.vue` SFCs or render functions (`h()`). Runtime template strings are not supported.
3. **Whitelisted components only**:
   - Console components from `window.RobotConsole.ui`: `GlassPanel`, `KpiTile`, `InfoTip`.
   - Element Plus components: `ElAlert`, `ElButton`, `ElCheckbox`, `ElDialog`, `ElDivider`, `ElDrawer`, `ElEmpty`, `ElForm`, `ElFormItem`, `ElIcon`, `ElInput`, `ElInputNumber`, `ElLink`, `ElOption`, `ElPopconfirm`, `ElProgress`, `ElRadio`, `ElRadioButton`, `ElRadioGroup`, `ElScrollbar`, `ElSelect`, `ElSwitch`, `ElTable`, `ElTableColumn`, `ElTag`, `ElTooltip`, `ElMessage`, `ElMessageBox`.
   - Do **not** import unlisted Element Plus components (they are `undefined` at runtime) and do **not** bundle full Element Plus CSS.
4. **Registration**: Call `window.RobotConsole.register({ id, messages, pages?, header? })` synchronously once. `pages[i].path` must match `^[a-z0-9][a-z0-9_-]{0,39}$`; `pages[i].title` must be concise bilingual `{zh, en}` (recommended <= 6 Chinese chars / <= 20 English chars).
5. **CSS isolation**: Prefix all custom classes with a short plugin-specific prefix (e.g. `.me-*`, `.lc-*`) and use `<style scoped>`. Never modify global `html`, `body`, `.glass`, `.chip`, `.panel`, or unscoped `.el-*` rules.

---

## 4. UI Design Requirements

The console uses a **clean frosted-glass HUD aesthetic** with full **Light** and **Dark (`html.dark`)** theme support. Plugin pages must feel native to the console.

### 4.1 Design Tokens (No Hardcoded Theme Colors)
Use the console's CSS variables from `web/src/style.css` so one stylesheet works in both Light and Dark looks:

- **Typography**: `var(--font-ui)` for UI copy; add `.mono` (`var(--font-mono)` + `tabular-nums`) for all numbers, coordinates, timestamps, matrices, paths and metrics.
- **Text**: `var(--ink)` (primary), `var(--ink-2)` (secondary), `var(--ink-3)` (muted/captions). Never hardcode `#333`, `#666`, `#000`, or `#fff` on theme surfaces.
- **Accent & status**: `var(--accent)`, `var(--accent-2)`, `var(--accent-grad)`, `var(--ok)`, `var(--warn)`, `var(--bad)`, `var(--idle)`. For colored text on tinted backgrounds, mix with `var(--ink)` or `var(--deepen)` via `color-mix(...)`.
- **Surfaces & hairlines**: `var(--glass)`, `var(--glass-strong)`, `var(--paper)`, `var(--hairline)`, `var(--glass-edge)`, `var(--canvas-bg)`.

### 4.2 Component & Layout Standards
- **Top-level sections**: Wrap major blocks in `GlassPanel` (pass `:flush="true"` for tables, `tip="..."` for section help). Stack panels with `gap: 14px`.
- **KPIs & status**: Use `KpiTile` (or a responsive card grid `minmax(220px, 1fr)`) for metrics, `.chip` (`success` / `warning` / `danger` / `primary` / `info`, optional `.live`) for status pills, and `InfoTip` beside non-obvious algorithm parameters. Avoid decorative emojis in UI labels.
- **Python environment gate**: Plugins declaring `python.requirements` **MUST** display a top notice with an **Install Python packages** button while `python.state !== 'ready'` and disable job submission until ready (keep history readable).
- **Responsive layout**:
  - The console rail collapses to a `68px` icon bar at `<= 1180px`; pages must fit cleanly at both **`1440x1000`** and **`1100x700`** (content width ~`980px`).
  - Use responsive grids (`repeat(auto-fill, minmax(260px, 1fr))`), allow long names/paths to wrap (`min-width: 0; overflow-wrap: anywhere`), and collapse multi-column result areas to a single column on narrow widths.
- **Header items & floating panels**: Never obstruct the top header clock (`top >= 64px`) or the bottom status / E-STOP bar (`bottom >= 84px`). Use `width="min(860px, 94vw)"` and `append-to-body` on `ElDialog`.
- **Charts & artifacts**: Prefer lightweight inline SVG (`viewBox`, CSS-variable colors, `<title>` tooltips) for simple plots. Include units (`m`, `deg`, `%`, `s`), colorbar legends for images, `<ElEmpty />` for empty states, and download links for `result.json` / generated files.

### 4.3 Mandatory UI Smoke Checks (`tools/ui_smoke.sh`)
Every plugin page must pass `tools/ui_smoke.sh` across **`1440x1000` & `1100x700`**, **`light` & `dark`**, and **`zh-CN` & `en`**:

- 0 uncaught exceptions, 0 `console.error`, 0 Vue/vue-i18n warnings, 0 unexpected 4xx/5xx responses.
- 0 raw i18n keys rendered in text, `title`, `aria-label`, or `placeholder`.
- 0 clipped elements, 0 unexpected horizontal scrollbars (including `el-table`), 0 elements past the right viewport edge.
- 0 multi-line wraps or box overflows on table headers (`th .cell`), buttons, `.chip` pills, radio buttons, or `.num`/`.name` table cells.
- Minimum WCAG contrast ratio **>= 2.2:1** everywhere (recommended >= 4.5:1 for body text) in both light and dark themes.

### 4.4 Bilingual Copy (i18n)
- Provide complete `zh-CN` and `en` translations in both `plugin.yaml` and `register({ messages })` (including `phases.*`, `warnings.*`, `errors.*`).
- Avoid unescaped vue-i18n special characters (`{`, `}`, `@`, `|`, `$`) in plain text outside `{param}` placeholders.
- Use `–` (en dash) for missing values.

---

## 5. Packaging & Submitting to the Market

### 5.1 Archive Requirements
`robot_console/plugin_market.py` enforces the following archive limits on every install:

- Exactly **one** top-level folder named `<id>/` containing a valid `plugin.yaml` whose `id`, `version`, and `api` match the index entry.
- **No** symbolic links, absolute paths, `..`, `node_modules`, `__pycache__`, `.pytest_cache`, `.vite`, `.pyc`/`.log`, or dotfiles.
- Maximum **5,000** files, **512 MB** unpacked, and **64 MB** zip download size.
- Reproducible zip output (sorted entries, fixed timestamps) so SHA-256 is deterministic.

### 5.2 Submission Steps
1. Run backend unit tests (`pytest`, offline with synthetic data) and frontend checks (`vue-tsc --noEmit`, `vite build`, and `tools/ui_smoke.sh`).
2. Build the frontend (`ui/plugin.js` + `ui/plugin.css`) and package with:
   ```bash
   python3 robot_console_plugin/package.py <id>
   ```
   This produces `dist/<id>-<version>.zip` and `dist/<id>-<version>.entry.json`.
3. Create a GitHub Release tagged `console-<id>-v<version>` in the plugin repository and attach `<id>-<version>.zip`. Ensure the entry's `url` uses `https://`.
4. Add or update the entry in this repository and verify the live download size and SHA-256:
   ```bash
   python3 tools/add_entry.py path/to/<id>-<version>.entry.json --check-url
   ```
5. Open a pull request (or commit) updating `index.json` with a brief summary of what the plugin does and how it was tested.

---

## 6. Pre-Submission Checklist

- [ ] `plugin.yaml` passes validation (`id`, `api: 1`, bilingual `name`/`description`, `license`, `upstream`, clean `python.requirements`)
- [ ] Backend uses `ctx.api` only, isolates third-party packages in subprocesses (`ctx.jobs` / `ctx.run_python`), and contains no hardcoded secrets or machine paths
- [ ] Frontend is pre-built to `ui/plugin.js` + `ui/plugin.css`, externalizes `vue` & `element-plus`, and uses only whitelisted SDK components
- [ ] Styling uses console CSS tokens + plugin class prefixes, includes `PythonGate` / `InfoTip` / `ElEmpty`, and never obscures the header clock or bottom E-STOP bar
- [ ] `tools/ui_smoke.sh` passes at `1440x1000` & `1100x700` x `light` & `dark` x `zh-CN` & `en`
- [ ] Unit tests pass; `package.py` + `tools/add_entry.py --check-url` succeed cleanly
