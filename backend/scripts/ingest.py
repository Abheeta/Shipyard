"""Parse the Instagram exports and print a profile. Does not build the index.

    python -m scripts.ingest
"""
from __future__ import annotations

from collections import Counter

from shipyard.config import settings
from shipyard.ingest import build_corpus


def main() -> None:
    print(f"saved: {settings.saved_file}")
    print(f"liked: {settings.liked_file}")
    df = build_corpus(settings.saved_file, settings.liked_file)

    print(f"\n{len(df)} items after de-dup")
    print(df["source"].value_counts().to_string())

    has_cap = (df["caption"].str.len() > 0).sum()
    print(f"\ncaption present: {has_cap}/{len(df)} ({has_cap/len(df):.0%})")
    print(f"flagged as ad:   {int(df['is_ad'].sum())}")

    yrs = Counter(df["year"].dropna().astype(int).tolist())
    print("\nby year:", dict(sorted(yrs.items())))

    top = df.groupby(["creator", "source"]).size().sort_values(ascending=False).head(10)
    print("\ntop creator/source pairs:")
    print(top.to_string())


if __name__ == "__main__":
    main()
