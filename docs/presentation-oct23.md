# Oct 23 – Tech slides: Deployment & CI Strategy

Five slides, roughly 2 minutes of the team's 10 minutes.

## Slide 1 – Tech stack & why
Use the "Key decisions" table from `architecture.md` (choice + one-line reason each).

## Slide 2 – System architecture
The box diagram from `architecture.md`. Say: "Three containers, frontend → API → database. The API also calls ClinicalTrials.gov."

## Slide 3 – Containers & dependencies
- Docker for every service, Docker Compose as orchestrator
- `uv.lock` / `package-lock.json` → identical versions for every teammate, CI and server
- Show the `docker compose up` command and the running app

## Slide 4 – Environments
The Dev / Stage / Live table. Live demo idea: open the Codespace link on the projector.

## Slide 5 – CI pipeline
Screenshot of a green GitHub Actions run:
`lint → tests → frontend build → Docker images build`
Say: "No code reaches main without passing these checks."

## Likely coach questions (prepare answers)
- *Why not Kubernetes?* → 3 services, small team. Compose is simpler and enough. We can migrate later.
- *Where is data stored and is it GDPR-safe?* → EU region (Frankfurt). Public data only, no patient data.
- *How do secrets work?* → `.env` file, never committed. Different values per environment.
- *What's next?* → Feature Set 1 (Nov 6): Criteria Analyzer with evidence highlighting + LLM comparison.
