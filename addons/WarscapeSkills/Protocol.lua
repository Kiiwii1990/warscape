-- Lua 5.1 / original 3.3.5a. Snapshot assembly is separate from UI for testing.
WarscapeSkillsProtocol = {}
local P = WarscapeSkillsProtocol
local function integer(s, min, max)
    local n = tonumber(s)
    if n and n == math.floor(n) and n >= min and n <= max then return n end
end
function P.New(token)
    return {token = token, revision = 0}
end
function P.Receive(state, message, now)
    if #message > 240 then return end
    local f = {}
    for value in string.gmatch(message .. "|", "([^|]*)|") do f[#f + 1] = value end
    local rev = integer(f[4], 1, 4294967295)
    if f[2] ~= "1" or f[3] ~= state.token or not rev or rev <= state.revision then return end
    if f[1] == "B" and #f == 5 then
        local count = integer(f[5], 1, 64)
        if count then state.pending = {revision = rev, count = count, rows = {}, order = {}, started = now} end
        return
    end
    local p = state.pending
    if not p or p.revision ~= rev or now - p.started > 5 then return end
    if f[1] == "S" and #f == 10 then
        local id = f[5]
        if not string.match(id, "^[a-z][a-z0-9_]*$") or #id > 32 or p.rows[id] or #p.order >= p.count then return end
        local base = integer(f[6], 1, 99)
        local effective = f[7] ~= "-" and integer(f[7], 0, 255) or nil
        local xp = integer(f[8], 0, 200000000)
        local floor = integer(f[9], 0, 200000000)
        local nextXP = f[10] ~= "-" and integer(f[10], 1, 200000000) or nil
        if not base or not xp or not floor or xp < floor then return end
        if f[7] ~= "-" and not effective then return end
        if base == 99 then
            if f[10] ~= "-" then return end
        elseif not nextXP or nextXP <= floor or xp >= nextXP then return end
        p.rows[id] = {id = id, base = base, effective = effective, xp = xp, floor = floor, nextXP = nextXP}
        p.order[#p.order + 1] = id
    elseif f[1] == "E" and #f == 4 and #p.order == p.count then
        state.revision = rev
        state.pending = nil
        return p
    end
end
