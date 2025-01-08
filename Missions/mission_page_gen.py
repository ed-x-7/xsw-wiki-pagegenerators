# Based on the BDATs converted to CSVs from the original game
import csv
import sys
import re

fld_questlist = "fld_questlist.csv"
fld_questtask = "fld_questtask.csv"
quest_itemset = "quest_itemset.csv"
chr_enlist = "chr_enlist_ms.csv"
multilanguage_base = "Languages/quest_ms_{lng}.csv"
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

def csv_to_list(file_name):
    a = []
    with open(file_name, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, skipinitialspace=True):
            for k, v in row.items():
                a.append(v)
    return a


def get_details_by_ID(search_dict, id, idx="ID"):
    return next((q for q in search_dict if isinstance(q, dict) and q[idx] == str(id)), None)

# Returns the quest details into "quest details" and "objective details".
def split_questlist(quest_details):
    quest = ["ID","quest_title","category","name","area","summary","GameCondition","Difficulty","ClearCheckflg","ArrivalCheckflg","HexCondition","balloonCond","balloonNpc","result_text_a","result_text_b","reward_disp","sortID","itemset_id_1","itemset_id_2","consent","window_disp","flg_type_a","dead_count","next_quest_a","ScriptA","next_quest_b","ScriptB","quest_report"]
    objective = ["ID","quest_name","waitComp","prt_quest_id","flg_type_b","task_id","cancel_count","next_quest_a","ScriptA","next_quest_b","ScriptB"]
    mission_dict = dict()
    objective_dict = dict()
    for q in quest:
        mission_dict[q] = quest_details[q]
    for q in objective:
        objective_dict[q] = quest_details[q]

    return (mission_dict,objective_dict)

