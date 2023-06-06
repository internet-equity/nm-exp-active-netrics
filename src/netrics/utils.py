from subprocess import Popen, PIPE

def popen_exec(cmd):
    pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out = pipe.stdout.read().decode('utf-8')
    err = pipe.stderr.read().decode('utf-8')
    return out, err

