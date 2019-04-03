# PerforceGource
Compiles Perforce Changes into a Gource Readable Log

This is just a quick Python script I hacked together in between classes

## Usage
It's a **Console application**, so using the console, type:  
`PerforceGource.exe <//DEPOTPATH> [-o <Output Path>] [-c <Captions Output Path>]`  
`-o` is the output path for the gource log (default is `Gource.log`)  
`-c` is the output path for the gource captions log (default is none)  
  
Example: `PerforceGource.exe //gamep_group01/` (this is the minumum amount of parameters)

Before using the above command, make sure Perforce is running and that you're logged in!  
  
If everything goes well, the console will look something like this:
![AllGood](https://i.imgur.com/8xDWSq9.png)
