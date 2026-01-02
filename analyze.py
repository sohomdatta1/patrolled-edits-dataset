#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# licensed under CC-Zero: https://creativecommons.org/publicdomain/zero/1.0

import json
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} patrol_log_analysis.json")
    sys.exit(1)

path = sys.argv[1]

with open(path, "r", encoding="utf-8") as f:
    rows = json.load(f)


total_count = 0
patrolled = 0
manually_patrolled = 0
patrolled_or_reverted = 0
reverted_count = 0
log_params_contains_auto = 0
reverted_but_not_patrolled = 0
patrolled_and_reverted = 0
all_has_logs = 0
manually_patrolled_with_logs = 0
manually_patrolled_without_logs = 0
automatically_patrolled_with_logs = 0
automatically_patrolled_without_logs = 0
data = []
cheque = []
for r in rows:
    if r['rc_patrolled'] == 2:
        continue

    if r['rc_namespace'] != 0:
        continue

    total_count += 1

    if r['rc_patrolled'] == 1:
        patrolled += 1

    if r['rc_patrolled'] == 1 and r['reverted'] == False:
        manually_patrolled += 1
        cheque.append(r)

    if r['rc_patrolled'] == 1 and r['reverted'] == False and r['has_patrol_log'] == True:
        manually_patrolled_with_logs += 1
    elif r['rc_patrolled'] == 1 and r['reverted'] == False and r['has_patrol_log'] == False:
        manually_patrolled_without_logs += 1
    
    if r['rc_patrolled'] == 1 and r['reverted'] == True and r['has_patrol_log'] == True:
        automatically_patrolled_with_logs += 1
    elif r['rc_patrolled'] == 1 and r['reverted'] == True and r['has_patrol_log'] == False:
        automatically_patrolled_without_logs += 1

    if r['rc_patrolled'] == 1 and r['reverted'] == False and r['has_patrol_log'] == False:
        data.append(r)

    if r['rc_patrolled'] == 0 and r['reverted'] == True:
        reverted_but_not_patrolled += 1

    if r['rc_patrolled'] == 1 and r['reverted'] == True:
        patrolled_and_reverted += 1

    if r['reverted'] == True:
        reverted_count += 1

    if (r['reverted'] == True or r['rc_patrolled'] == 1):
        patrolled_or_reverted += 1

    if r['log_params'] is not None and 'auto' in r['log_params']:
        log_params_contains_auto += 1

    if r['has_patrol_log'] == True:
        all_has_logs += 1


print('Patrolled or reverted %:\t\t\t', f"{(patrolled_or_reverted/total_count) * 100:.2f}%")
print('All patrolled %:\t\t\t\t', f"{(patrolled/total_count) * 100:.2f}%")
print('- Patrolled but not reverted %:\t\t\t', f"{(manually_patrolled/total_count) * 100:.2f}%")
print("- -  Patrolled but not reverted with logs %:\t", f"{(manually_patrolled_with_logs/total_count) * 100:.2f}%")
print("- -  Patrolled but not reverted without logs %:\t", f"{(manually_patrolled_without_logs/total_count) * 100:.2f}%")
print('- Patrolled but reverted %:\t\t\t', f"{(patrolled_and_reverted/total_count) * 100:.2f}%")
print("- -  Patrolled but reverted with logs %:\t", f"{(automatically_patrolled_with_logs/total_count) * 100:.2f}%")
print("- -  Patrolled but reverted without logs %:\t", f"{(automatically_patrolled_without_logs/total_count) * 100:.2f}%")
print('- All patrols with patrol logs %:\t\t', f"{(all_has_logs/total_count) * 100:.2f}%")
print('Reverted %:\t\t\t\t\t', f"{(reverted_count/total_count) * 100:.2f}%")
print('- Reverted and patrolled %:\t\t\t', f"{(patrolled_and_reverted/total_count) * 100:.2f}%")
print('- Reverted but not patrolled %:\t\t\t', f"{(reverted_but_not_patrolled/total_count) * 100:.2f}%")
print('- Total count (non-AP + mainspace):\t\t', total_count, 'edits')
print('No logs, not reverted, but patrolled:\t\t', len(data[1]), 'edits')
#print('Sample data:', cheque[1:6])
