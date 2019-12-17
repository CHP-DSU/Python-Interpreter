#cybery looking prompt
import socket

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

# Error Codes
SERVER_IP = "172.16.68.101"
NO_ERROR = 0
MISSING_OPERATION = -1 
NO_INT_AFTER_POWER = 1
GROUP_STRUCT_ERROR = 2
SET_QUERY_CONFLICT = 3
LOAD_ONINE_CONFLICT= 4

# globals
error = NO_ERROR
realerror = ''
command = ''
prompt = bcolors.OKGREEN + bcolors.BOLD + "::> " + bcolors.OFF
commandFlags = {'set': 0, 'power': 0, 'powerLvl': 0, 'groups': 0, 'group#s': 0, 'query': 0, 'load': 0, 'online': 0}
firstArgs = {'set', 'help', 'query', 'q'}



def sendcommand(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = SERVER_IP
    port =8000
    s.connect((host,port))
    s.send(command.encode())
    data = s.recv(1024).decode()
    print (bcolors.OKGREEN + data)
    s.close()


def interpreter(text):
    #print(text)
    global error
    global realerror
    global command
    global commandFlags
    if not error == NO_ERROR:
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
            error = MISSING_OPERATION
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
            error = GROUP_STRUCT_ERROR
            realerror = e
            commandFlags['group#s'] = 0
    elif text[0] == 'query'or text[0] == 'q':
        commandFlags['query'] = 1
        command = command + 'Query: '
    elif text[0] == 'load':
        commandFlags['load'] = 1
        command = command + 'loading '
    elif text[0] == 'online':
        commandFlags['online'] = 1
        command = command + 'online '



    text.pop(0)
    interpreter(text)

def printHelp():
    print("=========== Help Page ===========                                                     ")
    print("#### set                                                                              ")
    print("                                                                                      ")
    print("Allows the hard setting of a state. Overrides previous state of the given             ")
    print("groups. 'set' defaults to all groups.                                                 ")
    print("                                                                                      ")
    print("Flags:                                                                                ")
    print("  power                                                                               ")
    print("    sets the power                                                                    ")
    print("    usage:  set power 85                                                              ")
    print("            (sets power to 85%)                                                       ")
    print(" group (groups)                                                                       ")
    print("    allows the user to specifiy groups, can be combined with power                    ")
    print("    usage:  set groups 1,2,3 power 75                                                 ")
    print("                                                                                      ")
    print("##### query (q)                                                                       ")
    print("                                                                                      ")
    print("Allows the user to request information of a given group. Defaults to all groups.      ")
    print("                                                                                      ")
    print("Flags:                                                                                ")
    print("  load                                                                                ")
    print("    retrives most up to date power usage on a given set of groups, defaults to global.")
    print("    usage: query load groups 1,7,2                                                    ")
    print("  online                                                                              ")
    print("    gets the status of devices and retrives what devices are online of a given group. ")
    print("    usage: query load online group 5                                                  ")
    print("                                                                                      ")
    print("## Console                                                                            ") 
    print("                                                                                      ")
    print("help                                                                                  ")
    print("  display the global help pages                                                       ")
    print("quit                                                                                  ")
    print("  quit the terminal                                                                   ")
    print("=================================                                                     ")
    return

def resetGlobal():
    global error
    global realerror
    global command
    global commandFlags
    error = NO_ERROR
    realerror = ''
    command = ''
    commandFlags = {'set': 0, 'power': 0, 'powerLvl': 0, 'groups': 0, 'group#s': 0, 'query': 0, 'load': 0, 'online': 0}

def ifValidFirst(first_command):
    if first_command in firstArgs:
        return True
    else:
        return False

def run():
    global error
    global realerror
    global command
    global commandFlags
    text = input(prompt + bcolors.OKBLUE).lower().split(' ')
    if text[0].strip('\n') == 'quit':
        return
    if not ifValidFirst( text[0].strip('\n') ):
        print(bcolors.FAIL + bcolors.BOLD + "ERROR: '" + bcolors.YELLOW + text[0].strip('\n') + bcolors.OFF + bcolors.FAIL + "' is not a valid command.")
    else:
        if text[0].strip('\n') == 'help':
            printHelp()
        interpreter(text)
        #print(commandFlags)

        if error == NO_ERROR:
                ###################################
                #               set               #
                ################################### 
            if commandFlags.get('set') == 1 and commandFlags.get('power') == 1 and commandFlags.get('powerLvl') == 1:
                if commandFlags.get('query') == 1:
                    error = SET_QUERY_CONFLICT
                    # tried to querry and set together. 
                elif commandFlags.get('groups') == 1:
                    if commandFlags.get('group#s') == 1:
                        #Send Command
                        print(bcolors.YELLOW + command)
                        try:
                            sendcommand(command)
                        except:
                            print(bcolors.FAIL + 'Connection Failed')
                    else:
                        error = MISSING_OPERATION
                else:
                    #Send Command
                    print(bcolors.YELLOW + command + 'to all groups. ')
                    try:
                        sendcommand(command)
                    except:
                        print(bcolors.FAIL + 'Connection Failed')

                ###################################
                #           query load            #
                ###################################    
            elif commandFlags.get('query') == 1 and commandFlags.get('load') == 1:
                if commandFlags.get('set') == 1:
                    error = SET_QUERY_CONFLICT
                    # tried to querry and set together. 
                if commandFlags.get('online') == 1:
                    error = LOAD_ONINE_CONFLICT
                elif commandFlags.get('groups') == 1:
                    if commandFlags.get('group#s') == 1:
                        print(bcolors.YELLOW + command)
                        try:
                            sendcommand(command)
                        except:
                            print(bcolors.FAIL + 'Connection Failed')
                    else:
                        error = MISSING_OPERATION
                else:
                    print(bcolors.YELLOW + command + 'all groups.')
                    try:
                        sendcommand(command)
                    except:
                        print(bcolors.FAIL + 'Connection Failed')

                ###################################
                #          query online           #
                ################################### 
            elif commandFlags.get('query') == 1 and commandFlags.get('online'):
                if commandFlags.get('set') == 1:
                    error = SET_QUERY_CONFLICT
                    # tried to querry and set together. 
                if commandFlags.get('load') == 1:
                    error = LOAD_ONINE_CONFLICT
                    # tried to querry load and online together. 
                elif commandFlags.get('groups') == 1:
                    if commandFlags.get('group#s') == 1:
                        print(bcolors.YELLOW + command)
                        try:
                            sendcommand(command)
                        except:
                            print(bcolors.FAIL + 'Connection Failed')
                    else:
                        error = MISSING_OPERATION
                else:
                    print(bcolors.YELLOW + command + 'all groups.')
                    try:
                        sendcommand(command)
                    except:
                        print(bcolors.FAIL + 'Connection Failed')




        if error == MISSING_OPERATION:
            print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Missing command operation")
        elif error == NO_INT_AFTER_POWER:
            print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Expecting integer after 'power'.")
        elif error == GROUP_STRUCT_ERROR:
            print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Invalid group structure. example: 'groups 1,4,5'.")
        elif error == SET_QUERY_CONFLICT:
            print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Cannot use 'set' and 'query' together.")
        elif error == LOAD_ONINE_CONFLICT:
            print(bcolors.FAIL + bcolors.BOLD + "ERROR:" + bcolors.OFF + bcolors.FAIL +" Cannot use 'load' and 'online' together.")

    resetGlobal()
    run()
 

if __name__== "__main__":
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("exit")
        exit()