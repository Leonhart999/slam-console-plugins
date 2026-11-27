# SLAM & AutoNav console plugins

The plugin index of the [SLAM & AutoNav console](https://github.com/Leonhart999/slam-autonav-console). The
console's **Plugins → Plugin market** tab reads [`index.json`](index.json) from here, downloads the plugin zip of an
entry, checks its size and SHA-256 and unpacks it into the plugin folder. Installed plugins start disabled; enable
them, install their Python packages and restart the console.

The index lists both external market plugins (each maintained in its own repository) and the plugins bundled with the
console (published here as `bundled-<id>-v<version>` release assets so every plugin is visible in one catalog and can
be updated independently from the market without reinstalling the console).

| Plugin | Distribution | Repository (upstream) | What it does |
|---|---|---|---|
| `ai_assistant` AI assistant | Bundled + Market | [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console/tree/main/robot_console/plugins/ai_assistant) | Header chat drawer backed by user-configured OpenAI-compatible / Anthropic endpoints or embedded CPA OAuth accounts, with read/run console tools, history and usage stats. |
| `bag_convert` Bag converter | Bundled + Market | [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console/tree/main/robot_console/plugins/bag_convert) ([ternaris/rosbags](https://gitlab.com/ternaris/rosbags), Apache-2.0) | Converts ROS1 `.bag` files (including Livox `CustomMsg`) into ROS2 sqlite3/MCAP bags for the Playback page. |
| `dynamic_removal` Dynamic object removal | Bundled + Market | [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console/tree/main/robot_console/plugins/dynamic_removal) ([KTH-RPL/dufomap](https://github.com/KTH-RPL/dufomap), BSD-3) | Removes points left by moving objects from maps with raw scans using DUFOMap and saves a cleaned derived map version. |
| `eye_care_ui` Eye-care anti-blue-light UI | Bundled + Market | [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console/tree/main/robot_console/plugins/eye_care_ui) | Adds a warm amber low-blue-light UI theme with live filter strength, warmth and contrast controls. |
| `ground_seg` Ground segmentation | Bundled + Market | [Leonhart999/slam-autonav-console](https://github.com/Leonhart999/slam-autonav-console/tree/main/robot_console/plugins/ground_seg) ([url-kaist/patchwork-plusplus](https://github.com/url-kaist/patchwork-plusplus), BSD-2) | Segments ground/non-ground with Patchwork++ and rebuilds the 2D occupancy grid from height above local ground. |
| `loop_closures` Loop closure check | Market | [Leonhart999/MapClosures](https://github.com/Leonhart999/MapClosures/tree/main/robot_console_plugin) ([PRBonn/MapClosures](https://github.com/PRBonn/MapClosures), MIT) | Finds the places a mapping run revisited (maps recorded with *Save raw scans*) and measures how far the SLAM odometry had drifted at each loop. |
| `map_eval` Map quality evaluation | Market | [Leonhart999/small_gicp](https://github.com/Leonhart999/small_gicp/tree/master/robot_console_plugin) ([koide3/small_gicp](https://github.com/koide3/small_gicp), MIT) | Registers a map onto a reference cloud (another map, or an uploaded PCD/PLY) and computes accuracy, completeness, precision, F-score and Chamfer distance, with an error-coloured top view. |
| `map_merge` Map alignment & merge | Market | [Leonhart999/KISS-Matcher](https://github.com/Leonhart999/KISS-Matcher/tree/main/robot_console_plugin) ([MIT-SPARK/KISS-Matcher](https://github.com/MIT-SPARK/KISS-Matcher), MIT) | Globally aligns two 3D maps from different sessions or arbitrary frames without an initial guess (KISS-Matcher + small_gicp refinement), previews overlap, and saves a voxel-merged derived map version. |
| `remote_control` Remote control | Market | [Leonhart999/remote-control](https://github.com/Leonhart999/remote-control/tree/main/robot_console_plugin) ([Peteroooooooo/remote-control](https://github.com/Peteroooooooo/remote-control), Apache-2.0) | Installs and manages the Remote Control P2P remote desktop on the Windows PC the console runs on (console in WSL), so a phone app or another Windows PC can control it: install and update, background service, connection codes with a QR code, devices and settings. |

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

The plugin interface is described in the console's `docs/plugins.md`. Development rules, UI design requirements and
submission checks are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence

The index and the tools are MIT-licensed. Each plugin has its own licence (see its entry); the projects the plugins
are built on keep theirs.
