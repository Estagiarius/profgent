## 2025-02-21 - [ORM Overhead vs Tuples]
Learning: Loading 2000+ SQLAlchemy ORM objects just to convert them to a dictionary is ~2x slower than selecting specific columns as tuples.
Action: When fetching data solely for read-only aggregation or mapping (e.g., `grades_map`), always use `db.query(Model.col1, Model.col2)` instead of `db.query(Model)`.

## 2025-02-21 - [Lazy Loading UI Views]
Learning: Initializing all CustomTkinter views (and their heavy widget trees) at startup causes significant lag.
Action: Implemented Lazy Loading (Factory Pattern) in `MainApp`. Views are now instantiated only when requested via `show_view`. This reduced startup complexity from O(N) to O(1) (only Dashboard loads initially).

## 2025-02-21 - [Async UI Loading]
Learning: Running heavy data aggregation (O(N)) and Matplotlib generation on the main thread freezes the UI.
Action: Refactored `DashboardView` to use `run_async_task` with `asyncio.to_thread`. This offloads blocking calls to a worker thread while keeping the UI responsive with loading indicators.
