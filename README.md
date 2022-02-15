# AoE4 Overlay
 
* **[DOWNLOAD HERE](https://github.com/FluffyMaguro/AoE4_Overlay/releases/download/1.2.5/AoE4_Overlay.zip)** (Windows)
* Or run the script with Python 3.6+ (Windows/Mac/Linux)

![Screenshot](https://i.imgur.com/eN2zJ3c.jpg)

# What does the app do?
* Shows information about players you are in match with
* Provides additional player statistics in-app
* Shows an overlay widget for buildorders
* Supports a highly customizable streaming overlay (with CSS/JS).

API calls are done through [AoEIV.net](https://aoeiv.net/) and [AoE4World.com](https://aoe4world.com/). For questions and issues visit my [discord server](https://discord.gg/FtGdhqD).

# How to use

* Download and extract the archive
* Run `AoE4_Overlay.exe`
* Find your profile by entering your profile_id, steam_id or player name
* Set up the hotkey for showing/hiding overlay
  * Overlay will be automatically shown when a new game starts (or app starts)
* Build orders:
  * Add new build orders
  * Set up hotkeys for showing/hiding overlay and cycling between build orders
  * Use hotkeys to show/hide/cycle build orders 


*To update the app delete the app folder and extract the new archive elsewhere.*


# Screenshots

Build order widget:

![Screenshot](https://i.imgur.com/SnR3p7d.png)

Additional civilization stats (currently only for 1v1):

Wintime is the median game length of won games with given civilization (indicates in what game phase the player is the strongest).

![Screenshot](https://i.imgur.com/cpeq8ob.png)

Settings:

![Screenshot](https://i.imgur.com/hhH8R72.png)

Game history:

![Screenshot](https://i.imgur.com/L1V1wp2.png)

Rating history:

![Screenshot](https://i.imgur.com/QqojOJI.png)

Last 24 hours:

![Screenshot](https://i.imgur.com/8ODqTrw.png)

Various stats:

![Screenshot](https://i.imgur.com/aGXRnT2.png)

Build order tab:

![Screenshot](https://i.imgur.com/zuAdlX6.png)

Built-in randomizer:

![Screenshot](https://i.imgur.com/tV4dMfi.png)

# Streaming
To use the custom streaming overlay simply drag the `overlay.html` file to OBS or other streaming software. The file is located in `src/html` directory in the app folder. Move and rescale as necessary once some game information is shown.

![Screenshot](https://i.imgur.com/BK9AC6h.png)

If drag & drop doesn't work, add new source to your scene manually. The source type will be `Browser` and point to a local file `overlay.html`.

Overlay active:

![Screenshot](https://i.imgur.com/gNbxJBY.png)

* Streaming overlay supports team games as well
* The streaming overlay can be fully customized with CSS and JS, see the next section.
* The override tab can be used to change the information on the overlay. This might be useful when casting from replays or changing a player's barcode to their actual name.

![Screenshot](https://i.imgur.com/f1OGmyz.png)

Or change values to something completely different

![Screenshot](https://i.imgur.com/02YsXdI.png)

# Customization

1. **Overlay position and font size** can be changed in the app.

2. **Build order** font and position can be changed in the app. 
   Other attributres can be also customized in `config.json` (to find the file click `File/config & logs` in the app). You have to close the app before making changes to the config file. What can be changed:

    `"bo_bg_opacity": 0.5,` controls its background opacity (default: 0.5 = 50%; accepts values between 0 and 1)

    `"bo_showtitle": true,` sets whether build order name is visible (accepts true/false)

    `"bo_title_color": "orange",` changes the color of build order name (title), also accepts hex and rgb values as string


3. **Team colors** can be changed in the `config.json`. Colors are stored as a list of RGBA colors for team 1, 2, and so on.

    ```json
    "team_colors": [
        [74, 255, 2, 0.35],
        [3, 179, 255, 0.35],
        [255, 0, 0, 0.35]
      ]
    ```
    
4. **Civilization stats color** can be changed in `config.json`.
    ```json
    "civ_stats_color": "#BC8AEA",
    ```

5. **Streaming overlay** customization can be done via `custom.css` and `custom.js` in the `html` folder in app directory. These files will not be overridden with an app update. Look at `main.css` to see what you can change. In `custom.js` you can define this function that runs after each update.

    ```javascript
    function custom_func(data) {
        console.log("These are all the player data:", data);
    }
    ```

# Changelog & releases

[Here](https://github.com/FluffyMaguro/AoE4_Overlay/releases)