#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║           A B Y S S   P R O T O C O L           ║
║         Terminal Roguelike Dungeon Crawler        ║
║         Python 3 · stdlib only · single file     ║
╚══════════════════════════════════════════════════╝
"""

import random, os

# ══════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════
GRID    = 5
MAX_INV = 3
EMPTY, ENEMY, ITEM, BOSS = "empty", "enemy", "item", "boss"

# ══════════════════════════════════════════════════════════════
# FLAVOR TEXT
# ══════════════════════════════════════════════════════════════
ROOM_DESC = {
    EMPTY: [
        "Dust and silence. The torch flickers, then holds.",
        "Ancient bones litter the floor. Nothing moves — yet.",
        "Crude carvings cover every wall. You don't translate them.",
        "A cold wind cuts through from nowhere.",
        "Water drips somewhere in the dark. You are not alone.",
    ],
    ENEMY: [
        "Something shifts in the darkness ahead.",
        "Eyes. Many eyes. Watching from the corner.",
        "A low growl echoes off the stone.",
        "The stench of rot hits you before you see it.",
    ],
    ITEM: [
        "A faint glow catches your eye in the rubble.",
        "Tucked in a crevice — something left behind.",
        "Half-buried in dust, something useful glints.",
        "Someone camped here once. They left in a hurry.",
    ],
    BOSS: [
        "\n  The air turns to ice. The torches die."
        "\n\n  A voice that isn't a voice fills your skull:"
        '\n\n  "YOU SHOULD NOT HAVE COME HERE."\n',
    ],
}

HIT_MSGS   = ["You strike true!", "A clean blow lands!",
               "Your blade cuts deep!", "Direct hit!"]
ENEMY_ATKS = ["{} lunges!", "{} slashes viciously!",
               "{} tears into you!", "{} lands a heavy blow!"]
FLEE_OK    = ["You slip into the shadows — gone.",
               "You bolt through a side passage. Enemy lost."]
FLEE_FAIL  = ["No escape! {} cuts you off!", "The {} won't let you run!"]

# ══════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════
def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def pause(): input("\n  [Press ENTER to continue]")
def div():   print("  " + "─" * 46)


# ══════════════════════════════════════════════════════════════
# ITEM
# ══════════════════════════════════════════════════════════════
class Item:
    def __init__(self, name, effect, value):
        self.name   = name
        self.effect = effect   # "heal" | "attack_boost" | "shield"
        self.value  = value

    def __str__(self):
        labels = {
            "heal":         f"Restores {self.value} HP",
            "attack_boost": f"Next hit +{self.value} ATK",
            "shield":       f"Absorbs up to {self.value} damage",
        }
        return f"{self.name}  [{labels.get(self.effect, '?')}]"


ITEM_POOL = [
    Item("Health Potion", "heal",         30),
    Item("Power Shard",   "attack_boost", 10),
    Item("Shield Core",   "shield",       15),
]

def make_item(): return random.choice(ITEM_POOL)


# ══════════════════════════════════════════════════════════════
# ENEMY
# ══════════════════════════════════════════════════════════════
class Enemy:
    def __init__(self, name, hp, atk):
        self.name    = name
        self.hp      = hp
        self.max_hp  = hp
        self.atk     = atk

    def alive(self):     return self.hp > 0
    def take_hit(self, d): self.hp = max(0, self.hp - d)


ENEMY_POOL = [("Goblin", 25, 6), ("Skeleton", 35, 9), ("Wraith", 20, 14)]

def make_enemy(): return Enemy(*random.choice(ENEMY_POOL))
def make_boss():  return Enemy("THE ABYSS GUARDIAN", 120, 20)


# ══════════════════════════════════════════════════════════════
# PLAYER
# ══════════════════════════════════════════════════════════════
class Player:
    def __init__(self):
        self.hp        = self.max_hp = 100
        self.atk       = 18
        self.inv       = []          # max MAX_INV items
        self.atk_boost = 0           # consumed on next attack
        self.shield    = 0           # consumed on next hit taken
        self.kills     = 0

    def alive(self): return self.hp > 0

    def take_hit(self, dmg):
        if self.shield > 0:
            blocked     = min(self.shield, dmg)
            dmg        -= blocked
            self.shield = 0
            print(f"    [Shield Core absorbs {blocked} damage!]")
        self.hp = max(0, self.hp - dmg)

    def heal(self, n): self.hp = min(self.max_hp, self.hp + n)

    def add_item(self, item):
        if len(self.inv) < MAX_INV:
            self.inv.append(item); return True
        return False

    def use_item(self, i):
        if not (0 <= i < len(self.inv)):
            print("    Invalid slot."); return False
        it = self.inv.pop(i)
        if   it.effect == "heal":
            self.heal(it.value)
            print(f"    Drank {it.name}. +{it.value} HP  (now {self.hp})")
        elif it.effect == "attack_boost":
            self.atk_boost += it.value
            print(f"    {it.name} activated. Next hit +{it.value} ATK.")
        elif it.effect == "shield":
            self.shield = it.value
            print(f"    Shield Core armed. Blocks up to {it.value} damage.")
        return True

    def stats_line(self):
        b = f" +{self.atk_boost}⚡" if self.atk_boost else ""
        s = f"  Shield:{self.shield}" if self.shield    else ""
        return f"HP {self.hp:>3}/{self.max_hp}  ATK {self.atk}{b}  Kills {self.kills}{s}"

    def inv_str(self):
        if not self.inv: return "    [empty]"
        return "\n".join(f"    {i+1}. {it}" for i, it in enumerate(self.inv))


# ══════════════════════════════════════════════════════════════
# ROOM
# ══════════════════════════════════════════════════════════════
class Room:
    def __init__(self, kind=EMPTY):
        self.kind    = kind
        self.visited = False
        self.enemy   = (make_enemy() if kind == ENEMY else
                        make_boss()  if kind == BOSS  else None)
        self.item    = make_item() if kind == ITEM else None


# ══════════════════════════════════════════════════════════════
# DUNGEON  (5×5 procedural grid)
# ══════════════════════════════════════════════════════════════
class Dungeon:
    def __init__(self):
        self.grid = [[Room() for _ in range(GRID)] for _ in range(GRID)]
        self.pos  = [0, 0]
        self._build()

    def _build(self):
        cells = [(r, c) for r in range(GRID) for c in range(GRID)]
        random.shuffle(cells)

        # Player spawn
        pr, pc = cells.pop()
        self.pos = [pr, pc]
        self.grid[pr][pc].visited = True

        # Boss — place at Manhattan distance > 2 if possible
        placed = False
        for r, c in cells[:]:
            if abs(r - pr) + abs(c - pc) > 2:
                self.grid[r][c] = Room(BOSS)
                cells.remove((r, c))
                placed = True; break
        if not placed:
            r, c = cells.pop(); self.grid[r][c] = Room(BOSS)

        # 7 enemy rooms, 4 item rooms
        for kind, n in [(ENEMY, 7), (ITEM, 4)]:
            for _ in range(n):
                if cells: r, c = cells.pop(); self.grid[r][c] = Room(kind)

    def current(self):
        r, c = self.pos; return self.grid[r][c]

    def move(self, dr, dc):
        nr, nc = self.pos[0] + dr, self.pos[1] + dc
        if 0 <= nr < GRID and 0 <= nc < GRID:
            self.pos = [nr, nc]; return True
        return False


# ══════════════════════════════════════════════════════════════
# MAP RENDERER
# ══════════════════════════════════════════════════════════════
def draw_map(d):
    pr, pc = d.pos
    w = GRID * 4 + 1
    print("\n  ┌" + "───┬" * (GRID - 1) + "───┐")
    for r in range(GRID):
        row = "  │"
        for c in range(GRID):
            rm = d.grid[r][c]
            if [r, c] == d.pos:                                        sym = "P"
            elif not rm.visited:                                        sym = "?"
            elif rm.kind == BOSS  and rm.enemy and rm.enemy.alive():   sym = "B"
            elif rm.kind == ENEMY and rm.enemy and rm.enemy.alive():   sym = "E"
            elif rm.kind == ITEM  and rm.item:                         sym = "I"
            else:                                                       sym = "·"
            row += f" {sym} │"
        print(row)
        if r < GRID - 1:
            print("  ├" + "───┼" * (GRID - 1) + "───┤")
    print("  └" + "───┴" * (GRID - 1) + "───┘")
    print("  P=You  E=Enemy  B=Boss  I=Item  ?=Dark  ·=Cleared\n")


# ══════════════════════════════════════════════════════════════
# COMBAT SYSTEM  (turn-based)
# ══════════════════════════════════════════════════════════════
def combat(player, enemy, boss=False):
    print(f"\n  {'═' * 44}")
    print(f"  ⚔  ENCOUNTER: {enemy.name}")
    print(f"  {'═' * 44}")
    first_turn = True

    while player.alive() and enemy.alive():
        if not first_turn: pause()
        first_turn = False

        print(f"\n  {enemy.name}  HP {enemy.hp}/{enemy.max_hp}")
        print(f"  Your HP: {player.hp}/{player.max_hp}"
              + (f"  [boost +{player.atk_boost}]" if player.atk_boost else ""))
        flee_opt = "" if boss else "   3. Flee"
        print(f"\n  1. Attack   2. Use Item{flee_opt}")
        cmd = input("  > ").strip()

        if cmd == "1":
            # --- Player attacks ---
            dmg = player.atk
            if player.atk_boost:
                print("  [Power Shard triggers!]")
                dmg += player.atk_boost
                player.atk_boost = 0
            print(f"  {random.choice(HIT_MSGS)} (-{dmg} HP)")
            enemy.take_hit(dmg)
            if not enemy.alive():
                break
            # --- Enemy counter ---
            e_dmg = max(1, enemy.atk + random.randint(-2, 3))
            print(f"  {random.choice(ENEMY_ATKS).format(enemy.name)} (-{e_dmg} HP)")
            player.take_hit(e_dmg)

        elif cmd == "2":
            if not player.inv:
                print("  Inventory empty."); first_turn = True; continue
            print("\n  Inventory:\n" + player.inv_str())
            sel = input("  Use #: ").strip()
            used = player.use_item(int(sel) - 1) if sel.isdigit() else False
            if not used: first_turn = True; continue
            # Enemy still swings while you rummage
            if enemy.alive():
                e_dmg = max(1, enemy.atk + random.randint(-2, 3))
                print(f"  {random.choice(ENEMY_ATKS).format(enemy.name)} (-{e_dmg} HP)")
                player.take_hit(e_dmg)

        elif cmd == "3" and not boss:
            if random.random() < 0.5:
                print(f"  {random.choice(FLEE_OK)}")
                return "fled"
            else:
                e_dmg = max(1, enemy.atk + random.randint(0, 5))
                msg   = random.choice(FLEE_FAIL).format(enemy.name)
                print(f"  {msg} (-{e_dmg} HP)")
                player.take_hit(e_dmg)
        else:
            print("  [Invalid input]"); first_turn = True

    if player.alive():
        print(f"\n  ✓  {enemy.name} has been defeated.")
        player.kills += 1
        return "won"
    return "lost"


# ══════════════════════════════════════════════════════════════
# ROOM RESOLVER  — handles all room events
# ══════════════════════════════════════════════════════════════
def resolve(player, dungeon):
    """
    Returns: "ok" | "silent" | "dead" | "victory"
    "silent" = already visited, nothing to show.
    """
    rm = dungeon.current()

    # Already-cleared non-boss rooms: skip silently
    if rm.visited and rm.kind != BOSS:
        return "silent"
    rm.visited = True

    # Print atmospheric description
    print(f"\n  {random.choice(ROOM_DESC.get(rm.kind, ROOM_DESC[EMPTY]))}")

    if rm.kind == EMPTY:
        pass  # Nothing to do

    elif rm.kind == ENEMY:
        if rm.enemy and rm.enemy.alive():
            result = combat(player, rm.enemy)
            if result == "lost": return "dead"
            # 40 % drop chance after a kill
            if result == "won" and random.random() < 0.4:
                drop = make_item()
                if player.add_item(drop):
                    print(f"\n  The creature dropped: {drop.name}!")
                else:
                    print(f"\n  Drop on the floor ({drop.name}) — inventory full.")

    elif rm.kind == ITEM:
        if rm.item:
            print(f"\n  You found: {rm.item}")
            if player.add_item(rm.item):
                print("  Added to inventory.")
                rm.item = None
            else:
                print("\n  Inventory full! Drop an item to make room?")
                print(player.inv_str())
                s = input("  Drop # (or ENTER to leave it): ").strip()
                if s.isdigit():
                    idx = int(s) - 1
                    if 0 <= idx < len(player.inv):
                        old = player.inv.pop(idx)
                        player.inv.append(rm.item)
                        print(f"  Dropped {old.name}, picked up {rm.item.name}.")
                        rm.item = None
                else:
                    print("  Left it behind.")

    elif rm.kind == BOSS:
        if rm.enemy and rm.enemy.alive():
            result = combat(player, rm.enemy, boss=True)
            if result == "lost":   return "dead"
            if result == "won":    return "victory"
        else:
            return "victory"   # Boss already dead (re-entry edge case)

    return "ok"


# ══════════════════════════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════════════════════════
def screen_title():
    clear()
    print("""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║       A B Y S S   P R O T O C O L           ║
  ║         Terminal Roguelike  v1.0             ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝

  You descend into a dungeon with no name.
  Something ancient waits at its core.
  You will probably die.

  WASD = Move   I = Inventory   Q = Quit
