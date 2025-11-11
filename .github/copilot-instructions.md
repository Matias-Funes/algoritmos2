## Quick orientation for AI coding agents

This repo is a small Pygame-based rescue-simulator (entrypoint: `rescue_simulator.py` → `src/game_engine.py:main`). Focus on small, local edits: features live in `src/` and behaviours are driven by strategy classes in `config/strategies/`.

- Architecture highlights
  - `rescue_simulator.py` calls `src.game_engine.main()` — the single-run entry point used in dev and CI.
  - World state: `src/world.py` (grid-based map, resources: `world.resources`, mines: `world.mines`). Grid uses tile coordinates; many systems convert between cell <-> pixel via `World.cell_to_pixel` and `World.pixel_to_cell`.
  - Vehicles: `src/aircraft.py` defines `Vehicle` and subclasses (`Jeep`, `Moto`, `Camion`, `Auto`). Vehicles use pixel coordinates, have `allowed_cargo`, `trips_left`, `cargo`, `strategy`, and call `strategy.decide(self, world)` each tick.
  - Strategies: `config/strategies/*.py` implement `BaseStrategy.decide(vehicle, world)` and return actions as dicts: e.g. `{"type":"move","target":(x,y)}` or `{"type":"collect","target":resource}`. Use these files to change AI behavior.
  - Pathfinding: `src/pathfinding.py::a_star(start, goal, world)` expects grid coordinates (gx,gy) and uses `world.get_neighbors`.

- Important conventions & patterns (project-specific)
  - Strategies control high-level decisions; concrete movement/collections are handled by `Vehicle.execute_action` in `src/aircraft.py`.
  - Resource objects in `world.resources` have `.type`, `.value`, `.x`, `.y`. Strategies should prefer resources by reading `.value` and distance.
  - Mines have different types and radii defined in `src/constants.py` (`MINE_TYPES`, `MINES_COUNT`) and `BaseStrategy.evade_mines` is used widely — avoid bypassing it.
  - Visual/asset paths use `assets/images/...` (sprites loaded in `World.__init__`). Keep asset filenames stable when editing drawing code.

- Dev / run / test workflows (concrete)
  - Install: create a venv and install `requirements.txt` (Windows PowerShell):
    - python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt
  - Run simulator (interactive): python rescue_simulator.py
  - Tests: `tests/` exist but currently empty — no CI test suite configured. Use pytest if adding tests.

- Editing guidance for AI agents
  - If changing AI behavior, edit `config/strategies/*.py`. Keep `decide(vehicle, world)` return format unchanged (dict with `type` and `target`).
  - When changing world/grid logic, be mindful of pixel↔grid conversions and `pathfinding.a_star` inputs. Use `world.random_position()` for safe exploration points.
  - Avoid blocking calls in `game_engine.main()` (it is the real-time loop at 60 FPS). Keep updates fast and deterministic for tests.

- Integration points to review when changing behavior
  - `src/game_engine.py` — sets up vehicles and assigns strategy instances.
  - `src/aircraft.py` — movement, collision (mines), collection and scoring logic; changing here affects scoring and end conditions.
  - `src/world.py` — resource/mine placement and draw routines; also exposes `world.resources`, `world.mines` and helper methods used by strategies.

If any section is unclear or you'd like more examples (for instance: how to add a new vehicle type, or an example strategy change), tell me which area and I'll expand with a small, tested edit.