# Returns an article title.
def mission_name_disambig(mission_name, mission_details, enemy_list):
    base_name = mission_name
    mission_id_int = int(mission_details["ID"])
    # Other game confusion
    shared_other_game = ["Ambush", "The Ties That Bind", "Gold Rush", "Stop, Thief!", "A Friend in Need", "Missing in Action"]
    shared_article = ["Miranium", "Skell License", "Flight Module", "Dodonga Caravan", "Dorian Caravan", "Yelv's Partner"]

    suffix = "" # Should start with a space
    if base_name.startswith("Chapter"): # Chapters
        suffix = " (XCX)"
    if base_name in shared_other_game:
        suffix = " (XCX)"
    elif base_name in shared_article:
        suffix = " (mission)"

    # Handle enemy names
    if base_name in enemy_list:
        suffix = " (mission)"

    match mission_id_int: # Basic missions
        case 1825: # Adsecula Extermination
            suffix = " (Shadow)"
        case 1921:
            suffix = " (Sparrow)"
        case 1707: # Arms Testers Wanted
            suffix = " (Titanium Knife II)"
        case 1767:
            suffix = " (Soldier Avagar)"
        case 1813:
            suffix = " (Warrior Dual Guns)"
        case 1841:
            suffix = " (Warrior Raygun)"
        case 1897:
            suffix = " (Chrome Shield)"
        case 2015:
            suffix = " (Ophidian Psylans)"
        case 2089:
            suffix = " (Chromoly Parce)"
        case 2111:
            suffix = " (Cermet Slair)"
        case 2151:
            suffix = " (Cermet Blades)"
        case 2217:
            suffix = " (Carbide Saber)"
        case 2233:
            suffix = " (Delta Retic)"
        case 2259:
            suffix = " (Delta Machine)"
        case 2361: # Backup Request
            suffix = " (Bozé)"
        case 2367: # Backup Request
            suffix = " (Phog)"
        case 1731: # Blatta Splatter
            suffix = " (Zeppelin)"
        case 1753: 
            suffix = " (Rust)"
        case 1871: # Culling Caecuses
            suffix = " (Thug)"
        case 2037:
            suffix = " (Villainous)"
        case 1787: # Fending Off Forfexes
            suffix = " (Cobalt)"
        case 2145:
            suffix = " (Native)"
        case 1735: # From Idea to Inventory
            suffix = " (Opaque Mirror)"
        case 1797:
            suffix = " (Beryl Aetrygon Horn)"
        case 1857:
            suffix = " (Aprica Back Moss)"
        case 2021:
            suffix = " (Fine Aprica Wood)"
        case 2079: 
            suffix = " (Ornate Progen Horn)"
        case 2219:
            suffix = " (Lucky Cervus Sapling)"
        case 1745: # Germivores No More
            suffix = " (Echo)"
        case 2137:
            suffix = " (Terrible)"
        case 1955: # Ictus Infestation
            suffix = " (Inferno)"
        case 2107:
            suffix = " (Warlord)"
        case 2277:
            suffix = " (Hermit)"
        case 1727: # Indigen Investigation
            suffix = " (Golden Mortifole Feather)"
        case 1783:
            suffix = " (Saltat Horn)"
        case 1903:
            suffix = " (Moving Thallus Tail)"
        case 2009:
            suffix = " (Slimy Tongue)"
        case 2185:
            suffix = " (Muscled Simius Bulge)"
        case 1931: # Laying Lophids Low
            suffix = " (Blazing)"
        case 1949:
            suffix = " (Ocean)"
        case 1873: # Marnuck Masher
            suffix = " (Aspirer)"
        case 1937: 
            suffix = " (Soldier)"
        case 1701: # Miranium Request
            suffix = " (700 units)"
        case 1737:
            suffix = " (1,200 units)"
        case 1761:
            suffix = " (1,800 units)"
        case 1821:
            suffix = " (2,400 units)"
        case 1881:
            suffix = " (3,600 units)"
        case 1941:
            suffix = " (4,000 units)"
        case 2061:
            suffix = " (5,700 units)"
        case 2121:
            suffix = " (9,300 units)"
        case 2181:
            suffix = " (7,000 units)"
        case 2241:
            suffix = " (12,000 units)"
        case 1721: # Mortifole Mulching
            suffix = " (Lake)"
        case 2127:
            suffix = " (Pit)"
        case 1741:
            suffix = " (White)"
        case 1827:
            suffix = " (Docile)"
        case 1851:
            suffix = " (Prowler)"
        case 1801: # Papil Punisher
            suffix = " (Sorcerer)"
        case 2007:
            suffix = " (Lake)"
        case 1743: # Partners in Prototyping
            suffix = " (Glowing Retina)"
        case 1779:
            suffix = " (Blue Forfex Shell)"
        case 1899:
            suffix = " (Insidia Mohawk)"
        case 1925:
            suffix = " (Vivohast Crescent Hook)"
        case 2031:
            suffix = " (Adsecula Oil Drop)"
        case 2197:
            suffix = " (Ingrown Virago Claw)"
        case 2245:
            suffix = " (Thick Cinicula Horn)"
        case 2275:
            suffix = " (Quality Vigent Claw)"
        case 2457: # This one should be skipped since no rewards and duplicate.
            suffix = " (Blue Forfex Shell)"
        case 2269: # Petramand Patrol
            suffix = " (Malium)"
        case 2289:
            suffix = " (Terbium)"
        case 2071: # Plucking Auravises
            suffix = " (Reaver)"
        case 2265:
            suffix = " (Tempest)"
        case 1811: # Pounding Puges
            suffix = " (Porter)"
        case 1981:
            suffix = " (Knight)"
        case 1747: # Reclaiming the Whale
            suffix = " (Cordless Transformer)"
        case 1785:
            suffix = " (Gesture Glove)"
        case 2155:
            suffix = " (5th Gen Recycler)"
        case 2029: # Ridding Insidias
            suffix = " (Javelin)"
        case 2075:
            suffix = " (Vermilion)"
        case 1717: # Search Request
            suffix = " (Primordia)"
        case 2001:
            suffix = " (Oblivia)"
        case 2099:
            suffix = " (Sylvalum)"
        case 2139:
            suffix = " (Noctilum)"
        case 2299:
            suffix = " (Cauldros)"
        case 1781: # Squashing Scirpos
            suffix = " (Amrita)"
        case 1951:
            suffix = " (Jade)"
        case 2251:
            suffix = " (Native)"
        case 1705: # Suid Sweep
            suffix = " (Brass)"
        case 1895:
            suffix = " (Forest)"
        case 1957: # Sundering Saltats
            suffix = " (Jocular)"
        case 2125:
            suffix = " (Viridian)"
        case 1803: # The Jewelmonger
            suffix = " (Giant Blue Pearl)"
        case 2065:
            suffix = " (Lepyx Sunstone)"
        case 2149:
            suffix = " (Gremlin Stone)"
        case 2293:
            suffix = " (Hidden Cantor Hoard)"
        case 1723: # The Next Big Thing
            suffix = " (Scirpo Silk)"
        case 1815:
            suffix = " (Petramand Black Silk)"
        case 1863:
            suffix = " (Shimmering Silk)"
        case 1933:
            suffix = " (Alluring Lophid Extract)"
        case 2257:
            suffix = " (Distilled Sap)"
        case 1791: # Thinning the Thalluses
            suffix = " (Recluse)"
        case 2077:
            suffix = " (False)"
        case 2443: # Top-Secret Mission
            suffix = " (Julius)"
        case 2447:
            suffix = " (Stella)"
        case 2453:
            suffix = " (Lara Mara)"

    # Special case: New Orders
    if base_name == "New Orders":
        # Need to figure out which chapter was started.
        match mission_id_int:
            case 2311:
                suffix = " (Chapter 4)"
            case 2313:
                suffix = " (Chapter 5)"
            case 2315:
                suffix = " (Chapter 6)"
            case 2317:
                suffix = " (Chapter 7)"
            case 2319:
                suffix = " (Chapter 8)"
            case 2321:
                suffix = " (Chapter 9)"
            case 2323:
                suffix = " (Chapter 10)"
            case 2325:
                suffix = " (Chapter 11)"
            case 2327:
                suffix = " (Chapter 12)"
    # Special case: Miranium Exchange
    if base_name == "Miranium Exchange":
        # List by the number of credits. Always giving 10k though
        match mission_id_int:
            case 2301:
                suffix = " (10,000 credits)"
            case 2303:
                suffix = " (20,000 credits)"
            case 2305:
                suffix = " (50,000 credits)"
            case 2307:
                suffix = " (75,000 credits)"
            case 2309:
                suffix = " (100,000 credits)"
    # Special case: Off the Record
    if base_name == "Off the Record":
        match mission_id_int:
            case 2352:
                suffix = " (archaeological)"
            case 2355:
                suffix = " (mechanical)"
            case 2358:
                suffix = " (biological)"

    return mission_name + suffix

