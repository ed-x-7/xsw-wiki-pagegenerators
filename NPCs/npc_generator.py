# Based on the BDATs converted to CSVs from the original game

import csv
import sys
import re

npc_union = "npc_union.csv"
relatelist = "npc_relatelist_ms.csv" # Lists relations
infolist = "npc_peopleinfolist_ms.csv" # Lists occupations, bios
multilanguage_base = "Languages/npc_union_ms_{lng}.csv"
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

def npc_navbox(npc_id, npc_details, npc_name, relate_dict, info_dict):
    # Add details from npc
    head = "{{Infobox XCX NPC\n"
    navbox = head
    for key in npc_details.keys():
        toWrite = npc_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"
        elif key == "name":
            navbox += "|" + key + "=" + npc_name + "\n"
        elif key.startswith("job") or key.startswith("outline"):
            if int(toWrite) != 0:
                navbox += "|" + key + "=" + get_details_by_ID(info_dict, int(toWrite))["name"].replace("[ST:n ]", " ") + "\n"
            else:
                navbox += "|" + key + "=" + "\n"
        else:
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"

    tail = "}}"
    navbox += tail

    print(navbox)
    return navbox

def summary(npc_name, npc_details):
    species_type = int(npc_details["family"])
    species = "unknown"
    match species_type:
        case 1:
            species = "a {{XCX|human}} NPC"
        case 2:
            species = "a [[Ma-non]] NPC"
        case 3:
            species = "a [[Prone]] NPC from the [[Tree Clan]]"
        case 4:
            species = "a [[Prone]] NPC from the [[Cavern Clan]]"
        case 5:
            species = "an [[Orphean]] NPC"
        case 6:
            species = "a [[Nopon]] NPC"
        case 7:
            species = "a [[Zaruboggan]] NPC"
        case 8:
            species = "a [[Wrothian]] NPC"
        case 9:
            species = "the leader of the [[Definian]]s"
        case 10:
            species = "a B°&7k%±l (a human from a few hundred million years in the future)"
        case 11:
            species = "a [[Definian]] NPC"
        case 12:
            species = "a [[Qlurian]]"
        case 13:
            species = "a [[Gaur]] NPC"
        case 14:
            species = "an indigen NPC"
        case 15:
            species = "a xenoform NPC"
        case 16:
            species = "an NPC of unknown species"

    return "'''{name}''' is {species} in ''[[Xenoblade Chronicles X]]''.".format(name=npc_name, species=species)

def augments(drop_details, silver_augment_details, gold_augment_details): 
    augs = "{{XCX Skell npc Augments\n"
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

def other_languages(language_detail_list, wpn_linenumber, npc_name):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_npcname = language_detail_list[i][wpn_linenumber]["name"]
        if languages[i] == "jp":
            lng_npcname = "{{ja|" + lng_npcname + "|}}"
        language_box += "|" + languages[i] + " = " + lng_npcname + "\n"
        if languages[i] != "en":
            meaning = ""
            if (lng_npcname == npc_name):
                meaning = "—"
            language_box += "|" + languages[i] + " meaning = " + meaning + "\n"

    language_box += "}}"
    return language_box

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

# Init all dictionaries
npc_dict = csv_to_dict(npc_union, ["Flag"])
relate_dict = csv_to_dict(relatelist)
info_dict = csv_to_dict(infolist)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("NPCs/result.txt","w", encoding="utf-8") as outputFile:
    for npc_id_int in range(1,1418):
        npc_id = str(npc_id_int)
        npc_details = get_details_by_ID(npc_dict, npc_id)
        npc_name_id = npc_details['name']
        npc_name = get_details_by_ID(language_detail_list[0], npc_name_id)['name']
        print(npc_id_int)
        print(npc_name)
        article_title = npc_name
        if npc_name.startswith("nm_") or npc_name.startswith("?"):
            print("unused name "+str(npc_id)+", skipping")
            continue

        # Populate the page.
        infobox_npc = npc_navbox(npc_name_id, npc_details, npc_name, relate_dict, info_dict)
        #print(infobox_npc)

        fullText = infobox_npc + "\n\n"

        fullText += summary(npc_name, npc_details) + "\n\n"

        # SECTION FOR THE PARTS WE NEED FILLED IN MANUALLY
        appearance_delimiter = "==Appearance and personality==\n"
        fullText += appearance_delimiter
        fullText += "{{incomplete}}\n\n"

        story_delimiter = "==Story arc==\n"
        fullText += story_delimiter
        fullText += "{{incomplete}}\n\n"

        # SECTION FOR AFFINITY LINKS
        affinity_links_delimiter = "==Affinity links==\n"
        fullText += affinity_links_delimiter
        fullText += "{{XCX affinity links by NPC|" + npc_id + "}}\n\n"

        # SECTION FOR MISSIONS (manual now)
        mission_delimiter = "==Missions==\n"
        fullText += mission_delimiter
        fullText += "{{incomplete}}\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        wpn_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == npc_name_id:
                wpn_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, wpn_linenumber, npc_name) + "\n\n"

        # SECTION FOR GALLERY
        gallery_delimiter = "==Gallery==\n"
        fullText += gallery_delimiter
        fullText += "{{image needed}}\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
