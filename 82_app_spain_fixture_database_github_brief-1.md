# 82 App / Grounds Quest: Spain Historical Fixtures & Regional Challenge Database Brief

## 1. Project summary

We are building a structured Spanish football fixtures and grounds database for the **82 App / Grounds Quest** product.

The app will allow users to:

1. browse Spanish football teams by season, competition, ground and region;
2. click on a team and view every fixture that team played from the 2021/22 season onward;
3. select a specific fixture they attended;
4. track progress across team, ground, league and regional challenges;
5. calculate regional challenge progress using hidden autonomous-region tags attached to each team and ground.

This brief covers the data-extraction and database-build work required to create app-ready CSV and SQLite outputs.

---

## 2. Competitions and seasons in scope

The database should cover all fixtures and results from the following Spanish competitions, starting with the **2021/22 season**:

| Level | Competition | Grouping | Source priority |
|---|---|---|---|
| 1 | Primera División / LaLiga | Single national league | LaLiga official results pages |
| 2 | Segunda División / LaLiga Hypermotion | Single national league | LaLiga official results pages |
| 3 | Primera Federación | Group 1 | RFEF official competition, calendar, results and acta pages |
| 3 | Primera Federación | Group 2 | RFEF official competition, calendar, results and acta pages |

Initial historical coverage:

```text
2021/22
2022/23
2023/24
2024/25
2025/26
```

The extraction pipeline should be reusable so it can later be rerun for:

```text
2026/27 onward
```

---

## 3. Source principles

Use official or reputable association sources wherever possible.

Preferred hierarchy:

1. **LaLiga official result pages** for Primera División and Segunda División.
2. **RFEF official pages** for Primera Federación, including competition pages, calendars, classifications, results and actas.
3. **Official club websites** only where needed to reconcile venue names, stadium details or naming inconsistencies.
4. **OpenStreetMap / Wikidata-style sources** only for enrichment such as coordinates or geographic metadata, not as the primary authority for fixtures/results.
5. Avoid media sites as primary sources.

Every extracted fixture should retain its original source URL for audit and future rechecking.

---

## 4. Core app requirement

The database must support this user journey:

```text
User clicks a team
↓
Selects a season
↓
Views every fixture that team played in that season
↓
Selects the match they attended
↓
Saves it to their profile
```

Example:

```text
User clicks Barcelona
↓
Selects 2022/23
↓
Views every Barcelona fixture from that season, home and away
↓
Chooses Barcelona v Rayo Vallecano, Real Sociedad v Barcelona, etc.
```

Therefore, the data model needs two fixture layers:

1. **Source-of-truth fixture table**: one row per actual match.
2. **Team fixture index table**: two rows per match, one from each team’s perspective.

This is essential because the app needs to show all fixtures for a selected team without having to calculate home/away logic dynamically every time.

---

## 5. Required output files

The extraction project should generate these files:

```text
spain_fixtures_results_2021_22_onward.csv
spain_team_fixture_index_2021_22_onward.csv
spain_teams.csv
spain_team_aliases.csv
spain_grounds.csv
spain_ground_aliases.csv
spain_competitions.csv
spain_seasons.csv
spain_autonomous_regions.csv
spain_fixture_source_audit.csv
spain_unresolved_team_aliases.csv
spain_unresolved_ground_aliases.csv
spain_fixtures.sqlite
validation_report.md
```

The CSV files should be upload-ready for the web app.

The SQLite database should contain the same data in relational form so that developers can test queries and validate the import before loading it into the production app.

---

## 6. Table design

### 6.1 `fixtures_results.csv`

This is the source-of-truth match table. Each fixture should appear once.

Required fields:

```text
fixture_id
season_id
competition_id
competition_name
competition_level
competition_group
matchday
round_label
fixture_date
kickoff_time_local
home_team_id
home_team_name_source
away_team_id
away_team_name_source
home_score
away_score
result_status
venue_id
venue_name_source
attendance
referee
match_report_url
rfef_acta_url
laliga_match_url
source_system
source_url
source_retrieved_at
data_confidence
notes
```

