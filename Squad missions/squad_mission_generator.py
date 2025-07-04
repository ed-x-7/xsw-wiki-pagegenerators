import csv
import sys

items_filename = "SCL_SquadItemPerList.csv"
items_filename_DE = "SCL_SquadItemPerList_DE.csv"
progress_filename = "SCL_SquadProgressList.csv"
purpose_filename = "MultiQuest_Purpose_ms.csv"
summary_filename = "MultiQuest_Summary_ms.csv"
quest_filename = "SCL_SquadQuestList_DE.csv"
rewards_filename = "SCL_SquadRewardList.csv"
rewards_filename_DE = "SCL_SquadRewardList_DE.csv"
tasks_filename = "SCL_SquadTaskList.csv"
quest_table_filename = "SCL_QuestTableList.csv"
mission_requirements_filename = "SCL_SquadMissionList.csv"
multilanguage_base = "Languages/MultiQuest_Title_ms_{lng}.csv"
languages = ["en", "jp", "fr", "de", "es", "it", "zh-tr", "zh-si", "ko"]

def csv_to_dict(file_name, bitfield_sections = []):
    a = []
    with open(file_name, encoding="utf-8-sig") as f:
        row_num = 1
        if (file_name == quest_filename):
            # IDs start at 20000 for SquadQuestList.
            row_num += (20000 - 1)
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

def filter_text(filter_str):
    return filter_str.replace("[ST:n ]", " ").replace("\n", " ").replace("  ", " ").replace("\\\"", "\"")

def squad_mission_infobox(quest, quest_title, quest_summary, quest_purpose, quest_table, mission_requirements):
    head = "{{Infobox XCX squad mission\n"
    navbox = head
    for key in quest.keys():
        toWrite = quest[key]
        if key == "title":
            toWrite = filter_text(quest_title)
        if key == "summary":
            toWrite = filter_text(quest_summary)
        if key == "PurposeTxt":
            toWrite = filter_text(quest_purpose)
        navbox += "|" + key + " = " + toWrite + "\n"

    # Now to handle the difficult part of auto-populating SquadMissionPanel, TargetType, SquadTarget, BladeQuestNo
    SquadMissionPanel = 0
    BladeQuestID = 0
    quest_id = quest["ID"]
    for quest_row in quest_table:
        for i in range(1, 11):
            QuestIDStr = f"QuestID{i}"
            QuestConditionStr = f"QuestCondition{i}"
            
            if int(quest_row[QuestIDStr]) == int(quest_id) and int(quest_row[QuestConditionStr]) != 0:
                SquadMissionPanel = int(quest_row[QuestConditionStr]) - 5293 # 5294 = panel 1, 5295 = panel 2, etc.
                BladeQuestID = quest_row["ID"]

    # Only write things in if we actually have these values
    if BladeQuestID != 0:
        # Given the ID, load the TargetType, SquadTarget, and BladeQuestNo
        SecretMission = False
        MissionRequirementColumn = SquadMissionPanel
        if SquadMissionPanel > 5:
            SecretMission = True
            MissionRequirementColumn -= 15

        mission_requirements_row = get_details_by_ID(mission_requirements, BladeQuestID)
        SquadTargetStr = f"SquadTarget{MissionRequirementColumn}"
        TargetTypeStr = f"TargetType{MissionRequirementColumn}"
        SquadTarget = mission_requirements_row[SquadTargetStr]
        TargetType = mission_requirements_row[TargetTypeStr]
        BladeQuestNo = mission_requirements_row["BladeQuestNo"]

        # Write them all in
        navbox += "\n"
        navbox += f"|BladeQuestNo = {BladeQuestNo}\n"
        navbox += f"|BladeQuestID = {BladeQuestID}\n"
        navbox += f"|TargetType = {TargetType}\n"
        navbox += f"|SquadTarget = {SquadTarget}\n"
        navbox += f"|SquadMissionPanel = {SquadMissionPanel}\n"
        navbox += f"|SecretMission = {SecretMission}\n"

    tail = "}}"
    navbox += tail
    return navbox

def summary_txt(quest_name):
    return "'''" + quest_name + "''' is a [[Squad Mission]] in ''[[Xenoblade Chronicles X]]''."

def objectives(progress, task):
    head = "{{XCX squad mission objectives\n"
    navbox = head
    lastTaskEmpty = True

    for key in progress.keys():
        toWrite = progress[key]
        if key.startswith("TaskID"):
            if not (len(toWrite) == 0 or int(toWrite) == 0):
                task_index = key.replace("TaskID", "")

                toWrite = toWrite.replace("[ST:n ]", " ").replace("BLADE barracks", "[[BLADE barracks]]")
                navbox += "|" + key + " = " + toWrite + "\n"

                task_id = toWrite
                
                if (int(task_id) != 0):
                    task_details = get_details_by_ID(task, task_id)
                    navbox += task_info(task_details, task_index)
                lastTaskEmpty = False
            else:
                lastTaskEmpty = True
        elif key.startswith("TaskTxt"):
            if not lastTaskEmpty:
                toWrite = toWrite.replace("[ST:n ]", " ").replace("BLADE barracks", "[[BLADE barracks]]")
                navbox += "|" + key + " = " + toWrite + "\n\n"
        else:
            navbox += "|" + key + " = " + toWrite + "\n"

    tail = "}}"
    navbox += tail
    return navbox

