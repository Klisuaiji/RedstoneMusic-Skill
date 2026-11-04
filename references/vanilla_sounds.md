# Vanilla sound-effect palette (no resource pack)

This file documents the curated vanilla sound events that may be used as non-pitched musical
events in `song.json`. They are played with the ordinary `/playsound` command, so they require
**no resource pack and no mod**.

## Supported events

| Event ID (without namespace) | Suggested musical use | Minimum Java version |
|---|---|---:|
| `entity.villager.ambient` | short vocal-like rhythmic motif / background texture | 1.13 |
| `entity.parrot.ambient` | chirp-like accent / syncopation | 1.13 |
| `item.flintandsteel.use` | sharp transient / beat accent | 1.13 |
| `block.fire.ambient` | sustained low-level texture (use sparingly) | 1.13 |
| `block.fire.extinguish` | short transition accent | 1.13 |

The palette is deliberately curated rather than accepting arbitrary event strings. This catches
misspelled or unavailable IDs during validation. Add an event only after checking it against the
target Java version's vanilla sound-event registry.

## song.json schema

Sound effects are separate from pitched note tracks:

```json
{
  "effects": [
    {
      "t": 24,
      "sound": "entity.villager.ambient",
      "vol": 0.35,
      "pitch": 1.0,
      "category": "voice"
    },
    {
      "t": 48,
      "sound": "item.flintandsteel.use",
      "vol": 0.55,
      "pitch": 1.0,
      "category": "player"
    },
    {
      "t": 72,
      "sound": "entity.parrot.ambient",
      "vol": 0.4,
      "pitch": 1.15,
      "category": "ambient"
    }
  ]
}
```

- `t` uses the same timeline units as note events in the same song.
- `sound` is the vanilla sound-event ID **without** the `minecraft:` namespace.
- `vol` defaults to `1.0`; valid range is `0.0..16.0`.
- `pitch` defaults to `1.0`; valid range is `0.5..2.0`. This changes playback speed/pitch,
  but does not turn the effect into a pitched instrument.
- `category` defaults to `voice`; supported values are `master`, `music`, `record`,
  `weather`, `block`, `hostile`, `neutral`, `player`, `ambient`, and `voice`.
- Multiple effects may occur on the same tick, including alongside note-block notes.

## Arrangement guidance

Use effects as accents, fills, transitions, or restrained ambience. They should not replace the
MIDI melody or obscure its attacks. A useful starting point is to keep effect volume below the lead
melody and avoid continuous loud ambience. The generator preserves their exact timeline positions;
the final balance must still be judged by listening in Minecraft.
