# Based on the BDATs converted to CSVs from the original game
import csv
import sys
import re

itm_beaconlist = "itm_beaconlist.csv"
multilanguage_base = "Languages/ITM_BeaconList_ms_{lng}.csv"
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

def data_probe_infobox(data_probe_id, data_probe_details, data_probe_name, lang_details):
    # Add details from collectlist
    head = "{{Infobox XCX data probe\n"
    infobox = head
    for key in data_probe_details.keys():
        toWrite = data_probe_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            infobox += "|" + key + "=" + toWrite + "\n"
        elif key == "Name":
            infobox += "|" + key + "=" + data_probe_name + "\n"
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

def summary(data_probe_name, data_probe_details):
    # Describe the summary of the data probe.
    return "The '''{name}''' is a [[Data Probe]] in ''[[Xenoblade Chronicles X]]''.".format(name=data_probe_name)

def sources(data_probe_id):
    # Describe the source template
    return "{{{{XCX data probe sources\n|{id}\n|manualentry=\n}}}}".format(id=data_probe_id)

def other_languages(language_detail_list, dp_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_amrname = language_detail_list[i][dp_linenumber]["name"]
        if languages[i] == "jp":
            lng_amrname = "{{ja|" + lng_amrname + "|}}"
        language_box += "|" + languages[i] + " = " + lng_amrname + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

# Init all dictionaries
collect_dict = csv_to_dict(itm_beaconlist)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("data_probes/result.txt","w", encoding="utf-8") as outputFile:
    for data_probe_id_int in range(1,40):
        data_probe_id = str(data_probe_id_int)
        data_probe_details = get_details_by_ID(collect_dict, data_probe_id)
        data_probe_name_id = data_probe_details['Name']
        data_probe_name = get_details_by_ID(language_detail_list[0], data_probe_name_id)['name']
        print(data_probe_id_int)
        print(data_probe_name)
        article_title = data_probe_name

        print(data_probe_name_id)

        # Populate the page.
        infobox_data_probe = data_probe_infobox(data_probe_id, data_probe_details, data_probe_name, language_detail_list[0])

        fullText = infobox_data_probe + "\n\n"

        fullText += summary(data_probe_name, data_probe_details) + "\n\n"

        # SECTION FOR SOURCES 
        sources_delimiter = "==Sources==\n"
        fullText += sources_delimiter

        # Use template for this.
        fullText += sources(data_probe_id) + "\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        dp_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == data_probe_name_id:
                dp_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, dp_linenumber) + "\n"
        fullText += "\n"

        # SECTION FOR GALLERY
        gallery_delimiter = "==Gallery==\n"
        image_needed = "{{image needed}}";
        fullText += gallery_delimiter + image_needed + "\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
