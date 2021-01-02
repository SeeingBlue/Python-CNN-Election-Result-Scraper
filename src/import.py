import requests, time, os, json, sqlite3, sys
from requests.exceptions import HTTPError
from datetime import datetime

def main():

    #Make sure we can connec to the db.
    sqlconn = sqlite3.connect("../report.db")
    if sqlconn == None:
        print("../report.db is missing.")
        exit(1)
    else:
        print("report.db found.")
        
    #Set a static value, use for some custom importing in the db.
    d = "2020-11-04 05:11:00.000000"

    #Open each file in the static directory and load .json into DB.
    for file in os.listdir("../snapshots/11-04-2020_05-11"):
        jsonResponse = open("../snapshots/11-04-2020_05-11/" + file)
        s = jsonResponse.read().strip()
        l = eval(s)
        if jsonResponse != None:            
            tokens = json.loads(json.dumps(l))
            for c in tokens:             
                for cands in c['candidates']:
                    if cands['lastNameSlug'] == 'trump':
                        trumpvotes = cands['voteNum']
                        trumppercent = cands['votePercentStr']
                    elif cands['lastNameSlug'] == 'biden':
                        bidenvotes = cands['voteNum']
                        bidenpercent = cands['votePercentStr']
                sqlconn.execute(f"INSERT INTO snapshots('timestamp', 'countyfip', 'reportedpercent', 'status', 'votets', 'ingested', 'stateid', 'bidenvotes', 'trumpvotes', 'bidenpercent', 'trumppercent') VALUES ('{d}', {c['countyFipsCode']}, '{c['percentReporting']}', '{c['editorialStatus']}', '{c['voteTimestamp']}', {c['ingestedAt']}, {c['stateId']}, {bidenvotes}, {trumpvotes}, '{bidenpercent}', '{trumppercent}');")

    sqlconn.commit()
    print("Records submitted.")

main()