You are transcribing one page image of an RLUSD monthly examination report. Read the image file given below with the Read tool.
The page has a table of RLUSD in circulation and the reserve, by asset class, with two date columns (left = mid-month date, right = month-end date).

Return ONLY a JSON object, no prose, no code fence:
{"circulation": [left, right], "reserve_fair_value": [left, right], "rows": [{"label": "...", "values": [left, right]}]}

Rules:
- circulation = the "RLUSD in circulation" (or similar) line. reserve_fair_value = the total reserve / fair value line right below it.
- rows = every line of the table after those two lines, top to bottom, including subtotal lines, CUSIP lines (labels like 912797...) and lines whose label is blank (use "").
- Copy numbers exactly as printed, as integers in US dollars without commas. A dash "-" means 0. Parentheses mean negative.
- Do not compute, sum, round, or correct anything. If a value is unreadable, use null.
