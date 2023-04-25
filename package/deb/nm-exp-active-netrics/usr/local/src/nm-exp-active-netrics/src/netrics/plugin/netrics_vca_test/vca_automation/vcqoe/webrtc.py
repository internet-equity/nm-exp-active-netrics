"""functions for parsing a webrtc json file to summarised metrics"""

import json, csv 
import dateutil.parser
import os
import re, sys, ast
import numpy as np

key_prefixes = {'meet': 'IT01V', 'teams': 'IT01V'}

def get_active_stream(webrtc_stats, pref):
    """
    Get most active stream in webrtc

    Args:
        webrtc_stats: webrtc stats as a dict
        pref: prefix to search

    Returns:
        List of active streams
    """
    id_map = {}
    for k in webrtc_stats:
        m = re.search(f"{pref}(\d+)-", k)
        if not m:
            continue
        id1 = m.group(1)
        id_map[id1] = 1
    return list(id_map.keys())

def get_most_active(webrtc_stats, id_list, prefix):
    """
    Get most active stream in webrtc

    Args:
        webrtc_stats: webrtc stats as a dict
        prefix: prefix from key prefixes dict
        id_list: list of active streams
                
    Returns:
        returns the is of most active stream
    """
    stat_temp = f"{prefix}%s-framesPerSecond"
    valid_id_list = [x for x in id_list if stat_temp % x[1] in webrtc_stats[x[0]]['stats']]
    if len(valid_id_list) == 0:
        return ""
    sum_list = [sum(ast.literal_eval(webrtc_stats[x[0]]['stats'][stat_temp % x[1]]["values"])) for x in valid_id_list]
    index_max = np.argmax(sum_list)
    return valid_id_list[index_max]

def get_ts(dt_str):
    """
    parse date string and to date object
    """
    ts = dateutil.parser.parse(dt_str)
    return ts

def get_webrtc(filename, logger, vca_name):
    """
    Get parsed webrtc with summarised metrics

    Args:
        filename: webrtc file name
        logger: logger file object
        vca_name: name of vca conference
                
    Returns:
        returns dict of parsed webrtc metrics
    """
    if not os.path.exists(filename):
        logger.error("%s does not exist",filename)
        return dict(), False

    try:
        webrtc = json.load(open(filename))
    except:
        logger.error("failed to load webrtc file")
        return dict(),False

    if len(webrtc["PeerConnections"]) == 0:
        logger.error("No peer connections in webrtc")
        return dict(),False

    active_ids = []
    for key in webrtc["PeerConnections"]:
        webrtc_stats = webrtc["PeerConnections"][key]["stats"]
        pref = key_prefixes[vca_name]
        active_ids += [(key, x) for x in get_active_stream(webrtc_stats, pref)] # Gets a list of SSRC IDs
    
    if len(active_ids) == 0:
        print("no inbound stream")
        logger.error("no inbound stream")        
        return dict(),False

    # list of stats that are parsed
    wanted_stats = {key_prefixes[vca_name] : ["packetsReceived","bytesReceived","framesReceived"]}
    id1 = get_most_active(webrtc["PeerConnections"], active_ids, key_prefixes[vca_name])#active_ids[0]
    if len(id1) == 0:
        return dict(),False


    webrtc_stats = webrtc["PeerConnections"][id1[0]]['stats']
    id1 = id1[1]
    metrics = {}
    for stat in wanted_stats[pref]:
        stat_name = f"{pref}{id1}-{stat}" 
        
        if 'call_duration' not in metrics:
            (st_time, et_time) = (webrtc_stats[stat_name]["startTime"], webrtc_stats[stat_name]["endTime"])
        metrics['call_duration'] = (get_ts(et_time) - get_ts(st_time)).total_seconds()
        
        val_str = webrtc_stats[stat_name]["values"]
        val_list = ast.literal_eval(val_str)
        metrics[stat] = val_list[-1]
    return metrics,True

