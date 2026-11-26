#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 luci-theme-carbon-legacy-main 的 legacy/21.02 树打包成可直接 opkg install 的 IPK。

无 SDK 依赖：IPK 就是 ar 包 + 两个 tar.gz（control.tar.gz / data.tar.gz），
opkg 1bf042dd（OpenWrt 21.02）原生支持该格式。

用法: python build_ipk.py <项目根> <输出目录>
"""
import io, os, sys, tarfile, time, hashlib

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "dist-legacy")

PKG = "luci-theme-carbon-legacy"
VERSION = "1.1.9"
RELEASE = "22"
ARCH = "all"
DESC = "Carbon Theme Legacy (Lua LuCI / OpenWrt 21.02)"
MAINTAINER = "Carbon Theme contributors"
LICENSE = "Apache-2.0"

KT = 315532800  # 1980-01-01, 与 OpenWrt ipkg 一致（可复现构建）


def add(files, arcname, mode=0o644):
    """files: [(本地绝对路径, 包内相对路径)]"""
    for src, rel in files:
        with open(src, "rb") as f:
            data = f.read()
        ti = tarfile.TarInfo(rel)
        ti.size = len(data)
        ti.mtime = KT
        ti.mode = mode if mode is not None else (0o755 if os.access(src, os.X_OK) else 0o644)
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        tar.addfile(ti, io.BytesIO(data))


def walk(base, prefix="", skip_dirs=()):
    out = []
    for r, ds, fs in os.walk(base):
        ds[:] = sorted(d for d in ds if d not in skip_dirs)
        for f in sorted(fs):
            full = os.path.join(r, f)
            rel = os.path.relpath(full, base).replace("\\", "/")
            out.append((full, (prefix + "/" + rel) if prefix else rel))
    return out


def build_data():
    files = []
    legacy = os.path.join(ROOT, "legacy", "21.02")
    # luasrc（Lua 模板 + controller）
    files += walk(os.path.join(legacy, "luasrc"), "usr/lib/lua/luci")
    # legacy 自带 root/（uci-defaults、version 标记）
    files += walk(os.path.join(legacy, "root"))
    # 静态资源（与仓库根共享）
    htd = os.path.join(ROOT, "htdocs", "luci-static")
    files += walk(os.path.join(htd, "carbon"), "www/luci-static/carbon")
    files += [(os.path.join(htd, "resources", "menu-carbon.js"),
               "www/luci-static/resources/menu-carbon.js")]
    files += walk(os.path.join(htd, "resources", "carbon"), "www/luci-static/resources/carbon")

    buf = io.BytesIO()
    tar = tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT)

    def perm(rel):
        # 只给会被执行的脚本 / Lua 模板 755，其余静态资源一律 644
        if rel.startswith("etc/uci-defaults/"):
            return 0o755
        if rel.startswith("usr/lib/lua/"):
            return 0o755
        # rpcd 后端必须可执行，否则 rpcd 无法 exec 它，
        # 表现为 ubus 对象不存在 → 前端保存报 -32002 Access denied
        if rel.startswith("usr/libexec/rpcd/"):
            return 0o755
        return 0o644

    # ★ 必须显式写入目录条目并排在文件之前。
    #   opkg 解包时不递归建父目录：缺 dir 条目时它 fopen 子文件直接
    #   "wfopen: ... No such file or directory"，而且仍把包标记为 installed。
    dirs = set()
    for _, rel in files:
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))

    for d in sorted(dirs):
        ti = tarfile.TarInfo("./" + d + "/")
        ti.type = tarfile.DIRTYPE
        ti.mode = 0o755
        ti.mtime = KT
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        tar.addfile(ti)

    for src, rel in sorted(files, key=lambda x: x[1]):
        mode = perm(rel)
        with open(src, "rb") as f:
            data = f.read()
        ti = tarfile.TarInfo("./" + rel)
        ti.size, ti.mtime, ti.mode, ti.uid, ti.gid = len(data), KT, mode, 0, 0
        ti.uname = ti.gname = "root"
        tar.addfile(ti, io.BytesIO(data))
    tar.close()
    return gzip_bytes(buf.getvalue()), files


def gzip_bytes(raw):
    return __import__("gzip").compress(raw, 9, mtime=0)


def build_control(installed_size_kb, file_count):
    postinst = """#!/bin/sh
