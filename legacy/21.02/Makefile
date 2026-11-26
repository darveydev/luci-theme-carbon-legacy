include $(TOPDIR)/rules.mk

LUCI_TITLE:=Carbon Theme Legacy (Lua LuCI / OpenWrt 21.02)
LUCI_DEPENDS:=+luci-base +luci-mod-admin-full
LUCI_PKGARCH:=all
LUCI_TYPE:=theme

PKG_NAME:=luci-theme-carbon-legacy
PKG_VERSION:=1.1.9
PKG_RELEASE:=22
PKG_LICENSE:=Apache-2.0
PKG_MAINTAINER:=Carbon Theme contributors

define Package/luci-theme-carbon-legacy/postrm
#!/bin/sh
[ "$${PKG_UPGRADE}" = 1 ] || [ "$$1" = upgrade ] && exit 0
[ -n "$${IPKG_INSTROOT}" ] && exit 0
uci -q delete luci.themes.Carbon
if [ "$$(uci -q get luci.main.mediaurlbase)" = "/luci-static/carbon" ]; then
	uci set luci.main.mediaurlbase=/luci-static/bootstrap
	uci commit luci
fi
rm -f /tmp/luci-indexcache*
exit 0
endef

include $(TOPDIR)/feeds/luci/luci.mk

# Place this directory at package/luci-theme-carbon-legacy in the matching GL.iNet
# 21.02 SDK. Static resources remain shared with the repository root.
