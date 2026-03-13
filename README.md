ABYSS PROTOCOL
Terminal Roguelike Dungeon Crawler · Python 3 · stdlib only · single file
---
Description
A fully procedural, turn-based dungeon crawler that runs entirely in your terminal.
Every run generates a new 5×5 dungeon with randomised enemy placements, item drops,
and a boss room. No external dependencies. No setup. Just descend.
---
Features
Procedural dungeon — 5×5 grid, randomised every run
Turn-based combat — Attack, use items, or attempt to flee
3 enemy types — Goblin, Skeleton, Wraith (distinct HP/ATK profiles)
Boss encounter — THE ABYSS GUARDIAN (no escape allowed)
Inventory system — 3-slot cap; Health Potion, Power Shard, Shield Core
Item drops — 40% chance enemies drop an item on death
ASCII map — Live dungeon map with fog-of-war on unexplored rooms
Atmospheric flavor text — Unique room descriptions, varied combat messages
Victory & death screens — With kill count and HP summary
---
Controls
Key	Action
`W`	Move up
`A`	Move left
`S`	Move down
`D`	Move right
`I`	Open inventory (use items outside combat)
`Q`	Quit
---
How to Run
```bash
python main.py
```
Requires Python 3.6+. No pip installs. No virtual env. Works on macOS, Linux, Windows, and Replit.
---
Items
Item	Effect
Health Potion	Restores 30 HP
Power Shard	Next attack deals +10 damage (consumed on hit)
Shield Core	Absorbs up to 15 damage from the next hit taken
Items can be used during combat (enemy still counter-attacks) or from the inventory screen between rooms.
---
Map Legend
```
P = You (current position)
E = Enemy room (alive)
B = Boss room
I = Item available
· = Cleared / visited
? = Unexplored (fog of war)
```
---
Example Gameplay
```
  ┌───┬───┬───┬───┬───┐
  │ · │ E │ ? │ ? │ ? │
  ├───┼───┼───┼───┼───┤
  │ · │ P │ ? │ ? │ ? │
  ├───┼───┼───┼───┼───┤
  │ ? │ ? │ ? │ B │ ? │
  ├───┼───┼───┼───┼───┤
  │ ? │ I │ ? │ ? │ ? │
  ├───┼───┼───┼───┼───┤
  │ ? │ ? │ ? │ ? │ ? │
  └───┴───┴───┴───┴───┘
  ──────────────────────────────────────────────
  HP  87/100  ATK 18  Kills 2
  ──────────────────────────────────────────────

  Move: W A S D   |   I = Inventory   Q = Quit
  > d

  Eyes. Many eyes. Watching from the corner.

  ════════════════════════════════════════════
  ⚔  ENCOUNTER: Wraith
  ════════════════════════════════════════════

  Wraith  HP 20/20
  Your HP: 87/100

  1. Attack   2. Use Item   3. Flee
  > 1
  Direct hit! (-18 HP)
  Wraith lunges! (-12 HP)
  ...
  ✓  Wraith has been defeated.
  The creature dropped: Power Shard!
```
---
Architecture
```
main.py
 ├── Item         — name, effect, value; __str__ display
 ├── Enemy        — name, hp, atk; alive()/take_hit()
 ├── Player       — hp, atk, inv[3], shield, atk_boost
 ├── Room         — kind, visited flag, enemy/item slots
 ├── Dungeon      — 5×5 grid, procedural _build(), move()
 ├── draw_map()   — ASCII fog-of-war renderer
 ├── combat()     — full turn-based loop, returns won/lost/fled
 ├── resolve()    — room event dispatcher
 ├── game_loop()  — main input/render loop
 └── screens      — title, death, victory
```
---
Possible Future Improvements
Multiple dungeon floors — stairs leading deeper, scaling difficulty
Ranged weapon slot — separate from inventory, limited ammo
Enemy variety — Lich, Demon, Mimic; status effects (poison, stun)
Character classes — Warrior (high HP), Rogue (flee always succeeds), Mage (spell charges)
Shop rooms — spend kill count as currency
Persistent leaderboard — store high scores in a local `.json`
Colour output — `curses` or ANSI escape codes for HP bars and dungeon tiles
Saving/loading — `pickle` game state between sessions
