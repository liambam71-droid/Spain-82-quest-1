# Primera Federación 2025–26 Data Status

## Current status

This repository currently includes a QA-clean candidate dataset for Primera Federación 2025–26.

Included:

- Grupo 1: Jornadas 1–36
- Grupo 2: Jornadas 1–38

Current fixture coverage:

- Grupo 1: 360 / 380 fixtures
- Grupo 2: 380 / 380 fixtures
- Total: 740 / 760 regular-season fixtures

Outstanding:

- Grupo 1 Jornada 37: 10 fixtures missing
- Grupo 1 Jornada 38: 10 fixtures missing

## Source status

The dataset was assembled from RFEF-derived extraction outputs.

Grupo 1 fixtures were extracted from RFEF results/calendar routes.

Grupo 2 fixtures were extracted from a successful RFEF marcadores calendar-view probe.

The final QA-clean fixtures file blanks ambiguous partial score values where the RFEF calendar view provided only single-number fragments.

## Files

App data:

- `public/data/primerafed_2025_26_fixtures_results_final_candidate_QA_clean.csv`
- `public/data/primerafed_2025_26_team_fixture_index_final_candidate_QA_clean.csv`

Audit files:

- `docs/data-audit/primerafed_2025_26_final_merge_validation_QA_clean.csv`
- `docs/data-audit/primerafed_2025_26_missing_fixtures_audit.csv`

## Next action

Do not treat the dataset as complete until Grupo 1 Jornadas 37–38 are added or validated from RFEF/secondary source.
