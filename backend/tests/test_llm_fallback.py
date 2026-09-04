"""The no-key heuristic path must always produce usable output."""
from shipyard import llm


def test_heuristic_enrich_shape():
    items = [
        {"caption": "How to make a quick weeknight dal. Soak, boil, temper.",
         "hashtags": ["recipe", "indianfood"], "creator_name": "cook"},
        {"caption": "", "hashtags": [], "creator_name": "nobody", "creator": "nobody"},
    ]
    out = llm.enrich_items(items)
    assert len(out) == 2
    assert out[0]["summary"]
    assert out[0]["tags"][:2] == ["recipe", "indianfood"]
    assert out[0]["is_actionable"] is True
    assert out[1]["summary"]                    # never empty


def test_heuristic_actionable_split():
    assert llm._heuristic_actionable("Step by step tutorial on gauge swatching") is True
    assert llm._heuristic_actionable("Breaking: election results commentary") is False


def test_answer_without_llm_lists_matches():
    items = [{"creator": "cook", "summary": "quick dal recipe", "caption": "..."}]
    answer, used = llm.answer_question("what have I saved about lentils", items)
    assert used is False
    assert "cook" in answer


def test_cluster_name_fallback():
    name = llm.name_cluster(0, ["crochet gauge tension swatch", "blocking a crochet shawl"])
    assert name and name != ""
