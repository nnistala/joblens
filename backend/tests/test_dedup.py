from app.services.dedup import (
    compute_dedup_hash,
    fuzzy_title_match,
    normalize_company_name,
    normalize_title,
)


def test_normalize_company_name():
    assert normalize_company_name("Tata Consultancy Services Pvt. Ltd.") == "tata consultancy services"
    assert normalize_company_name("Infosys Limited") == "infosys"
    assert normalize_company_name("  Wipro  Technologies  ") == "wipro technologies"


def test_normalize_title():
    assert normalize_title("Sr. Software Eng") == "senior software engineer"
    assert normalize_title("Jr. Dev") == "junior developer"
    assert normalize_title("Mgr, Product") == "manager, product"


def test_compute_dedup_hash():
    h1 = compute_dedup_hash("Infosys", "Senior Software Engineer", "Bangalore")
    h2 = compute_dedup_hash("INFOSYS LIMITED", "Sr. Software Eng", "Bangalore")
    assert h1 == h2, "Same job from different sources should produce same hash"


def test_fuzzy_title_match():
    score = fuzzy_title_match("senior software engineer", "senior software developer")
    assert score > 0.7

    score = fuzzy_title_match("senior software engineer", "junior data analyst")
    assert score < 0.5


def test_dedup_hash_different_jobs():
    h1 = compute_dedup_hash("Infosys", "Senior Software Engineer", "Bangalore")
    h2 = compute_dedup_hash("Infosys", "Data Analyst", "Bangalore")
    assert h1 != h2
