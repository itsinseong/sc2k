#!/bin/zsh
# 원본(../run_safe.sh)을 gemini 폴더용으로 복사. 여유 메모리 8% 미만이 30초 이어지면 멈춘다.
S=${0:A:h}; cd ${S:h:h:h}/docs/research/읽기엔진시험_2026-10-09/gemini
caffeinate -i nice -n 15 ~/.venvs/paddleocr/bin/python $S/paddle_gemini_json.py > paddle_gemini_json.log 2>&1 &
pid=$!; low=0
while kill -0 $pid 2>/dev/null; do
  f=$(memory_pressure | awk '/free percentage/{gsub("%","",$5);print $5}')
  if [ "$f" -lt 8 ]; then low=$((low+1)); else low=0; fi
  if [ $low -ge 6 ]; then pkill -f paddle_gemini_json.py; echo "$(date +%H:%M) 메모리 여유 ${f}%가 30초 이어져 멈춤" >> times.txt; break; fi
  sleep 5
done
