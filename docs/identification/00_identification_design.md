# Identification Design

## Event Definition

The event is the first public disclosure date of a concrete GenAI initiative by a focal customer firm.

Default source priority:

1. CNINFO formal announcement.
2. Qualified securities disclosure media or company release, only when it clearly predates CNINFO and can be verified.
3. General financial-news database records only as leads; they must be traced back to a company action or qualified disclosure source.

## Pre-Manual-Coding Diagnostic

Before the final manual event table is complete, the current 1,055-row CNINFO priority PDF pool may be used for a provisional event-study run.

This run has a limited purpose:

- verify that rebuilt CNINFO events can be linked to historical supplier relationships;
- check whether market-return and AR/CAR code runs on the new event source;
- compare signs across noisy treatment definitions before spending manual-coding time;
- identify whether sample loss occurs mainly at event validation, supplier linking, or return availability.

This run is not the final replication test. The 1,055 rows are priority PDF candidates, not verified GenAI initiatives. Any estimate from this run should be labeled `pre-manual-coding diagnostic` and excluded from the acceptance rule below.

## Event Date Alignment

- Non-trading-day events are moved to the next trading day.
- If an after-market release time is known, the event date is moved to the next trading day.
- If only the disclosure date is known, use the trading day corresponding to that date.

## Supplier Link

The main relationship is:

```text
focal customer -> upstream listed supplier
```

Rules:

- Use pre-existing supply-chain relationships only.
- Keep relation years before the event year.
- Prefer relation years from event year minus 5 through event year minus 1.
- Keep A-share listed suppliers.
- Drop `customer = supplier`.
- If duplicate edges exist, keep the most recent pre-event relationship.

## Main Outcome

Primary Qian-style outcome:

- supplier `AR0`

Auxiliary China timing outcome:

- supplier `CAR[0,+1]`

Day `-1` should be reported as a pre-event check rather than a treatment effect.

## Confounding Filters

Minimum filters:

- Drop supplier observations where the supplier has its own GenAI event before or on the customer event date.
- Drop non-trading observations, suspended days, price-limit days when identifiable, and rows without valid market-model parameters.
- Keep broader earnings, M&A, and major-announcement contamination as a documented limitation until a dedicated announcement-cleaning pass is run.

## Acceptance Rule

Classify the China replication as having a Qian-style signal only if:

- upstream supplier `AR0` or `CAR[0,+1]` is positive;
- the effect is at least marginally significant, `p < 0.10`;
- day `-1` is not significant in the same direction;
- the positive-return proportion is above 0.5.

If not, report that the main supplier reaction does not replicate under the audited China event definition.
