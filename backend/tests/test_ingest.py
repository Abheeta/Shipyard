"""Parsing tests — no network, no model, no index required."""
import json
from pathlib import Path

from shipyard.ingest import build_corpus, parse_export, embed_text

SAMPLE = [
    {
        "timestamp": 1787643794,
        "media": [],
        "label_values": [
            {"label": "URL", "value": "https://www.instagram.com/reel/AAA/"},
            {"label": "Caption", "value": "Tunisian crochet uses less yarn. One myth busted."},
            {"label": "Title", "value": ""},
            {"title": "Hashtags", "dict": [{"dict": [{"label": "Name", "value": "crochet"}]}]},
            {"title": "Owner", "dict": [{"dict": [
                {"label": "Name", "value": "Jen"},
                {"label": "Username", "value": "violet.loops"},
            ]}]},
            {"title": "Brand partner", "dict": []},
        ],
        "fbid": "111",
    },
    {
        "timestamp": 1787643380,
        "media": [],
        "label_values": [
            {"label": "URL", "value": "https://www.instagram.com/p/BBB/"},
            {"title": "Hashtags", "dict": []},
            {"title": "Owner", "dict": [{"dict": [{"label": "Username", "value": "sunohstudio"}]}]},
            {"title": "Brand partner", "dict": [{"dict": [{"label": "Name", "value": "x"}]}]},
        ],
        "fbid": "222",
    },
]


def _write(tmp_path: Path, name: str, data) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_parse_export(tmp_path):
    rows = parse_export(_write(tmp_path, "s.json", SAMPLE), "saved")
    assert len(rows) == 2
    a, b = rows
    assert a["id"] == "saved:111"
    assert a["creator"] == "violet.loops"
    assert a["creator_name"] == "Jen"
    assert a["hashtags"] == ["crochet"]
    assert a["is_ad"] is False
    assert b["caption"] == ""              # missing caption tolerated
    assert b["is_ad"] is True             # brand partner => sponsored


def test_build_corpus_dedup(tmp_path):
    dup = SAMPLE + [SAMPLE[0]]
    df = build_corpus(_write(tmp_path, "s.json", dup), _write(tmp_path, "l.json", []))
    assert (df["source"] == "saved").sum() == 2   # de-duped on url
    assert set(df.columns) >= {"summary", "tags", "cluster_id", "is_actionable"}


def test_embed_text_includes_signal():
    row = {"caption": "how to block a shawl", "title": "", "hashtags": ["crochet"],
           "creator_name": "Jen"}
    t = embed_text(row)
    assert "shawl" in t and "crochet" in t and "Jen" in t