def caption_scrub(caption):
    return caption.replace("[ST:n ][ST:n ]", " ").replace("[ST:n ]", " ").replace("\\\"", "\"").replace("- ", "-").replace("  ", " ")

def mission_infobox(mission_id, mission_details, mission_name, quest_text):
    # Add details from fld_questlist
    head = "{{Infobox XCX Mission\n"
    navbox = head
    for key in mission_details.keys():
        toWrite = mission_details[key]
        if key == "ID":
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"
        elif key == "quest_title":
            navbox += "|title=" + mission_name + "\n"
        elif key == "summary":
            if int(toWrite) != 0:
                navbox += "|" + key + "=" + caption_scrub(get_details_by_ID(quest_text, int(toWrite))["name"]) + "\n"
            else:
                navbox += "|" + key + "=" + "\n"
        else:
            if toWrite == "":
                toWrite = "0"
            navbox += "|" + key + "=" + toWrite + "\n"

    tail = "}}"
    navbox += tail

    return navbox

def objective(mission_details, task_details, quest_text):
    head = "{{XCX mission objective\n"
    navbox = head
    purpose_msgs = ["purpose_log1", "purpose_log2", "purpose_log3"]
    for key in mission_details.keys():
        toWrite = mission_details[key]
        navbox += "|" + key + "=" + toWrite + " "

    for key in task_details.keys():
        toWrite = task_details[key]
        if key == "ID": # Covered by task_id
            continue
        elif key not in purpose_msgs:
            if toWrite == "":
                toWrite = "0"
            navbox += "|task_" + key + "=" + toWrite + " "
    navbox += "\n"
    # Handle the purpose_log values next
    for key in purpose_msgs:
        toWrite = task_details[key]
        if int(toWrite) != 0:
            navbox += "|task_" + key + "=" + caption_scrub(get_details_by_ID(quest_text, int(toWrite))["name"]) + "\n"
    tail = "}}"
    navbox += tail

    return navbox

