#### 2020/11/11 Edited by Goodhat
A new directory `Tracks` is established. 
There are two new scripts:
- `generalGpxCreator.py`
  - This script can generate .gpx files that can be used repeatedly in the later experiments.
  -  The setting of parameters is directly in the script. **(TODO: Probably should have a higher level config.)**
  -  Run `python3 generalTrackCreator.py` to generate a gpx file. The file will be save in another subdirectory called `tracks`.

- `expGpxCreator.py`
  - This script extends one .gpx file into a set of .gpx files, in order to generate multiple vehicles in experiments.
  - The setting of parameters is directly in the script. **(TODO: Probably should have a higher level config.)**
  - The script will create a directory with suffix `_sets`, and save the generated files in it.
  - The script will also record the config info in `gpx_config.json` in the same directory.

**Example**:
If we generated a gpx file with `generalGpxCreator.py` called `ladder.gpx`, and then extend it by `expGpxCreator.py`, the file structure in `Tracks` will be like:

```js
Tracks                                  
├─ ladder_sets                          
│  ├─ gpx_config.json                   
│  ├─ ladder_0.gpx                      
│  ├─ ladder_1.gpx                      
│  ├─ ladder_2.gpx
│  └─  ...            
├─ tracks                               
│  └─ ladder.gpx                        
├─ coordinateToolkit.py                 
├─ expGpxCreator.py                     
└─ generalGpxCreator.py                 
```

⚠️ Note that the path parameters in the scripts are all hardcoded. Scripts will only run correctly in the directory.  