## 2025-02-21 - [ORM Overhead vs Tuples]
Learning: Loading 2000+ SQLAlchemy ORM objects just to convert them to a dictionary is ~2x slower than selecting specific columns as tuples.
Action: When fetching data solely for read-only aggregation or mapping (e.g., `grades_map`), always use `db.query(Model.col1, Model.col2)` instead of `db.query(Model)`.
