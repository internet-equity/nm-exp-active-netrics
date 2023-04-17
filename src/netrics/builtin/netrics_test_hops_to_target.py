from .. utils import popen_exec
import logging

log = logging.getLogger(__name__)


def test_hops_to_target(key, measurement, args, results, quiet):
    """
    Method counts the number of hops to the target site
    """

    tr_res = None
    error_found = False

    labels = args["labels"]
    conf = args["conf"]
    targets = ['www.google.com']

    if 'targets' in conf['hops_to_target']:
        targets = conf['hops_to_target']['targets']

    tr_res = {}
    for target in targets:
        try:
            label = labels[target]
        except KeyError:
            label = target

        tr_cmd = f'traceroute -m 20 -q 5 -w 2 {target} | tail -1 | awk "{{print $1}}"'
        tr_res[label], err = popen_exec(tr_cmd)
        if len(err) > 0:
            print(f"ERROR: {err}")
            log.error(err)
            results[key][f'{label}_error'] = f'{err}'
            #TODO: save the output regardless?
            #tr_res[label] = { f'{label}': tr_res[label], 'error' : f'{err}' }
            tr_res[label] = { 'error' : f'{err}' }
            error_found = True
            continue

        tr_res_s = tr_res
        tr_res_s = tr_res_s[label].strip().split(" ")

        hops = -1

        if len(tr_res_s):
            hops = int(tr_res_s[0])

        results[key][f'hops_to_{label}'] = hops

    results[key]["error"] = error_found

    if not quiet:
        print('\n --- Hops to Target ---')
        for target in targets:
            try:
                label = labels[target]
            except KeyError:
                label = target
            if f'{label}_error' in results[key]:
                print("Hops to {}: {}".format(target,
                                        results[key][f'{label}_error']))
            else:
                print("Hops to {}: {}".format(target,
                                        results[key][f'hops_to_{label}']))

    return tr_res