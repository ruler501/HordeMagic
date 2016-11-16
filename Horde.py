import random
import gnureadline
import sys

def loadList(*, extraArgs=[], **kwargs):
    path = None
    if len(extraArgs) > 0:
        path = extraArgs[0]
    with open(path) as f:
        deck = []
        commander = None
        for line in f:
            if line.startswith("//"):
                continue
            elif line.startswith("SB:"):
                commander = " ".join(line.split()[2:])
            else:
                vals = line.split()
                num = int(vals[0])
                deck += [" ".join(vals[1:])]*num
        random.shuffle(deck)
        if len(extraArgs) > 1:
            num = int(extraArgs[1]) - 1
            while len(deck) < num:
                add = min(len(deck), num - len(deck))
                deck += deck[0:add]
                random.shuffle(deck)
            if len(deck) > num:
                deck = deck[:num]
        return {"command":commander, "library":deck}

def printHelp(*, extraArgs=[], **kwargs):
    """
    Print off the various options for a set of commands or all of them
    """
    if len(extraArgs) == 0:
        extraArgs = commands.keys()
    for arg in extraArgs:
        try:
            print(arg+')'+'\t'+commands[arg].__doc__.strip())
        except KeyError:
            print("Invalid Command "+arg)
        except Exception:
            pass
    return {}

def printList(*, battlefield=[], graveyard=[], command=[], **kwargs):
    """
    Display a list of everything owned/controlled by the Horde in public zones
    """
    print("Battlefield")
    for i, card in enumerate(battlefield):
        print("\tb"+str(i)+") "+card[0]+": "+card[1])

    print("\nGraveyard")
    for i, card in enumerate(graveyard):
        print("\tg"+str(i)+") "+card)

    print("\nCommand")
    if command is not None:
        print("\tc) "+command)

    return {}

def printBattlefield(*, battlefield=[], **kwargs):
    """
    List everything controlled by the Horde on the battlefield along with annotations
    """
    print("Just Battlefield")
    for i, card in enumerate(battlefield):
        print("\tb"+str(i)+") "+card[0]+": "+card[1])
    return {}

def quitHorde(**kwargs):
    """
    Quit the program
    """
    return {"cont": False}

def calcXCost(turnNumber):
    d = 2*turnNumber+4
    res = 1
    choice = d-1
    while choice == d-1:
        choice = random.randint(0,d-1)
        res += choice
    return res

def printXMana(*, turnNumber=1, **kwargs):
    """
    Show how much mana the Horde has for an X cost spell or ability
    """
    print("Have "+str(calcXCost(turnNumber))+" Mana available")
    return {}

def hordeTurn(*, battlefield=[], graveyard=[], library=[], hand=[], 
                 command=None, turnNumber=1, infinite=False, **kwargs):
    """
    Have the Horde take a turn consisting of playing out hand, revealing from top till nontoken,
    place all tokens onto the battlefield and cast the spell/permanent, then see if has enough mana
    for commander and if so cast that.
    """
    for card in hand:
        invalid = True
        while invalid:
            invalid = False
            cType = input("Type of "+card+" p(ermanent), s(pell): ")
            if cType.startswith('p'):
                battlefield.append((card, ""))
                print("Mana for X "+str(calcXCost(turnNumber)))
            elif cType.startswith('s'):
                graveyard.append(card)
                print("Mana for X "+str(calcXCost(turnNumber)))
            else:
                print("Invalid choice")
                invalid = True
    cont = True
    while cont and len(library) > 0:
        card = ""
        if infinite:
            card = random.choice(library)
        else:
            card = library.pop()
        invalid = True
        while invalid:
            invalid = False
            cType = input("Type of "+card+" p(ermanent), t(oken), s(pell): ")
            if cType.startswith('p'):
                battlefield.append((card, ""))
                print("Mana for X "+str(calcXCost(turnNumber)))
                cont = False
            elif cType.startswith('s'):
                graveyard.append(card)
                print("Mana for X "+str(calcXCost(turnNumber)))
                cont = False
            elif cType.startswith('t'):
                battlefield.append((card, ""))
            else:
                print("Invalid choice")
                invalid = True
    if command is not None:
        invalid = True
        cMana = calcXCost(turnNumber)
        while invalid:
            invalid = False
            cCast = input("Mana for Commander "+str(cMana)+" should cast y/n? ")
            if cCast.lower().startswith("y"):
                battlefield.append((command, ""))
                command=None
            elif cCast.lower().startswith("n"):
                pass
            else:
                print("Invalid choice")
                invalid = True
    print("Remember to do attacks and abilities")
    return {"hand":[], "command":command, "battlefield":battlefield,
            "graveyard":graveyard, "library": library, "turnNumber":turnNumber+1}

