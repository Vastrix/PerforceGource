#! /usr/bin/python
#By Vastrix for you
import subprocess, typing, re, datetime, optparse, colorama, sys

colorama.init()

DEPOT = ""
parser = optparse.OptionParser()
parser.add_option("-o", dest="output", default ="Gource.log",help="Where to store the output file")
(options, args) = parser.parse_args()

if not len(args)==1:
    print(colorama.Fore.RED+"I need you to give me your depot path, for example: //gamep_group01/"+colorama.Fore.RESET)
    sys.exit(1)
else:
    DEPOT = args[0]
    if not DEPOT[-1]=='/':
        DEPOT+='/'

try: #Idiot Proofing..
    a = open(options.output, 'w')
    a.close()
except:
    print(colorama.Fore.RED+"Check if {} is a correct accessible path, and that I have perms to write to it..".format(options.output)+colorama.Fore.RESET)
    sys.exit(1)


def FetchChanges(depot:str)->typing.List[str]:
    print(colorama.Fore.LIGHTBLACK_EX+"Fetching Changes..", end='')

    try:
        data = subprocess.check_output("p4 changes {}...".format(depot), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if(e.stderr.decode("utf-8", errors ="ignore").find("must refer to client")!=-1):
            print(colorama.Fore.RED+"According to this error P4 gave me, you don't have access to the {} depot!".format(DEPOT)+colorama.Fore.RESET)
        else:
            print(colorama.Fore.RED+'\n'+e.stderr.decode("utf-8", errors ="ignore")+colorama.Fore.RESET)
    else:

        data = data.decode("utf-8", errors ="ignore")
        print("DONE"+colorama.Fore.RESET)
        return [change for change in data.split('\n') if change]

    sys.exit(1)


def ParseChanges(changes:typing.List[str])->typing.List[str]:

    result = []

    getChange = re.compile(r"Change (\d+)", re.RegexFlag.IGNORECASE)
    nameDate = re.compile(r".*\s(\w*)@.*(\d{4,}\/\d{2}\/\d{2}\s.*)\s.*")
    fileAction = re.compile(r"\.\.\. (.*)#\d+\s(\w*).*", re.RegexFlag.MULTILINE)

    parsed = 1
    for change in changes:
        changeNum = int(re.match(getChange, change)[1]) #TODO: Checks..

        # multiplier = int(parsed/(len(changes)*.01))
        # print('['+'█'*multiplier+'　'*(100-multiplier)+']'+'\r') #Boi, I suck at ascii art
        print("Parsing ChangeNums [{}/{}]".format(parsed, len(changes)), end='\r')
        parsed+=1

        try:
            description = subprocess.check_output("p4 describe -s {}".format(changeNum), stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(colorama.Fore.RED+e.stderr.decode("utf-8", errors ="ignore")+colorama.Fore.RESET)
            sys.exit(1)
        else:
            description = description.decode("utf-8", errors ="ignore")

            name = re.match(nameDate, description)
            date = name[2] ; name = name[1]
            date = int(datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S\r").timestamp())

            description = description[description.rfind("Affected files ...\r\n\r\n")+len("Affected files ...\r\n\r\n"):] #Anti Injection
            fileActionMatches = re.findall(fileAction, description)
            for match in fileActionMatches:
                if match[1] not in "add edit delete branch integrate" : continue

                result.append("{}|{}|{}|{}".format(
                    date,
                    name,
                    'A' if match[1] in "add branch" else 'M' if match[1] in "edit integrate" else 'D' if match[1] == "delete" else match[1],
                    match[0]
                ))

    print('')
    result.reverse()
    return result


def Serialize(gourceChanges:typing.List[str]):
    print(colorama.Fore.LIGHTBLACK_EX+"Serializing..", end='')
    with open(options.output, 'w') as file:
        for change in gourceChanges:
            file.write(change+'\n')
    print("DONE"+colorama.Fore.RESET)

Serialize(ParseChanges(FetchChanges(DEPOT))) #Yeah, functions aren't really necessary for this, but meh
print(colorama.Fore.GREEN+"All went well it seems, Now you can simple add the log to the gource command line.\ngource.exe {}\n\no/".format(options.output)+colorama.Fore.RESET)