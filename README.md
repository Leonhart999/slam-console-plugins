# SLAM & AutoNav console plugins

The plugin index of the [SLAM & AutoNav console](https://github.com/Leonhart999/slam-autonav-console). The
console's **Plugins → Plugin market** tab reads [`index.json`](index.json) from here, downloads the plugin zip of an
entry, checks its size and SHA-256 and unpacks it into the plugin folder. Installed plugins start disabled; enable
them, install their Python packages and restart the console.

Each plugin lives in a fork of the open-source project it is built on, in `robot_console_plugin/<id>/`, and its zip
is a release asset of that fork.

| Plugin | Repository (upstream) | What it does |
|---|---|---|
| `map_eval` Map quality evaluation | [Leonhart999/small_gicp](https://github.com/Leonhart999/small_gicp/tree/master/robot_console_plugin) ([koide3/small_gicp](https://github.com/koide3/small_gicp), MIT) | Registers a map onto a reference cloud (another map, or an uploaded PCD/PLY) and computes accuracy, completeness, precision, F-score and Chamfer distance, with an error-coloured top view. |
| `loop_closures` Loop closure check | [Leonhart999/MapClosures](https://github.com/Leonhart999/MapClosures/tree/main/robot_console_plugin) ([PRBonn/MapClosures](https://github.com/PRBonn/MapClosures), MIT) | Finds the places a mapping run revisited (maps recorded with *Save raw scans*) and measures how far the SLAM odometry had drifted at each loop. |

The console also ships three tool plugins of its own (bag converter, ground segmentation, dynamic object removal) and
the AI assistant; they are not listed here.

## Index format

```json
{
  "format": 1,
  "name": "SLAM & AutoNav console plugins",
  "updated": "2026-11-21",
  "plugins": [
    {
      "id": "map_eval", "version": "0.1.0", "api": 1,
      "name": {"zh": "...", "en": "..."}, "description": {"zh": "...", "en": "..."},
      "author": "...", "license": "MIT", "homepage": "https://...", "source": "https://...", "upstream": "https://...",
      "requirements": ["small_gicp==1.0.1", "numpy>=1.23,<3"],
      "url": "https://github.com/<owner>/<repo>/releases/download/console-map_eval-v0.1.0/map_eval-0.1.0.zip",
      "sha256": "<64 hex digits>", "size": 123456, "published": "2026-11-21"
    }
  ]
}
```

One entry per plugin (the newest version). `api` is the console plugin interface the plugin needs; consoles that do
not support it show the entry as incompatible. `requirements` are shown before installing; the console installs them
into the plugin's own virtual environment when the user asks for it.

## Adding or updating a plugin

1. In the plugin's repository: build its page, then `python3 robot_console_plugin/package.py <id>` writes
   `dist/<id>-<version>.zip` (reproducible) and `dist/<id>-<version>.entry.json`.
2. Create a release `console-<id>-v<version>` of that repository with the zip attached.
3. Here: `python3 tools/add_entry.py path/to/<id>-<version>.entry.json --check-url` (downloads the zip and compares
   size and SHA-256), commit and push `index.json`.

The plugin interface is described in the console's `docs/plugins.md`.

## Licence

The index and the tools are MIT-licensed. Each plugin has its own licence (see its entry); the projects the plugins
are built on keep theirs.
