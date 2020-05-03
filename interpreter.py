#!/usr/bin/python3

# Imports
import signal
from os import system
# Import sockets so that we can open up sockets to listen/send commands across ip 
import socket
import errno
from socket import error as socket_error

# Class for colors
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

# Constants
SERVER_IP = "172.16.68.100"
SERVER_PORT = 8001
TIMEOUT = 30

# Error Codes
NO_ERROR = 0
MISSING_OPERATION = -1 
NO_INT_AFTER_POWER = 1
GROUP_STRUCT_ERROR = 2
SET_QUERY_CONFLICT = 3
LOAD_ONINE_CONFLICT= 4

# Globals
error = NO_ERROR
realerror = ''
command = ''
prompt = bcolors.OKGREEN + bcolors.BOLD + "::> " + bcolors.OFF
commandFlags = {'set': 0, 'power': 0, 'powerLvl': -1, 'groups': 0, 'group#s': -1, 'query': 0, 'load': 0, 'online': 0}
firstArgs = {'set', 'help', 'query', 'q'}
percent = 0



# Function to create the session to connect to
# 
def sendcommand(sendcommand):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(TIMEOUT)
    try:
        global command
        # Define the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Define the host IP (IP of the server connecting to [is a string])
        host = SERVER_IP
        # Port the host is listening on
        port = SERVER_PORT
        # Connect using the socket, notices it uses the host and port given.
        try:
            s.connect((host,port))
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # Not the error we are looking for, re-raise
                raise serr
            else:
                print(bcolors.FAIL + 'Connection Failed')
                signal.alarm(0)
                return
        # Send the command. String must be encoded (sent as bytes). .encode does this for us. 
        s.send(sendcommand.encode())
        # Capture and recieved messege. Must decode (transfer from bytes to chars). 1024 means we can recieve 1024 bytes at most. Can be increased. 
        data = s.recv(1024).decode()
        # Print recieved message
        print (bcolors.OKGREEN + data)
        print(bcolors.YELLOW + command)
        data = s.recv(1024).decode()
        print (bcolors.FAIL + data)
        data = s.recv(1024).decode()
        print (bcolors.FAIL + data)
        signal.alarm(0)
        # Close the socket (kill connection). We do this for a variety of reasons. 
        # 1, We only want to have communication with the host when we decide. We dont want to constantly be listening/waiting to send if we dont have to. 
        # 2, Security, this way we ONLY listen when we open a connection to send a command. 
        # 3, Allows more devices to be able to talk with the host because we free up space when we are done setting a command. 
        # (At the current moment, the host can have up to 5 connections at any given time (realistically this will be plenty))
        s.close()
    except (OSError) as e:
        s.close()
    except (Exception) as e:
        print(e)
    signal.alarm(0)

def handler(signum, frame):
    print(bcolors.FAIL + 'Timed out waiting for response...')
    raise OSError("No second response!")

def interpreter(text):
    #print(text)
    # Global Variables
    global error
    global realerror
    #lets see what is happening here with the commands. 
    global command
    global commandFlags

    # Because we use recursion (which makes our life easier) we need to check if each iteration has an error. 
    # This will just stop us from running into any issues along the way.
    if not error == NO_ERROR:
        return
    # Check if we have no more words to process. 
    if len(text) == 0:
        return
    # Check if our current word is '___'
    if text[0] == 'set':
        commandFlags['set'] = 1
    elif text[0] == 'power':
        commandFlags['power'] = 1
        #put a try catch here to see what is going on with the command flags
        try:
            percent = int(text[1].strip('\n'))
            text.pop(0)
            commandFlags['powerLvl'] = percent
        except (ValueError, IndexError) as e:
            error = MISSING_OPERATION
            realerror = e
            commandFlags['powerLvl'] = -1
    elif text[0] == 'group' or text[0] == 'groups' or text[0] == 'g':
        commandFlags['groups'] = 1
        try:
            groupList = text[1].split(',')
            #this glag will check to see if we get the groups flags
            commandFlags['group#s'] = ''
            for g in groupList:
                intg = int(g)
                commandFlags['group#s'] += str(intg) + ','
            text.pop(0)
        except (ValueError, IndexError) as e:
            error = GROUP_STRUCT_ERROR
            realerror = e
            commandFlags['group#s'] = -1
    elif text[0] == 'query'or text[0] == 'q':
        commandFlags['query'] = 1
    elif text[0] == 'load':
        commandFlags['load'] = 1
    elif text[0] == 'online':
        commandFlags['online'] = 1
    else:
        print(bcolors.FAIL + "'" +text[0] + "' is an invalid operand.")
        return
    # Remove the first word. 
    text.pop(0)
    # Pass in the rest of the string. (If it is empty it will still pass it).
    interpreter(text)

