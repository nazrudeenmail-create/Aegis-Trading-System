# 06 — Alembic Migration Standards

```text
Document Status : Draft
Phase           : 2C
Version         : 1.0
Last Updated    : 2026-07-10
```

---

## Purpose

This document defines the migration standards for the Aegis Trading System. Every database schema change goes through Alembic, and every migration must conform to these rules.

When a migration is written, this document is the single source of truth. If a convention changes, this document changes first — then all future migrations follow the new standard.

---

## 1. Configuration

### 1.1 Database URL

The database URL is **never** hardcoded in `alembic.ini`. It is always read from the application config system:

```python
# alembic/env.py
from app.core.config import get_settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

This ensures the same environment variable (`DATABASE_URL`) that runs the application also runs the migrations. No drift between app config and migration config.

### 1.2 Target Metadata

`env.py` targets `Base.metadata` from `app.database.base`. All models must be imported before Alembic runs so their tables are registered:

```python
# alembic/env.py
from app.database.base import Base
import app.database.models  # noqa: F401 — registers all 15 models

target_metadata = Base.metadata
```

### 1.3 Run Location

All Alembic commands are run from the `backend/` directory:

```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "description"
```

---

## 2. Migration Naming

### 2.1 Filename Convention

```
NNN_short_description.py
```

| Element | Format | Example |
|---|---|---|
| Number | 3-digit, zero-padded, sequential | `001`, `002`, `003` |
| Separator | Underscore | `_` |
| Description | `snake_case`, short, descriptive | `initial_schema`, `add_user_table`, `add_email_to_accounts` |

**Examples:**
- `001_initial_schema.py`
- `002_add_volume_profile_table.py`
- `003_add_email_to_accounts.py`

### 2.2 Revision Message

The `revision` message (used in `alembic revision -m`) matches the filename description:

```bash
alembic revision --autogenerate -m "add_email_to_accounts"
```

### 2.3 Down Revision Chain

Each migration references its parent:

```python
# 001_initial_schema.py
down_revision = None  # First migration

# 002_add_volume_profile_table.py
down_revision = "001_initial_schema"

# 003_add_email_to_accounts.py
down_revision = "002_add_volume_profile_table"
```

The chain is strictly linear. No branching unless multiple developers work on independent schema changes simultaneously (unlikely in Phase 2).

---

## 3. Revision Workflow

### 3.1 When to Autogenerate

Use `--autogenerate` for **simple, structural changes** detected by model diffing:

```bash
alembic revision --autogenerate -m "add_new_table"
```

Autogenerate is appropriate for:
- Adding a new table with columns, PK, and basic indexes
- Adding a column to an existing table
- Adding a simple index

### 3.2 When to Hand-Write

Write migrations by hand when autogenerate cannot capture the intent:

- **ENUM creation** — autogenerate with `create_type=True` may create ENUMs out of order. Hand-write to control creation order.
- **Data migrations** — migrating existing data between columns/tables
- **Complex constraints** — partial indexes, conditional constraints
- **Index changes** — renaming or replacing an index
- **Custom SQL** — anything requiring raw SQL (e.g., `CREATE EXTENSION`)

### 3.3 Review Checklist Before Committing

Every migration must pass this review before being committed:

- [ ] `upgrade()` and `downgrade()` both exist and are tested
- [ ] ENUMs are created before tables that reference them
- [ ] FK-dependent tables are created after their parent tables
- [ ] All `op.f()` calls use the correct table/column names (matching the design doc)
- [ ] Index names follow the `ix_<table>_<column>` convention
- [ ] No `CASCADE` deletes (always `RESTRICT`)
- [ ] Migration has been round-trip tested (upgrade → downgrade → upgrade)

---

## 4. Upgrade/Downgrade Policy

### 4.1 Every Upgrade Must Have a Downgrade

Every `upgrade()` function must have a matching `downgrade()` that reverses it completely. No "irreversible" migrations.

```python
def upgrade() -> None:
    op.create_table("new_table", ...)
    op.create_enum("new_enum", ["VALUE_A", "VALUE_B"])

