<div align="center">

<img src="htdocs/luci-static/carbon/logo.svg" width="72" height="72" alt="Carbon">

# luci-theme-carbon-legacy

The Apple-style glassmorphism Carbon LuCI theme, packaged for **Lua LuCI / OpenWrt 21.02** firmware — built for GL.iNet routers.

**This is a Legacy-only fork.** All OpenWrt 23.05+ (ucode LuCI) code, the online updater, the custom-logo uploader and the APK packaging from the upstream project have been removed; this tree ships only the Lua-template theme for 21.02-based firmware.

**English** · [简体中文](README.zh-CN.md)

Upstream: [mrjoechen/luci-theme-carbon](https://github.com/mrjoechen/luci-theme-carbon) · License: [Apache-2.0](LICENSE)

</div>

## What works on OpenWrt 21.02 (GL.iNet firmware)

- **Custom dashboard** on Status → Overview: multi-interface live traffic, resource usage, temperature, Wi-Fi and network panels, with presets, show/hide and reordering — **persisted in `/etc/config/carbon`** and restored on every page load.
- **Per-device up/down speed** via `nlbwmon` (optional `nftables` named counters, see [docs/device-traffic.md](docs/device-traffic.md)).
- **Discovered devices** merged from DHCP leases, Wi-Fi stations and ARP neighbours, with brand identification.
- **Simple / professional menu modes**; the simple menu is freely editable (add, remove, reorder any installed LuCI page) and **persisted in `/etc/config/carbon`**.
- Frosted-glass collapsible sidebar (<kbd>Ctrl</kbd>/<kbd>⌘</kbd> + <kbd>\\</kbd>), light/dark/auto appearance, bundled translations (13 languages).
- Phone-friendly: the sidebar becomes a drawer, tables turn into cards.

Online theme updates and the custom logo upload are **not available** in this Legacy port (they require the modern rpcd backend).

## Install

Copy the IPK to `/tmp` and install over SSH:

```sh
scp -O dist-legacy/luci-theme-carbon-legacy_*_all.ipk root@192.168.8.1:/tmp/
ssh root@192.168.8.1
opkg install /tmp/luci-theme-carbon-legacy_*_all.ipk
```

Then refresh the browser and **log out and back in once** (rpcd ACLs need a fresh session for the dashboard and saving to work).

## Build

No SDK is required for the ready-to-install IPK:

```sh
python3 scripts/build-ipk-nosdk.py . dist-legacy
```

Alternatively, build with the matching GL.iNet 21.02 SDK via `scripts/build-legacy-ipk.sh` — see [docs/gl-mt6000-legacy-21.02.md](docs/gl-mt6000-legacy-21.02.md) for device verification, manual build steps and recovery instructions.

## Layout

| Path | Purpose |
|---|---|
| `legacy/21.02/` | Lua theme shell: `header.htm` / `footer.htm`, controller, rpcd backend (`set_dashboard`, `set_simple_menu`), ACL, uci-defaults |
| `htdocs/luci-static/carbon/` | Shared theme assets: `carbon.css` (generated from `styles/`), `carbon.js` (all theme logic), i18n, icons |
| `htdocs/luci-static/resources/` | LuCI client glue: `menu-carbon.js` (menu + dashboard mount), `carbon/traffic.js` (traffic collectors) |
| `preview/` | Standalone browser demo of the theme UI (mock data) |
| `scripts/` | Build tooling: CSS/i18n generators, SDK-free IPK builder, SDK-based legacy builder |
| `tests/` | Node unit tests and Playwright browser tests |

## Fix included: saved customisations survive reloads

The upstream Legacy port saved dashboard/menu customisations through rpcd but never read them back on page render, so changes were lost after refresh. `legacy/21.02/luasrc/view/themes/carbon/header.htm` now injects the saved `carbon.dashboard` / `carbon.simple_menu` UCI sections as `data-dashboard` / `data-simple-menu` attributes (same validation rules as the rpcd backend), matching what the modern ucode template does.
