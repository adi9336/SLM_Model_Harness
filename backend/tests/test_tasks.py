from automation.tasks import score

def test_score_match(tmp_path):
    a = tmp_path / "a.csv"; a.write_text("x,y\n1,2\n3,4\n")
    e = tmp_path / "e.csv"; e.write_text("x,y\n3,4\n1,2\n")
    assert score(str(a), str(e))["match"] is True

def test_score_mismatch(tmp_path):
    a = tmp_path / "a.csv"; a.write_text("x,y\n1,2\n")
    e = tmp_path / "e.csv"; e.write_text("x,z\n1,2\n")
    assert score(str(a), str(e))["match"] is False

def test_score_missing_file(tmp_path):
    e = tmp_path / "e.csv"; e.write_text("x,y\n1,2\n")
    r = score(str(tmp_path / "nope.csv"), str(e))
    assert r["match"] is False and r["missing"] is True
