# Based on the BDATs converted to CSVs from the original game

import csv
import sys
import re

wpn_dllist = "wpn_dllist.csv"
item_table = "drp_itemtable.csv" # Lists the drop table
affix_table = "drp_affixtable.csv"
dlwpntable_gold = "drp_dlwpntable_gold.csv" # Contains the drop ID. Need to get the column based on drop ID.
dlwpntable_silver = "drp_dlwpntable_silver.csv" # Contains the drop ID. Need to get the column based on drop ID.
wpn_blueprint = "itm_blueprint.csv"
wpn_resource = "RSC_DlWpnList.csv"
multilanguage_base = "Languages/WPN_DlList_ms_{lng}.csv"
blueprint_name_table = "Languages/ITM_Blueprint_ms.csv"
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

def skell_weapon_navbox(all_weapon_ids, all_maker_lvs, weapon_details, rsc_details, weapon_name, drop_id, drop_itemtype):
    # Add details from weapon
    head = "{{Infobox XCX Skell weapon\n"
    navbox = head
    one_weapon = len(all_weapon_ids) == 1
    for key in weapon_details.keys():
        toWrite = weapon_details[key]
        if key == "ID":
            for i in range(len(all_weapon_ids)):
                val = i+1
                key = "ID_{d}".format(d=val)
                if one_weapon:
                    key = "ID"
                navbox += "|" + key + "=" + all_weapon_ids[i] + "\n"
        elif key == "Name":
            navbox += "|" + key + "=" + weapon_name + "\n"
        elif key == "MakerLv":
            for i in range(len(all_maker_lvs)):
                val = i+1
                key = "MakerLv_{d}".format(d=val)
                if one_weapon:
                    key = "MakerLv"
                navbox += "|" + key + "=" + all_maker_lvs[i] + "\n"
        else:
            if key.startswith("Affix["):
                index = int(key[-2]) + 1
                key = "Affix" + str(index)
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"

    navbox += "\n"
    if rsc_details != None:
        for key in rsc_details.keys():
            if key != "ID":
                navbox += "|" + key + "=" + rsc_details[key] + "\n"

    if drop_id is not None:
        navbox += "\n"
        navbox += "|DRP_ID=" + drop_id + "\n"
        navbox += "|DRP_ItemType=" + drop_itemtype + "\n"

    tail = "}}"
    navbox += tail

    print(navbox)
    return navbox

def summary(weapon_name, weapon_details):
    # Describe the summary of the weapon.

    match int(weapon_details["TypeWpn"]):
        case 1: 
            mounting = "a back-mounted"
        case 2: 
            mounting = "a shoulder-mounted"
        case 3: 
            mounting = "an arm-mounted"
        case 4: 
            mounting = "a sidearm"
        case 5: 
            mounting = "a spare"
        case _:
            mounting = "an unknown"

    if (int(weapon_details["Hanger"]) >> 3) % 2 == 0:
        SideL = True
    if (int(weapon_details["Hanger"]) >> 2) % 2 == 0:
        BackL = True

    weapon_series = weapon_name.split()[-1]

    return "'''{name}''' is {mount} [[Skell weapon]] in ''[[Xenoblade Chronicles X]]'' as part of the [[{series}]] series of weapons.".format(name=weapon_name, mount=mounting, series=weapon_series)

def augments(drop_details, silver_augment_details, gold_augment_details): 
    augs = "{{XCX Skell weapon Augments\n"
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

def weapon_table_columns(drop_id, weapon_table):
    # First iterate over the columns.
    column_set = set()
    for row in weapon_table:
        for key in row.keys():
            if row[key] == drop_id:
                column_set.add(key)

    return list(column_set)

def blueprint(blueprint_details, blueprint_names):
    bp = "{{XCX blueprint\n"
    for key in blueprint_details.keys():
        if key == "Name":
            bp_linenumber = int(blueprint_details[key])-1
            toWrite = blueprint_names[bp_linenumber]["name"]
        else:
            toWrite = blueprint_details[key]
        if toWrite == "":
            toWrite = "0"
        bp += "|" + key + "=" + toWrite + "\n"

    bp += "}}"
    return bp

def sources(all_weapon_ids, DRP_ID, all_columns, all_columns_silver):
    weapon_sources = "{{XCX Skell weapon sources\n"
    for i in range(len(all_weapon_ids)):
        val = i+1
        key = "ID_{d}".format(d=val)
        weapon_sources += "|" + key + "=" + all_weapon_ids[i] + "\n"
    # Get the weapon sources by normal Id, drop ID, and the columns.
    if DRP_ID is not None:
        weapon_sources += "|DRP_ID=" + DRP_ID + "\n"

    j = 0
    for colnum in all_columns:
        j += 1
        weapon_sources += "|weapon_col{col}={number}\n".format(col=j, number=colnum)

    for colnum in all_columns_silver:
        j += 1
        weapon_sources += "|weapon_col_silver{col}={number}\n".format(col=j, number=colnum)

    weapon_sources += "}}"
    return weapon_sources

