# Warscape world-generation terrain policy

Read the repository AGENTS.md and `doc/WarscapeTerrainGeneration.md` before changing or creating a generator.

New landscapes receive biome-appropriate, irregular local relief on walkable ground by default during initial generation. Flat terrain requires an explicit request or a deliberately protected surface.

- Use `terrain_detail.py`; do not duplicate a private noise implementation as the default for a new map.
- `generate.adt`/`generate.main`, `lumbridge.adt`, and `briarbrook.Village.height_field` enable the shared treatment. New custom encoders must invoke `terrain_detail.prepare` or `field` too.
- Apply after broad terrain grading. Ground objects against the final sampler. Keep floors, foundations, entrances, bridges, NPC standing areas and liquid boundaries protected, with gradual falloffs. Roads are gentler, not perfectly flat strips.
- `prepare` retains the raw base when reconfigured. Regenerate from an immutable base, never from a previously displaced output. Saved-map refinements require explicit component accounting and preservation of newer edits.
- Use `detail_applied=True` only for an already detailed sampler or an explicitly preserved saved surface; never use it to silently omit the new-map default. The native encoder recognizes `DetailedHeight` automatically.
- Explicit flat practice/template maps use `ground_detail.flat: true` or `generate.adt(..., flat=True)`. Keep intentionally level designed surfaces level.
- Preserve existing maps, saved Noggit work and unrelated changes. Archived fixed-ID generators are historical references, not safe new-map templates; wire a fork into the shared stage before creating a new landscape.
- Test continuity across actual ADT edges, normals, protected surfaces, repeatability/idempotence and the flat exception. Use a disposable undeployed generation for new default changes. User performs game visual/gameplay testing.
