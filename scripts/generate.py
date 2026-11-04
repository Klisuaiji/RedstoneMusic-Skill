#!/usr/bin/env python3
# song.json → lemon-style mcfunction (algorithm reverse-verified against the lemon reference pack)
import json, os, sys, argparse, math

INSTRUMENTS = {
    "harp":            {"min": "1.13", "sound": "block.note_block.harp",               "base": 54},
    "bass":            {"min": "1.13", "sound": "block.note_block.bass",               "base": 30},
    "basedrum":        {"min": "1.13", "sound": "block.note_block.basedrum",           "base": 54},
    "snare":           {"min": "1.13", "sound": "block.note_block.snare",              "base": 54},
    "hat":             {"min": "1.13", "sound": "block.note_block.hat",                "base": 54},
    "bell":            {"min": "1.13", "sound": "block.note_block.bell",               "base": 78},
    "flute":           {"min": "1.13", "sound": "block.note_block.flute",              "base": 66},
    "chime":           {"min": "1.13", "sound": "block.note_block.chime",              "base": 78},
    "guitar":          {"min": "1.13", "sound": "block.note_block.guitar",             "base": 42},
    "xylophone":       {"min": "1.13", "sound": "block.note_block.xylophone",          "base": 78},
    "iron_xylophone":  {"min": "1.14", "sound": "block.note_block.iron_xylophone",     "base": 54},
    "cow_bell":        {"min": "1.14", "sound": "block.note_block.cow_bell",           "base": 54},
    "didgeridoo":      {"min": "1.14", "sound": "block.note_block.didgeridoo",         "base": 30},
    "bit":             {"min": "1.14", "sound": "block.note_block.bit",                "base": 54},
    "banjo":           {"min": "1.14", "sound": "block.note_block.banjo",              "base": 54},
    "pling":           {"min": "1.14", "sound": "block.note_block.pling",               "base": 54},
    "skeleton":        {"min": "1.20", "sound": "block.note_block.imitate.skeleton",        "base": 54},
    "wither_skeleton": {"min": "1.20", "sound": "block.note_block.imitate.wither_skeleton", "base": 54},
    "zombie":          {"min": "1.20", "sound": "block.note_block.imitate.zombie",          "base": 54},
    "creeper":         {"min": "1.20", "sound": "block.note_block.imitate.creeper",         "base": 54},
    "piglin":          {"min": "1.20", "sound": "block.note_block.imitate.piglin",         "base": 54},
    "dragon":          {"min": "1.20", "sound": "block.note_block.imitate.ender_dragon",   "base": 54},
    "trumpet":         {"min": "26.1", "sound": "block.note_block.trumpet",                "base": 54},
    "trumpet_exposed": {"min": "26.1", "sound": "block.note_block.trumpet_exposed",        "base": 54},
    "trumpet_weathered":{"min": "26.1","sound": "block.note_block.trumpet_weathered",      "base": 42},
    "trumpet_oxidized":{"min": "26.1", "sound": "block.note_block.trumpet_oxidized",       "base": 42},
}
HEADS = ("skeleton","wither_skeleton","zombie","creeper","piglin","dragon")

# Curated vanilla sound events used as non-pitched musical accents. Keep in sync with
# references/vanilla_sounds.md and validate_pack.py.
SOUND_EFFECTS = {
    "entity.villager.ambient": "1.13",
    "entity.parrot.ambient": "1.13",
    "item.flintandsteel.use": "1.13",
    "block.fire.ambient": "1.13",
    "block.fire.extinguish": "1.13",
}
SOUND_CATEGORIES = ("master", "music", "record", "weather", "block", "hostile",
                    "neutral", "player", "ambient", "voice")

