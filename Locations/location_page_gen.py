# Based on the BDATs converted to CSVs from the original game
import csv
import sys
import re

fld_location = "fld_location.csv"
fld_skiptravel = "fld_skiptravel.csv"
fnetveinlist = "fnetveinlist.csv"
multilanguage_base = "Languages/fieldnamelist_ms_{lng}.csv"
fnetveintext = "fnt_veinlist_ms.csv"
languages = ["en", "jp", "fr", "de", "es", "it"]

def csv_to_dict(file_name, bitfield_sections = [], first_row = 1):
    a = []
    with open(file_name, encoding="utf-8-sig") as f:
        row_num = first_row
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
            row_num += 1
    return a

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

def caption_scrub(caption):
    return caption.replace("[ST:n ][ST:n ]", " ").replace("[ST:n ]", " ").replace("\\\"", "\"")

def location_infobox(location_id, location_details, skiptravel_details, fnet_details, location_name, lang_details, fnet_name_details):
    # Add details from csvs
    head = "{{Infobox XCX location\n"
    infobox = head

    # Extra bits for image and caption
    infobox += "|image=\n|caption=\n\n"

    for key in location_details.keys():
        toWrite = location_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"
        elif key == "name":
            key = "internal_name"
            infobox += "|" + key + "=" + toWrite + "\n"
        elif key == "Loc_name":
            infobox += "|" + key + "=" + location_name + "\n"
        else:
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"

    infobox += "\n"
    for key in skiptravel_details.keys():
        toWrite = skiptravel_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            infobox += "|skiptravel_" + key + "=" + toWrite + "\n"
        elif key == "loc_name":
            key = "skiptravel_name"
            print(toWrite)
            infobox += "|" + key + "=" + get_details_by_ID(lang_details, int(toWrite))['name'] + "\n"
        elif key == "Loc_type":
            if toWrite == "":
                toWrite = "0"
            infobox += "|skiptravel_" + key + "=" + toWrite + "\n"
        else:
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"

    if len(fnet_details.keys()) > 0:
        infobox += "\n"
    for key in fnet_details.keys():
        toWrite = fnet_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            infobox += "|fnet_" + key + "=" + toWrite + "\n"
        elif key == "caption":
            infobox += "|fnet_" + key + "=" + caption_scrub(get_details_by_ID(fnet_name_details, int(toWrite))['name']) + "\n"
        else:
            if key.startswith("connection["):
                index = int(key[-2]) + 1
                key = "connection" + str(index)
            if key.startswith("sight["):
                index = int(key[-2]) + 1
                key = "sight" + str(index)
            if toWrite == "":
                toWrite = "0"
            infobox += "|fnet_" + key + "=" + toWrite + "\n"

    tail = "}}"
    infobox += tail

    print(infobox)
    return infobox

def summary(location_name, location_details, skiptravel_details, fnet_details):
    # Describe the summary of the location.
    loc_type = int(location_details["Loc_type"])
    prio = int(location_details["prio"])
    location_type = "unknown"
    match loc_type:
        case 1:
            location_type = "a {{XCX|landmark}}"
        case 2:
            location_type = "an [[Unexplored Territory]]"
        case 3:
            location_type = "a [[Scenic Viewpoint]]"
        case 4:
            if prio == 5:
                location_type = "a [[Base Camp]]"
            else:
                location_type = "an {{XCX|area}}"
        case 5:
            location_type = "a [[FrontierNav Site]]"

    zoneID = int(skiptravel_details["zone_id"])
    region = "unknown"
    match zoneID:
        case 1:
            region = "[[NLA Waters]]"
        case 2:
            region = "[[Primordia]]"
        case 3:
            region = "the {{XCX|Commercial District}}"
        case 4:
            region = "[[Noctilum]]"
        case 5:
            region = "[[Oblivia]]"
        case 6:
            region = "[[Cauldros]]"
        case 7:
            region = "[[Sylvalum]]"
        case 8:
            region = "[[Noctilum Waters]]"
        case 9:
            region = "[[Oblivia Waters]]"
        case 10:
            region = "the [[BLADE Barracks]]"
        case 11:
            region = "[[Cauldros Waters]]"
        case 12:
            region = "[[Sylvalum Waters]]"
        case 13:
            region = "the [[Industrial District]]"
        case 14:
            region = "the [[Ma-non Ship]]"
        case 15:
            region = "the {{XCX|Residential District}}"
        case 16:
            region = "the [[Administrative District]]"
        case 17:
            region = "the [[Lifehold Core]]"
        case 19:
            region = "[[Primordia Waters]]"

    return "'''{name}''' is {type} in ''[[Xenoblade Chronicles X]]'' located in {region}.".format(name=location_name, type=location_type, region=region)

