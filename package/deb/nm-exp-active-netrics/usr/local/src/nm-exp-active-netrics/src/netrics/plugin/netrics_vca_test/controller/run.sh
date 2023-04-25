vca=$1

## Set the display
if [ -z "$DISPLAY" ]
then
      export DISPLAY=:99
fi

## replace the vca 
config_file="../vca_automation/config.toml"
sed -i "s/vca=.*/vca='$vca'/" $config_file


## run the vca call
cd ../vca_automation

python main_client.py


