You are transcribing one page image of a Gemini dollar (GUSD) monthly reserves report. Read the image file given below with the Read tool.

Return ONLY a JSON object, no prose, no code fence:
{"lines": [{"text": "...", "values": [left, right]}]}

Rules:
- Transcribe EVERY line of text on the page, top to bottom, exactly as printed (headings, bullets, table rows, paragraphs, signature block lines, footnotes). Merge a wrapped sentence into one entry per printed line.
- For table rows that have amounts, put the label in "text" and the amounts in "values" [left column, right column] as printed strings (keep commas, decimals, parentheses, "-" and "$" as printed). For all other lines, "values" is null.
- For the handwritten/e-signature image, add an entry {"text": "[signature image: <name you read> ]", "values": null}.
- Do not compute, sum, round, or correct anything. If something is unreadable, use null.
