from pathlib import Path
import pandas as pd
from pipelines.pipeline import EventsSchema


def test_schema_validation_passes():
    df = pd.read_csv(Path("data/raw/events.csv"))
    EventsSchema.validate(df)
