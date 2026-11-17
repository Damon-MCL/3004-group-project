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