""")
    input("  [Press ENTER to descend]\n")


def screen_dead(p):
    clear()
    print(f"""
  ╔══════════════════════════════════════════════╗
  ║             Y O U   D I E D                 ║
  ╚══════════════════════════════════════════════╝

  The Abyss has claimed another soul.

  Kills: {p.kills}
  Final HP: 0 / {p.max_hp}

  The darkness was always going to win.
""")


def screen_victory(p):
    clear()
    print(f"""
  ╔══════════════════════════════════════════════╗
  ║    T H E   A B Y S S   I S   S I L E N T   ║
  ╚══════════════════════════════════════════════╝

  The Guardian collapses. Its ancient form
  dissolves into cold light.

  For the first time in a thousand years —
  silence.

  ★  V I C T O R Y  ★

  HP Remaining : {p.hp} / {p.max_hp}
  Enemies Killed: {p.kills}

  The Protocol is complete.
""")


# ══════════════════════════════════════════════════════════════
# GAME LOOP
# ══════════════════════════════════════════════════════════════
DIRS = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}


def game_loop():
    player  = Player()
    dungeon = Dungeon()
    moved   = True    # resolve the starting room immediately

    while True:
        clear()
        draw_map(dungeon)
        div()
        print(f"  {player.stats_line()}")
        div()

        # ── Resolve room on entry ─────────────────────────────
        if moved:
            status = resolve(player, dungeon)
            moved  = False
            if status == "dead":
                pause(); screen_dead(player); break
            if status == "victory":
                pause(); screen_victory(player); break
            if status != "silent":
                pause()

        # ── Player input ──────────────────────────────────────
        print("\n  Move: W A S D   |   I = Inventory   Q = Quit")
        cmd = input("  > ").strip().lower()

        if cmd == 'q':
            print("\n  You retreat from the Abyss. It will remember.")
            break

        elif cmd == 'i':
            clear()
            slots = "■" * len(player.inv) + "□" * (MAX_INV - len(player.inv))
            print(f"\n  ── INVENTORY  [{slots}] ──\n")
            print(player.inv_str())
            print(f"\n  {player.stats_line()}")
            sel = input("\n  Use item # (ENTER = back): ").strip()
            if sel.isdigit():
                player.use_item(int(sel) - 1)
                pause()

        elif cmd in DIRS:
            if dungeon.move(*DIRS[cmd]):
                moved = True
            else:
                print("  A wall blocks your path.")
                pause()

        else:
            print("  Unknown command.")
            pause()


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════
def main():
    screen_title()
    game_loop()
    print("\n  Thanks for playing ABYSS PROTOCOL.\n")


if __name__ == "__main__":
    main()
