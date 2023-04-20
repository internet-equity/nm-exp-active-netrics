from .. utils import popen_exec
import logging
import re
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

def test_goresp(key, conf, results, quiet=False):

    #read the sites from conf
    try:
        labels = conf['reference_site_dict']
        sites = conf['goresp']['targets']
    except Exception as err:
        print("config file not configured correctly for go responsiveness: ",err)
        results[key][f'error'] = f'{err}'
        log.error(err)
        return

    goresp_res = {}

    for site in sites:

        label = labels[site]
        port = site[site.find(":")+1:]
        site = site[:site.find(":")]
        goresp_cmd = f"/home/ubuntu/goresponsiveness/networkQuality --config {site} -port {port}"
        goresp_res[label], err = popen_exec(goresp_cmd)
        
        if len(err) > 0:            
            print(f"ERROR: {err}")
            results[key][label][f'error'] = f'{err}'
            log.error(err)
            continue
            
        try:
            rpm_p90 = re.search(r"RPM:\s+(\d+)\s+\(P90\)", goresp_res[label]).group(1)
            rpm_mean = re.search(r"RPM:\s+(\d+)\s+\(Double-Sided 10% Trimmed Mean\)", goresp_res[label]).group(1)
            download_speed = re.search(r"Download:\s+([\d.]+)\s+Mbps", goresp_res[label]).group(1)
            upload_speed = re.search(r"Upload:\s+([\d.]+)\s+Mbps", goresp_res[label]).group(1)
        except Exception as e:
            err = "Metrics not found in so responsiveness output"
            print(f"ERROR: {err}")
            results[key][label][f'error'] = f'{err}'
            log.error(err)            
            continue

        if not quiet:
            print("RPM (P90): {:>4}".format(rpm_p90))
            print("RPM (Double-Sided 10% Trimmed Mean): {:>4}".format(rpm_mean))
            print("Download speed: {:.3f} Mbps".format(float(download_speed)))
            print("Upload speed: {:.3f} Mbps".format(float(upload_speed)))

        results[key][f'{label}_goresp_rpm_p90'] = rpm_p90
        results[key][f'{label}_goresp_rpm_mean'] = rpm_mean
        results[key][f'{label}_goresp_download_speed'] = download_speed
        results[key][f'{label}_goresp_upload_speed'] = upload_speed

    return goresp_res


