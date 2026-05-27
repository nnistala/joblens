#!/usr/bin/env python3
"""Seed the companies table with top Indian employers and major GCCs.

Usage:
    python infra/scripts/seed_companies.py

Requires DATABASE_URL environment variable or .env file in the project root.
Uses psycopg2 (sync) for simplicity in scripts.
"""

import os
import sys
import uuid

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("ERROR: psycopg2 is required. Install with: pip install psycopg2-binary")
    sys.exit(1)

# ── Company seed data ─────────────────────────────────────────
# Fields: name, domain, career_page_url, industry, size_bucket, ats_platform

COMPANIES = [
    # ── Indian IT Services ────────────────────────────────────
    ("Tata Consultancy Services", "tcs.com", "https://ibegin.tcs.com/iBegin/jobs/search", "IT Services", "100000+", "custom"),
    ("Infosys", "infosys.com", "https://career.infosys.com/joblist", "IT Services", "100000+", "custom"),
    ("Wipro", "wipro.com", "https://careers.wipro.com/search-jobs", "IT Services", "100000+", "custom"),
    ("HCLTech", "hcltech.com", "https://www.hcltech.com/careers", "IT Services", "100000+", "custom"),
    ("Tech Mahindra", "techmahindra.com", "https://careers.techmahindra.com", "IT Services", "50000+", "custom"),
    ("LTIMindtree", "ltimindtree.com", "https://careers.ltimindtree.com", "IT Services", "50000+", "custom"),
    ("Mphasis", "mphasis.com", "https://careers.mphasis.com", "IT Services", "10000+", "custom"),
    ("Persistent Systems", "persistent.com", "https://careers.persistent.com", "IT Services", "10000+", "custom"),
    ("Coforge", "coforge.com", "https://careers.coforge.com", "IT Services", "10000+", "custom"),
    ("Zensar Technologies", "zensar.com", "https://careers.zensar.com", "IT Services", "5000+", "custom"),

    # ── Indian Product / Startups ─────────────────────────────
    ("Flipkart", "flipkart.com", "https://www.flipkartcareers.com", "E-Commerce", "10000+", "custom"),
    ("Swiggy", "swiggy.com", "https://careers.swiggy.com", "Food Delivery", "5000+", "greenhouse"),
    ("Zomato", "zomato.com", "https://www.zomato.com/careers", "Food Delivery", "5000+", "custom"),
    ("Razorpay", "razorpay.com", "https://razorpay.com/jobs", "Fintech", "1000+", "greenhouse"),
    ("CRED", "cred.club", "https://careers.cred.club", "Fintech", "1000+", "lever"),
    ("PhonePe", "phonepe.com", "https://www.phonepe.com/careers", "Fintech", "5000+", "custom"),
    ("Paytm", "paytm.com", "https://jobs.paytm.com", "Fintech", "5000+", "custom"),
    ("Ola", "olacabs.com", "https://www.olacabs.com/careers", "Mobility", "5000+", "custom"),
    ("Dream11", "dream11.com", "https://www.dream11.com/careers", "Gaming", "1000+", "lever"),
    ("Freshworks", "freshworks.com", "https://careers.freshworks.com", "SaaS", "5000+", "greenhouse"),
    ("Zoho", "zoho.com", "https://careers.zoho.com", "SaaS", "10000+", "custom"),
    ("Meesho", "meesho.com", "https://careers.meesho.com", "E-Commerce", "1000+", "lever"),
    ("Groww", "groww.in", "https://groww.in/careers", "Fintech", "1000+", "lever"),
    ("Zerodha", "zerodha.com", "https://zerodha.com/careers", "Fintech", "1000+", "custom"),
    ("ShareChat", "sharechat.com", "https://sharechat.com/careers", "Social Media", "1000+", "lever"),
    ("Myntra", "myntra.com", "https://careers.myntra.com", "E-Commerce", "5000+", "custom"),
    ("BigBasket", "bigbasket.com", "https://careers.bigbasket.com", "E-Commerce", "5000+", "custom"),
    ("Nykaa", "nykaa.com", "https://careers.nykaa.com", "E-Commerce", "5000+", "custom"),
    ("Lenskart", "lenskart.com", "https://lenskart.com/careers", "E-Commerce", "5000+", "custom"),
    ("Jupiter", "jupiter.money", "https://jupiter.money/careers", "Fintech", "500+", "lever"),
    ("Slice", "sliceit.com", "https://sliceit.com/careers", "Fintech", "500+", "lever"),
    ("Unacademy", "unacademy.com", "https://unacademy.com/careers", "EdTech", "1000+", "custom"),
    ("upGrad", "upgrad.com", "https://www.upgrad.com/careers", "EdTech", "5000+", "custom"),
    ("Delhivery", "delhivery.com", "https://www.delhivery.com/careers", "Logistics", "10000+", "custom"),
    ("Dunzo", "dunzo.com", "https://www.dunzo.com/careers", "Logistics", "1000+", "lever"),
    ("Rapido", "rapido.bike", "https://rapido.bike/careers", "Mobility", "500+", "custom"),
    ("Urban Company", "urbancompany.com", "https://careers.urbancompany.com", "Services", "1000+", "greenhouse"),
    ("InMobi", "inmobi.com", "https://www.inmobi.com/company/careers", "AdTech", "1000+", "greenhouse"),
    ("Postman", "postman.com", "https://www.postman.com/careers", "Developer Tools", "1000+", "greenhouse"),
    ("BrowserStack", "browserstack.com", "https://www.browserstack.com/careers", "Developer Tools", "1000+", "greenhouse"),
    ("Chargebee", "chargebee.com", "https://www.chargebee.com/careers", "SaaS", "1000+", "greenhouse"),
    ("Clevertap", "clevertap.com", "https://clevertap.com/careers", "SaaS", "500+", "greenhouse"),
    ("MoEngage", "moengage.com", "https://www.moengage.com/careers", "SaaS", "500+", "greenhouse"),
    ("Hasura", "hasura.io", "https://hasura.io/careers", "Developer Tools", "200+", "greenhouse"),
    ("Razorpay", "razorpay.com", "https://razorpay.com/jobs", "Fintech", "1000+", "greenhouse"),

    # ── Indian Conglomerates / Large Enterprises ──────────────
    ("Reliance Industries", "ril.com", "https://careers.ril.com", "Conglomerate", "100000+", "custom"),
    ("Jio", "jio.com", "https://careers.jio.com", "Telecom", "10000+", "custom"),
    ("Tata Motors", "tatamotors.com", "https://careers.tatamotors.com", "Automotive", "50000+", "custom"),
    ("Mahindra & Mahindra", "mahindra.com", "https://careers.mahindra.com", "Conglomerate", "50000+", "custom"),
    ("Bajaj Finserv", "bajajfinserv.in", "https://careers.bajajfinserv.in", "Financial Services", "10000+", "custom"),
    ("HDFC Bank", "hdfcbank.com", "https://www.hdfcbank.com/personal/about-us/careers", "Banking", "100000+", "custom"),
    ("ICICI Bank", "icicibank.com", "https://careers.icicibank.com", "Banking", "50000+", "custom"),

    # ── GCCs (Global Capability Centers) in India ─────────────
    ("Google India", "google.com", "https://www.google.com/about/careers/applications/jobs/results/?location=India", "Technology", "10000+", "custom"),
    ("Microsoft India", "microsoft.com", "https://careers.microsoft.com/us/en/search-results?country=India", "Technology", "10000+", "custom"),
    ("Amazon India", "amazon.in", "https://www.amazon.jobs/en/locations/india", "E-Commerce / Cloud", "50000+", "custom"),
    ("Meta India", "meta.com", "https://www.metacareers.com/jobs?offices[0]=India", "Technology", "1000+", "custom"),
    ("Apple India", "apple.com", "https://jobs.apple.com/en-in/search?location=india", "Technology", "5000+", "custom"),
    ("Goldman Sachs India", "goldmansachs.com", "https://www.goldmansachs.com/careers/find-a-job/?location=Bengaluru", "Financial Services", "10000+", "custom"),
    ("JP Morgan India", "jpmorgan.com", "https://careers.jpmorgan.com/global/en/search?location=India", "Financial Services", "50000+", "custom"),
    ("Morgan Stanley India", "morganstanley.com", "https://www.morganstanley.com/careers/find-a-job?country=India", "Financial Services", "10000+", "custom"),
    ("Deutsche Bank India", "db.com", "https://careers.db.com/explore-the-bank/careers-in-india/", "Financial Services", "10000+", "custom"),
    ("Barclays India", "barclays.com", "https://search.jobs.barclays/search-jobs/India", "Financial Services", "10000+", "custom"),
    ("SAP Labs India", "sap.com", "https://jobs.sap.com/search/?q=&locationsearch=India", "Enterprise Software", "10000+", "custom"),
    ("Adobe India", "adobe.com", "https://careers.adobe.com/us/en/search-results?keywords=&location=India", "Software", "5000+", "custom"),
    ("Salesforce India", "salesforce.com", "https://careers.salesforce.com/en/jobs/?country=India", "SaaS", "5000+", "custom"),
    ("Uber India", "uber.com", "https://www.uber.com/in/en/careers/list/?location=IND-Bangalore", "Mobility", "1000+", "greenhouse"),
    ("Netflix India", "netflix.com", "https://jobs.netflix.com/search?location=India", "Entertainment", "500+", "custom"),
    ("Twitter / X India", "x.com", "https://careers.twitter.com/en/roles.html#location=india", "Social Media", "500+", "custom"),
    ("Walmart Global Tech India", "walmart.com", "https://careers.walmart.com/results?q=&page=1&sort=rank&country=IN", "Retail / Technology", "5000+", "custom"),
    ("Intuit India", "intuit.com", "https://jobs.intuit.com/search-jobs/India", "Financial Software", "1000+", "custom"),
    ("VMware India", "vmware.com", "https://careers.vmware.com/main/jobs?location=India", "Cloud / Virtualization", "5000+", "custom"),
    ("Cisco India", "cisco.com", "https://jobs.cisco.com/jobs/SearchJobs/?listFilterMode=1&21178=&21178_format=6020&21180=%5B169482%5D", "Networking", "10000+", "custom"),
    ("Oracle India", "oracle.com", "https://www.oracle.com/in/corporate/careers/", "Enterprise Software", "10000+", "custom"),
    ("IBM India", "ibm.com", "https://www.ibm.com/careers/search?field_keyword_08[0]=India", "Technology", "50000+", "custom"),
    ("Atlassian India", "atlassian.com", "https://www.atlassian.com/company/careers/all-jobs?location=Bengaluru", "Developer Tools", "1000+", "greenhouse"),
    ("Stripe India", "stripe.com", "https://stripe.com/jobs/search?office_locations=Asia+Pacific--Bengaluru", "Fintech", "500+", "custom"),
    ("Twilio India", "twilio.com", "https://www.twilio.com/en-us/company/jobs?location=India", "Communications", "500+", "greenhouse"),
]