def task_info(task, index):
    navbox = ""
    for key in task.keys():
        toWrite = task[key]
        if key != "ID":
            if key != "TaskType":
                if task[key] != '0' and len(task[key]) > 0:
                    toWrite = task[key]
                    navbox += f"|Task{index}_{key} = {toWrite}\n"
            else:
                toWrite = task[key]
                navbox += f"|Task{index}_{key} = {toWrite}\n"
    return navbox

def rewards(reward_details, reward_details_DE, items_details, items_details_DE):
    head = "{{XCX squad mission rewards\n"
    navbox = head
    for key in reward_details.keys():
        toWrite = reward_details[key]
        toWrite_DE = reward_details_DE[key]
        
        navbox += "|" + key + " = " + toWrite + "\n"
        if (toWrite != toWrite_DE):
            navbox += "|" + key + " DE = " + toWrite_DE + "\n"

    itemNum = 0
    print(items_details)
    if items_details != None:
        for item in items_details:
            navbox += "\n"
            itemNum += 1
            for key in item.keys():
                if key.startswith("ref_item_bdat") or key.startswith("item_id") or key.startswith("itmPer"):
                    if item[key] != '0':
                        toWrite = item[key]
                        toWrite_DE = items_details_DE[0][key]

                        navbox += f"|Item{itemNum}_{key} = {toWrite}\n"
                        if (toWrite != toWrite_DE):
                            navbox += f"|Item{itemNum}_{key} DE = {toWrite_DE}\n"
                elif key != "QuestID":
                    toWrite = item[key]
                    toWrite_DE = items_details_DE[0][key]

                    navbox += f"|Item{itemNum}_{key} = {toWrite}\n"
                    if (toWrite != toWrite_DE):
                        navbox += f"|Item{itemNum}_{key} DE = {toWrite_DE}\n"
                
    tail = "}}"
    navbox += tail
    return navbox

def other_languages(language_detail_list, title_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_mission_name = get_details_by_ID(language_detail_list[i], title_linenumber)["name"]
        if languages[i] == "jp":
            lng_mission_name = "{{ja|" + lng_mission_name + "|}}"
        if languages[i] == "zh-si" or languages[i] == "zh-tr":
            lng_mission_name = "{{zh|" + lng_mission_name + "|}}"
        if languages[i] == "ko":
            lng_mission_name = "{{ko|" + lng_mission_name + "|}}"
        language_box += "|" + languages[i] + " = " + lng_mission_name + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

# Init all dictionaries
items = csv_to_dict(items_filename)
items_DE = csv_to_dict(items_filename_DE)
progress = csv_to_dict(progress_filename)
purpose = csv_to_dict(purpose_filename)
reward = csv_to_dict(rewards_filename)
reward_DE = csv_to_dict(rewards_filename_DE)
summary = csv_to_dict(summary_filename)
task = csv_to_dict(tasks_filename)
quest = csv_to_dict(quest_filename)
quest_table = csv_to_dict(quest_table_filename)
mission_requirements = csv_to_dict(mission_requirements_filename)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

with open("missions/result.txt","w", encoding="utf-8") as outputFile:
    for quest_id in range(20000,20234):
        # Find the proper quest given the ID
        quest_details = get_details_by_ID(quest, quest_id)
        print(quest_details)

        # Find the proper title given the ID
        title_id = int(quest_details["title"])
        quest_title = get_details_by_ID(language_detail_list[0], title_id)["name"]

        # Find the proper caption given the ID
        caption_id = int(quest_details["summary"])
        quest_summary = get_details_by_ID(summary, caption_id)["name"]

        purpose_id = int(quest_details["PurposeTxt"])
        quest_purpose = get_details_by_ID(purpose, purpose_id)["name"]

        # Populate the page.
        infobox_squad_mission = squad_mission_infobox(quest_details, quest_title, quest_summary, quest_purpose, quest_table, mission_requirements)
        
        fullText = infobox_squad_mission + "\n\n"

        fullText += summary_txt(quest_title) + "\n\n"

        objective_delimiter = "==Objectives==\n"
        progress_id = quest_details["task"]
        progress_details = get_details_by_ID(progress, progress_id)

        fullText += objective_delimiter
        fullText += objectives(progress_details, task) + "\n\n"

        reward_delimiter = "==Rewards==\n"
        reward_id = quest_details["reward"]
        reward_details = get_details_by_ID(reward, reward_id)
        reward_details_DE = get_details_by_ID(reward_DE, reward_id)
        drop_details = [q for q in items if int(q["QuestID"]) == int(quest_id)]
        drop_details_DE = [q for q in items_DE if int(q["QuestID"]) == int(quest_id)]

        fullText += reward_delimiter

        fullText += rewards(reward_details, reward_details_DE, drop_details, drop_details_DE) + "\n\n"

        other_languages_delimiter = "==In other languages==\n"
        fullText += other_languages_delimiter
        print(title_id)
        fullText += other_languages(language_detail_list, title_id)

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+quest_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("\n{{-stop-}}\n")

print("done")
