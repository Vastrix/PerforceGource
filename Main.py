#! /usr/bin/python
#By Vastrix for you
import subprocess, typing, re, datetime, optparse, colorama, sys

colorama.init()

DEPOT = ""
parser = optparse.OptionParser()
parser.add_option("-o", dest="output", default ="Gource.log",help="Where to store the output file")
parser.add_option("-c", dest="captions", default = "", help="Caption file (if any)\nCaptions will be the commit messages")
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
if(options.captions):
    try: #Idiot Proofing..
        a = open(options.captions, 'w')
        a.close()
    except:
        print(colorama.Fore.RED+"Check if {} is a correct accessible path, and that I have perms to write to it..".format(options.captions)+colorama.Fore.RESET)
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


def ParseChanges(changes:typing.List[str])->typing.List[typing.List[str]]:

    result = []
    resultCaptions = []

    getChangeNumDesc = re.compile(r"Change (\d+).*'(.*)'", re.RegexFlag.IGNORECASE)
    nameDate = re.compile(r".*\s(\w*)@.*(\d{4,}\/\d{2}\/\d{2}\s.*)\s.*")
    fileAction = re.compile(r"\.\.\. (.*)#\d+\s(\w*).*", re.RegexFlag.MULTILINE)
    description = re.compile(r"^\t((?:.|\n|\r)+)\nAffected", re.RegexFlag.MULTILINE)

    parsed = 1
    for change in changes:
        match = re.match(getChangeNumDesc, change)
        changeNum = int(match[1]) #TODO: Checks..

        # multiplier = int(parsed/(len(changes)*.01))
        # print('['+'█'*multiplier+'　'*(100-multiplier)+']'+'\r') #Boi, I suck at ascii art
        print("Parsing ChangeNums [{}/{}]".format(parsed, len(changes)), end='\r')
        parsed+=1

        try:
            descResult = subprocess.check_output("p4 describe -s {}".format(changeNum), stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(colorama.Fore.RED+e.stderr.decode("utf-8", errors ="ignore")+colorama.Fore.RESET)
            sys.exit(1)
        else:
            descResult = descResult.decode("utf-8", errors ="ignore")
            desc = re.search(description, descResult[:descResult.rfind("Affected files ...\r")+20])[1].replace('\n', '').replace('\r', '')

            name = re.match(nameDate, descResult)
            date = name[2] ; name = name[1]
            date = int(datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S\r").timestamp())
            resultCaptions.append("{}|{}".format(date, desc))

            descResult = descResult[descResult.rfind("Affected files ...\r\n\r\n")+len("Affected files ...\r\n\r\n"):] #Anti Injection
            fileActionMatches = re.findall(fileAction, descResult)
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
    resultCaptions.reverse()
    return [result, resultCaptions]


def Serialize(gourceChanges:typing.List[typing.List[str]]):
    print(colorama.Fore.LIGHTBLACK_EX+"Serializing log..", end='')
    with open(options.output, 'w') as file:
        for change in gourceChanges[0]:
            file.write(change+'\n')
    print("DONE"+colorama.Fore.RESET)

    if(options.captions):
        print(colorama.Fore.LIGHTBLACK_EX + "Serializing captions..", end='')
        with open(options.captions, 'w') as file:
            for change in gourceChanges[1]:
                file.write(change + '\n')
        print("DONE"+colorama.Fore.RESET)

Serialize(ParseChanges(FetchChanges(DEPOT))) #Yeah, functions aren't really necessary for this, but meh
print(colorama.Fore.GREEN+"All went well it seems, Now you can simple add the log to the gource command line.\ngource.exe {}\n\no/".format(options.output)+colorama.Fore.RESET)