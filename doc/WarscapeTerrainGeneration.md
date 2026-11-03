# Warscape natural-ground generation default

Confirmed by the user, 31 October 2026:

> New landscapes receive biome-appropriate, irregular local relief on walkable ground by default during initial generation. Flat terrain requires an explicit request or a deliberately protected surface.

This is an initial-generation default, not authorization to change existing maps. Ashen Crown 911 is the only existing map included in the current implementation request. Preserve every other saved project and runtime deployment.

## Shared implementation

`contrib/warscape/worldgen/terrain_detail.py` supplies:

- `Settings`: reproducible seed, biome, feature scale in metres, density and strength, plus native vertex spacing and explicit flat/disabled controls.
- `field(east, north, settings)`: a continuous world-coordinate local-height component, supporting scalar Python and NumPy arrays. Domain warping, jittered compact anisotropic features, coherent smaller variation and broad density modulation produce overlapping mounds/hollows with quieter patches. The field does not use per-vertex random offsets or repeated circular brush stamps. Its minimum feature radius is three native corner spacings.
- `Protection`: circles, boxes and roads, with smooth falloffs. Roads retain a reduced contribution; protected structures/liquids use zero contribution.
- `prepare(base_sampler, cfg, protection=...)`: a final height sampler in server X/Y coordinates. It evaluates relief at east=-Y, north=X, excludes steep base slopes, and retains its original base. Rewrapping replaces settings instead of stacking displacement.
- `config_protection`: native WMO/prepared-building footprints, already grounded M2 bases, OSRS-transformed roads/paving/river margins, and explicitly declared critical surfaces.

The default field uses woodland hummocks/hollows; volcanic settings bias towards irregular ash accumulation and shallow subsidence; snow uses more elongated drift forms; settlement strength is restrained. These adapt one standard, rather than applying the same pattern to every biome. Seed changes produce independent layouts.

Example configuration:

```json
{
  "ground_detail": {
    "seed": 91321,
    "biome": "volcanic",
    "scale": 25.0,
    "density": 1.15,
    "strength": 1.0,
    "protected": [
      {"kind": "circle", "center": [25, -40], "radius": 5, "falloff": 9},
      {"kind": "box", "bounds": [-20, -30, 20, 0], "falloff": 12}
    ]
  }
}
```

Scale changes feature spacing/width; density changes how frequently features appear, with mesh-resolution limits; strength changes their height. Increase frequency by tuning scale/density before increasing strength. All coordinates in explicit protection entries are east/north world metres. Callers with polygonal liquids or additional critical surfaces should supply a matching distance/protection callback, not rely on filenames or approximate global elevations.

## Entry points and stage order

| Entry point | Default treatment and ordering |
|---|---|
| `generate.py` CLI | `Settings.from_config` is passed to the native ADT generator during initial creation. Existing Test 1 and development sandbox configs explicitly request flat output. |
| `generate.adt` | Natural local relief and matching normals by default, including direct calls. `flat=True` creates an exact constant-height template. |
| `build.py` | Extracts the generated natural-height tiles and validates their navigation; level-tile validation is restricted to explicitly flat configurations. |
| `lumbridge.adt` | Wraps the caller's final graded height sampler by default, including independent custom samplers. Native placement/road/liquid masks preserve existing grounding and designed surfaces. Height queries are batched for performance. |
| `briarbrook.Village.height_field` | Applies the field after broad hills and foundation grading, before cellar excavation, scenery grounding and serialization. Its encoder call uses `detail_applied=True`. |
| `refine_briarbrook.py` | Explicit saved-map refiner; retains its authorized saved surface and uses `detail_applied=True`. It does not implicitly retrofit the new default to an existing map. |

`lumbridge.height` remains the historical broad/base sampler. Initial ADT creation adds the shared final stage; code needing a preview or to ground new scenery against the final field should prepare that sampler before those operations:

```python
from terrain_detail import prepare, config_protection

mask = config_protection(cfg, native_placements, world=existing_osrs_to_world)
final_height = prepare(authored_base_height, cfg, protection=mask)
# Use final_height for both object grounding and initial ADT creation.
data = lumbridge.adt(cfg, tx, ty, assets, native_placements,
                    height_sampler=final_height, surface_sampler=paint)
```

The native encoder recognizes `DetailedHeight` and does not add another contribution. For an already sampled/detailed array exposed by an ordinary callback, pass `detail_applied=True`. Do not use this flag to omit the default for a new landscape. Later grading/smoothing must either precede the detail stage or be deliberately confined to protected surfaces. Native MCVT normals must be calculated from the final sampler.

### Independent historical authors

The fixed-ID Ashen Crown `author_ashen.py`, Rebuild-001 custom encoder, and TutorialIsland2 variant `author_variants.py` rebuild native chunks independently. They are archived authors/refiners of already existing maps, outside the reusable initial-generation CLI; they are not executed or silently rewritten for this default. Their live projects remain untouched. A new-map fork must replace/extend its final height sampler with `terrain_detail.prepare` or add `field` once after grading, then ground scenery and regenerate normals/collision/navigation. The shared sampler API above covers those encoders without rerunning an old author over saved Noggit work. Project instructions in both the repository and `C:\WoWDev\Worldgen\AGENTS.md` require this integration for any new fork.

## Explicit flat exception

Use `"ground_detail": {"flat": true}` in a flat practice/template config or `generate.adt(..., flat=True)` for direct calls. The permanent sandbox and original flat loading-probe configurations now state that intent explicitly. Their output remains exactly flat, with up normals and no displacement. Protected floors/foundations are also exact, without disabling natural variation across the rest of a map.

When forking a historical flat-probe config for a new natural landscape, remove its `flat: true` setting unless the user explicitly requests a flat map.

## Repeatability and verification

Rebuild initial landscapes from the authored base, not from exported MCVT heights. `prepare` unwraps its previous component when reconfigured. Existing-map refinements need a verified prior contribution or another explicit base/component decomposition; never blindly apply the field over a previously detailed saved map.

Focused tests:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -m unittest discover -s contrib/warscape/worldgen -p test_terrain_detail.py -v
```

Tests cover scalar/array parity, coordinate-partition invariance, reconfiguration without accumulation, exact protection/flat exceptions, biome differences, frequency versus height and actual neighbouring ADT heights/normals. Use targeted existing serializer/generator tests after integration changes. Verify a small disposable generation outside Git with no DBC registration or deployment. Native/offline visuals do not establish live game appearance or comfortable traversal; the user performs those checks.
