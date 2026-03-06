# 36-aws-reliability-security-db2

A portfolio-grade repository focused on **DB2-safe operations patterns** and governance:
offline demos, deterministic guardrails, and explicit validation modes.


## The top pains this repo addresses
1) Designing a resilient, scalable cloud platform foundation—Kubernetes/container orchestration, networking, and standard patterns teams can reuse.
2) Building a data platform people trust—reliable pipelines, clear ownership, data quality checks, and governance that scales without slowing delivery.
3) Replacing manual, risky changes with automated delivery—repeatable infrastructure, safe deployments, and drift-free environments (IaC + CI/CD + GitOps).

## Quick demo (local)
```bash
make demo-offline
make test
```

What you get:
- offline demo pipeline output (no pip installs needed)
- DB2 governance guardrails report (`artifacts/db2_guardrails.json`)
- explicit `TEST_MODE=demo|production` tests with safe production gating

## Tests (two explicit modes)

- `TEST_MODE=demo` (default): offline-only checks, deterministic artifacts
- `TEST_MODE=production`: real integrations (requires explicit opt-in + configuration)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

Production integration options:
- Set `DB2_TEST_DSN` to run a DB2 client connectivity check (requires the `db2` CLI)
- Or set `TERRAFORM_VALIDATE=1` to validate the included Terraform example (requires `terraform`)

## Guardrails

Generate evidence:

```bash
python3 tools/db2_guardrails.py --format json --out artifacts/db2_guardrails.json
```

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
