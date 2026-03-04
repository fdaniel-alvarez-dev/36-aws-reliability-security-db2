from __future__ import annotations

from pathlib import Path
import pandas as pd
import pandera as pa
from pandera.typing import Series


class EventsSchema(pa.DataFrameModel):
    event_id: Series[int] = pa.Field(ge=1)
    user_id: Series[int] = pa.Field(ge=1)
    event_type: Series[str] = pa.Field(isin=["signup", "login", "purchase"])
    event_ts: Series[str]


def main() -> None:
    raw_path = Path("data/raw/events.csv")
    out_dir = Path("data/processed/events_parquet")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path)
    df = EventsSchema.validate(df)

    out_path = out_dir / "events.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Wrote {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
