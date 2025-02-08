import re
import shlex
import subprocess
from main import path_to_wordlist, path_to_johnpot, path_to_johnrec

def calc_password_strength(password):
    score = 0
    if len(password) >= 8:
        score +=1
    if len(password) >= 16:
        score +=1
    if len(password) >= 20:
        score +=1
    if len(password) >= 25:
        score +=1
    if re.search(r'[A-Z]', password):
        score += 1

    # Check for lowercase letters
    if re.search(r'[a-z]', password):
        score += 1

    # Check for digits
    if re.search(r'\d', password):
        score += 1

    # Check for special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 1:
        return "Very Weak"
    elif score == 2:
        return "Weak"
    elif score == 3:
        return "Moderate"
    elif score == 4:
        return "Strong"
    elif score >= 5:
        return "Very Strong"

def generate_command(password, hash_algorithm, hash_digest, prog, method):
    if "hashcat" in prog:
        if "MD5" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "stdbuf -oL hashcat -a 0 -m 0 {0} {1} --potfile-path /dev/null".format(hash_digest, path_to_wordlist)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    pattern = "?a"
                    mask = ""
                    for char in password:
                        mask += pattern
                    print(mask)
                    command = "hashcat -a 3 -m 0 {0} {1} --potfile-path /dev/null".format(hash_digest, mask)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass
        if "SHA2" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "stdbuf -oL hashcat -a 0 -m 1400 {0} {1} --potfile-path /dev/null".format(hash_digest, path_to_wordlist)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    pattern = "?a"
                    mask = ""
                    for char in password:
                        mask += pattern
                    print(mask)
                    command = "stdbuf -oL hashcat -a 3 -m 1400 {0} {1} --potfile-path /dev/null".format(hash_digest, mask)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass
        if "bcrypt" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "stdbuf -oL hashcat -a 0 -m 3200 {0} {1} --potfile-path /dev/null".format(hash_digest, path_to_wordlist)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    pattern = "?a"
                    mask = ""
                    for char in password:
                        mask += pattern
                    print(mask)
                    command = "stdbuf -oL hashcat -a 3 -m 3200 {0} {1} --potfile-path /dev/null".format(hash_digest, mask)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass
    if "john" in prog:
        if path_to_johnpot.exists():
            delete_command = "rm {0}".format(path_to_johnpot)
            shlex_command = shlex.split(delete_command)
            subprocess.run(shlex_command)
        if path_to_johnrec.exists():
            delete_command = "rm {0}".format(path_to_johnrec)
            shlex_command = shlex.split(delete_command)
            subprocess.run(shlex_command)
        with open("hash.txt", "w") as f:
                f.write(hash_digest)
        if "MD5" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "john hash.txt --format=Raw-MD5 --wordlist={0} --pot={1}".format(path_to_wordlist, path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    command = "john hash.txt --format=Raw-MD5 --incremental --min-length={0} --pot={1}".format(len(password), path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass
        if "SHA2" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "john hash.txt --format=Raw-SHA256 --wordlist={0} --pot={1}".format(path_to_wordlist, path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    command = "john hash.txt --format=Raw-SHA256 --incremental --min-length={0} --pot={1}".format(len(password), path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass
        if "bcrypt" in hash_algorithm:
            match method:
                case "dictionary":
                    command = "john hash.txt --format=bcrypt --wordlist={0} --pot={1}".format(path_to_wordlist, path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "brute-force":
                    command = "john hash.txt --format=bcrypt --incremental --min-length={0} --pot={1}".format(len(password), path_to_johnpot)
                    shlex_command = shlex.split(command)
                    return shlex_command
                case "Rules (best64)":
                    #To be implemented
                    pass