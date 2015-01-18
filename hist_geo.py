from math import radians, cos, sin, asin, sqrt
from instagram.client import InstagramAPI
import sys, csv, datetime, time
from config import InstaConfig, Mongo

def insert(item,db_name):
    try:
        db_name.insert(item)
    except Exception as inst:
        print "========EXCEPTION============"
        print inst
        pass

def write_csv(stmt):
    f = open("tracked_users.csv","a")
    stmt = str(stmt) + ","
    f.write(stmt)
    f.close()

def search(api, dist, start_lat, start_lng, mint, maxt, store):
    time.sleep(0.2)
    db = Mongo()
    last_time = 0
    n_responses=0
    print "Searching"
    for mention in api.media_search(distance=dist,return_json=True,lat=start_lat,lng=start_lng, min_timestamp=mint, max_timestamp=maxt,count=200):
        n_responses+=1
        user = mention["user"]
        last_time = mention["created_time"]
        username = mention["user"]["username"]
        write_csv(mention["user"]["id"])
        insert(user,db.past_users)
        insert(mention,db.past_user_mention)
    print n_responses
    return last_time

def main():
    writer = csv.writer(file(sys.argv[1], 'wb'), delimiter = '\t')
    trip_start_time  = 1418515200 #12-14-2015
    trip_stop_time = 1420329600 #1-4-2015
    region1_lat = 40.761380
    region1_lon = -73.977209
    #array of client ids
    cid = []
    api = InstagramAPI(client_id = cid[0])
    store = {}
    last_time = trip_stop_time
    print "starting"
    search_count=0
    i=0
    while trip_start_time < trip_stop_time:
        try:
            temp_trip_stop_time = search(api, 75, region1_lat, region1_lon, trip_start_time, trip_stop_time, store)
            search_count+=1
            if(search_count%50 == 0):
                i= (i+1)%len(cid)
                api = InstagramAPI(client_id = cid[i])
                print "switched"
            print "search " + str(search_count)
            print "Time returned from search"
            print datetime.datetime.utcfromtimestamp(int(temp_trip_stop_time))
            print "Time sent to api"
            print datetime.datetime.utcfromtimestamp(int(trip_stop_time))
            temp_trip_stop_time = int(temp_trip_stop_time)
            trip_stop_time = int(trip_stop_time)
            #print int(temp_trip_stop_time) >= int(trip_stop_time)
            if temp_trip_stop_time >= trip_stop_time:
                trip_stop_time = int(trip_stop_time) - 1
                print "change time"
                print datetime.datetime.utcfromtimestamp(int(trip_stop_time))
            else:
                trip_stop_time = temp_trip_stop_time
        except:
            print "Exception"
            break

main()
