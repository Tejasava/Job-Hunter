#!/usr/bin/env python3
"""Test real job scraping"""

import sys
sys.path.insert(0, '/Users/tejasavayadav/Desktop/git hub projects/job hunter')

from bot_main import SimpleJobScraper

print("=" * 60)
print("🔍 Testing Real Job Scraping")
print("=" * 60)

scraper = SimpleJobScraper()

print("\n1️⃣  Testing Indeed Job Scraping...")
print("-" * 60)
indeed_jobs = scraper.search_indeed('Developer')
print(f"✅ Found {len(indeed_jobs)} Indeed jobs\n")
for i, job in enumerate(indeed_jobs[:5], 1):
    print(f"{i}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   Location: {job['location']}")
    print(f"   Salary: {job['salary']}")
    print(f"   🔗 URL: {job['url']}")
    print()

print("\n2️⃣  Testing LinkedIn Job Scraping...")
print("-" * 60)
linkedin_jobs = scraper.search_linkedin('Developer')
print(f"✅ Found {len(linkedin_jobs)} LinkedIn jobs\n")
for i, job in enumerate(linkedin_jobs[:5], 1):
    print(f"{i}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   Location: {job['location']}")
    print(f"   🔗 URL: {job['url']}")
    print()

if not indeed_jobs and not linkedin_jobs:
    print("⚠️  No real jobs found (sites might require authentication)")
    print("Using fallback sample jobs...")
    sample = scraper.search_sample_jobs('Developer')
    print(f"✅ Found {len(sample)} sample jobs")
    for i, job in enumerate(sample[:3], 1):
        print(f"{i}. {job['title']} - {job['url']}")

print("\n" + "=" * 60)
print("✅ Test Complete")
print("=" * 60)
