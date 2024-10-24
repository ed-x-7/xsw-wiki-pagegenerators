# Copy the files below from https://xenobladedata.github.io/xbx/bdat/index.html
# Then paste them into an Excel or other spreadsheet editor 
# Delete the "Referenced By" column and the "Return to BDAT index" row and then save as CSV

import csv
import sys

itm_preciouslist = "ITM_PreciousList.csv"
item_table = "drp_itemtable.csv" # Lists the drop table
multilanguage_base = "Languages/itm_preciouslist_ms_{lng}.csv"
languages = ["en", "jp", "fr", "de", "es", "it"]

def csv_to_dict(file_name):
    with open(file_name, encoding="utf-8-sig") as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return a

def csv_to_dict_v2(file_name, bitfield_sections = []):
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

def important_navbox(important_details):
	head = "{{Infobox XCX important item\n"
	navbox = head
	for key in important_details.keys():
		toWrite = important_details[key]
		if key == "Caption":
			toWrite = toWrite.replace("[ST:n ]", " ").replace("\\\"", "\"")
		navbox += "|" + key + " = " + toWrite + "\n"
	tail = "}}"
	navbox += tail
	return navbox

def summary(item_name):
	return "'''" + item_name + "''' is an [[Important Item]] in ''[[Xenoblade Chronicles X]]''."

def sources(ids, DRP_ID):
    item_sources = "{{XCX important item sources\n"
    for i in range(len(ids)):
        val = i+1
        key = "ID_{d}".format(d=val)
        item_sources += "|" + key + "=" + ids[i] + "\n"
    # Get the armor sources by normal Id, drop ID, and the columns.
    if DRP_ID is not None:
        item_sources += "|DRP_ID=" + DRP_ID + "\n"

    item_sources += "}}"
    return item_sources

def other_languages(language_detail_list, item_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        print(len(language_detail_list), i, item_linenumber)
        lng_amrname = language_detail_list[i][item_linenumber]["name"]
        if languages[i] == "jp":
            lng_amrname = "{{ja|" + lng_amrname + "|}}"
        language_box += "|" + languages[i] + " = " + lng_amrname + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

# Check arguments
if len(sys.argv) <= 1:
	print("Please enter the important item ID number.")
	sys.exit()

# Init all dictionaries
blh_dict = csv_to_dict(itm_preciouslist)
item_dict = csv_to_dict_v2(item_table)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict_v2, all_language_files))

# Find the proper item given the ID
itm_id = sys.argv[1]
item_details = next((q for q in blh_dict if q["ID"] == itm_id), None)

ItemID = item_details["ID"]
ItemName = item_details["Name"]

drop_details = next((q for q in item_dict if (q["ItemID"] == ItemID and q["ItemType"] in ["29"])), None)
if drop_details is not None:
    drop_id = drop_details["ID"]
    drop_itemtype = drop_details["ItemType"]
else:
    drop_id = None
    drop_itemtype = None

# Populate the page.
infobox_item = important_navbox(item_details)
print(infobox_item)

fullText = infobox_item + "\n\n"

fullText += summary(ItemName) + "\n\n"

# SECTION FOR SOURCES 
if drop_id is not None:
	sources_delimiter = "==Sources==\n"
	fullText += sources_delimiter

	fullText += sources([ItemID], drop_id) + "\n\n"

other_languages_delimiter = "==In other languages==\n"
fullText += other_languages_delimiter

item_linenumber = int(ItemID)-1
print(item_linenumber)

fullText += other_languages(language_detail_list, item_linenumber)

outputFile=open(ItemID + "-" + ItemName + ".txt","w",encoding="utf-8-sig")
outputFile.write(fullText)
outputFile.close()

print("done")
