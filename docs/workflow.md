# Team workflow (agile)

## Board (GitHub Projects)

Columns: **Backlog → To Do (this sprint) → In Progress → Review → Done**

Each card = one **user story**:
> *As a* trial coordinator, *I want* to paste eligibility criteria and see them structured, *so that* I can spot hard-to-meet criteria quickly.

Add **acceptance criteria** (a checklist of what "done" means) and a priority label: `must`, `should`, `could`.

## From idea to code

```
user story → wireframe (Figma/paper) → screen design → implementation → test → review → Done
```

Take a screenshot at each step. You'll need them for the Nov 6 presentation.

## Sprints

- 1-week sprints, starting Monday
- Monday: 15-min planning (pick cards for the week)
- Friday: short review (what's done, what's blocked)

## Git rules

1. Never push directly to `main`.
2. One branch per card: `feature/criteria-table`, `fix/age-regex`.
3. Open a Pull Request → CI must be green ✅ → one teammate reviews → merge.
4. Small PRs (under ~300 lines) get reviewed faster.

```bash
git switch -c feature/my-feature
# ...work...
git add . && git commit -m "Add age range rule"
git push -u origin feature/my-feature
# then open a Pull Request on GitHub
```

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Tests added/updated, CI green
- [ ] Reviewed by one teammate
- [ ] Works in Stage (Codespaces)
