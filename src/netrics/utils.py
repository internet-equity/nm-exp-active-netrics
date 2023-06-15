from subprocess import Popen, PIPE


def popen_exec_pipe(cmd):
    pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    return pipe

def popen_exec(cmd):
    pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out = pipe.stdout.read().decode('utf-8')
    err = pipe.stderr.read().decode('utf-8')
    return out, err

# function taken from
# https://stackoverflow.com/questions/11264005/using-a-regex-to-match-ip-addresses
def valid_ip(address):
    """
    Check if a site in self.sites is an IP address
    """
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >=0 and b<=255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False
