# GL-MT6000 Legacy LuCI theme port

This package target is the Lua-template LuCI found on GL.iNet firmware based on OpenWrt 21.02. It is a separate package (`luci-theme-carbon-legacy`) and must be built using the matching GL.iNet SDK/buildroot. The normal Carbon package in this repository targets ucode-based LuCI and must not be installed on 21.02.

## Verify the device first

On the router, run:

```sh
cat /etc/openwrt_release
cat /etc/glversion 2>/dev/null
opkg list-installed | grep -E '^(luci|rpcd|ucode|lua)'
ls /usr/lib/lua/luci/view/themes
```

Build for the exact GL-MT6000 firmware release and target. GL.iNet firmware contains vendor changes; do not replace LuCI, rpcd, kernel modules, or vendor packages with packages from a generic OpenWrt feed.

## Build

Put the project on the build host, then pass the matching SDK/buildroot directory to the helper:

```sh
sh scripts/build-legacy-ipk.sh /path/to/gl-mt6000-matching-sdk
```

The generated package is copied to `dist-legacy/`. The helper stages the package under `package/luci-theme-carbon-legacy`, copies the shared static resources, and invokes the SDK build. If building manually, copy `legacy/21.02` into that package directory, add `htdocs/luci-static/carbon` and `htdocs/luci-static/resources/menu-carbon.js`, then build:

```sh
make package/luci-theme-carbon-legacy/compile V=s
```

The package is architecture-independent, but building with the matching SDK is still required to resolve the old LuCI packaging rules and dependencies.

## Install and recover

Copy the IPK to `/tmp` and install over SSH:

```sh
scp -O dist-legacy/luci-theme-carbon-legacy_*_all.ipk root@192.168.8.1:/tmp/
ssh root@192.168.8.1
opkg install /tmp/luci-theme-carbon-legacy_*_all.ipk
```

Refresh the browser and log into LuCI again. To restore the previous theme, use the router's LuCI System → System → Language and Interface page if available, or over SSH:

```sh
uci set luci.main.mediaurlbase=/luci-static/bootstrap
uci commit luci
rm -f /tmp/luci-indexcache*
```

Then uninstall the legacy package:

```sh
opkg remove luci-theme-carbon-legacy
```

If this GL firmware does not have `/luci-static/bootstrap`, substitute the theme path present under `/www/luci-static/`. Keep SSH access available during first installation.

## Port status and limits

The Legacy tree provides a Lua header/footer and controller entry point while reusing Carbon's static CSS, JavaScript, translations, and icons. It does not ship the modern ucode templates, JSON menu registration, or updater backend. The visual shell and dashboard scripts depend on the LuCI JavaScript modules and ubus objects exposed by the installed GL firmware. Verify these on the target device before broad deployment; the current tree has not been validated against every GL-MT6000 stock firmware revision. A missing RPC endpoint can disable its dashboard widget, and persistence or online-update functions that depend on the modern Carbon rpcd backend are not provided by this Legacy package yet.
