# Copy the files below from https://xenobladedata.github.io/xbx/bdat/index.html
# Then paste them into an Excel or other spreadsheet editor 
# Delete the "Referenced By" column and the "Return to BDAT index" row and then save as CSV

import csv
import sys

blh_figurelist = "BLH_FigureList.csv"
holofigure_drop_detailss = "DRP_ItemTable.csv"
itm_figlist = "ITM_FigList.csv"
multilanguage_base = "Languages/ITM_FigList_ms_{lng}.csv"
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
    return caption.replace("[ST:n ]", " ").replace("\\\"", "\"").replace("BLADE barracks", "[[BLADE barracks]]")
def holofigure_infobox(figure_details, figure_blh, drop_details, lang_details):
    head = "{{Infobox XCX holofigure\n"
    infobox = head
    for key in figure_details.keys():
        toWrite = figure_details[key]
        if key == "Name":
            infobox += "|" + key + "=" + get_details_by_ID(lang_details, int(toWrite))["name"] + "\n"
        elif key == "Caption":
            if int(toWrite) != 0:
                infobox += "|" + key + "=" + caption_scrub(get_details_by_ID(lang_details, int(toWrite))["name"]) + "\n"
            else:
                infobox += "|" + key + "=" + "\n"
        else:
        	infobox += "|" + key + "=" + toWrite + "\n"

    infobox += "\n"
    for key in figure_blh.keys():
        if key != "ID" and key != "Name":
            infobox += "|" + key + " = " + figure_blh[key] + "\n"

    if drop_details != None:
        infobox += "\n"
        infobox += "|DRP_ID = " + drop_details["ID"] + "\n"

    tail = "}}"
    infobox += tail
    return infobox

def summary(holofigure_name):
    return "'''" + holofigure_name + "''' is a [[Holofigure]] in ''[[Xenoblade Chronicles X]]''."

def sources(normal_id, drop_details):
    if drop_details != None:
        return "{{XCX holofigure sources|" + normal_id + "|" + drop_details["ID"] + "}}"
    else:
        return "{{XCX holofigure sources|" + normal_id + "}}"

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

# Init all dictionaries
blh_dict = csv_to_dict(blh_figurelist)
drop_detailss = csv_to_dict(holofigure_drop_detailss)
fig_dict = csv_to_dict(itm_figlist)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("holofigures/result.txt","w", encoding="utf-8") as outputFile:
    # for holofigure_id_int in range(1, 941):
    for holofigure_id_int in range(1,500):
        holofigure_id = str(holofigure_id_int)
        holofigure_details = get_details_by_ID(fig_dict, holofigure_id)
        holofigure_name_id = holofigure_details['Name']
        holofigure_name = get_details_by_ID(language_detail_list[0], holofigure_name_id)['name']

        blh_figdetails = get_details_by_ID(blh_dict, holofigure_id)
        drop_details = next((q for q in drop_detailss if int(q["ItemID"]) == holofigure_id_int and int(q["ItemType"]) == 64), None)

        print(holofigure_id_int)
        print(holofigure_name)
        article_title = holofigure_name
        if holofigure_name.startswith("ITM_"):
            print("unused holofigure "+str(holofigure_id)+", skipping")
            continue

        for_text = ""
        if holofigure_name.endswith("Series"):
            article_title = article_title + " (holofigure)"
            for_text ="{{for|the holofigure|the weapon series|"+ holofigure_name + "}}\n"

        # Other disambiguations needed due to shared name
        if holofigure_name in ["Legendary Nopopopopon", "White Whale", "The Blood Lobster", "Sword of Legendaryness", "Factory 1.21"]:
            article_title = article_title + " (holofigure)"

        print(holofigure_name_id)

        # Populate the page.
        infobox_holofigure = holofigure_infobox(holofigure_details, blh_figdetails, drop_details, language_detail_list[0])

        fullText = infobox_holofigure + "\n\n"

        # For text at beginning
        fullText += for_text
        fullText += summary(holofigure_name) + "\n\n"

        # SECTION FOR SOURCES 
        sources_delimiter = "==Sources==\n"
        fullText += sources_delimiter

        # Use template for this.
        fullText += sources(holofigure_id, drop_details) + "\n\n"

        # SECTION FOR OTHER LANGUAGES
        other_languages_delimiter = "==In other languages==\n"

        clb_linenumber = 0
        for i in range(len(language_detail_list[0])):
            if language_detail_list[0][i]["ID"] == holofigure_name_id:
                clb_linenumber = i
                print(i)

        fullText += other_languages_delimiter

        fullText += other_languages(language_detail_list, clb_linenumber) + "\n"
        fullText += "\n"

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
