import json

song = ""

need_moderate = False

with open(f"./songs/{song}/chart.json", "r") as f:
    jdata = json.load(f)

with open(f"./songs/{song}/chart.txt", "w", encoding="utf-8") as file:
    last = -1
    
    for one_note in jdata["notes"]:
        moderate = (60000/jdata["BPM"]) if need_moderate else 0
        k3 = 60/(jdata["BPM"]*one_note["LPB"])
        beatsec = k3 * one_note["LPB"]
        arrive_time = int(1000*beatsec*one_note["num"]/one_note["LPB"] + moderate)
        block = one_note["block"]

        if last == arrive_time:
            file.write(f",{block}")
        else:
            if last != -1: file.write("\n")
            last = arrive_time
            file.write(f"{arrive_time} {block}")
    