def create_objective(mission_list, task_list, route, route_index, quest_text):
    current_details = get_details_by_ID(mission_list, route[route_index])
    # Limit it to just quest details
    if int(current_details["task_id"]) == 0:
        return ""
    (_, obj_details) = split_questlist(current_details)
    task_details = get_details_by_ID(task_list, int(obj_details["task_id"]))
    return objective(obj_details, task_details, quest_text) + "\n"

def objectives_section(mission_details, mission_list, task_list, quest_text):
    # Structure:
    # The first detail points to another row with the task in next_quest_a (next_quest_b if it branches).
    # This points to the task ID in task_list.
    # Mission ends with route A if next_quest = 10000, B if quest = 10001
    # QuestTask structure:
    # condition=0: achieve all objectives in set
    # condition=1: achieve any objective
    # Objective may have to be hidden if purpose = 0.
    next_details = mission_details

    # List the quest IDs required for routes A and B.
    route_a = []
    route_b = []
    end_a = False
    end_b = False
    while next_details is not None and not end_a:
        route_a.append(int(next_details["ID"]))
        # Iterate over quest A details.
        if next_details["next_quest_a"] in [0, 10000, 10001]:
            end_a = True
        else:
            next_details = get_details_by_ID(mission_list, int(next_details["next_quest_a"]))
    # Check route B
    step_count = 0
    next_details = mission_details
    end_a = False
    visited_b = False
    while next_details is not None and not end_b:
        route_b.append(int(next_details["ID"]))
        next_details_a = get_details_by_ID(mission_list, int(next_details["next_quest_a"]))
        next_details_b = get_details_by_ID(mission_list, int(next_details["next_quest_b"]))

        if next_details["next_quest_b"] in [10000, 10001]:
            end_b = True

        # Check if we can go to next_quest_b
        if next_details_b is not None:
            visited_b = True
            next_details = next_details_b
        else:
            next_details = next_details_a

    objective_list_text = "<ol>\n"
    split_section = min(len(route_a),len(route_b)) # Set split section to the default.
    for i in range(split_section):
        if route_a[i] == route_b[i]:
            # Paths are same here. Create objectives for this.
            objective_list_text += create_objective(mission_list, task_list, route_a, i, quest_text)
        else:
            split_section = i
            break

    if split_section != len(route_a):
        objective_list_text += "</ol>\n"
        objective_list_text += "===Route A===\n"
        objective_list_text += "<ol start=\"{start}\">\n".format(start=split_section)

    for i in range(split_section, len(route_a)):
        # Set Route A paths
        objective_list_text += create_objective(mission_list, task_list, route_a, i, quest_text)

    if split_section != len(route_b):
        objective_list_text += "</ol>\n"
        objective_list_text += "===Route B===\n"
        objective_list_text += "<ol start=\"{start}\">\n".format(start=split_section)

    for i in range(split_section, len(route_b)):
        # Set Route B paths
        objective_list_text += create_objective(mission_list, task_list, route_b, i, quest_text)

    objective_list_text += "</ol>"
    return objective_list_text

def reward(rewards_details, id_2 = "0"):
    head = "{{XCX mission rewards\n"
    navbox = head
    for key in rewards_details.keys():
        toWrite = rewards_details[key]
        if toWrite == "":
            toWrite = "0"
        navbox += "|" + key + "=" + toWrite + "\n"
        if key == "ID" and id_2 != "0":
            navbox += "|ID_2" + "=" + id_2 + "\n"

    tail = "}}"
    navbox += tail

    return navbox

