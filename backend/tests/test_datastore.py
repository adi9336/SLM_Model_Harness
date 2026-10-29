from automation.datastore import DataStore

def test_load_csv(tmp_path):
    f = tmp_path / "s.csv"
    f.write_text("cust_id,amount,sale_date\nc1,100,2024-01-02\nc2,250,2024-02-15\n")
    ds = DataStore()
    r = ds.load_csv(f, "sales")
    assert r["rows"] == 2 and r["columns"] == ["cust_id", "amount", "sale_date"]

def test_preview(tmp_path):
    f = tmp_path / "s.csv"
    f.write_text("a,b\n1,2\n3,4\n")
    ds = DataStore(); ds.load_csv(f, "t")
    p = ds.preview("t", limit=1)
    assert p["columns"] == ["a", "b"] and p["rows"] == [["1", "2"]]

def test_join(tmp_path):
    ds = DataStore()
    l = tmp_path / "l.csv"; l.write_text("cust_id,amount\nc1,100\nc2,250\nc3,75\n")
    r = tmp_path / "r.csv"; r.write_text("customer_id,name\nc1,Acme\nc2,Beta\nc4,Gamma\n")
    ds.load_csv(l, "left"); ds.load_csv(r, "right")
    out = ds.join_tables("left", "right", "cust_id", "customer_id", "inner", "joined")
    assert out["rows"] == 2
    p = ds.preview("joined", 10)
    assert ("c1", "100", "c1", "Acme") in [tuple(x) for x in p["rows"]]

def test_aggregate(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"; f.write_text("cust_id,amount\nc1,100\nc1,50\nc2,250\n")
    ds.load_csv(f, "sales")
    ds.aggregate("sales", "cust_id", "amount", "sum", "agg")
    p = ds.preview("agg", 10)
    assert ("c1", 150) in [tuple(x) for x in p["rows"]]

def test_clean_dates(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"
    f.write_text("id,d\n1,01/02/2024\n2,2024-02-15\n3,13/10/2024\n")
    ds.load_csv(f, "t")
    r = ds.clean_dates("t", "d")
    assert r["fixed"] == 3 and r["failed"] == 0
    vals = {row[1] for row in ds.preview("t", 10)["rows"]}
    assert vals == {"2024-01-02", "2024-02-15", "2024-10-13"}

def test_filter_rows(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"
    f.write_text("cust_id,amount\nc1,100\nc2,250\nc3,75\n")
    ds.load_csv(f, "sales")
    ds.cast_column("sales", "amount", "number")   # numeric compare requires cast first
    out = ds.filter_rows("sales", "amount", ">", 100, "big")
    assert out["rows"] == 1
    assert ("c2", 250.0) in [tuple(x) for x in ds.preview("big", 10)["rows"]]

def test_cast_column(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"
    f.write_text('id,amount\n1,"$1,234.56"\n2,99\n')
    ds.load_csv(f, "t")
    r = ds.cast_column("t", "amount", "number")
    assert r["fixed"] == 2 and r["failed"] == 0
    assert ("1", 1234.56) in [tuple(x) for x in ds.preview("t", 10)["rows"]]

def test_dedupe(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"
    f.write_text("a,b\n1,2\n1,2\n3,4\n")
    ds.load_csv(f, "t")
    out = ds.dedupe("t", "deduped")
    assert out["rows"] == 2

def test_rename_column(tmp_path):
    ds = DataStore()
    f = tmp_path / "s.csv"
    f.write_text("Customer ID,Amount\nc1,100\n")
    ds.load_csv(f, "t")
    ds.rename_column("t", "Customer ID", "customer_id")
    assert "customer_id" in ds._cols("t")


def test_merge_tables_appends_rows(tmp_path):
    ds = DataStore(":memory:")
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    b.write_text("x,y\n5,6\n", encoding="utf-8")
    ds.load_csv(str(a), "t1")
    ds.load_csv(str(b), "t2")
    r = ds.merge_tables(["t1", "t2"], "merged")
    assert r["rows"] == 3
    assert ds._count("merged") == 3