def get_database_url() -> str:
    """Resolve database URL from env or .env file, converting async URL to sync."""
    url = os.getenv("DATABASE_URL", "")

    if not url:
        # Try to read from .env file
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATABASE_URL="):
                        url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break

    if not url:
        url = "postgresql+asyncpg://joblens:joblens@localhost:5432/joblens"

    # Convert asyncpg URL to psycopg2-compatible URL
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


def deduplicate_companies(companies: list[tuple]) -> list[tuple]:
    """Remove duplicate companies by domain."""
    seen_domains: set[str] = set()
    unique: list[tuple] = []
    for company in companies:
        domain = company[1]
        if domain not in seen_domains:
            seen_domains.add(domain)
            unique.append(company)
    return unique


def seed_companies() -> None:
    """Insert seed companies into the database."""
    db_url = get_database_url()
    companies = deduplicate_companies(COMPANIES)

    print(f"Connecting to database...")
    print(f"Seeding {len(companies)} companies...")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    try:
        # Prepare data with UUIDs
        rows = []
        for name, domain, career_page_url, industry, size_bucket, ats_platform in companies:
            rows.append((
                str(uuid.uuid4()),
                name,
                domain,
                career_page_url,
                industry,
                size_bucket,
                ats_platform,
                True,   # is_verified
                False,  # is_hr_direct
            ))

        # Upsert: insert or skip if domain already exists
        execute_values(
            cur,
            """
            INSERT INTO companies (id, name, domain, career_page_url, industry, size_bucket, careers_ats_platform, is_verified, is_hr_direct)
            VALUES %s
            ON CONFLICT (domain) DO NOTHING
            """,
            rows,
        )

        inserted = cur.rowcount
        conn.commit()
        print(f"Successfully seeded {inserted} new companies ({len(companies) - inserted} already existed).")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    seed_companies()