def reward_section(mission_details, rewards_a, rewards_b):
    if rewards_a is None:
        return "None."
    if rewards_b is not None:
        # Check if the rewards are the exact same.
        same_rewards = True
        for key in rewards_a.keys():
            if key != "ID":
                if rewards_a[key] != rewards_b[key]:
                    same_rewards = False
        if same_rewards and rewards_a["ID"] != rewards_b["ID"]:
            return reward(rewards_a, rewards_b["ID"])
        rewardSection = ""
        rewardSection += "===Route A===" + "\n"
        rewardSection += reward(rewards_a) + "\n"

        rewardSection += "===Route B===" + "\n"
        rewardSection += reward(rewards_b) + "\n"
        return rewardSection
    else:
        return reward(rewards_a)

    return ""

def result(text_id, quest_text):
    return "''" + caption_scrub(get_details_by_ID(quest_text, int(text_id))["name"]) + "''"

def result_text(mission_details, two_results, quest_text):
    if two_results:
        text_id_a = mission_details["result_text_a"]
        text_id_b = mission_details["result_text_b"]

        result_a = result(text_id_a, quest_text)
        result_b = result(text_id_b, quest_text)

        if result_a == result_b:
            return result_a
        else:
            resultSection = ""
            resultSection += "===Route A===" + "\n"
            resultSection += result_a + "\n"

            resultSection += "===Route B===" + "\n"
            resultSection += result_b
            return resultSection
    else:
        text_id = mission_details["result_text_a"]
        return result(text_id, quest_text)

def summary(mission_name, mission_details):
    # Describe the summary of the mission.
    mis_type = int(mission_details["category"])
    mission_type = "unknown"
    match mis_type:
        case 1:
            mission_type = "a [[Story Mission]]"
        case 2:
            mission_type = "a [[Normal Mission]]"
        case 3:
            mission_type = "an [[Affinity Mission]]"
        case 4:
            mission_type = "a [[Basic Mission]]"

    return "'''{name}''' is {type} in ''[[Xenoblade Chronicles X]]''.".format(name=mission_name, type=mission_type)

def other_languages(language_detail_list, clb_linenumber):
    language_box = "{{in other languages\n"
    for i in range(len(languages)):
        # languages
        lng_mission_name = language_detail_list[i][clb_linenumber]["name"]
        if languages[i] == "jp":
            lng_mission_name = "{{ja|" + lng_mission_name + "|}}"
        language_box += "|" + languages[i] + " = " + lng_mission_name + "\n"
        if languages[i] != "en":
            language_box += "|" + languages[i] + " meaning = \n"

    language_box += "}}"
    return language_box

# Init all dictionaries
quest_dict = csv_to_dict(fld_questlist)
objective_dict = csv_to_dict(fld_questtask)
itemset_dict = csv_to_dict(quest_itemset)
enemy_list = csv_to_list(chr_enlist)
all_language_files = map(lambda lang: multilanguage_base.format(lng=lang), languages)
language_detail_list = list(map(csv_to_dict, all_language_files))

duplicate_mission_id_versions = \
[
89, # Story Missions Complete (not a mission)
1190, # A Dish Served Cold
1646, # Blitzkrieg (Frye)
1645, # Fortun and Glory
1591, # Haywire!
1197, # Lionhearted (this one has just 1 objective)
1179, 1181, # Mamma Mia!
2457, # Partners in Prototyping (no rewards)
1682, 1684, 1686, 1693, 1695, 1698, # Proficiency Exam 7 (there's 7 versions!)
1194, # Rise of the Blood Lobster
1184, 1186, 1188, # The Bodyguard
]

