
import json
import datetime

from libs.losses_utils import LossesUtils
from libs.utils import Utils



with open('config.json') as cfg:
    config = json.load(cfg)
    assert(config)


output_file = open('output.txt', 'w')
    

lu = LossesUtils(config)
u  = Utils(config)


# Most used ship of specified alliance
#for alliance in config['alliances']:
#    s = lu.query(config['alliances'][alliance])

    #print(alliance)

    
    #for i in s:
        #print(i.characterName, i.killID, i.killTime, i.kills)
        
  
        #print(i.killID, u.lookup_typename(i.shipTypeID), u.lookup_typename(i.kills.shipTypeID))
    
    
    #ships = sorted(lu.query_total(config['alliances'][alliance]), key=lambda x: x[1])

    #for q in ships:
    #    print(u.lookup_typename(q[0]), q[1])


# KNOWN FLEET COMPISITION 

for alliance in config['alliances']:

    # Dict of the ships used and the ship that was killed, grouped by killID
    kill_dict = {}

    # Dict of ship grouping only 
    ship_dict  = {}
    start_date = datetime.datetime.now() - datetime.timedelta(days=100)

    s = lu.query(config['alliances'][alliance], start_date=start_date)

    output_file.write('============= %s ============= \n\n\n' % (alliance))
    output_file.write('oldest record: %s' % (lu.oldest_record(config['alliances'][alliance], start_date)))

    for i in s:
        if i.killID not in kill_dict.keys():
            kill_dict[i.killID] = [{'used':u.lookup_typename(i.shipTypeID),'killed':u.lookup_typename(i.kills.shipTypeID)}]

        else:
            kill_dict[i.killID].append({'used':u.lookup_typename(i.shipTypeID), 'killed':u.lookup_typename(i.kills.shipTypeID)})

    for i in s:
        if i.killID not in ship_dict.keys():
            ship_dict[i.killID] = [u.lookup_typename(i.shipTypeID)]

        else:
            ship_dict[i.killID].append(u.lookup_typename(i.shipTypeID))

    for k in kill_dict.keys():
        output_file.write('\n\n')
        ships_used = []
        output_file.write('KILL ID: %s\n' % (k))

        output_file.write('Ship killed: %s\n' % (kill_dict[k][0]['killed']))
        for v in kill_dict[k]:
            ships_used.append(v['used'])
            #output_file.write('%s\n' % (v['used']))
            
        
        for ship in set(ships_used):
            c = ships_used.count(ship)
          
            if c > 0:
                output_file.write('%s %sx\n' % (ship, c))

            else:
                output_file.write('%s\n')


    s = lu.query(config['alliances'][alliance], start_date)

     
    ships = sorted(lu.query_total(config['alliances'][alliance], start_date), key=lambda x: x[1])


    output_file.write('\n\n')
    output_file.write('COMMONLY USED SHIPS (SHIP/NUMBER OF KILLS)\n')

    total_kills = 0
    for q in ships:
        total_kills += q[1]

    output_file.write('total kills accounted for: %s\n\n' % (total_kills))

    for q in ships:
        percentage = (100 * float(q[1])/float(total_kills))
        output_file.write('%s %s (%.2f%%)\n' % (u.lookup_typename(q[0]),q[1], percentage))

    #for s in ship_dict.keys():
    #    if len(ship_dict[s]) > 1:
    #        output_file.write('%s\n' % (ship_dict[s]))

    

#https://zkillboard.com/api/killID/56826868/
