You are transcribing one page image of a stablecoin reserve examination report (independent accountant's report page). Read the image file given below with the Read tool.

Return ONLY a JSON object, no prose, no code fence:
{"lines": ["...", "..."], "logo_text": "..." , "handwritten": ["..."]}

Rules:
- "lines": EVERY line of printed text on the page, top to bottom, exactly as printed (headings, paragraphs, firm name lines, place and date lines, page number, footer). One entry per printed line.
- "logo_text": the text shown in any logo image, exactly as it appears; null if there is no logo.
- "handwritten": the text of each handwritten or script-style signature, as you read it, one entry per signature; [] if none.
- Do not compute, correct, expand, or guess. If something is unreadable, use null.
