# Minecraft Item Scraper

To run, first ensure you have the BeautifulSoup module:

```bash
pip install bs4
```

Then run,

```bash
python minecraft_items.py <folder-to-save-images-to> <csv-file-name>
```

This will download the images to the folder you specified, and write relevant metadata to the csv provided.

## Example Usage

```bash
python minecraft_items.py img data.csv
```

Resulting file structure:

```txt
📦MinecraftItemListWebScraper
┣ 📜minecraft_items.py
┣ 📜data.csv
┗ 📂img
  ┣ 📜acacia_door acacia_door.png
  ┣ 📜acacia_fence acacia_fence.png
  ┗ ...
```

`Data.csv`:

```txt
name, id_name, id, data_value, image_path
Acacia Door, minecraft:acacia_door, 430, 0, img/acacia_door acacia_door.png
Acacia Fence, minecraft:acacia_fence, 192, 0, img/acacia_fence acacia_fence.png
...
```
