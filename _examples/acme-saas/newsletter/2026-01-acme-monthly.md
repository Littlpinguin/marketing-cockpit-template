---
source: newsletter
date: 2026-01-31
subject: "Acme Monthly — January 2026"
preview: "Our 2025 reliability report, what we shipped, and why we're hiring differently."
author: Acme SaaS team
language: en
example: true
---

# Acme Monthly — January 2026

## What shipped

- **Parallel test orchestration.** Tests now run across up to 32 workers instead of 8. Median build time dropped from 11 min to 3 min 40 sec on our benchmark suite.
- **Revamped audit log.** Every pipeline action now has a structured audit trail, queryable via API. SOC 2 auditors will thank us.
- **New regions.** `eu-north` (Stockholm) and `asia-south` (Mumbai) entered GA. 23 ms p95 latency targets hit in both.

## Data corner

**2025 reliability report, short version:**

| Metric | 2024 | 2025 |
|---|---|---|
| Uptime | 99.93% | 99.97% |
| P50 build queue time | 18 sec | 9 sec |
| P95 build queue time | 2 min 11 sec | 54 sec |
| Incidents | 7 | 4 |
| Mean time to recovery | 1h 02min | 33 min |

Full post-mortems for all four 2025 incidents are at acme.dev/incidents/2025. No redactions, no marketing spin.

## Community

- **Office hours** every Thursday 17:00 CET. Drop in, ask anything. Last week's recording: "Scaling CI for monorepos" — 26 minutes.
- **Open roles**: senior backend engineer (EU remote), platform SRE (EU remote), developer advocate (EU remote or Paris office). Details at acme.dev/careers.

## What we're reading

- The post-mortem of GitLab's February 2024 incident. We stole the "chaos engineering as a weekly ritual" idea from it.
- "Accelerate" by Forsgren, Humble & Kim. Still the best book on engineering velocity, six years after publication.

Talk soon,
The Acme team

---

*You're receiving this because you signed up at acme.dev. Unsubscribe anytime — no hurt feelings.*
