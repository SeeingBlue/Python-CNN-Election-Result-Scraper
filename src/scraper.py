import requests, time, os, json, sqlite3
from requests.exceptions import HTTPError
from datetime import datetime

#array of all 50 states to iterate
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

def main():

    #make sure we can connect to the db
    sqlconn = sqlite3.connect("../report.db")
    if sqlconn == None:
        print("../report.db is missing.")
        exit(1)
    else:
        print("report.db found.")
        
    #set date to now for storage in snapshot
    d = datetime.now()

    #iterate states array
    for s in states:

        #get the json string for each state
        jsonResponse = getJson(s)

        #make sure we got results
        if jsonResponse != None:
            print(f"Processing {s}.")
            tokens = json.loads(jsonResponse)

            #iterate json array
            for c in tokens: 

                #set only biden and trump variables.             
                for cands in c['candidates']:
                    if cands['lastNameSlug'] == 'trump':
                        trumpvotes = cands['voteNum']
                        trumppercent = cands['votePercentStr']
                    elif cands['lastNameSlug'] == 'biden':
                        bidenvotes = cands['voteNum']
                        bidenpercent = cands['votePercentStr']

                #don't need first line after inital insert, second line updates snapshot table.
                #sqlconn.execute("INSERT INTO counties('fip', 'name', 'jurisdiction', 'stateabbr', 'statename', 'stateslug') VALUES ({countyFipsCode}, '{countyName}', {jurisdictionCode}, '{stateAbbreviation}', '{stateName}', '{stateNameSlug}');".format(countyFipsCode=c['countyFipsCode'], countyName=str(c['countyName']).replace("'","''"), jurisdictionCode=c['jurisdictionCode'], stateAbbreviation=c['stateAbbreviation'], stateName=c['stateName'], stateNameSlug=c['stateNameSlug']))
                sqlconn.execute(f"INSERT INTO snapshots('timestamp', 'countyfip', 'reportedpercent', 'status', 'votets', 'ingested', 'stateid', 'bidenvotes', 'trumpvotes', 'bidenpercent', 'trumppercent') VALUES ('{d}', {c['countyFipsCode']}, '{c['percentReporting']}', '{c['editorialStatus']}', '{c['voteTimestamp']}', {c['ingestedAt']}, {c['stateId']}, {bidenvotes}, {trumpvotes}, '{bidenpercent}', '{trumppercent}');")

    sqlconn.commit()
    print("Records submitted.")

def getJson(s):
    try:

        #checking cnn api for state and county voter data
        url = "https://politics-elex-results.data.api.cnn.io/results/view/2020-county-races-PG-"
        time.sleep(1)
        url = url + s + ".json"
        response = requests.get(url)
        response.raise_for_status()
        return(response.text)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return(None)
    except Exception as err:
        print(f'Other error occurred: {err}') 
        return(None)

main()