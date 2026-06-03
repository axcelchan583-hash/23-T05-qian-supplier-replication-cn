# Research Question

## Main Question

Can Qian et al.'s supplier abnormal-return main effect be replicated in China?

More precisely:

```text
When an A-share listed downstream customer publicly announces a concrete GenAI initiative,
do its pre-existing A-share listed suppliers earn positive abnormal returns around the event date?
```

## Current Scope

This project is a replication audit, not a new paper package.

The target is the minimum main effect:

- focal firm: A-share listed customer announcing a concrete GenAI initiative;
- affected firm: pre-existing listed supplier;
- relationship window: supplier relation observed before the event;
- outcome: supplier `AR0` as the Qian-style primary outcome, with `CAR[0,+1]` retained for China's disclosure-timing imprecision.

## Reporting Windows

Two event windows should be reported:

1. `2023-2024`: U.S.-comparable window.
2. `2023-2026`: China extended adoption window.

The extended window should be described as a China institutional-timing adaptation, not as a direct same-calendar replication.

## What This Project Does Not Claim

- It does not claim that every CNINFO GenAI mention is an initiative.
- It does not claim that media discussion alone is treatment.
- It does not claim a new identification strategy beyond a Qian-style event-study replication.
- It does not yet support heterogeneity, PSM, Heckman, IV, or publication-style mechanism claims.

