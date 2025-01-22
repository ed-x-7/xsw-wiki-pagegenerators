# Based on the BDATs converted to CSVs from the original game

import csv
import sys
import re

amr_dllist = "amr_dllist.csv"
item_table = "drp_itemtable.csv" # Lists the drop table
affix_table = "drp_affixtable.csv"
dlarmortable_gold = "drp_dlarmortable_gold.csv" # Contains the drop ID. Need to get the column based on drop ID.
multilanguage_base = "Languages/amr_dllist_ms_{lng}.csv"
languages = ["en", "jp", "fr", "de", "es", "it"]

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

def skell_armor_navbox(all_armor_ids, all_maker_lvs, armor_details, armor_name, drop_id, drop_itemtype):
    # Add details from armor
    head = "{{Infobox XCX Skell armor\n"
    navbox = head
    one_armor = len(all_armor_ids) == 1
    for key in armor_details.keys():
        toWrite = armor_details[key]
        if key == "ID":
            for i in range(len(all_armor_ids)):
                val = i+1
                key = "ID_{d}".format(d=val)
                if one_armor:
                    key = "ID"
                navbox += "|" + key + "=" + all_armor_ids[i] + "\n"
        elif key == "Name":
            navbox += "|" + key + "=" + armor_name + "\n"
        elif key == "MakerLv":
            for i in range(len(all_maker_lvs)):
                val = i+1
                key = "MakerLv_{d}".format(d=val)
                if one_armor:
                    key = "MakerLv"
                navbox += "|" + key + "=" + all_maker_lvs[i] + "\n"
        else:
            if key.startswith("Affix["):
                index = int(key[-2]) + 1
                key = "Affix" + str(index)
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"

    if drop_id is not None:
        navbox += "\n"
        navbox += "|DRP_ID=" + drop_id + "\n"
        navbox += "|DRP_ItemType=" + drop_itemtype + "\n"

    tail = "}}"
    navbox += tail

    print(navbox)
    return navbox

def summary(armor_name, armor_details):
    # Describe which section is covered.
    mounts = ["unknown", "head", "torso", "right arm", "left arm", "legs"]
    mounting = mounts[int(armor_details["TypeAmr"])]

    weights = ["unknown", "light", "medium", "heavy"]
    weight = weights[int(armor_details["ArmLv"])]

    return "'''{name}''' is a piece of [[Skell armor]] in ''[[Xenoblade Chronicles X]]''. This {weight} armor covers the {section}.".format(name=armor_name, weight=weight, section=mounting)

def augments(drop_details, silver_augment_details, gold_augment_details): 
    augs = "{{XCX Skell armor Augments\n"
    for key in drop_details.keys():
        toWrite = drop_details[key]
        if toWrite == "":
            toWrite = "0"
        if key != "ItemID":
            augs += "|" + key + "=" + toWrite + "\n"

    if silver_augment_details:
        for key in silver_augment_details.keys():
            toWrite = silver_augment_details[key]
            if toWrite == "":
                toWrite = "0"
            if key != "ID":
                augs += "|Affix_" + key + "=" + toWrite + "\n"

    if gold_augment_details:
        for key in gold_augment_details.keys():
            toWrite = gold_augment_details[key]
            if toWrite == "":
                toWrite = "0"
            if key != "ID":
                augs += "|AffixGood_" + key + "=" + toWrite + "\n"

    augs += "}}"
    return augs

def armor_table_columns(drop_id, armor_table):
    # First iterate over the columns.
    column_set = set()
    for row in armor_table:
        for key in row.keys():
            if row[key] == drop_id:
                column_set.add(key)

    return list(column_set)

