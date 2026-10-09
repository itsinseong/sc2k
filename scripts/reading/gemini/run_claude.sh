#!/bin/zsh
S=${0:A:h}; G=${S:h:h:h}/docs/research/읽기엔진시험_2026-10-09/gemini
cd ${G:h}/png/gemini  # claude가 그림을 읽는 곳
for m in 2024-10 2026-03; do
  s=$(date +%s)
  claude -p "$(cat $S/prompt_gemini_page_v1.md)
Image file: gemini_${m}_p4.png" --model claude-opus-5-5 --effort max --output-format json --allowedTools Read > $G/claude_opus_$m.json 2> $G/claude_$m.err
  echo "$m $(( $(date +%s)-s ))s" >> $G/claude_times.txt
done
echo ALL DONE >> $G/claude_times.txt
