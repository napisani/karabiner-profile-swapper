
## karabiner profile swapper
this utility allows you to swap karabiner 
profiles based on the current foreground application
a JSON config file is used to define Mac OS X application bundle names 
to karabiner profile names

first create a new map file in the following location:
```bash
touch  ~/.config/karabiner/karabiner-profile-swap.json
```


here is an example mapping, make sure to provide a 'default'
mapping with the key 'default' for any bundle names that do not
match a specific karabiner profile. Please note that the keys of this map
must match the karabiner profile names in ~/.config/karabiner/karabiner.json
```json 
{
	"default" : "default",
	"com.googlecode.iterm2" : "terminal",
	"com.jetbrains.intellij" : "jetbrains",
	"com.jetbrains.pycharm": "jetbrains",
	"com.jetbrains.WebStorm": "jetbrains"
}
``` 

use the following commands to install the script and configure 
launchctl to start the karabiner profile swapper upon every startup
```bash
cp com.napisani.karabiner-profile-swapper.plist ~/Library/LaunchAgents/
cp karabiner-profile-switcher.py /usr/local/bin/
launchctl unload -w com.napisani.karabiner-profile-swapper.plist
launchctl load -w com.napisani.karabiner-profile-swapper.plist
launchctl start com.napisani.karabiner-profile-swapper
launchctl list | grep "com.napisani" # make sure it started without error
```

