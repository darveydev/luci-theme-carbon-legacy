<div align="center">

<img src="htdocs/luci-static/carbon/logo.svg" width="72" height="72" alt="Carbon">

# luci-theme-carbon-legacy

Apple 风格毛玻璃 LuCI 主题 Carbon 的 **OpenWrt 21.02（Lua LuCI）专用移植版**，面向 GL.iNet 路由器。

**本仓库只保留 Legacy（21.02）代码。** 上游项目中 OpenWrt 23.05 及以上（ucode LuCI）的代码、网页在线升级、自定义 Logo 上传和 APK 打包均已移除。

[English](README.md) · **简体中文**

上游项目：[mrjoechen/luci-theme-carbon](https://github.com/mrjoechen/luci-theme-carbon) · 许可：[Apache-2.0](LICENSE)

</div>

## 在 OpenWrt 21.02（GL.iNet 固件）上的功能

- **自定义仪表盘**（状态 → 概览）：多接口实时流量、资源占用、温度、Wi-Fi 与网络状态面板，支持预设、显隐与排序——**保存在 `/etc/config/carbon`，刷新页面不丢失**。
- **设备上下行网速**：默认使用 `nlbwmon`，可选 `nftables` 命名计数器（见 [docs/device-traffic.md](docs/device-traffic.md)）。
- **已发现设备**：整合 DHCP 租约、Wi-Fi 终端与 ARP 邻居，支持品牌识别。
- **简洁 / 专业双模式菜单**：简洁模式可自由增删排序任意已安装的 LuCI 页面，**同样持久化保存**。
- 毛玻璃可收起侧栏（<kbd>Ctrl</kbd>/<kbd>⌘</kbd> + <kbd>\\</kbd>）、浅色 / 深色 / 跟随系统、内置 13 种语言。
- 适配手机：侧栏变抽屉，表格变卡片。

Legacy 版**不包含**网页在线升级和自定义 Logo 上传（需要现代版的 rpcd 后端）。

## 安装

把 IPK 传到路由器 `/tmp` 后通过 SSH 安装：

```sh
scp -O dist-legacy/luci-theme-carbon-legacy_*_all.ipk root@192.168.8.1:/tmp/
ssh root@192.168.8.1
opkg install /tmp/luci-theme-carbon-legacy_*_all.ipk
```

安装后刷新浏览器并**退出重新登录一次**（rpcd ACL 需要新会话，仪表盘和保存功能才能生效）。

## 构建

无需 SDK 即可打出可直接安装的 IPK：

```sh
python3 scripts/build-ipk-nosdk.py . dist-legacy
```

也可以使用匹配的 GL.iNet 21.02 SDK 构建（`scripts/build-legacy-ipk.sh`），设备验证、手动构建与回退步骤见 [docs/gl-mt6000-legacy-21.02.md](docs/gl-mt6000-legacy-21.02.md)。

## 目录结构

| 路径 | 说明 |
|---|---|
| `legacy/21.02/` | Lua 主题外壳：`header.htm` / `footer.htm`、controller、rpcd 后端（`set_dashboard`、`set_simple_menu`）、ACL、uci-defaults |
| `htdocs/luci-static/carbon/` | 共享主题资源：`carbon.css`（由 `styles/` 生成）、`carbon.js`（全部主题逻辑）、i18n、图标 |
| `htdocs/luci-static/resources/` | LuCI 客户端胶水层：`menu-carbon.js`（菜单 + 仪表盘挂载）、`carbon/traffic.js`（流量采集） |
| `preview/` | 主题 UI 独立浏览器演示（模拟数据） |
| `scripts/` | 构建工具：CSS / i18n 生成器、无 SDK IPK 打包、SDK 构建脚本 |
| `tests/` | Node 单元测试与 Playwright 浏览器测试 |

## 已修复：自定义配置刷新后不再丢失

上游 Legacy 移植版虽然能通过 rpcd 把仪表盘/菜单自定义写入 UCI，但页面渲染时不回读，导致刷新后配置"丢失"。现在 `legacy/21.02/luasrc/view/themes/carbon/header.htm` 会把已保存的 `carbon.dashboard` / `carbon.simple_menu` UCI 配置注入为 `data-dashboard` / `data-simple-menu` 属性（校验规则与 rpcd 后端一致），与现代 ucode 模板行为对齐。