Example:

```text
fixture_id: 2022-23_LALIGA_EA_J01_FC_BARCELONA_RAYO_VALLECANO
season_id: 2022-23
competition_id: LALIGA_EA
competition_name: Primera División
competition_level: 1
competition_group: 
matchday: 1
round_label: Jornada 1
fixture_date: 2022-08-13
kickoff_time_local: 20:00
home_team_id: FC_BARCELONA
home_team_name_source: FC Barcelona
away_team_id: RAYO_VALLECANO
away_team_name_source: Rayo Vallecano
home_score: 0
away_score: 0
result_status: Played
venue_id: CAMP_NOU
venue_name_source: Spotify Camp Nou
source_system: LaLiga
source_url: official LaLiga jornada page
```

---

### 6.2 `team_fixture_index.csv`

This is the key app-facing table.

Each fixture should generate **two rows**:

1. one from the home team’s perspective;
2. one from the away team’s perspective.

Required fields:

```text
team_fixture_id
fixture_id
team_id
season_id
competition_id
competition_name
competition_group
matchday
fixture_date
opponent_team_id
home_or_away
team_score
opponent_score
result_for_team
venue_id
is_home_ground
team_autonomous_region_id
team_autonomous_region_name
team_autonomous_region_slug
opponent_autonomous_region_id
opponent_autonomous_region_name
opponent_autonomous_region_slug
source_url
```

Example home-team row:

```text
team_fixture_id: 2022-23_LALIGA_EA_J01_FC_BARCELONA_RAYO_VALLECANO__FC_BARCELONA
fixture_id: 2022-23_LALIGA_EA_J01_FC_BARCELONA_RAYO_VALLECANO
team_id: FC_BARCELONA
season_id: 2022-23
competition_id: LALIGA_EA
competition_name: Primera División
matchday: 1
fixture_date: 2022-08-13
opponent_team_id: RAYO_VALLECANO
home_or_away: Home
team_score: 0
opponent_score: 0
result_for_team: Draw
venue_id: CAMP_NOU
is_home_ground: true
team_autonomous_region_id: CT
team_autonomous_region_name: Catalonia
team_autonomous_region_slug: catalonia
opponent_autonomous_region_id: MD
opponent_autonomous_region_name: Community of Madrid
opponent_autonomous_region_slug: community-of-madrid
```

Example away-team row:

```text
team_fixture_id: 2022-23_LALIGA_EA_J01_FC_BARCELONA_RAYO_VALLECANO__RAYO_VALLECANO
fixture_id: 2022-23_LALIGA_EA_J01_FC_BARCELONA_RAYO_VALLECANO
team_id: RAYO_VALLECANO
season_id: 2022-23
competition_id: LALIGA_EA
competition_name: Primera División
matchday: 1
fixture_date: 2022-08-13
opponent_team_id: FC_BARCELONA
home_or_away: Away
team_score: 0
opponent_score: 0
result_for_team: Draw
venue_id: CAMP_NOU
is_home_ground: false
team_autonomous_region_id: MD
team_autonomous_region_name: Community of Madrid
team_autonomous_region_slug: community-of-madrid
opponent_autonomous_region_id: CT
opponent_autonomous_region_name: Catalonia
opponent_autonomous_region_slug: catalonia
```

This allows a simple app query:

```sql
SELECT *
FROM team_fixture_index
WHERE team_id = 'FC_BARCELONA'
AND season_id = '2022-23'
ORDER BY fixture_date;
```

---

### 6.3 `teams.csv`

This table stores the club/team records used by the app.

Required fields:

```text
team_id
club_name_official
club_name_short
club_name_display
slug
season_id
competition_id
competition_name
competition_level
competition_group
home_ground_id
home_ground_name
city
province
autonomous_region_id
autonomous_region_name
autonomous_region_slug
regional_challenge_eligible
regional_challenge_group_name
official_club_url
source_url
active_in_current_82_app
historical_team
notes
```

