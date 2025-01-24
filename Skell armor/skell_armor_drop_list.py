import csv
import sys

dlwpntable_silver = "drp_dlarmortable_silver.csv" # Contains the silver drop ID. Need to get the column based on drop ID.
dlwpntable_gold = "drp_dlarmortable_gold.csv" # Contains the gold drop ID. Need to get the column based on drop ID.

def csv_nth_column(file_name, col_num):
    column = []
    with open(file_name, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            column.append(row[col_num])
    return column

def summary(pool_num):
    top_section = "{{{{DISPLAYTITLE:List of Skell armor drops (pool {pool})}}}}\n{{{{float TOC}}}}\n".format(pool=pool_num)

    return top_section + "This is a list of all [[Skell armor]] that enemies in Skell armor pool " + str(pool_num) + " can drop, as well as a list of enemies that drop armor in that pool.\n{{clear}}"

def armor_list_section(armor_lots): 
    template = "{{XCX item lot Skell armor\n"
    for lot in armor_lots:
        if lot != "":
            toWrite = lot
            template += "|" + toWrite + "\n"

    template += "}}"
    return template

def enemy_list(pool_num, min_level, max_level):
    return "{{{{XCX enemies by lot pool|313|314|{0}|{1}|{2}}}}}".format(pool_num, min_level, max_level)

def final_navbox():
    navbox = "{{XCX drop navbox}}"
    return navbox

with open("Pools/result.txt","w", encoding="utf-8") as outputFile:
    drop = ""
    for p in range(7):
        pool_num = p+1
        armor_list = csv_nth_column(dlwpntable_silver, p)[1:]
        # INTRO SECTION
        fullText = summary(pool_num) + "\n"

        # LEVELS SECTION
        for tier in range(2,7):
            minLevel = (10*tier)+1
            maxLevel = 10*(tier+1)
            if tier == 2:
                minLevel = 1
            if tier == 6:
                maxLevel = 99
            fullText += "==Levels {0}-{1}==\n".format(minLevel, maxLevel)

            armor_by_level = armor_list[10*tier:10*tier+10]
            fullText += armor_list_section(armor_by_level) + "\n"
            fullText += "{{fake header|Enemies|3}}" + "\n"
            fullText += enemy_list(pool_num, minLevel, maxLevel) + "\n\n"

        fullText += final_navbox() + "\n"

        article_title = "List of Skell armor drops/{pool}".format(pool=pool_num)

        outputFile.write("{{-start-}}\n")
        outputFile.write("'''"+article_title+"'''\n")
        outputFile.write(fullText)
        outputFile.write("{{-stop-}}\n")

print("done")
