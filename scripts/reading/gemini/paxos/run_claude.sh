#!/bin/zsh
S=${0:A:h}; O=${S:h:h:h:h}/docs/research/읽기엔진시험_2026-10-09/gemini/paxos
cd ${O:h:h}/png/gemini/paxos  # claude가 그림을 읽는 곳
for n in pyusd_2023-08_p4 usdg_2025-01_p4; do
  s=$(date +%s)
  claude -p "$(cat $S/prompt_paxos_page_v1.md)
Image file: ${n}.png" --model claude-opus-5-5 --effort max --output-format json --allowedTools Read < /dev/null > $O/claude_opus_$n.json 2> $O/claude_$n.err
  echo "$n $(( $(date +%s)-s ))s" >> $O/claude_times.txt
done
echo ALL DONE >> $O/claude_times.txt