Every team must have an autonomous-region tag. This tag may be invisible in the UI but must be present in the data.

Example:

```text
team_id: FC_BARCELONA
club_name_official: Fútbol Club Barcelona
club_name_short: Barcelona
club_name_display: FC Barcelona
autonomous_region_id: CT
autonomous_region_name: Catalonia
autonomous_region_slug: catalonia
regional_challenge_eligible: true
regional_challenge_group_name: Catalonia Challenge
```

---

### 6.4 `grounds.csv`

This table stores stadium/ground records.

Required fields:

```text
ground_id
ground_name
city
province
autonomous_region_id
autonomous_region_name
autonomous_region_slug
capacity
latitude
longitude
opened_year
primary_tenant_team_id
official_source_url
notes
```

The ground should also carry a regional tag because some future app challenges may be based on grounds rather than clubs.

---

### 6.5 `team_aliases.csv`

This table maps source names to stable app team IDs.

Official sources may use different versions of a club name, so aliases are essential to avoid fragmented team histories.

Required fields:

```text
alias_id
team_id
source_name
normalised_name
source_system
valid_from_season
valid_to_season
notes
```

Examples:

```text
FC Barcelona → FC_BARCELONA
Fútbol Club Barcelona → FC_BARCELONA
Barcelona → FC_BARCELONA
Barça → FC_BARCELONA
```

---

### 6.6 `ground_aliases.csv`

This table maps source venue names to stable app ground IDs.

Required fields:

```text
alias_id
ground_id
source_name
normalised_name
source_system
valid_from_season
valid_to_season
notes
```

---

### 6.7 `autonomous_regions.csv`

Controlled vocabulary for Spanish autonomous regions and cities.

Required fields:

```text
autonomous_region_id
autonomous_region_name
autonomous_region_slug
regional_challenge_group_name
regional_challenge_eligible
notes
```

Recommended reference list:

```text
AN | Andalusia | andalusia | Andalusia Challenge
AR | Aragon | aragon | Aragon Challenge
AS | Asturias | asturias | Asturias Challenge
IB | Balearic Islands | balearic-islands | Balearic Islands Challenge
PV | Basque Country | basque-country | Basque Country Challenge
CN | Canary Islands | canary-islands | Canary Islands Challenge
CB | Cantabria | cantabria | Cantabria Challenge
CM | Castilla-La Mancha | castilla-la-mancha | Castilla-La Mancha Challenge
CL | Castile and León | castile-and-leon | Castile and León Challenge
CT | Catalonia | catalonia | Catalonia Challenge
EX | Extremadura | extremadura | Extremadura Challenge
GA | Galicia | galicia | Galicia Challenge
MD | Community of Madrid | community-of-madrid | Madrid Challenge
MU | Region of Murcia | region-of-murcia | Murcia Challenge
NC | Navarre | navarre | Navarre Challenge
RI | La Rioja | la-rioja | La Rioja Challenge
VC | Valencian Community | valencian-community | Valencian Community Challenge
CE | Ceuta | ceuta | Ceuta Challenge
ML | Melilla | melilla | Melilla Challenge
```

Where a club’s administrative address and stadium location differ, use the autonomous region of the club’s **primary home ground** for regional challenge purposes unless the app owner explicitly overrides it.

---

## 7. Invisible regional challenge tag

Each team entry must carry an invisible autonomous-region tag.

This tag will not necessarily be shown to users on every screen, but it is required for challenge logic such as:

```text
Complete all Catalonia grounds
Complete all Andalusia grounds
How many Basque Country teams are in the current 82 challenge?
Show my progress across Madrid-based clubs
```

Required regional fields on `teams.csv`:

