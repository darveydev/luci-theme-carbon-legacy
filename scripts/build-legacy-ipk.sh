#!/bin/sh
# Build the Lua-template Legacy package using a matching OpenWrt/GL.iNet SDK.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SDK=${1:?Usage: build-legacy-ipk.sh /path/to/matching-sdk [output-dir]}
OUT=${2:-"$ROOT/dist-legacy"}
PKG="$SDK/package/luci-theme-carbon-legacy"

[ -f "$SDK/include/toplevel.mk" ] || { echo "Not an OpenWrt SDK/buildroot: $SDK" >&2; exit 1; }
[ ! -e "$PKG" ] || { echo "Refusing to overwrite existing package directory: $PKG" >&2; exit 1; }
mkdir -p "$PKG/luasrc/view/themes/carbon" "$PKG/luasrc/view/carbon" "$PKG/luasrc/controller" "$PKG/root"
cp "$ROOT/legacy/21.02/Makefile" "$PKG/Makefile"
cp -R "$ROOT/legacy/21.02/luasrc/." "$PKG/luasrc/"
cp -R "$ROOT/legacy/21.02/root/." "$PKG/root/"
mkdir -p "$PKG/htdocs/luci-static"
cp -R "$ROOT/htdocs/luci-static/carbon" "$PKG/htdocs/luci-static/"
mkdir -p "$PKG/htdocs/luci-static/resources"
cp -R "$ROOT/htdocs/luci-static/resources/menu-carbon.js" "$PKG/htdocs/luci-static/resources/"
cp -R "$ROOT/htdocs/luci-static/resources/carbon" "$PKG/htdocs/luci-static/resources/"
chmod 0755 "$PKG/root/etc/uci-defaults/30_luci-theme-carbon"
make -C "$SDK" package/luci-theme-carbon-legacy/compile V=s
mkdir -p "$OUT"
find "$SDK/bin/packages" -type f -name 'luci-theme-carbon-legacy_*_all.ipk' -exec cp -v {} "$OUT/" \;
if ! find "$OUT" -maxdepth 1 -type f -name 'luci-theme-carbon-legacy_*_all.ipk' | grep -q .; then
	echo "Build completed but no Legacy IPK was found under $SDK/bin/packages" >&2
	exit 1
fi
