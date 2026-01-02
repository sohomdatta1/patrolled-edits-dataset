#!/usr/bin/python
# -*- coding: UTF-8 -*-
# licensed under CC-Zero: https://creativecommons.org/publicdomain/zero/1.0

from os.path import expanduser
from time import strftime

import mariadb
import json

db = mariadb.connect(
        host='frwiki.analytics.db.svc.wikimedia.cloud',
        database='frwiki_p',
        default_file=f'{expanduser("~")}/replica.my.cnf'
    )

def get_all_rc():
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT
            rc.rc_id,
            rc.rc_this_oldid,
            rc.rc_patrolled,
            MAX(ct.ct_tag_id = 174) IS TRUE AS reverted, # 174 is mw-reverted
            rc.rc_namespace
        FROM recentchanges rc
        LEFT JOIN change_tag ct
            ON rc.rc_id = ct.ct_rc_id
        WHERE rc.rc_source = 'mw.edit'
        GROUP BY rc.rc_id, rc.rc_patrolled
        """
    )
    return cursor.fetchall()


def find_patrol_in_log_for_edit(oldid):
    # log_params looks like a:3:{s:8:"4::curid";s:9:"";s:9:"5::previd";s:9:"221673096";s:7:"6::auto";i:0;}
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT l.log_id, l.log_params
        FROM logging l
        WHERE l.log_type = 'patrol'
            AND l.log_action = 'patrol'
            AND l.log_params LIKE CONCAT('%::curid";s:9:"', ?, '";%')
            AND l.log_timestamp >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 35 DAY), '%Y%m%d%H%i%S')
        LIMIT 1
        """,
        (oldid,)
    )
    return cursor.fetchone()

def main():
    all_rc = get_all_rc()
    total = len(all_rc)
    print(f"Total recent changes to process: {total}")

    data = []

    for index, (rc_id, rc_this_oldid, rc_patrolled, reverted, rc_namespace) in enumerate(all_rc, start=1):
        if rc_patrolled == 0 or rc_patrolled == 2:
            log_data = None
        else:
            log_data = find_patrol_in_log_for_edit(rc_this_oldid)
        data.append({
            'rc_id': rc_id,
            'rc_this_oldid': rc_this_oldid,
            'rc_namespace': rc_namespace,
            'rc_patrolled': rc_patrolled,
            'reverted': reverted,
            'has_patrol_log': log_data is not None,
            'log_id': log_data[0] if log_data else None,
            'log_params': (log_data[1].decode('utf-8')) if log_data else None,
        })

        if index % 1000 == 0 or index == total:
            print(f"[{strftime('%Y-%m-%d %H:%M:%S')}] Processed {index}/{total} recent changes")
    
    with open('patrol_log_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == '__main__':
    main()