def other_languages(language_detail_list, clb_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_amrname = language_detail_list[i][clb_linenumber]["name"]
        if languages[i] == "jp":
            lng_amrname = "{{ja|" + lng_amrname + "|}}"
        language_box += "|" + languages[i] + " = " + lng_amrname + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

def navbox(skiptravel_details):
    # Describe the summary of the location.
    zoneID = int(skiptravel_details["zone_id"])

    return "{{{{XCX places by area navbox|{zoneID}}}}}".format(zoneID=zoneID)

# Init all dictionaries
location_dict = csv_to_dict(fld_location)
skiptravel_dict = csv_to_dict(fld_skiptravel)
fnet_dict = csv_to_dict(fnetveinlist, [], 0) # Indexed at 0 unlike the rest, likely since NLA is area 0.
fnet_text = csv_to_dict(fnetveintext)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("locations/result.txt","w", encoding="utf-8") as outputFile:
    # for location_id_int in range(1, 941):
    for location_id_int in range(1,446):
        location_id = str(location_id_int)
        location_details = get_details_by_ID(location_dict, location_id)
        location_name_id = location_details['Loc_name']
        location_name = get_details_by_ID(language_detail_list[0], location_name_id)['name']
        skiptravel_id = location_details['SkipTravel_id']
        skiptravel_details = get_details_by_ID(skiptravel_dict, skiptravel_id)
        fnet_id = location_details["F_spot"]
        fnet_details = {}
        if int(fnet_id) != 0:
            fnet_details = get_details_by_ID(fnet_dict, fnet_id)
        article_title = location_name
        if article_title in ["Lifehold Core"]: # distinguish from region
            article_title += " (area)"
        if article_title in ["BLADE Barracks"]: # distinguish from region
            article_title += " (landmark)"
        if article_title in ["Cathedral", "Cleansing Spring", "Hangar"]: # distinguish from areas in other Xenoblade games
            article_title += " (XCX)"

        if location_name.startswith("camp"): # unused camps
            print("unused location "+str(location_id)+", skipping")
            continue
        if location_name.startswith("fld_"): # Case of Old Ceremonial Hollow
            print("unused location "+str(location_id)+", skipping")
            continue

        print(location_name_id)

        # Populate the page.
        infobox_location = location_infobox(location_id, location_details, skiptravel_details, fnet_details, location_name, language_detail_list[0], fnet_text)

        fullText = infobox_location + "\n\n"

        fullText += summary(location_name, location_details, skiptravel_details, fnet_details) + "\n\n"

        # SECTION FOR ENEMIES OR NPCs
        zoneID = int(skiptravel_details["zone_id"])
        if zoneID in [3, 10, 13, 14, 15, 16]:
            npc_delimiter = "==NPCs==\n"
            fullText += npc_delimiter
        else:
            enemies_delimiter = "==Enemies==\n"
            fullText += enemies_delimiter

        # Need to fill this in manually, set as incomplete.
        fullText += "{{incomplete}}\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        clb_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == location_name_id:
                clb_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, clb_linenumber) + "\n"
        fullText += "\n"

        # SECTION FOR GALLERY
        gallery_delimiter = "==Gallery==\n"
        fullText += gallery_delimiter
        fullText += "{{image needed}}\n\n"

        # SECTION FOR INFOBOX
        fullText += navbox(skiptravel_details) + "\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