def vt(v): return tuple(int(x) for x in str(v).split("."))
def pitch_of(uc): return 2 ** ((uc - 12) / 12.0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file"); ap.add_argument("-o","--out",required=True)
    ap.add_argument("--speed",type=int,default=None)
    ap.add_argument("--style",choices=["lemon","standalone"],default=None)
    a = ap.parse_args()
    song = json.load(open(a.json_file, encoding="utf-8"))
    m = song["meta"]
    speed = a.speed if a.speed is not None else m.get("speed", 2)
    style = a.style or m.get("style", "lemon")
    ns = m.get("namespace","minecraft")
    path = m.get("path","music/"+m.get("name","song"))
    sid = m.get("song_id",1); tag = m.get("mute_tag","no_music")
    nxt = m.get("next_song"); ver = m.get("mc_version","1.21")
    unit = m.get("time_unit","nbs_ticks"); tps = m.get("tempo_tps",10)
    scale = {"nbs_ticks": 20.0/tps*speed, "game_ticks": float(speed),
             "nbs_s_units": 1.0}.get(unit, 1.0)

    # Each event: (sound id, pitch, volume, sound category, kind).
    events, warns = {}, []
    for tr in song.get("tracks", []):
        if tr.get("include", True) is False: continue
        dinst = tr.get("instrument_default","harp")
        for n in tr.get("notes", []):
            raw = n["t"]*scale; t = round(raw)
            if abs(raw-t) > 1e-6:
                sys.exit("time %s does not convert to a whole number (%s); adjust tempo/speed or quantize" % (n["t"], raw))
            inst = n.get("inst", dinst)
            if inst not in INSTRUMENTS: sys.exit("unknown instrument: "+inst)
            if vt(ver) < vt(INSTRUMENTS[inst]["min"]):
                sys.exit("instrument %s needs MC %s+ (target %s)" % (inst, INSTRUMENTS[inst]["min"], ver))
            uc = n["midi"] - INSTRUMENTS[inst]["base"]
            if not 0 <= uc <= 24:
                warns.append("t=%s %s out of pitch range (uc=%d), clamped" % (n["t"], inst, uc)); uc = min(24,max(0,uc))
            if inst in HEADS: warns.append("t=%s head instrument ignores pitch" % n["t"])
            events.setdefault(t,[]).append((INSTRUMENTS[inst]["sound"], "%.6f"%pitch_of(uc),
                                            float(n.get("vol",1.0)), "voice", "note"))

    for e in song.get("effects", []):
        raw_t = e.get("t")
        if not isinstance(raw_t, (int, float)) or not math.isfinite(raw_t) or raw_t < 0:
            sys.exit("effect t must be a finite non-negative number: %r" % raw_t)
        raw = raw_t * scale; t = round(raw)
        if abs(raw-t) > 1e-6:
            sys.exit("effect time %s does not convert to a whole number (%s); quantize it first" % (raw_t, raw))
        sound = str(e.get("sound", ""))
        if sound.startswith("minecraft:"):
            sound = sound[len("minecraft:"): ]
        if sound not in SOUND_EFFECTS:
            sys.exit("unknown vanilla sound effect %r (see references/vanilla_sounds.md)" % sound)
        if vt(ver) < vt(SOUND_EFFECTS[sound]):
            sys.exit("sound effect %s needs MC %s+ (target %s)" % (sound, SOUND_EFFECTS[sound], ver))
        category = e.get("category", "voice")
        if category not in SOUND_CATEGORIES:
            sys.exit("invalid sound category %r (allowed: %s)" % (category, ", ".join(SOUND_CATEGORIES)))
        vol = float(e.get("vol", 1.0)); pitch = float(e.get("pitch", 1.0))
        if not math.isfinite(vol) or not 0.0 <= vol <= 16.0:
            sys.exit("effect volume must be in [0,16]: %r" % vol)
        if not math.isfinite(pitch) or not 0.5 <= pitch <= 2.0:
            sys.exit("effect pitch must be in [0.5,2.0]: %r" % pitch)
        events.setdefault(t,[]).append((sound, "%.6f"%pitch, vol, category, "effect"))

    if not events: sys.exit("no notes or sound effects!")
    ticks = sorted(events); maxt = ticks[-1]
    N = 1
    while N <= maxt: N *= 2
    root = "0_%d" % (N-1)
    ntset = set(ticks); tree = {}
    def build(x, y):
        rng = [t for t in ntset if x <= t <= y]
        if not rng: return None
        name = "%d_%d" % (x, y)
        # A leaf must be 1 wide: adjacent ticks must never be merged into one leaf.
        if y == x:
            t = rng[0]; guard = "-1" if t == 0 else str(t-1)
            tree[name] = ("execute if score music_progress nbs_s matches %d..%d "
                          "if score music_progress nbs_t matches ..%s run function %s:%s/notes/%d"
                          % (80*x, 80*y+160, guard, ns, path, t))
            return name
        mid = (x+y)//2; lines = []
        L = build(x, mid)
        if L: lines.append("execute if score music_progress nbs_s matches %d..%d run function %s:%s/tree/%s"
                           % (80*x, 80*(mid+3), ns, path, L))
        R = build(mid+1, y)
        if R: lines.append("execute if score music_progress nbs_s matches %d..%d run function %s:%s/tree/%s"
                           % (80*(mid+1), 80*(y+4), ns, path, R))
        tree[name] = "\r\n".join(lines); return name
    build(0, N-1)

    os.makedirs(os.path.join(a.out,"notes"), exist_ok=True)
    os.makedirs(os.path.join(a.out,"tree"), exist_ok=True)
    for t in ticks:
        lines = ["execute as @a[tag=!%s] at @s run playsound minecraft:%s %s @s ^0 ^ ^ %g %s 1"
                 % (tag, s, category, v, p) for (s,p,v,category,kind) in events[t]]
        if t == maxt and m.get("auto_stop", True):
            lines.append("function %s:%s/stop" % (ns, path))
        else:
            lines.append("scoreboard players set music_progress nbs_t %d" % t)
        open(os.path.join(a.out,"notes","%d.mcfunction"%t),"w",encoding="utf-8",newline="").write("\r\n".join(lines)+"\r\n")
    for name, c in tree.items():
        open(os.path.join(a.out,"tree",name+".mcfunction"),"w",encoding="utf-8",newline="").write(c+"\r\n")
    def w(fn, txt): open(os.path.join(a.out,fn),"w",encoding="utf-8",newline="").write(txt.replace("\n","\r\n"))
    w("play.mcfunction", "scoreboard players set music_progress music_type %d\nscoreboard players set music_progress nbs_s 0\nscoreboard players set music_progress nbs_t -1\n" % sid)
    w("stop.mcfunction", "scoreboard players set music_progress nbs_s 0\nscoreboard players reset music_progress nbs_t\n" + (("function %s\n"%nxt) if nxt else ""))
    w("tick.mcfunction", "execute if score music_progress music_type matches %d run scoreboard players operation music_progress nbs_s += #speed nbs_s\nexecute if score music_progress music_type matches %d run function %s:%s/tree/%s\n" % (sid, sid, ns, path, root))
    if style == "standalone":
        w("_standalone_init.mcfunction", "scoreboard objectives add music_type dummy\nscoreboard objectives add nbs_s dummy\nscoreboard objectives add nbs_t dummy\nscoreboard players set #speed nbs_s %d\n" % speed)
        w("_standalone_tick.mcfunction", "function %s:%s/tick\n" % (ns, path))
    for x in warns: print("WARN:", x, file=sys.stderr)
    note_count = sum(1 for evs in events.values() for e in evs if e[4] == "note")
    effect_count = sum(1 for evs in events.values() for e in evs if e[4] == "effect")
    print("OK: %d event ticks / %d note events / %d vanilla effects / %d tree nodes / root %s → %s"
          % (len(ticks), note_count, effect_count, len(tree), root, a.out))

if __name__ == "__main__": main()