with open("missions/result.txt","w", encoding="utf-8") as outputFile:
    # for mission_id_int in range(1, 941):
    for mission_id_int in range(1,2459):
        if mission_id_int in duplicate_mission_id_versions: # Manually checking for duplicate missions.
            continue
        mission_id = str(mission_id_int)
        quest_details = get_details_by_ID(quest_dict, mission_id)
        # Split it into mission and objective details.
        (mission_dict, _) = split_questlist(quest_details)

        mission_name_id = mission_dict['quest_title']

        if int(mission_name_id) != 0: # Actual mission.
            # Setup mission name.
            mission_name = get_details_by_ID(language_detail_list[0], mission_name_id)['name']

            if mission_name.startswith("qst"): # Name not showing up in the actual game.
                continue

            # Check for name clash
            article_title = mission_name_disambig(mission_name, mission_dict, enemy_list)
            print(article_title)

            # Populate the page.
            infobox_mission = mission_infobox(mission_id, mission_dict, mission_name,language_detail_list[0])

            fullText = infobox_mission + "\n"

            # Handle Tyrant "for" section
            if mission_name in enemy_list:
                fullText += "{{for|the [[Basic Mission]]|the [[Tyrant]]|"+mission_name+"}}" + "\n"
            else:
                fullText += "\n"

            fullText += summary(mission_name, mission_dict) + "\n\n"

            # Check if we have two endings, for Objectives/Rewards/Results
            two_results = int(mission_dict["result_text_a"]) != 0 and int(mission_dict["result_text_b"]) != 0
            
            # SECTION FOR OBJECTIVES
            objectives_delimiter = "==Objectives==\n"
            fullText += objectives_delimiter
            fullText += objectives_section(mission_dict, quest_dict, objective_dict, language_detail_list[0])
            fullText += "\n\n"

            # SECTION FOR DIALOGUE (for Affinity/Normal Missions only)
            mis_type = int(mission_dict["category"])
            mission_type = "unknown"
            match mis_type:
                case 1: # Story
                    dialogue_delimiter = "==Dialogue==\n"
                    fullText += dialogue_delimiter + "{{main|Script of Xenoblade Chronicles X/" + mission_name + "}}" + "\n\n" # Do this manually later
                case 2: # Normal
                    dialogue_delimiter = "==Dialogue==\n"
                    fullText += dialogue_delimiter + "{{main|"+article_title+"/Script}}" + "\n\n" # Do this manually later
                case 3: # Affinity
                    dialogue_delimiter = "==Dialogue==\n"
                    fullText += dialogue_delimiter + "{{main|"+article_title+"/Script}}" + "\n\n" # Do this manually later

            # SECTION FOR REWARDS
            rewards_delimiter = "==Rewards==\n"
            rewards_a = get_details_by_ID(itemset_dict, int(mission_dict["itemset_id_1"]))
            if two_results:
                rewards_b = get_details_by_ID(itemset_dict, int(mission_dict["itemset_id_2"]))
            else:
                rewards_b = None
            fullText += rewards_delimiter
            fullText += reward_section(mission_dict, rewards_a, rewards_b)
            fullText += "\n"

            # SECTION FOR RESULTS
            results_delimiter = "==Results==\n"
            fullText += results_delimiter
            fullText += result_text(mission_dict, two_results, language_detail_list[0])
            fullText += "\n\n"

            # SECTION FOR OTHER LANGUAGES
            other_languages_delimiter = "==In other languages==\n"

            clb_linenumber = 0
            for i in range(len(language_detail_list[0])):
                if language_detail_list[0][i]["ID"] == mission_name_id:
                    clb_linenumber = i

            fullText += other_languages_delimiter

            fullText += other_languages(language_detail_list, clb_linenumber) + "\n"

            # SECTION FOR GALLERY (only for non-Basic Missions)
            if mis_type != 4:
                fullText += "\n"
                gallery_delimiter = "==Gallery==\n"
                fullText += gallery_delimiter
                fullText += "{{image needed}}\n"

            outputFile.write("{{-start-}}\n")
            outputFile.write("'''"+article_title+"'''\n")
            outputFile.write(fullText)
            outputFile.write("{{-stop-}}\n")

print("done")
