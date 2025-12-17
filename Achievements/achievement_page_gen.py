import csv

namefile_name = 'MNU_Achievement_ms_WU.csv'
namefile_name_DE = 'MNU_Achievement_ms_DE.csv'
achievementmap_name = 'SCL_AchiveList_WU.csv'
achievementmap_name_DE = 'SCL_AchiveList_DE.csv'

def csv_to_dict_new(file_name, bitfield_sections = []):
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

def caption_scrub(caption):
    return caption.replace("[ST:n ]", " ").replace("\\\"", "\"")

def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if q[idx] == str(id)), None)

def csv_to_dict_old(file_name, bitfield_sections = []):
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


table_intro = "{|class=\"wikitable sortable\"\n!Name\n!Description\n!Count\n!Type\n!Notes\n|-"

story_delimiter = "==Story==\n" + table_intro
combat_delimiter = "==Combat==\n" + table_intro
world_delimiter = "==World==\n" + table_intro

story_list = story_delimiter
world_list = world_delimiter
combat_list = combat_delimiter
ach_startline = "{{XCX achievement entry\n"
ach_finalline = "}}"

achievement_dict_wiiu = csv_to_dict_old(achievementmap_name)
achievement_dict_de = csv_to_dict_new(achievementmap_name_DE)

language_file_wiiu = csv_to_dict_old(namefile_name)
language_file_de = csv_to_dict_new(namefile_name_DE)

with open("achievement_pages.txt", "w", encoding="utf-8") as outputFile:
	for ach_id in range(1,844):
		row = []
		row_DE = []
		row = get_details_by_ID(achievement_dict_wiiu, ach_id)
		entryInnards = ""
		if row != None and ach_id != 790: #790 is an exception
			# Set "Disp" to 1
			row = get_details_by_ID(achievement_dict_wiiu, ach_id)
			row_DE = get_details_by_ID(achievement_dict_de, ach_id)
			title = caption_scrub(get_details_by_ID(language_file_wiiu, row["Title"])["name"])
			if title.startswith("ACM_") or title.startswith("ACE_"):
				continue # Skipping things starting with ACM
			description = caption_scrub(get_details_by_ID(language_file_wiiu, row["Description"])["name"])
			title_DE = caption_scrub(get_details_by_ID(language_file_de, row_DE["Title"])["name"])
			description_DE = caption_scrub(get_details_by_ID(language_file_de, row_DE["Description"])["name"])
			disp = row["Disp"]
			disp_DE = row_DE["Disp"]

		else:
			# Set "Disp" for Wii U to 0
			row_DE = get_details_by_ID(achievement_dict_de, ach_id)
			row = row_DE
			title_DE = caption_scrub(get_details_by_ID(language_file_de, row_DE["Title"])["name"])
			description_DE = caption_scrub(get_details_by_ID(language_file_de, row_DE["Description"])["name"])
			if title_DE.startswith("ACM_"):
				continue # Skipping things starting with ACM
			title = title_DE
			description = description_DE
			disp = "0"
			disp_DE = row_DE["Disp"]

		entryInnards += "|ID = " + str(ach_id) + "\n"
		entryInnards += "|title = " + title + "\n"
		if (title != title_DE):
			entryInnards += "|title_DE = " + title_DE + "\n"
		entryInnards += "|description = " + description + "\n"
		if (description != description_DE):
			entryInnards += "|description_DE = " + description_DE + "\n"
		entryInnards += "|StatsID = " + row["StatsID"] + " |count = " + row["Count"] + "\n"
		entryInnards += "|type = " + row["Type"] + " |sortID = " + row["sortID"] + "\n"
		entryInnards += "|Disp = " + disp + " |Disp_DE = " + disp_DE + "\n"
		entryInnards += "|HideGoal = " + row["HideGoal"] + "\n"
		entryInnards += "|Unlock = " + row["Unlock"] + " |Title_replace_ms = " + row["Title_replace_ms"] + "|Title_replace_id = " + row["Title_replace_id"] + "\n"
		entryInnards += "|Desc_replace_ms = " + row["Desc_replace_ms"] + " |Desc_replace_id = " + row["Desc_replace_id"] + "\n"

		achType = row["Type"]
		fullEntry = ach_startline + entryInnards + ach_finalline
		if achType == '0':
			story_list += "\n" + fullEntry
		elif achType == '1':
			combat_list += "\n" + fullEntry
		elif achType == '2':
			world_list += "\n" + fullEntry

	fullText = story_list + "\n|}\n\n" + combat_list + "\n|}\n\n" + world_list + "\n|}\n"

	outputFile.write(fullText)

print("done")