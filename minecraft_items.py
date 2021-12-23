from bs4 import BeautifulSoup
from dataclasses import dataclass
from multiprocessing import Pool
import os
import requests
import shutil
import sys

DIG_MINECRAFT_WEBSITE = "https://www.digminecraft.com"

@dataclass
class MinecraftItem:
    name: str
    id_name: str
    id: int
    data_value: int
    image_src: str
    image_path: str


def remove_substrings(string, substrings):
    string = str(string)
    for substring in substrings:
        string = string.replace(substring, "")
    return string

def create_model():
    item_list_source = requests.get(DIG_MINECRAFT_WEBSITE + "/lists/item_id_list_pc_1_8.php")
    item_list_soup = BeautifulSoup(item_list_source.text, "html.parser")

    # The first line is ignored as that is the column header
    item_list = item_list_soup.table.find_all('tr')[1:]

    model = []
    for item_html in item_list:
        # Each item_html looks like the following
        # <tr>
        #     <td><img class="img-rounded b-lazy" src="/images/loading_50x50.svg" data-src="/basic_recipes/images/oak_fence_gate.png" alt="oak fence gate" width="50" height="50"></td>
        #     <td><a href="/basic_recipes/make_oak_fence_gate.php">Oak Fence Gate</a><br>(<em>minecraft:<wbr>fence_<wbr>gate</em>)</td>
        #     <td>107</td>
        #     <td>0</td>
        # </tr>
        image_html, href_html, id_html, data_value_html = item_html.find_all("td")
        image_src = str(image_html.img["data-src"])
        image_alt_text = str(image_html.img["alt"])
        
        # Some don't have a hyperlink associated with them. This accounts for this
        # by reading the item name from a different spot for the line.
        if href_html.a is not None:
            item_name = str(href_html.a.string)
        else:
            item_name = str(href_html.next_element)
        
        # A quick sanity check to show that the alt text can be derived from the
        # item's name
        assert(item_name.lower() == image_alt_text)

        # Removes any extra html tags that are included in the original text
        id_name = remove_substrings(href_html.contents[-2], ["<em>", "</em>", "<wbr>", "<wbr/>"])
        
        # Some entries don't have an id, thus are not real items. eg, flowing lava.
        # We can ignore these rows if the conversion fails.
        try:
            id = int(id_html.string)
        except ValueError:
            continue
        data_value = int(data_value_html.string)

        # Includes the minecraft_id_name in the file name as some blocks have the
        # same name as items (eg. Melons). Ensures that items that actually share
        # the same png are represented correctly.
        id_name_short = id_name.split(":")[1]
        clean_image_src = id_name_short + " " + image_src.split("/")[-1]

        # Generates the entry based on the information gathered
        model_item = MinecraftItem(item_name, id_name, id, data_value, image_src, clean_image_src)
        model.append(model_item)
    
    return model

def scrape_one_item_image(item, folder_name):
    # Only downloads the image if it doesn't exist yet
    if os.path.exists(folder_name + "/" + item.image_path):
        return
    
    # Downloading images using requests module
    # https://stackoverflow.com/a/18043472
    response = requests.get(DIG_MINECRAFT_WEBSITE + item.image_src, stream=True)
    with open(folder_name + "/" + item.image_path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)
    del response

def scrape_all_item_images(model, folder_name):
    # Creates the folder if it doesn't exist yet
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    
    # Scrapes the images using multiple threads
    tasks = []
    with Pool(processes=os.cpu_count() - 1) as pool:
        for item in model:
            future = pool.apply_async(scrape_one_item_image, [item, folder_name])
            tasks.append(future)
        
        for result in tasks:
            result.get()

def save_model_as_csv(model, folder_name, csv_name):
    header = "name, id_name, id, data_value, image_path"
    with open(csv_name, "w") as f:
        f.write(header + "\n")
        for item in model:
            f.write("{}, {}, {}, {}, {}/{}\n".format(
                item.name, item.id_name, item.id,
                item.data_value, folder_name, item.image_path))

def main():
    if len(sys.argv) < 3:
        print("Usage: python minecraft_items.py <folder-to-save-images-to> <csv-file-name>")
        return
    
    model = create_model()
    
    folder_name = sys.argv[1]
    scrape_all_item_images(model, folder_name)

    csv_name = sys.argv[2]
    save_model_as_csv(model, folder_name, csv_name)


if __name__ == "__main__":
    main()