def other_languages(language_detail_list, wpn_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_amrname = language_detail_list[i][wpn_linenumber]["name"]
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
wpn_dict = csv_to_dict(wpn_dllist, ["ItemInfo", "Hanger"])
item_dict = csv_to_dict(item_table)
affix_dict = csv_to_dict(affix_table)
weapon_columns = csv_to_dict(dlwpntable_gold)
weapon_columns_silver = csv_to_dict(dlwpntable_silver)
blueprint_dict = csv_to_dict(wpn_blueprint)
rsc_dict = csv_to_dict(wpn_resource)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
blueprint_names = csv_to_dict(blueprint_name_table)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("SkellWeapons/result.txt","w", encoding="utf-8") as outputFile:
    for weapon_id_int in [2673,2679,2754]:
        weapon_id = str(weapon_id_int)
        weapon_name_id = get_details_by_ID(wpn_dict, weapon_id)['Name']
        weapon_name = get_details_by_ID(language_detail_list[0], weapon_name_id)['name']
        print(weapon_id_int)
        print(weapon_name)
        article_title = weapon_name
        if weapon_name.startswith("WPN_"):
            print("unused weapon "+str(weapon_id)+", skipping")
            continue

        print(weapon_name_id)
        all_weapon_details = list(filter(lambda weapon: weapon["Name"] == weapon_name_id, wpn_dict))

        if weapon_name.startswith("Busted Skell Weapon"):
            # set it to the weapon id instead
            all_weapon_details = [get_details_by_ID(wpn_dict, weapon_id)]
            weapon_type = all_weapon_details[0]["TypeWpn"]
            match int(weapon_type):
                case 1: 
                    article_title += " (Back)"
                case 2: 
                    article_title += " (Shoulder)"
                case 3: 
                    article_title += " (Arm)"
                case 4: 
                    article_title += " (Sidearm)"
                case 5: 
                    article_title += " (Spare)"
                case _:
                    article_title += " (Mystery)"                    

        all_weapon_ids = [weapon['ID'] for weapon in all_weapon_details]
        all_maker_lvs = [weapon['MakerLv'] for weapon in all_weapon_details]        

        main_weapon_details = all_weapon_details[-1]

        drop_details = next((q for q in item_dict if (q["ItemID"] == main_weapon_details["ID"] and q["ItemType"] in ["15","16","17","18","19"])), None)
        if drop_details is not None:
            drop_id = drop_details["ID"]
            drop_itemtype = drop_details["ItemType"]
        else:
            drop_id = None
            drop_itemtype = None

        rsc_details = get_details_by_ID(rsc_dict, main_weapon_details["RBodyRscID"])

        # Populate the page.
        infobox_weapon = skell_weapon_navbox(all_weapon_ids, all_maker_lvs, main_weapon_details, rsc_details, weapon_name, drop_id, drop_itemtype)
        #print(infobox_weapon)

        fullText = infobox_weapon + "\n\n"

        fullText += summary(weapon_name, main_weapon_details) + "\n\n"

        # IF SECTION FOR AUGMENTS
        if drop_details is not None:
            fullText += "==Augments==\n"
            silver_details = next((q for q in affix_dict if q["ID"] == drop_details["AffixLot"]), None)
            gold_details = next((q for q in affix_dict if q["ID"] == drop_details["AffixLotGood"]), None)

            fullText += augments(drop_details, silver_details, gold_details) + "\n\n"

        # SECTION FOR SOURCES 
        sources_delimiter = "==Sources==\n"
        fullText += sources_delimiter

        # Check if has blueprints
        blueprint_details = next((q for q in blueprint_dict if q["itemID"] == main_weapon_details["ID"] and q["category"] in ["15","16","17","18","19"]), None)
         
        # Check if it is dropped by enemies, and return the columns.
        enemy_columns = []
        col_nums = []
        col_nums_silver = []
        if drop_id != None:
            enemy_columns = weapon_table_columns(drop_id, weapon_columns)
            # the result is "wpn[0], wpn[1], etc." so turn that into "1, 2"
            for c in enemy_columns:
                col_numbers = re.findall(r'\d+', c)
                col_number = int(col_numbers[0]) + 1
                col_nums.append(col_number)
            col_nums.sort()
        if drop_id != None:
            enemy_columns = weapon_table_columns(drop_id, weapon_columns_silver)
            # the result is "wpn[0], wpn[1], etc." so turn that into "1, 2"
            for c in enemy_columns:
                col_numbers = re.findall(r'\d+', c)
                col_number = int(col_numbers[0]) + 1
                col_nums_silver.append(col_number)
            col_nums_silver.sort()

        if blueprint_details == None:
            fullText += sources(all_weapon_ids, drop_id, col_nums, col_nums_silver) + "\n\n"
        else:
            # SECTION FOR BLUEPRINTS
            fullText += "This weapon needs to be developed at the [[AM Terminal]].\n\n"
            blueprint_delimiter = "==Blueprint==\n"
            fullText += blueprint_delimiter
            print(blueprint_details)
            fullText += blueprint(blueprint_details, blueprint_names) + "\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        wpn_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == weapon_name_id:
                wpn_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, wpn_linenumber) + "\n\n"

        # SECTION FOR GALLERY
        gallery_delimiter = "==Gallery==\n"
        fullText += gallery_delimiter
        fullText += "{{image needed}}\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
