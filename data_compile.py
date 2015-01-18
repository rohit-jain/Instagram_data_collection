from pymongo import MongoClient
from math import radians, cos, sin, asin, sqrt
import csv,sys
from datetime import datetime

def get_collection(collection_name):
    client = MongoClient(machine_name,27020)
    db = client['moma2']
    collection = db[collection_name]
    return collection

def write_post(mention):
    data_file = open('data.tsv','a')
    writer = csv.writer(data_file, delimiter = '\t')
    if mention["location"] == None:
        return
    un = mention["user"]["username"]
    pid = mention["_id"]
    filter_type = mention["filter"]
    link = mention["link"]
    try:
        lat = mention["location"]["latitude"]
        lon = mention["location"]["longitude"]
    except:
        lat = ""
        lon = ""
    created_time = mention["created_time"]
    comments = mention["comments"]["count"]
    likes = mention["likes"]["count"]
    try:
        cap_text = mention["caption"]["text"]
    except:
        cap_text = ""
    row = [str(un), str(pid), str(filter_type), str(link), str(lat), str(lon), str(created_time), str(comments), str(likes), cap_text.encode('utf-8')]
    #print row[0],row[1],row[2],row[3]
    writer.writerow(row)
    data_file.flush()
    data_file.close()

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km

def in_nyc(ll,lll):
    city_lat = 40.706667
    city_lon = -73.866383
    latitude=ll
    longitude = lll
    distance = (haversine(city_lat, city_lon, latitude, longitude))
    return (distance < 20)

def write_log(statement):
    log_file = open("past.log",'a')
    statement = str(statement) + "\n"
    log_file.write(statement)
    log_file.close()

def write_resident(uid):
    res_file=open("res.csv",'a')
    uid = (str(uid) + ",")
    res_file.write(uid)
    res_file.close()

def get_users():
    #all_users=db_users.distinct("id")
    f=open("tracked_users.csv")
    l=f.read()
    a=set(l.split(","))
    return list(a)

def write_tracked(uid):
    res_file=open("tracked_data.csv",'a')
    uid = (str(uid) + ",")
    res_file.write(uid)
    res_file.close()

def get_untracked(users):
    f=open("tracked_data.csv")
    l=f.read()
    a=set(l.split(","))
    b=set(users)
    b_a = list(b - a)
    return b_a

def get_residents(users,db_posts):
    resident = []
    users = get_untracked(users)
    users_processed = 0
    for uid in users:
        print uid
        write_log(uid)
        users_processed +=1
        print "processing user " + str(users_processed)
        print datetime.now()
        #posts = db_posts.find({"user.id":str(uid)}).limit(50)
        #print datetime.now()
        nyc = {}
        count=0
        count_exception = 0
        print "processing posts"
        #for post in posts:
        for post in list(db_posts.find({"user.id":str(uid)})):
            try:
                l=post["location"]
                if l==None:
                    #write_log("first null exception")
                    count_exception+=1
                    #break
                else:
                    ll=post["location"]["latitude"]
                    lll=post["location"]["longitude"]
                    if ll!=None and lll!=None:
                        if in_nyc(ll,lll):
                        #print "in city on"
                            #try:
                                #print post['created_time']
                            nyc[datetime.utcfromtimestamp(float(post['created_time'])).date()]  = True
                            #except:
                            #    nyc["0"] = True
                            #    write_log( "Time Null")
                            #    write_log( post )
                    else:
                        #write_log("preliminary location none exception")
                        count_exception+=1
                        #print len(nyc)
            except KeyError:
            #else:
                #write_log("preliminary location exception")
                count_exception+=1
            #print datetime.now()
            if  len(nyc) >= 15:
                write_resident(uid)
                print "resident " + str(uid)
                resident += [str(uid)]
                break
            #if(count_exception>=3):
            #    print "skipped"
                #write_log("user skipped because of exception")
            #    break
        write_tracked(uid)
        if len(nyc) < 15:
            print "non-resident " + str(uid) 
    return resident

if __name__ == '__main__':
    db_users = get_collection("moma2.past_users")
    db_posts = get_collection("moma2.past_users_mention")
    db_timelines = get_collection("moma2.past_users_timeline_posts")
    #users = db_users.distinct("id")
    users = get_users()
    print len(users)
    residents = get_residents(users, db_timelines)
    print len(residents)
    for user in residents:
        mentions = list(db_posts.find({"user.id":str(user)}).limit(1))
        count = 0
        if(mentions != []):
            #write mention to file
            row = []
            write_post(mentions[0])
            #get timeline from user_posts
            for mention in db_timelines.find({"user.id":str(user)}):
                count+=1
                #write to file
                write_post(mention)
        print count
