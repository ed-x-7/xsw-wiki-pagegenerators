import csv
import sys

items_filename = "squad_item_list.csv"
progress_filename = "squad_progress_list.csv"
purpose_filename = "squad_purposetxt.csv"
quest_filename = "squad_quest_list.csv"
rewards_filename = "squad_reward_list.csv"
summary_filename = "squad_summary.csv"
tasks_filename = "squad_task_list.csv"
formations_filename = "formation_list.csv"

def csv_to_dict(file_name):
    with open(file_name, encoding='utf-8-sig') as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return a

def squad_mission_navbox(quest, quest_summary, quest_purpose):
	head = "{{Infobox XCX squad mission\n"
	navbox = head
	for key in quest.keys():
		toWrite = quest[key]
		if key == "summary":
			toWrite = quest_summary.replace("[ST:n ]", " ").replace("BLADE barracks", "[[BLADE barracks]]")
		if key == "PurposeTxt":
			toWrite = quest_purpose.replace("[ST:n ]", " ").replace("BLADE barracks", "[[BLADE barracks]]")
		navbox += "|" + key + " = " + toWrite + "\n"

	navbox += "\n"
	navbox += "|condType1 = Type21\n|cond1 = 7\n"
	tail = "}}"
	navbox += tail
	return navbox

def summary_txt(quest_name):
	return "'''" + quest_name + "''' is a [[Support Mission]] in ''[[Xenoblade Chronicles X]]''."

def objectives(progress, task):
	head = "{{XCX squad mission objectives\n"
	navbox = head
	lastTaskEmpty = True

	for key in progress.keys():
		toWrite = progress[key]
		if key.startswith("TaskID"):
			if not (toWrite.isspace() or len(toWrite) == 0):
				task_index = key.replace("TaskID", "")

				toWrite = toWrite.replace("[ST:n ]", " ").replace("BLADE barracks", "[[BLADE barracks]]")
				navbox += "|" + key + " = " + toWrite + "\n"

				task_id = toWrite
				task_details = next((q for q in task if q["ID"] == task_id), None)

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
			navbox += "|Task" + index + "_" + key + " = " + toWrite + "\n"
	return navbox

def rewards(reward_details, items_details):
	head = "{{XCX squad mission rewards\n"
	navbox = head
	for key in reward_details.keys():
		toWrite = reward_details[key]
		navbox += "|" + key + " = " + toWrite + "\n"

	# TODO still need to populate item rewards

	tail = "}}"
	navbox += tail
	return navbox

def other_languages(quest_name):
	return "{{in other languages\n|en = " + quest_name + "\n|jp = \n|jp meaning = \n|fr = \n|fr meaning = \n|de = \n|de meaning = \n|es = \n|es meaning = \n|it = \n|it meaning = \n}}"

# Check arguments
if len(sys.argv) <= 1:
	print("Please enter the squad mission/quest ID number.")
	sys.exit()

# Init all dictionaries
items = csv_to_dict(items_filename)
progress = csv_to_dict(progress_filename)
purpose = csv_to_dict(purpose_filename)
reward = csv_to_dict(rewards_filename)
summary = csv_to_dict(summary_filename)
task = csv_to_dict(tasks_filename)
formations = csv_to_dict(formations_filename)

quest = csv_to_dict(quest_filename)

# Find the proper quest given the ID
quest_id = sys.argv[1]
quest_details = next((q for q in quest if q["ID"] == quest_id), None)
print(quest_details)

# Find the proper caption given the ID
caption_id = quest_details["summary"]
quest_summary = next((s for s in summary if s["ID"] == caption_id), None)["name"]
print(quest_summary)

purpose_id = quest_details["PurposeTxt"]
quest_purpose = next((s for s in purpose if s["ID"] == purpose_id), None)["name"]
print(quest_purpose)

# Populate
QuestID = quest_details["ID"]
quest_name = quest_details["title"]

# Populate the page.
infobox_squad_mission = squad_mission_navbox(quest_details, quest_summary, quest_purpose)
print(infobox_squad_mission)

fullText = infobox_squad_mission + "\n\n"

fullText += summary_txt(quest_name) + "\n\n"

objective_delimiter = "==Objectives==\n"
progress_id = quest_details["task"]
progress_details = next((q for q in progress if q["ID"] == progress_id), None)

fullText += objective_delimiter
fullText += objectives(progress_details, task) + "\n\n"

reward_delimiter = "==Rewards==\n"
reward_id = quest_details["reward"]
reward_details = next((q for q in reward if q["ID"] == reward_id), None)
drop_details = (q for q in items if q["QuestID"] == quest_id), None
print(reward_details)
print(drop_details)

fullText += reward_delimiter

fullText += rewards(reward_details, drop_details) + "\n\n"

other_languages_delimiter = "==In other languages==\n"
fullText += other_languages_delimiter

fullText += other_languages(quest_name)

outputFile=open(quest_name + ".txt","w")
outputFile.write(fullText)
outputFile.close()

print("done")
