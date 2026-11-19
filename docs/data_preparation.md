# 資料準備交接

本文件提供報告及簡報的資料部分，統計由 [01_data.ipynb](../01_data.ipynb) 產生。最終建模輸入為 [tuen_mun_aqhi.csv](../data/processed/tuen_mun_aqhi.csv)。

## 報告文字

本研究使用香港環境保護署於 2025 年 4 月至 2026 年 6 月發布的 15 份英文每月 AQHI CSV，擷取屯門站小時資料。原始檔以 UTF-8 BOM 保留，來源月份、2026 年 11 月 17 日下載日期、官方下載網址及 SHA-256 列於 [來源清單](../data/processed/source_manifest.csv)。下載日期依本專案的下載紀錄記載。官方欄位規格及 AQHI 說明於 2026 年 11 月 19 日查閱。[環保署資料集](https://data.gov.hk/en-data/dataset/hk-epd-airteam-past-record-of-air-quality-health-index-en)

原始資料表共有 11,400 行，包括 10,944 行小時讀數及 456 行 Daily Max。清理過程排除每日最高值的彙總行，於各原始檔內補齊同一天後續 10,488 行的空白日期，保留所有小時行，並按香港時間排序。原始 hour 01 記作同日 01:00，hour 24 記作次日 00:00，因此時間覆蓋 2025-04-01 01:00 至 2026-07-01 00:00（UTC+08:00）。月度及訓練／測試統計依原始報告日歸組，計算方式是 timestamp 減一小時後取日期。這使月末 24 時留在原始月份。

清理後共有 10,944 個唯一小時，重複及缺少時段均為 0。有時間紀錄但 AQHI 缺失的共有 18 行，包括 12 個空白和 6 個字元 -。2025 年 9 月和 2026 年 6 月各有 9 個缺失讀數。這些讀數保留為 NaN，CSV 內為空欄。- 的具體官方定義未在所查閱規格中找到，本專案將其作缺失值。沒有補造讀數或插入不存在的時段。

共有 1,083 個小時採用環保署以星號標記的替代讀數，占全部時段 9.90%，占 10,926 個有效讀數 9.91%。星號被轉成 is_substituted=True，讀數本身保留。環保署說明星號表示站點或設備暫停期間採用最相近站點的 AQHI，原始檔未列替代站名稱。2026 年 6 月有 596 個替代讀數，占該月 720 個時段的 82.78%，占 711 個有效讀數的 83.83%，應交由建模成員評估替代值的影響。

環保署以 1–10 及 10+ 分級，10+ 屬 Serious 級別。交接檔以 11 保留 15 個 10+ 讀數的順序資訊。11 是專案編碼，模型使用時需保留其級別含義。這項編碼及 hour 24 的時間表示已在 PR 提出，仍待 Damon 明確確認。[環保署 AQHI 說明](https://www.aqhi.gov.hk/en/what-is-aqhi/about-aqhi.html)

| 原始報告日期範圍 | 全部時段 | 有效讀數 | 缺失讀數 | 替代讀數 | 有效屯門站本身讀數 | AQHI ≥ 7 有效讀數 |
|---|---:|---:|---:|---:|---:|---:|
| 訓練期 2025-04 至 2026-03 | 8,760 | 8,751 | 9 | 411 | 8,340 | 271 |
| 測試期 2026-04 至 2026-06 | 2,184 | 2,175 | 9 | 672 | 1,503 | 34 |

替代讀數已包含於有效讀數。訓練期時間邊界為 2025-04-01 01:00 至 2026-04-01 00:00，測試期為 2026-04-01 01:00 至 2026-07-01 00:00。這些是清理後讀數統計。Damon 需在建立 6 小時後目標時確認可用特徵、缺失值處理、跨分組目標及最終模型樣本數。

## 核驗及修訂

獨立解析路徑已核對所有 10,944 個小時的時間、AQHI 和替代標記。另記錄 93 個抽查例子，包括每月首日 01／12／24 時、月末 24 時、所有空白／-、每月首個星號及首個 10+。原件位置與結果見 [抽查表](../data/processed/source_spot_checks.csv)，完整輸出保存在 Notebook。核驗時未發現矛盾的重複紀錄。

本次補充品質統計、抽查及來源說明，已交接 CSV 的內容與 SHA-256 一致。未發生資料值或時間戳修訂。未來若規則改動，PR 應列出受影響時間戳及原因。

在專案根目錄以 Python 3 執行 python scripts/run_data_notebook.py，或在 Python kernel 執行 Notebook 全部儲存格。需要 pandas 及 Asia/Hong_Kong 時區資料，Windows 可安裝 tzdata。重跑會執行 Notebook 內的資料處理及核驗，保存輸出，將版本與來源／產物雜湊寫入 [重跑紀錄](../data/processed/data_preparation_run.json)。重跑亦檢查最終 CSV 與原交接檔一致，如規則或原件修訂使資料不同，會明確報錯供覆核。

## Presentation slide text

**Data collection and preparation**

- Collected 15 official EPD monthly CSV files covering April 2025 to June 2026 and extracted Tuen Mun hourly records.
- Retained 10,944 hourly rows after excluding 456 daily maximum summary rows.
- Recovered blank dates within each file and converted source hour 24 to midnight on the following day in Hong Kong time.
- Found no duplicate timestamps or absent hours. Kept 18 unavailable readings as missing values.
- Flagged 1,083 substitute readings, representing 9.90% of all hourly rows.
- Verified all hourly rows against the original files and documented 93 source spot checks.

**Speaker notes**

We collected fifteen monthly files directly from Hong Kong EPD and retained the original files for traceability. The cleaned dataset contains 10,944 hourly records for Tuen Mun. We distinguished absent timestamps from missing measurements. Every expected hour is present, while eighteen measurements remain missing. We retained valid substitute readings and identified them with a Boolean flag. June 2026 has a particularly high substitute share, which should be considered during modeling. The training and test periods contain 8,751 and 2,175 valid readings respectively. These are reading counts, and Damon will determine the final sample sizes after creating the six-hour-ahead target. We documented the project encoding of the 10+ category as 11 and have requested confirmation of that convention.

## Damon 確認紀錄

目前狀態為待確認。請在本次 PR 回覆是否採用現有 10+ → 11 轉換，以及 source hour 24 → 次日 00:00 的小時結束時間表示。另請確認建立六小時後目標時的分組邊界及替代讀數使用方式。此處會依實際回覆更新，沒有將已合併上一版 PR 視為對轉換細節的明確確認。

