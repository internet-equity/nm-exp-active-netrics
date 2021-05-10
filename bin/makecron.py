import argparse, toml

tomlconf = "/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml"

class keyvalue(argparse.Action):
    def __call__( self , parser, namespace,
                 values, option_string = None):
        setattr(namespace, self.dest, dict())
          
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value
  
parser = argparse.ArgumentParser()
  
parser.add_argument('-c', '--config', 
                    nargs='*', 
                    action = keyvalue,
                    help = "config as a list of key=value, eg (--config param1=value1 param2=value2)")
  
args = parser.parse_args()

c = args.config
print(c)

cron=toml.load('/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml')['cron']['netrics']
#print(cron)
for k,v in c.items():
  print(f'{k} = {v}')
  cron = cron.replace(f'{{{k}}}', v)

#print(cron)

with open("/etc/cron.d/cron-nm-exp-active-netrics", 'w') as f:
    f.write(cron)