def sources(all_armor_ids, DRP_ID, all_columns):
    armor_sources = "{{XCX Skell armor sources\n"
    for i in range(len(all_armor_ids)):
        val = i+1
        key = "ID_{d}".format(d=val)
        armor_sources += "|" + key + "=" + all_armor_ids[i] + "\n"
    # Get the armor sources by normal Id, drop ID, and the columns.
    if DRP_ID is not None:
        armor_sources += "|DRP_ID=" + DRP_ID + "\n"

    j = 0
    for colnum in all_columns:
        j += 1
        armor_sources += "|armor_col{col}={number}\n".format(col=j, number=colnum)

    armor_sources += "}}"
    return armor_sources

def other_languages(language_detail_list, amr_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_amrname = language_detail_list[i][amr_linenumber]["name"]
        if languages[i] == "jp":
            lng_amrname = "{{ja|" + lng_amrname + "|_}}"
        language_box += "|" + languages[i] + " = " + lng_amrname + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

# Init all dictionaries
amr_dict = csv_to_dict(amr_dllist, ["ItemInfo", "Hanger"])
item_dict = csv_to_dict(item_table)
affix_dict = csv_to_dict(affix_table)
armor_columns = csv_to_dict(dlarmortable_gold)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("SkellArmor/result.txt","w", encoding="utf-8") as outputFile:
    for armor_id_int in range(1, 941):
        armor_id = str(armor_id_int)
        armor_name_id = get_details_by_ID(amr_dict, armor_id)['Name']
        armor_name = get_details_by_ID(language_detail_list[0], armor_name_id)['name']
        print(armor_id_int)
        print(armor_name)
        article_title = armor_name
        if armor_name.startswith("AMR_"):
            print("unused armor "+str(armor_id)+", skipping")
            continue

        print(armor_name_id)
        all_armor_details = list(filter(lambda armor: armor["Name"] == armor_name_id, amr_dict))

        # Special case for some Skydon armor which has an extra copy
        if len(all_armor_details) > 3:
            all_armor_details = all_armor_details[:3]

        all_armor_ids = [armor['ID'] for armor in all_armor_details]
        all_maker_lvs = [armor['MakerLv'] for armor in all_armor_details]        

        main_armor_details = all_armor_details[-1]

        if int(all_armor_ids[-1]) != armor_id_int:
            print("skipping, will handle later")
            continue

        drop_details = next((q for q in item_dict if (q["ItemID"] == main_armor_details["ID"] and q["ItemType"] in ["10","11","12","13","14"])), None)
        if drop_details is not None:
            drop_id = drop_details["ID"]
            drop_itemtype = drop_details["ItemType"]
        else:
            drop_id = None
            drop_itemtype = None

        # Populate the page.
        infobox_armor = skell_armor_navbox(all_armor_ids, all_maker_lvs, main_armor_details, armor_name, drop_id, drop_itemtype)
        #print(infobox_armor)

        fullText = infobox_armor + "\n\n"

        fullText += summary(armor_name, main_armor_details) + "\n\n"

        # IF SECTION FOR AUGMENTS
        if drop_details is not None:
            fullText += "==Augments==\n"
            silver_details = next((q for q in affix_dict if q["ID"] == drop_details["AffixLot"]), None)
            gold_details = next((q for q in affix_dict if q["ID"] == drop_details["AffixLotGood"]), None)

            fullText += augments(drop_details, silver_details, gold_details) + "\n\n"

        # SECTION FOR SOURCES 
        sources_delimiter = "==Sources==\n"
        fullText += sources_delimiter

        # Check if it is dropped by enemies, and return the columns.
        enemy_columns = []
        col_nums = []
        if drop_id != None:
            enemy_columns = armor_table_columns(drop_id, armor_columns)
            # the result is "amr[0], amr[1], etc." so turn that into "1, 2"
            for c in enemy_columns:
                col_numbers = re.findall(r'\d+', c)
                col_number = int(col_numbers[0]) + 1
                if col_number <= 7:
                    col_nums.append(col_number)
            col_nums.sort()

        fullText += sources(all_armor_ids, drop_id, col_nums) + "\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        amr_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == armor_name_id:
                amr_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, amr_linenumber) + "\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