```text
autonomous_region_id
autonomous_region_name
autonomous_region_slug
regional_challenge_eligible
regional_challenge_group_name
```

The same fields should be propagated into `team_fixture_index.csv` for both the selected team and the opponent.

This allows the app to calculate regional challenge counts without additional lookups if required.

Example regional count query:

```sql
SELECT autonomous_region_name, COUNT(DISTINCT team_id) AS team_count
FROM teams
WHERE active_in_current_82_app = true
AND regional_challenge_eligible = true
GROUP BY autonomous_region_name
ORDER BY autonomous_region_name;
```

---

## 8. Extraction process

The extraction should run in five stages.

### Stage 1: Build source map

Create a map covering every competition, season, group and matchday.

Output:

```text
official_source_map.csv
```

Fields:

```text
source_id
season_id
competition_id
competition_name
competition_group
matchday
source_system
source_url
expected_match_count
status
notes
```

For LaLiga competitions, URLs are expected to follow a jornada-based structure.

For RFEF / Primera Federación, the extractor may need to discover calendar and acta links rather than relying on a single predictable URL pattern.

---

### Stage 2: Pull raw match data

For each official source page, extract the raw match data before normalisation.

Required raw fields:

```text
season_id
competition_id
competition_group
matchday
date
kickoff_time
home_team_source_name
away_team_source_name
home_score
away_score
venue_name_source
referee
attendance
match_report_url
acta_url
source_system
source_url
source_retrieved_at
```

Output:

```text
raw_fixtures_extracted.csv
```

---

### Stage 3: Normalise teams and grounds

Map every source team name to a stable `team_id`.

Map every source venue name to a stable `ground_id`.

Unresolved names must be written to manual review files.

Outputs:

```text
team_aliases.csv
ground_aliases.csv
unresolved_team_aliases.csv
unresolved_ground_aliases.csv
```

---

### Stage 4: Generate fixture and team index tables

Create:

```text
fixtures_results.csv
team_fixture_index.csv
```

Rules:

1. Every fixture must have one row in `fixtures_results.csv`.
2. Every fixture must generate two rows in `team_fixture_index.csv`.
3. Both team index rows must carry regional metadata for the team and opponent.
4. Result from each team’s perspective must be calculated as `Win`, `Draw` or `Loss`.
5. The fixture source URL must be retained.

---

### Stage 5: Validate and audit

Create a validation report checking:

```text
Expected match counts by season and competition
Missing matchdays
Duplicate fixtures
Fixtures without two teams
Fixtures without two team fixture index rows
Unmapped teams
Unmapped grounds
Missing scores for completed matches
Missing source URLs
Missing autonomous-region tags
Regional challenge team counts
Regional fields propagated into team_fixture_index
```

Output:

```text
validation_report.md
```

---

## 9. Expected match volumes

Indicative volumes per season:

```text
Primera División: 380 matches
Segunda División: 462 matches
Primera Federación Group 1: approximately 380 matches
Primera Federación Group 2: approximately 380 matches
```

Indicative total for 2021/22 to 2025/26:

```text
Approximately 8,000 fixtures
Approximately 16,000 team fixture index rows
```

The validation report should flag any material deviation from expected volumes.

---

## 10. Required app queries

The database must support these app queries.

### 10.1 Team season fixture history

```sql
SELECT *
FROM team_fixture_index
WHERE team_id = 'FC_BARCELONA'
AND season_id = '2022-23'
ORDER BY fixture_date;
```

### 10.2 All fixtures at a ground

```sql
SELECT *
FROM fixtures_results
WHERE venue_id = 'CAMP_NOU'
ORDER BY fixture_date;
```

### 10.3 Regional challenge team count

```sql
SELECT autonomous_region_name, COUNT(DISTINCT team_id) AS team_count
FROM teams
WHERE regional_challenge_eligible = true
GROUP BY autonomous_region_name
ORDER BY autonomous_region_name;
```

### 10.4 User progress in a region

