# Tuen Mun AQHI handoff

Source: 15 Hong Kong EPD monthly English CSVs, April 2025 through June 2026.
Reproduce with [01_data.ipynb](../../01_data.ipynb). Modeling input: [tuen_mun_aqhi.csv](tuen_mun_aqhi.csv).

| Field | Type | Definition |
|---|---|---|
| timestamp | Timezone-aware datetime | Hong Kong hour endpoint (UTC+08:00). Source hour 24 is midnight the following day. |
| aqhi | float64 | AQHI level. 11 encodes the official 10+ category. An empty CSV field parses as NaN. |
| is_substituted | bool | True when EPD marked the reading with an asterisk, indicating a substitute station reading. |

## Quality checks

- Total hourly records: 10,944
- Duplicate timestamps: 0
- Rows involved in duplicates: 0
- Missing hours: 0
- Hours outside the expected grid: 0
- Missing AQHI (NaN): 18
- Original AQHI blanks: 12
- Original AQHI dashes: 6
- Substituted readings: 1,083
- Date/hour format or sequence issues: 0
- Unrecognized AQHI tokens: 0
- 10+ readings encoded as 11: 15
- Substituted share: 9.90% of all hourly rows and 9.91% of nonmissing AQHI.
- Timestamp coverage: 2025-04-01 01:00:00+08:00 to 2026-07-01 00:00:00+08:00 inclusive.
- The CSV contains hourly rows only. Original Daily Max rows remain in the source files.

## Sources and interpretation

Each row is the Hong Kong hour endpoint. Source hour 24 is midnight on the next day. Monthly quality and train/test tables group by the source reporting date (timestamp minus one hour). CSV timestamps contain an explicit +0800 offset.

EPD reports 1–10 and the 10+ category. The project encodes 10+ as 11 to retain its ordinal category. This is a project encoding and does not establish an exact continuous value. Asterisks indicate AQHI adopted from a similar station during station/equipment suspension. Missing values are exported as empty cells and read as NaN. The literal dash has no definition in the consulted specification and is treated as missing.

- [EPD dataset](https://data.gov.hk/en-data/dataset/hk-epd-airteam-past-record-of-air-quality-health-index-en)
- [EPD field specification](https://www.aqhi.gov.hk/psi/dd/hk_aqhien_en.pdf)
- [EPD AQHI scale](https://www.aqhi.gov.hk/en/what-is-aqhi/about-aqhi.html)

Official documents were consulted on 2026-11-19. Download dates in source_manifest.csv come from the project download session on 2026-11-17.

## Additional handoff files

- [Monthly quality summary](data_quality_summary.csv)
- [Training and test availability](train_test_quality_summary.csv)
- [Source manifest and SHA-256](source_manifest.csv)
- [Source spot checks with line numbers](source_spot_checks.csv)
- [Execution record and output SHA-256](data_preparation_run.json)
- [Report and presentation data text](../../docs/data_preparation.md)

In the monthly summary, duplicate_records counts extra rows beyond the first per timestamp. duplicate_timestamps counts affected timestamp keys. conflicting_timestamps counts keys with different AQHI or substitution flags. missing_hours counts absent timestamps. missing_readings counts existing rows with NaN. missing_timestamps lists missing endpoints with ISO 8601 timestamps. substituted_pct uses all hourly rows in the group as its denominator.

## Confirmation for Damon

Please confirm the existing 10+ to 11 mapping and the next-day-midnight timestamp for source hour 24 before finalizing model inputs. These rules are documented but explicit confirmation remains pending. Split counts describe cleaned readings. Final modeling sample counts depend on the six-hour-ahead target, feature availability, missing-data choices and treatment of targets across split boundaries.
