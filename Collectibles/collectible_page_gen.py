# Based on the BDATs converted to CSVs from the original game
import csv
import sys
import re

itm_collectlist = "itm_collectlist.csv"
reward_table = "collepediareward.csv" # Lists the drop table
fld_questcollect = "fld_questcollect.csv"
multilanguage_base = "Languages/ITM_CollectList_ms_{lng}.csv"
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

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

def caption_scrub(caption):
    return caption.replace("[ST:n ]", " ").replace("\\\"", "\"")

def collectible_infobox(collectible_id, collectible_details, collectible_name, lang_details):
    # Add details from collectlist
    head = "{{Infobox XCX collectible\n"
    infobox = head
    for key in collectible_details.keys():
        toWrite = collectible_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"
        elif key == "Name":
            infobox += "|" + key + "=" + collectible_name + "\n"
        elif key == "Caption":
            if int(toWrite) != 0:
                infobox += "|" + key + "=" + caption_scrub(get_details_by_ID(lang_details, int(toWrite))["name"]) + "\n"
            else:
                infobox += "|" + key + "=" + "\n"
        else:
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"

    tail = "}}"
    infobox += tail

    print(infobox)
    return infobox

def summary(collectible_name, collectible_details):
    # Describe the summary of the collectible.
    zoneID = int(collectible_details["zoneID"])
    region = "unknown"
    match zoneID:
        case 2:
            region = "Primordia"
        case 4:
            region = "Noctilum"
        case 5:
            region = "Oblivia"
        case 6:
            region = "Cauldros"
        case 7:
            region = "Sylvalum"

    return "'''{name}''' is a {{{{XCX|collectible}}}} in ''[[Xenoblade Chronicles X]]'' found in [[{region}]].".format(name=collectible_name, region=region)

def sources(collectible_id):
    # Describe the source template
    return "{{{{XCX collectible sources\n|{id}\n|manualentry=\n}}}}".format(id=collectible_id)

def uses(collectible_id):
    # Describe the uses template
    return "{{{{XCX collectible uses\n|{id}\n|manualentry=\n}}}}".format(id=collectible_id)

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

def navbox(collectible_details):
    # Describe the summary of the collectible.
    zoneID = int(collectible_details["zoneID"])
    region = "unknown"
    match zoneID:
        case 2:
            region = "Primordia"
        case 4:
            region = "Noctilum"
        case 5:
            region = "Oblivia"
        case 6:
            region = "Cauldros"
        case 7:
            region = "Sylvalum"

    return "{{{{XCX {region} Collectopedia}}}}".format(region=region)

# Init all dictionaries
collect_dict = csv_to_dict(itm_collectlist, ["ItemInfo", "Hanger"])
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("Collectibles/result.txt","w", encoding="utf-8") as outputFile:
    # for collectible_id_int in range(1, 941):
    for collectible_id_int in range(1,301):
        collectible_id = str(collectible_id_int)
        collectible_details = get_details_by_ID(collect_dict, collectible_id)
        collectible_name_id = collectible_details['Name']
        collectible_name = get_details_by_ID(language_detail_list[0], collectible_name_id)['name']
        print(collectible_id_int)
        print(collectible_name)
        article_title = collectible_name
        #if collectible_name.startswith("AMR_"):
        #    print("unused collectible "+str(collectible_id)+", skipping")
        #    continue

        print(collectible_name_id)

        # Populate the page.
        infobox_collectible = collectible_infobox(collectible_id, collectible_details, collectible_name, language_detail_list[0])

        fullText = infobox_collectible + "\n\n"

        fullText += summary(collectible_name, collectible_details) + "\n\n"

        # SECTION FOR SOURCES 
        sources_delimiter = "==Sources==\n"
        fullText += sources_delimiter

        # Use template for this.
        fullText += sources(collectible_id) + "\n\n"

        # SECTION FOR USES 
        sources_delimiter = "==Uses==\n"
        fullText += sources_delimiter

        # Use template for this.
        fullText += uses(collectible_id) + "\n\n"


        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        clb_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == collectible_name_id:
                clb_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, clb_linenumber) + "\n"
        fullText += "\n"

        # infobox
        fullText += navbox(collectible_details) + "\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
