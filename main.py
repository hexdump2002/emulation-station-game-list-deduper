import xml.etree.ElementTree as ET
from enum import Enum
from typing import List, re

tree = ET.parse('gamelist.xml')
root = tree.getroot()

elements = root.findall('./game')

games=[]
for element in elements:
    path = element.find("path").text
    name = element.find("name").text
    games.append([path,name])

gameGroups=[]


def getBestVersion(group:[]) -> []:
    assert len(group) > 0

    bestVer = group[0]

    bestVerRating = getRatingForGameName(bestVer[1])

    restOfFiles: List = group[1:]
    for game in restOfFiles:
        currentVerRating = getRatingForGameName(game[1])
        # print("*Checking: %s -> %s" % (game.absPath, currentVerRating))
        if currentVerRating > bestVerRating:
            bestVer = game
            bestVerRating = currentVerRating

    # print("Selected: %s with %s" % (bestVer.absPath, bestVerRating))

    return bestVer

class Find(Enum):
    WORD = 0
    REGEX= 1

def findWords(searchWords:[[]], text, trueIfAll=False):

    found = False
    for search in searchWords:
        word = search[0]
        matchFound = False
        if search[1]==Find.WORD:
            result = re.search(rf'\b{word}\b',text, re.IGNORECASE)
            matchFound = result is not None
        elif search[1]==Find.REGEX:
            result = re.search(rf'{word}', text, re.IGNORECASE)
            matchFound = result is not None
        else:
            assert False

        if matchFound:
            found = True;
            if not trueIfAll:
                break
        else:
            if trueIfAll:
                found=False
                break;

    return found

def getRatingForGameName(name):
    points = 0

    name = name.lower()

    isJap=False
    if findWords([["europe",Find.WORD],["eur",Find.WORD],["\(E\)",Find.REGEX]], name): points += 50
    if findWords([["japan",Find.WORD],["jap",Find.WORD],["\(J\)",Find.REGEX]], name):   points += 10; isJap=True
    if findWords([["usa",Find.WORD], ["\(U\)",Find.REGEX]], name): points += 30
    if findWords([["world",Find.WORD]], name): points += 20
    if findWords([["beta",Find.WORD]],name): points -=30
    if findWords([["\(proto.*?\)",Find.REGEX]], name): points -= 50
    if findWords([["spain",Find.WORD]],name): points += 100
    if findWords([["\[!\]",Find.REGEX]],name): points += 40
    if findWords([["\[b\d{0,2}\]",Find.REGEX]], name): points -= 40
    if findWords([["\[h\d{0,2}\]",Find.REGEX]], name): points -= 100
    if findWords([["\(UE\)",Find.REGEX],["\(EU\)",Find.REGEX]],name): points+=50
    if findWords([["\(UJ\)",Find.REGEX],["(JU)",Find.REGEX]], name): points += 30
    if findWords([["\[a\d{0,2}(?![-\w])\]",Find.REGEX]],name): points-=10
    if findWords([["\[o\d{0,2}(?![-\w])\]", Find.REGEX]], name): points -= 10 #Overdump

    if findWords([["\[t\-eng.*?\]", Find.REGEX]], name):
        points += 50
    elif findWords([["\[t\-spa.*?\]", Find.REGEX]], name): points += 60
    elif findWords([["\[t\-.*?\]", Find.REGEX]], name):
        if isJap:
            points += 40
        else:
            points -=40

    if findWords([["partial", Find.REGEX]], name):
        points-=10

    if findWords([["\[t\d{0,2}(?![-\w])\]", Find.REGEX]], name): points -= 20 #No trainers please

    return points

while len(games)>0:
    if len(games)==1:
        group = [games[0]]
        gameGroups.append(group)
        break;

    group=[]

    game = games[0]
    group.append(game)

    for index in range(1, len(games)):
        choice = games[index][1]
        if game[1] == choice:
            group.append(games[index])

    gameGroups.append(group)

    for game in group:
        games.remove(game)

for group in gameGroups:
    print("##############################")
    for game in group:
        print(game[1]+" -> "+game[0])
    print("##############################")