```sql
SELECT COUNT(DISTINCT t.team_id) AS completed_teams
FROM user_attended_fixtures u
JOIN teams t ON u.selected_team_id = t.team_id
WHERE u.user_id = ?
AND t.autonomous_region_slug = 'catalonia';
```

### 10.5 Fixtures missing regional tags

```sql
SELECT team_fixture_id, team_id
FROM team_fixture_index
WHERE team_autonomous_region_id IS NULL
OR team_autonomous_region_slug IS NULL;
```

---

## 11. Suggested repository structure

```text
/spain-fixtures-data
  /data
    /raw
    /processed
    /exports
  /scripts
    official_extraction_runner.py
    build_source_map.py
    build_team_fixture_index.py
    normalise_team_aliases.py
    normalise_ground_aliases.py
    validate_outputs.py
  /docs
    data_dictionary.md
    source_map_notes.md
    regional_challenge_notes.md
  README.md
  requirements.txt
```

---

## 12. Running environment

The extraction runner should be run from a normal HTTP-enabled Python environment, such as:

1. GitHub Codespaces;
2. a local laptop with Python installed;
3. Google Colab;
4. a developer-controlled server or cloud environment.

ChatGPT can help design, test, validate and debug the scripts, but the full extraction run should be executed in a proper Python environment because it needs to visit hundreds of official source pages, handle retries, save outputs and produce logs.

Recommended command flow:

```bash
cd spain-fixtures-data
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/official_extraction_runner.py
python scripts/build_team_fixture_index.py
python scripts/validate_outputs.py
```

Windows activation command may differ.

---

## 13. Definition of done

The project is complete when:

```text
1. All fixtures from 2021/22 onward are extracted for Primera División, Segunda División, Primera Federación Group 1 and Primera Federación Group 2.
2. Every fixture has a retained official source URL.
3. Every fixture has one source-of-truth row in fixtures_results.csv.
4. Every fixture generates two team-facing rows in team_fixture_index.csv.
5. Users can query all fixtures for a selected team and season.
6. Every team has an autonomous-region tag.
7. Every ground has an autonomous-region tag.
8. Regional challenge team counts can be calculated automatically.
9. Regional metadata is present in the team fixture index.
10. Unresolved team and ground aliases are either fixed or listed in manual review files.
11. Final CSVs are exportable and app-upload-ready.
12. SQLite database is generated for testing and validation.
13. validation_report.md confirms match counts, duplicate checks, alias gaps, source URL retention and regional challenge readiness.
```

---

## 14. Developer notes

The most important design principle is that the app should not merely store match results. It should store results in a way that supports the user’s browsing and attendance-recording journey.

In simple terms:

```text
fixtures_results.csv answers: What match happened?
team_fixture_index.csv answers: Which matches did this team play?
teams.csv answers: Which team is this, and what region does it belong to?
grounds.csv answers: Where was the match played?
user_attended_fixtures answers: Which match did the user attend?
```

The invisible autonomous-region tag is a core requirement because regional challenges will depend on it. For example, the app must be able to identify how many Catalonia teams are in the current challenge set, how many the user has completed, and which fixtures or grounds are still outstanding.

---

## 15. Plain-English task for GitHub issue

Build a reusable data extraction pipeline that collects official Spanish football results from 2021/22 onward and converts them into app-ready CSV and SQLite outputs for the 82 App / Grounds Quest.

The pipeline should cover Primera División, Segunda División, Primera Federación Group 1 and Primera Federación Group 2. It should use LaLiga and RFEF official sources wherever possible.

The critical app requirement is that users must be able to click a team, select a season, and view every fixture that team played. Therefore, each match should be stored once in a source-of-truth fixture table and twice in a team fixture index table, once from each team’s perspective.

Each team and ground must also carry an invisible autonomous-region tag, such as Catalonia, Andalusia, Basque Country or Community of Madrid. The app will use this hidden tag to calculate regional challenges and user progress.
