# AoE4 Overlay
 
* **DOWNLOAD HERE** (Windows)
* Or run the script with Python 3.6+ (should work in Mac and Linux)

![Screenshot](https://i.imgur.com/tkgKCxL.jpg)

**Use cases:**

1. Showing information about your opponents and teammates while you play
2. Personal statistics
3. Separarate overlay for streaming (as html, very customizable via CSS/JS).
4. Information about players that are streaming and don't have any overlay

API calls are done through [AoEIV.net](https://aoeiv.net/). For question and issues visit my [discord server](https://discord.gg/FtGdhqD).


![Screenshot](https://i.imgur.com/hhH8R72.png)
![Screenshot](https://i.imgur.com/L1V1wp2.png)
![Screenshot](https://i.imgur.com/QqojOJI.png)
![Screenshot](https://i.imgur.com/aGXRnT2.png)
![Screenshot](https://i.imgur.com/tV4dMfi.png)

# Streaming

** HOW to drag overlay and rescale

Override tab can be used to change the information on the overlay. This might be useful when casting from replays or changing a player barcode to their actual name.

![Screenshot](https://i.imgur.com/F5I3AAQ.png)

# Customization

1. Overlay position and font size can be changed in the app.

2. To change team colors navigate to the config file (`File/Config`). In the `config.json` change team_colors. Colors are stored as a list of RGBA colors for team 1, 2 and so on.

```json
"team_colors": [
    [74, 255, 2, 0.35],
    [3, 179, 255, 0.35],
    [255, 0, 0, 0.35]
  ]
```

3. Streaming overlay customization can be done via `custom.css` and `custom.js` in the `html` folder in app directory. These files will not be overriden with an update.


# Changelog

[link](https://github.com/FluffyMaguro/AoE4_Overlay/blob/main/changelog.md)