def downgrade() -> None:
    op.drop_table("new_table")
    op.drop_enum("new_enum")
```

### 4.2 Downgrade Order

The `downgrade()` function reverses `upgrade()` in **exact reverse order**:

1. Drop FK-dependent tables (reverse dependency order)
2. Drop standalone tables (reverse creation order)
3. Drop ENUM types (reverse creation order)
4. Drop indexes (if created separately)
5. Drop constraints (if created separately)

### 4.3 ENUM Downgrade

When dropping an ENUM type, ensure no table still references it:

```python
def downgrade() -> None:
    op.drop_table("child_table")      # Drop FK tables first
    op.drop_table("parent_table")      # Drop parent tables
    op.execute("DROP TYPE my_enum")    # Drop ENUM last
```

Use `op.execute("DROP TYPE ...")` rather than `op.drop_enum()` when you need explicit control.

---

## 5. ENUM Migration Policy

### 5.1 Creation Order

ENUM types must be created **before** any table that references them. The initial migration creates all 18 ENUMs first, then all 15 tables.

```python
def upgrade() -> None:
    # Step 1: All ENUMs
    op.execute("CREATE TYPE account_type AS ENUM ('PAPER', 'DEMO', 'LIVE')")
    op.execute("CREATE TYPE asset_class AS ENUM ('INDEX', 'FOREX', 'COMMODITY', 'CRYPTO', 'STOCK')")
    # ... all 18 ENUMs ...

    # Step 2: Standalone tables
    op.create_table("instruments", ...)

    # Step 3: FK-dependent tables
    op.create_table("candles", ...)
```

### 5.2 Adding ENUM Values

New enum values can be **appended** in future migrations:

```python
def upgrade() -> None:
    op.execute("ALTER TYPE signal_status ADD VALUE 'EXPIRED'")
```

**Do NOT** rename or remove existing ENUM values in production. That would break existing data.

### 5.3 Model vs. Migration

Models use `create_type=True` so they work in test environments that create tables from scratch. But migrations use explicit `CREATE TYPE` / `ALTER TYPE` SQL for precise ordering control. This is a deliberate dual approach — the model tells SQLAlchemy the type exists, and the migration creates it explicitly.

### 5.4 Complete ENUM Creation List (Initial Migration)

| # | ENUM Type Name | Values |
|---|---|---|
| 1 | `account_type` | `PAPER`, `DEMO`, `LIVE` |
| 2 | `asset_class` | `INDEX`, `FOREX`, `COMMODITY`, `CRYPTO`, `STOCK` |
| 3 | `timeframe` | `1M`, `5M`, `15M`, `1H`, `4H` |
| 4 | `indicator_type` | `ATR`, `EMA`, `MACD`, `RSI`, `CISD`, `MOMENTUM` |
| 5 | `market_bias` | `BULLISH`, `BEARISH`, `NEUTRAL` |
| 6 | `trend_health` | `HEALTHY`, `WEAK`, `BROKEN` |
| 7 | `direction` | `LONG`, `SHORT` |
| 8 | `signal_type` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` |
| 9 | `signal_status` | `PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`, `EXPIRED`, `CANCELLED` |
| 10 | `risk_check_type` | `POSITION_SIZE`, `STOP_LOSS_DISTANCE`, `EXPOSURE_LIMIT`, `MAX_DRAWDOWN`, `MAX_POSITIONS`, `DAILY_LOSS_LIMIT` |
| 11 | `order_type` | `MARKET`, `LIMIT`, `STOP` |
| 12 | `order_status` | `PENDING`, `FILLED`, `PARTIALLY_FILLED`, `CANCELLED`, `REJECTED` |
| 13 | `position_status` | `OPEN`, `CLOSED`, `PARTIALLY_CLOSED` |
| 14 | `trade_type` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY` |
| 15 | `setting_value_type` | `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `JSON` |
| 16 | `log_level` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| 17 | `decision_type` | `ENTRY`, `EXIT`, `PARTIAL_EXIT`, `RE_ENTRY`, `REJECT`, `CANCEL` |
| 18 | `decision_outcome` | `PENDING`, `SUCCESS`, `FAILURE`, `EXPIRED` |