def countZones(*, battlefield=[], library=[], command=None, hand=[], graveyard=[],
        infinite=False, **kwargs):
    """
    Display a count of how many cards the Horde has in each zone
    """
    print("Battlefield:", len(battlefield))
    if infinite:
        print("Library: Infinite")
    else:
        print("Library:", len(library))
    print("Command:", 1 if command is not None else 0)
    print("Hand:", len(hand))
    print("Graveyard:", len(graveyard))
    return {}

def moveCard(*, battlefield=[], library=[], command=None, hand=[], graveyard=[],
                extraArgs=[], **kwargs):
    """
    Move a card by id from a public zone to a specified non-public zones. Available zones are
    g: graveyard, b: battlefield, c: command, l: library, h: hand, e:exile
    Exile is treated as stopping existing
    """
    if len(extraArgs) < 2:
        print("Too few arguments")
        return {}
    item = extraArgs[0]
    dest = extraArgs[1]
    if dest.lower()[0] not in ["g", "b", "c", "l", "h", "e"]:
        print("Invalid destination")
        return {}
    res = {}
    if item.startswith("g"):
        item = graveyard.pop(int(item[1:]))
        res["graveyard"] = graveyard
    elif item.startswith("b"):
        item = battlefield.pop(int(item[1:]))[0]
        res["battlefield"] = battlefield
    elif item.startswith("c"):
        item = command
        res["command"] = None
    elif item.startswith("n"):
        item = item[1:]
    else:
        print("Invalid item")
        return {}

    if dest.lower().startswith("g"):
        graveyard.append(item)
        res["graveyard"] = graveyard
    elif dest.lower().startswith("b"):
        battlefield.append(item)
        res["battlefield"] = battlefield
    elif dest.lower().startswith("c"):
        res["command"] = item
    elif dest.lower().startswith("l"):
        library.append(item)
        res["library"] = library
    elif dest.lower().startswith("h"):
        hand.append(item)
        res["hand"] = hand

    return res

def addAnnotation(*, battlefield=[], extraArgs=[], **kwargs):
    """
    Add an annotation to a given card on the battlefield specified by id
    """
    if len(extraArgs) < 2:
        print("Not enough arguments")
        return {}
    item = extraArgs[0]
    index = int(item[1:])
    if item[0] is not "b" or not (0 <= index < len(battlefield)):
        print("Invalid item")
        return {}
    annotation = " ".join(extraArgs[1:])
    battlefield[index] = (battlefield[index][0], annotation)
    return {"battlefield": battlefield}

def setInfinite(*, infinite=False, **kwargs):
    """
    Toggle infinite mode
    """
    return {"infinite":not infinite}

def takeDamage(*, library=[], graveyard=[], extraArgs=[], infinite=False, **kwargs):
    """
    Deal damage to the Horde, deals damage as milling cards
    """
    if len(extraArgs) < 1:
        print("Invalid Argument")
        return {}
    n = int(extraArgs[0])
    for i in range(n):
        item = ""
        if infinite:
            item = random.choice(library)
        else:
            item = library.pop()
        graveyard.append(item)
    return {"library":library, "graveyard": graveyard}

def drawCards(*, library=[], hand=[], extraArgs=[], infinite=False, **kwargs):
    """
    Let the Horde draw cards
    """
    if len(extraArgs) < 1:
        print("Invalid Argument")
        return {}
    n = int(extraArgs[0])
    for i in range(n):
        item = ""
        if infinite:
            item = random.choice(library)
        else:
            item = library.pop()
        hand.append(item)
    return {"library":library, "hand":hand}