[ -n "${IPKG_INSTROOT}" ] && exit 0
uci -q get luci.themes.Carbon >/dev/null || uci set luci.themes.Carbon=/luci-static/carbon
uci -q get luci.main.mediaurlbase | grep -q '/luci-static/carbon' || uci set luci.main.mediaurlbase=/luci-static/carbon
uci -q commit luci
rm -f /tmp/luci-indexcache* /tmp/luci-modulecache/* 2>/dev/null
exit 0
"""
    prerm = """#!/bin/sh
[ -n "${IPKG_INSTROOT}" ] && exit 0
exit 0
"""
    postrm = """#!/bin/sh
[ -n "${IPKG_INSTROOT}" ] && exit 0
if [ "$(uci -q get luci.main.mediaurlbase)" = "/luci-static/carbon" ]; then
\tuci set luci.main.mediaurlbase=/luci-static/bootstrap
uci -q delete luci.themes.Carbon
uci -q commit luci
fi
rm -f /tmp/luci-indexcache* /tmp/luci-modulecache/* 2>/dev/null
exit 0
"""
    control = (
        f"Package: {PKG}\n"
        f"Version: {VERSION}-{RELEASE}\n"
        f"Depends: libc, luci-base\n"
        f"Source: package/{PKG}\n"
        f"SourceName: {PKG}\n"
        f"Section: luci\n"
        f"SourceDateEpoch: 0\n"
        f"Maintainer: {MAINTAINER}\n"
        f"Architecture: {ARCH}\n"
        f"Installed-Size: {installed_size_kb}\n"
        f"Description:  {DESC}\n"
        f" This package is a Lua-template LuCI theme for OpenWrt 21.02 / GL.iNet\n"
        f" firmware. It ships the Carbon CSS/JS/i18n assets and registers the\n"
        f" theme as 'Carbon' in /etc/config/luci.\n"
        f"License: {LICENSE}\n"
    )
    buf = io.BytesIO()
    tar = tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT)
    for name, content, mode in (("control", control, 0o644),
                                ("postinst", postinst, 0o755),
                                ("prerm", prerm, 0o755),
                                ("postrm", postrm, 0o755)):
        b = content.encode()
        ti = tarfile.TarInfo("./" + name)
        ti.size, ti.mtime, ti.mode, ti.uid, ti.gid = len(b), KT, mode, 0, 0
        ti.uname = ti.gname = "root"
        tar.addfile(ti, io.BytesIO(b))
    tar.close()
    return control, gzip_bytes(buf.getvalue())


def ar_member(name, data, mtime=KT):
    """经典 ar 头：60 字节，name[16] mtime[12] uid[6] gid[6] mode[8] size[10] magic[2]"""
    header = (
        name.ljust(16)[:16]
        + str(mtime).ljust(12)[:12]
        + "0".ljust(6)
        + "0".ljust(6)
        + "100644".ljust(8)
        + str(len(data)).ljust(10)[:10]
        + "`\n"
    ).encode("ascii")
    pad = b"\n" if len(data) % 2 else b""
    return header + data + pad


def tar_bytes(entries):
    """entries: [(name, data, mode)] -> 未压缩 tar 字节（./ 前缀、数值属主）"""
    buf = io.BytesIO()
    tar = tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT)
    for name, data, mode in entries:
        ti = tarfile.TarInfo("./" + name)
        ti.size, ti.mtime, ti.mode, ti.uid, ti.gid = len(data), KT, mode, 0, 0
        ti.uname = ti.gname = "root"
        tar.addfile(ti, io.BytesIO(data))
    tar.close()
    return buf.getvalue()


def main():
    data_gz, files = build_data()          # data.tar.gz（已 gzip）
    control_txt, control_gz = build_control(
        max(1, sum(os.path.getsize(s) for s, _ in files) // 1024), len(files))

    # ★ OpenWrt .ipk 外层 = gzip 压缩的 tar（不是 ar！ar 是 Debian .deb，opkg 会报
    #   "Malformed package file"）。顺序固定：./debian-binary, ./data.tar.gz, ./control.tar.gz
    outer = tar_bytes([
        ("debian-binary", b"2.0" + bytes([10]), 0o644),
        ("data.tar.gz", data_gz, 0o644),
        ("control.tar.gz", control_gz, 0o644),
    ])
    ipk_bytes = gzip_bytes(outer)

    os.makedirs(OUTDIR, exist_ok=True)
    ipk = os.path.join(OUTDIR, f"{PKG}_{VERSION}-{RELEASE}_{ARCH}.ipk")
    with open(ipk, "wb") as f:
        f.write(ipk_bytes)

    total = sum(os.path.getsize(s) for s, _ in files)
    print(control_txt)
    print(f"文件数: {len(files)}   解包后总大小: {total} B ({total/1024:.0f} KB)")
    print(f"IPK : {ipk}")
    print(f"大小: {len(ipk_bytes)} B   外层: tar.gz（OpenWrt 格式）")
    print(f"sha256: {hashlib.sha256(ipk_bytes).hexdigest()}")


if __name__ == "__main__":
    main()