---

## 6. Table Creation Order (Initial Migration)

Tables must be created in dependency order. A table must exist before any FK references it.

| Step | Table | FKs Reference |
|---|---|---|
| 1 | `instruments` | None (root table) |
| 2 | `accounts` | None |
| 3 | `market_sessions` | None |
| 4 | `market_holidays` | None |
| 5 | `settings` | None |
| 6 | `system_logs` | None |
| 7 | `candles` | `instruments` |
| 8 | `indicator_values` | `instruments`, `candles` |
| 9 | `market_analysis` | `instruments` |
| 10 | `signals` | `instruments` |
| 11 | `risk_checks` | `signals` |
| 12 | `orders` | `signals`, `instruments`, `accounts` |
| 13 | `positions` | `instruments`, `accounts` |
| 14 | `trades` | `positions`, `orders`, `instruments`, `accounts` |
| 15 | `decision_logs` | `signals`, `instruments` |

---

## 7. Production Migration Rules

### 7.1 Never Autogenerate Into Production

Always review autogenerated migrations before running them. Run `alembic upgrade head --sql` to preview the SQL:

```bash
alembic upgrade head --sql > migration_preview.sql
```

Review the SQL file, then run the actual migration.

### 7.2 Test on Staging First

Before applying a migration to production:
1. Apply it to a staging/development database
2. Run the test suite against the migrated database
3. Verify round-trip (upgrade → downgrade → upgrade)
4. Only then apply to production

### 7.3 Backup Before Migration

Production migrations should be preceded by a database backup (Phase 12 will automate this).

### 7.4 No Destructive Changes in Production

- Never `DROP COLUMN` without first deprecating it (one release gap)
- Never `DROP TABLE` without confirming it has zero references
- Never rename ENUM values (add new ones, deprecate old ones)
- Use `ALTER TYPE ... ADD VALUE` to extend (not modify) ENUMs

---

## 8. Testing Requirements

### 8.1 Round-Trip Test

Every migration must pass:

```bash
alembic upgrade head     # Apply all migrations
alembic downgrade base   # Reverse all migrations
alembic upgrade head     # Re-apply — must succeed
```

### 8.2 Schema Verification

After `alembic upgrade head`, verify:

```sql
-- All 15 tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- All 18 ENUM types exist
SELECT typname FROM pg_type
WHERE typtype = 'e';

-- All indexes exist
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public';

-- All constraints exist
SELECT conname FROM pg_constraint
WHERE connamespace = 'public'::regnamespace;
```

### 8.3 CI/CD Integration (Future Phase)

In Phase 12, the migration will be automatically tested in CI:
1. Spin up a fresh PostgreSQL container
2. Run `alembic upgrade head`
3. Run schema verification queries
4. Run `alembic downgrade base`
5. Run `alembic upgrade head` (round-trip)

---

## 9. Migration File Template

```python
"""
Migration: {description}

Revision ID: {revision_id}
Revises: {down_revision}
Create Date: {create_date}

Description:
    {detailed description of what this migration does}
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "{revision_id}"
down_revision: Union[str, Sequence[str], None] = "{down_revision}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply the migration."""
    # Step 1: Create ENUM types (if any)
    # Step 2: Create tables (dependency order)
    # Step 3: Create indexes (if not inline)
    pass


def downgrade() -> None:
    """Reverse the migration."""
    # Step 1: Drop indexes (if separate)
    # Step 2: Drop tables (reverse dependency order)
    # Step 3: Drop ENUM types (if any)
    pass
```

---

## 10. What NOT to Include in Migrations

- ❌ No hardcoded database URLs
- ❌ No application logic — migrations are pure DDL
- ❌ No data seeding (use fixtures or seed scripts, not migrations)
- ❌ No `CREATE DATABASE` or `DROP DATABASE` — migrations assume the database exists
- ❌ No `CASCADE` deletes
- ❌ No irreversible downgrades (every `upgrade` must have a `downgrade`)
- ❌ No `print()` statements — use Python's `logging` module if debug output is needed

---

END OF DOCUMENT