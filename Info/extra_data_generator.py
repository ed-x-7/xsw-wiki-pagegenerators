# Copy the files below from https://xenobladedata.github.io/xbx/bdat/index.html
# Then paste them into an Excel or other spreadsheet editor 
# Delete the "Referenced By" column and the "Return to BDAT index" row and then save as CSV

import csv
import sys

itm_preciouslist = "ITM_InfoList_DE.csv"
multilanguage_base = "Languages/itm_infolist_ms_{lng}.csv"
languages = ["en", "jp", "fr", "de", "es", "it", "zh-tr", "zh-si", "ko"]

def csv_to_dict(file_name, bitfield_sections = []):
    a = []
    with open(file_name, encoding="utf-8-sig") as f:
        row_num = 1
        for row in csv.DictReader(f, skipinitialspace=True):
            bitfields = {}
            new_row = { "ID": str(row_num) }
            for k, v in row.items():
                col_name = k[:-4] # Removing the " {2}" section
                field_start = col_name.split()[0]
                if field_start in bitfield_sections:
                    if field_start not in bitfields:
                        bitfields[field_start] = 0
                    bitfields[field_start] *= 2
                    bitfields[field_start] += int(v)
                else:
                    new_row[col_name] = v
            for k2, v2 in bitfields.items():
                new_row[k2] = str(v2)
            a.append(new_row)
            row_num = row_num + 1
    return a

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

def caption_scrub(caption):
    return caption.replace("[ST:n ]", " ").replace("\\\"", "\"").replace("\n", " ").replace("  ", " ")

def filter_hash(filter_str):
    return filter_str.replace("<", "").replace(">", "")

def info_infobox(important_details, lang_details):
    head = "{{XCX info\n"
    infobox = head
    for key in important_details.keys():
        toWrite = important_details[key]
        if key == "hashID":
            infobox += "|" + key + "=" + filter_hash(toWrite) + "\n"
        elif key == "Name":
            infobox += "|" + key + "=" + get_details_by_ID(lang_details, int(toWrite))["name"] + "\n"
        elif key == "Caption":
            if int(toWrite) != 0:
                infobox += "|" + key + "=" + caption_scrub(get_details_by_ID(lang_details, int(toWrite))["name"]) + "\n"
            else:
                infobox += "|" + key + "=" + "\n"
        else:
            infobox += "|" + key + " = " + toWrite + "\n"
    tail = "}}"
    infobox += tail
    return infobox

def other_languages(language_detail_list, item_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_amrname = get_details_by_ID(language_detail_list[i], item_linenumber)['name']
        if languages[i] == "jp":
            lng_amrname = "{{ja|" + lng_amrname + "|}}"
        if languages[i] == "zh-si" or languages[i] == "zh-tr":
            lng_amrname = "{{zh|" + lng_amrname + "|}}"
        if languages[i] == "ko":
            lng_amrname = "{{ko|" + lng_amrname + "|}}"
        language_box += "|" + languages[i] + " = " + lng_amrname + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

# Init all dictionaries
blh_dict = csv_to_dict(itm_preciouslist)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("info/extra_data.txt","w", encoding="utf-8") as outputFile:
    for itm_id_int in range(1,584):

        # Find the proper item given the ID
        itm_id = str(itm_id_int)
        item_details = next((q for q in blh_dict if q["ID"] == itm_id), None)

        ItemID = item_details["ID"]
        ItemName_id = item_details["Name"]

        if (int(ItemName_id) == 0):
            continue

        extra_base = "Extra data:Info (XCX)/{id}"

        info_name = extra_base.format(id=itm_id_int)

        if (info_name == ""):
            continue

        # Populate the page.
        fullText = info_infobox(item_details, language_detail_list[0])

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+info_name+"'''\n")
        outputFile.write(fullText)
        outputFile.write("\n{{-stop-}}\n")

print("done")
