# AoE4 Overlay
 
* **[DOWNLOAD HERE](https://github.com/FluffyMaguro/AoE4_Overlay/releases/download/1.0.1/AoE4_Overlay.zip)** (Windows)
* Or run the script with Python 3.6+ (Windows/Mac/Linux)

![Screenshot](https://i.imgur.com/eN2zJ3c.jpg)

**Use cases:**

1. Showing information about your opponents and teammates while you play
2. Personal statistics
3. Separate overlay for streaming (as html, very customizable via CSS/JS).
4. Information about players that are streaming and don't have any overlay

API calls are done through [AoEIV.net](https://aoeiv.net/). For questions and issues visit my [discord server](https://discord.gg/FtGdhqD).

# Screenshots

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

Built-in randomizer:

![Screenshot](https://i.imgur.com/tV4dMfi.png)

# Streaming
To use the custom streaming overlay simply drag the `overlay.html` file to OBS or other streaming software. The file is located in `src/html` directory in the app folder. Move and rescale as necessary once some game information is shown.

![Screenshot](https://i.imgur.com/BK9AC6h.png)

If drag & drop doesn't work, add new source to your scene. The source will be type of `Browser` and point to a local file of `overlay.html`.

Overlay active:

![Screenshot](https://i.imgur.com/gNbxJBY.png)

* Streaming overlay supports team games as well
* The streaming overlay can be fully customized with CSS and JS, see the next section.
* The override tab can be used to change the information on the overlay. This might be useful when casting from replays or changing a player's barcode to their actual name.

![Screenshot](https://i.imgur.com/f1OGmyz.png)

Or change values to something completely different

![Screenshot](https://i.imgur.com/02YsXdI.png)

# Customization

1. Overlay position and font size can be changed in the app.
2. To change team colors navigate to the config file (`File/Config`). In the `config.json` change team_colors. Colors are stored as a list of RGBA colors for team 1, 2, and so on.

```json
"team_colors": [
    [74, 255, 2, 0.35],
    [3, 179, 255, 0.35],
    [255, 0, 0, 0.35]
  ]
```

3. Streaming overlay customization can be done via `custom.css` and `custom.js` in the `html` folder in app directory. These files will not be overridden with an app update. Look at `main.css` to see what you can change. In `custom.js` you can define this function that runs after each update.

```javascript
function custom_func(data) {
    console.log("These are all the player data:", data);
}
```

# Changelog & releases

[Here](https://github.com/FluffyMaguro/AoE4_Overlay/releases)