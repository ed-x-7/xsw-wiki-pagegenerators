import csv
import sys

dlwpntable_silver = "drp_dlwpntable_silver.csv" # Contains the silver drop ID. Need to get the column based on drop ID.
dlwpntable_gold = "drp_dlwpntable_gold.csv" # Contains the gold drop ID. Need to get the column based on drop ID.

def csv_nth_column(file_name, col_num):
    column = []
    with open(file_name, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            column.append(row[col_num])
    return column

def summary(pool_num, drop_type):
    top_section = "{{{{DISPLAYTITLE:List of Skell weapon drops ({type}) (pool {pool})}}}}\n{{{{float TOC}}}}\n".format(type=drop_type, pool=pool_num)

    return top_section + "This is a list of all " + drop_type + "-tier [[Skell weapon]]s that enemies in weapon pool " + str(pool_num) + " can drop, as well as a list of enemies that drop weapons in that pool.\n{{clear}}"

def weapon_list_section(weapon_lots): 
    template = "{{XCX item lot Skell weapon\n"
    for lot in weapon_lots:
        if lot != "":
            toWrite = lot
            template += "|" + toWrite + "\n"

    template += "}}"
    return template

def enemy_list_gold(pool_num, min_level, max_level):
    return "{{{{XCX enemies by lot pool|309|0|{0}|{1}|{2}}}}}".format(pool_num, min_level, max_level)

def enemy_list_silver(pool_num, min_level, max_level):
    return "{{{{XCX enemies by lot pool|0|310|{0}|{1}|{2}}}}}".format(pool_num, min_level, max_level)

def final_navbox():
    navbox = "{{XCX drop navbox}}"
    return navbox

with open("Pools/result.txt","w", encoding="utf-8") as outputFile:
    drop = ""
    for p in range(24):
        pool_num = p+1
        for d in range(2):
            match d:
                case 0:
                    drop = "gold"
                    weapon_list = csv_nth_column(dlwpntable_gold, p)[1:]
                case 1:
                    drop = "silver"
                    weapon_list = csv_nth_column(dlwpntable_silver, p)[1:]
            # INTRO SECTION
            fullText = summary(pool_num, drop) + "\n"

            # LEVELS SECTION
            for tier in range(2,7):
                minLevel = (10*tier)+1
                maxLevel = 10*(tier+1)
                if tier == 2:
                    minLevel = 1
                if tier == 6:
                    maxLevel = 99
                fullText += "==Levels {0}-{1}==\n".format(minLevel, maxLevel)

                weapon_by_level = weapon_list[10*tier:10*tier+10]
                fullText += weapon_list_section(weapon_by_level) + "\n"
                fullText += "{{fake header|Enemies|3}}" + "\n"
                if d == 0:
                    fullText += enemy_list_gold(pool_num, minLevel, maxLevel) + "\n\n"
                if d == 1:
                    fullText += enemy_list_silver(pool_num, minLevel, maxLevel) + "\n\n"

            fullText += final_navbox() + "\n"

            article_title = "List of Skell weapon drops ({drop})/{pool}".format(drop=drop, pool=pool_num)

            outputFile.write("{{-start-}}\n")
            outputFile.write("'''"+article_title+"'''\n")
            outputFile.write(fullText)
            outputFile.write("{{-stop-}}\n")

print("done")