def healLife(*, library=[], graveyard=[], extraArgs=[], infinite=False, **kwargs):
    """
    Have the Horde gain life, does so by putting the top cards of the graveyard into
    the library, NOTE: Doesn't shuffle you'll need to it yourself
    """
    if len(extraArgs) < 1:
        print("Invalid Argument")
        return {}
    n = int(extraArgs[0])
    for i in range(n):
        item = ""
        item = graveyard.pop()
        if not infinite:
            library.append(item)
    library = shuffleLibrary(library="library")["library"]
    return {"library":library, "graveyard": graveyard}

def printTurnNumber(*, turnNumber=1, **kwargs):
    """
    Display the current turn number
    """
    print("Turn: ", turnNumber)
    return {}

def printIsInfinite(*, infinite=False, **kwargs):
    """
    Display whether the Horde is currently in infinite mode
    """
    print("Infinite:", infinite)
    return {}

def addCard(*, battlefield=[], extraArgs=[], **kwargs):
    """
    Add a given card name to the battlefield under the Horde's control
    """
    if(len(extraArgs) < 1):
        print("Invalid Argument")
        return {}
    battlefield.append((" ".join(extraArgs), ""))
    return {"battlefield":battlefield}

def discardCards(*, hand=[], graveyard=[], extraArgs=[], infinite=False, **kwargs):
    """
    Move cards from the Horde's hand into their graveyard
    """
    if len(extraArgs) < 1:
        print("Invalid Argument")
        return {}
    n = int(extraArgs[0])
    if n > len(hand):
        n = len(hand)
    for i in range(n):
        item = ""
        item = hand.pop()
        if not infinite:
            graveyard.append(item)
    return {"hand":hand, "graveyard": graveyard}

def revealFromZone(*, extraArgs=[], **kwargs):
    """
    Reveal a set number of cards from the given zone. Applicable zones:
    g: graveyard, h: hand, l: library, b: battlefield
    """
    if len(extraArgs) < 2:
        print("Invalid Argument")
        return {}
    zones = {"g": "graveyard", "h": "hand", "l": "library", "b": "battlefield"}
    z = extraArgs[0]
    n = int(extraArgs[1])
    if z not in zones:
        print("Invalid Zone")
        return {}
    if n > len(kwargs[zones[z]]):
        n = len(kwargs[zones[z]])
    print(zones[z])
    for i in range(n):
        print(kwargs[zones[z]][i])
    return {}

def randomGen(*, extraArgs=[], **kwargs):
    """
    Randomly generate a number between and including the two arguments
    """
    if len(extraArgs) < 2:
        print("Invalid Arguments")
        return {}
    print(random.randint(int(extraArgs[0]), int(extraArgs[1])))
    return {}

def shuffleLibrary(*, library=[], **kwargs):
    """
    Shuffle the Horde's library
    """
    random.shuffle(library)
    return {"library": library}

def printAttacks(*, battlefield=[], extraArgs=[], **kwargs): 
    """
    Print's off each permanent controlled by the Horde followed by a random number
    between one and the argument to this. Allows easy computation of attacks
    """
    if len(extraArgs) < 1:
        print("Invalid Arguments")
        return {}
    n = int(extraArgs[0])
    for i in battlefield:
        print(i[0] + ' ' + str(random.randint(1,n)))
    return {}

commands = {
            "l": printList, "help": printHelp, "o": loadList, "q": quitHorde,
            "t": hordeTurn, "c":countZones, "x": printXMana, "i": setInfinite,
            'm':moveCard, "a":addAnnotation, "d": takeDamage, "h":healLife,
            "dr":drawCards, "lb": printBattlefield, "tu": printTurnNumber,
            "ac":addCard, "di": discardCards, "rz": revealFromZone, "r": randomGen,
            "s":shuffleLibrary, "at": printAttacks
           }
def playHorde():
    env = {
           "library": [], "battlefield": [], "graveyard": [], "hand": [], 
           "command": None, "cont": True, "turnNumber": 1, "infinite": False
          }
    while env["cont"]:
        command = input("- ")
        vals = command.split()
        try:
            env.update(commands[vals[0]](extraArgs=vals[1:], **env))
        except KeyError:
            print("Invalid command")
        except IndexError as e:
            print("Horde out of cards")
            print(e)
            env["cont"] = False
        except Exception as e:
            print(e)


playHorde()
