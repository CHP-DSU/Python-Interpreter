#cybery looking prompt
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    OFF = "\033[0;0m"

error = 0
realerror = ''
command = ''
commandFlags = {'set': 0, 'power': 0, 'powerLvl': 0, 'groups': 0, 'group#s': 0, 'query': 0, 'load': 0, 'online': 0}

def interpreter(text):
    #print(text)
    global error
    global realerror
    global command
    global commandFlags
    if not error == 0:
        return
    if len(text) == 0:
        return
    if text[0] == 'set':
        commandFlags['set'] = 1
        command = command + 'Setting '
    elif text[0] == 'power':
        commandFlags['power'] = 1
        try:
            percent = int(text[1].strip('\n'))
            command = command + 'power to ' + str(percent) + '% '
            text.pop(0)
            commandFlags['powerLvl'] = 1
        except (ValueError, IndexError) as e:
            error = 1
            realerror = e
            commandFlags['powerLvl'] = 0
    elif text[0] == 'group' or text[0] == 'groups':
        commandFlags['groups'] = 1
        try:
            command = command + 'group(s) '
            groupList = text[1].split(',')
            for g in groupList:
                intg = int(g)
                command = command + str(intg)+ ' '
            text.pop(0)
            commandFlags['group#s'] = 1
        except (ValueError, IndexError) as e:
            error = 2
            realerror = e
            commandFlags['group#s'] = 0
    elif text[0] == 'query'or text[0] == 'q':
        commandFlags['query'] = 1
        command = command + 'Query: '
    elif text[0] == 'load':
        commandFlags['load'] = 1
        command = command + 'loading '



    text.pop(0)
    interpreter(text)

def printHelp():
    print("Help Page:")
    return

def resetGlobal():
    global error
    global realerror
    global command
    global commandFlags
    error = 0
    realerror = ''
    command = ''
    commandFlags = {'set': 0, 'power': 0, 'powerLvl': 0, 'groups': 0, 'group#s': 0, 'query': 0, 'load': 0, 'online': 0}

def run():
    global error
    global realerror
    global command
    global commandFlags
    text = input(bcolors.OKGREEN + bcolors.BOLD + '=> ' + bcolors.OFF + bcolors.OKBLUE).lower().split(' ')
    if text[0].strip('\n') == 'quit':
        return
    if text[0].strip('\n') == 'help':
        printHelp()
    interpreter(text)
    #print(commandFlags)

    if error == 0:
            #######
            # set #
            #######
        if commandFlags.get('set') == 1 and commandFlags.get('power') == 1 and commandFlags.get('powerLvl') == 1:
            if commandFlags.get('query') == 1:
                error = 3
                # tried to querry and set together. 
            elif commandFlags.get('groups') == 1:
                if commandFlags.get('group#s') == 1:
                    print(bcolors.YELLOW + command)
                else:
                    error = -1
            else:
                print(bcolors.YELLOW + command + 'to all groups. ')
        elif commandFlags.get('query') == 1 and commandFlags.get('load'):
            if commandFlags.get('set') == 1:
                error = 3
                # tried to querry and set together. 
            elif commandFlags.get('groups') == 1:
                if commandFlags.get('group#s') == 1:
                    print(bcolors.YELLOW + command)
                else:
                    error = -1
            else:
                print(bcolors.YELLOW + command + 'all groups.')



    if error == -1:
        print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Missing command operation")
    elif error == 1:
        print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Expecting integer after 'power'.")
    elif error == 2:
        print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Invalid group structure. example: 'groups 1,4,5'.")
    elif error == 3:
        print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Cannot use 'set' and 'query' together.")

    resetGlobal()
    run()
 

if __name__== "__main__":
     run()
