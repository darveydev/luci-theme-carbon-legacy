module("luci.controller.carbon", package.seeall)

-- Do NOT cache any upvalue for use inside index().
-- LuCI's createindex() serialises the index function with util.get_bytecode()
-- into /tmp/luci-indexcache.*.lua and reloads it via loadfile(); after that
-- round-trip every upvalue becomes nil. A module-level `local fs = require
-- "nixio.fs"` therefore turns into nil on the cached path and raises
-- "attempt to index upvalue 'fs' (a nil value)", which takes the whole LuCI
-- menu tree down with HTTP 500. Require inside index() instead; entry /
-- template / translate come from the dispatcher function environment
-- (__index = luci.dispatcher) and must not be captured either.
function index()
	local fs = require "nixio.fs"
	if not fs.access("/etc/config/luci") then return end

	local page = entry({"admin", "system", "carbon"}, template("carbon/settings"), _("Carbon Theme"), 95)
	page.dependent = true
	-- Requiring the theme ACL group grants the dashboard read access to
	-- /proc/stat, /proc/meminfo, /proc/net/arp and network.wireless status.
	-- Those are denied by the stock LuCI ACLs, which is why CPU / storage /
	-- traffic / wireless used to show "unavailable".
	page.acl_depends = { "luci-mod-admin-full", "luci-theme-carbon" }
end