# Print the help page. Not the easiest way to do it at the moment. Temporary, but is not a long term solution.
# A good long term solution would be to write all of this stuff to a text document. This would allow the file to 
# be edited much easier. We could then just print the content of the text file. 
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

# anything that needs to be reset after run() (command line reset, so that we can reuse the custom command line)
def resetGlobal():
    global error
    global realerror
    global command
    global commandFlags
    global percent
    error = NO_ERROR
    realerror = ''
    command = ''
    commandFlags = {'set': 0, 'power': 0, 'powerLvl': -1, 'groups': 0, 'group#s': -1, 'query': 0, 'load': 0, 'online': 0}
    percent = 0

# Check if the first word you entered if in a valid list of words. This is a temporary(maybe) way to check if a command is valid. 
# Commands are all based off of the first word anyway. ('set power 5' is determined off of the word 'set') So if the first
# words isnt in the approved list, we dont allow that command to continue. 
def ifValidFirst(first_command):
    if first_command in firstArgs:
        return True
    else:
        return False

# Read the dict that stores all of our flags / variable of our command.
# We use this method because it allows us to make sure we are reading it in the order we want. 
# By reading it in the order we want, we can thus build a command string in the order that we read from. 
# This also has a second layer of protection against inproper comand structure. If we come accross a command
# that dosent have a flag flipped that needs to be, this will not fill in the command with inproper stuff.se
def readDict(cmdDict):
    global command
    sendCommand = ''
    if cmdDict.get('set') != 0:
        sendCommand += 'set '
        command += 'Setting '
        if cmdDict.get('power') != 0:
            sendCommand += 'power '
            command += 'power '
            if cmdDict.get('powerLvl') != -1:
                sendCommand += str(cmdDict.get('powerLvl')) + ' '
                command += 'to ' + str(cmdDict.get('powerLvl')) + '% '
                if cmdDict.get('groups') != 0:
                    sendCommand += 'in '
                    command += 'in '
                    if cmdDict.get('group#s') != -1:
                        sendCommand += 'group(s) ' + str(cmdDict.get('group#s').strip(','))
                        command += 'group(s) ' + str(cmdDict.get('group#s').strip(',')) + '.'
                    else:
                       sendCommand += 'all groups'
                       command += 'all groups.'
                else:
                    sendCommand += 'in all groups'
                    command += 'in all groups.'
    elif(cmdDict.get('query')!= -1):
        sendCommand = 'query'
        command = 'Querrying device...'
    return sendCommand
    
def sender(flags):
    send = readDict(flags)
    sendcommand(send)

def run():
    global error
    global realerror
    global command
    global commandFlags
    resetGlobal()
    text = input(prompt + bcolors.OKBLUE).lower().split(' ')
    if text[0].strip('\n') == 'quit' or text[0].strip('\n') == 'exit':
        return
    elif text[0] == 'clear':
        _ = system('clear')
    elif text[0] == '':
        resetGlobal()
    elif not ifValidFirst( text[0].strip('\n') ):
        print(bcolors.FAIL + bcolors.BOLD + "ERROR: '" + bcolors.YELLOW + text[0].strip('\n') + bcolors.OFF + bcolors.FAIL + "' is not a valid command.")
    else:
        if text[0].strip('\n') == 'help':
            printHelp()
        interpreter(text)
        #print(commandFlags)

        # After intperpreter is done running lets figure out what to do:
        if error == NO_ERROR:
                ###################################
                #               set               #
                ################################### 
            if commandFlags.get('set') == 1 and commandFlags.get('power') == 1 and commandFlags.get('powerLvl') != -1:
                if commandFlags.get('query') == 1:
                    error = SET_QUERY_CONFLICT
                    # tried to querry and set together. 
                elif commandFlags.get('groups') == 1:
                    if commandFlags.get('group#s') != -1:
                        #Send Command
                        sender(commandFlags)
                    else:
                        error = MISSING_OPERATION
                else:
                    #Send Command
                        sender(commandFlags)

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
                    if commandFlags.get('group#s') != -1:
                        sender(commandFlags)
                    else:
                        error = MISSING_OPERATION
                else:
                    sender(commandFlags)

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
                    if commandFlags.get('group#s') != -1:
                        sender(commandFlags)
                    else:
                        error = MISSING_OPERATION
                else:
                    sender(commandFlags)


        #Print our error codes. 
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
   # print(commandFlags)
   # send = readDict(commandFlags)
   # print(send)
    resetGlobal()
    run()
 
# Main
if __name__== "__main__":
    _ = system('clear')
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("exit")
        exit()