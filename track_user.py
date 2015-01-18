from pymongo import MongoClient
#from config2 import InstaConfig2
from config import InstaConfig,InstaConfig2,InstaConfig3,InstaConfig4,InstaConfig5
import time
from datetime import datetime

def get_collection(collection_name):
    client = MongoClient(machine_name,27020)
    db = client['moma2']
    collection = db[collection_name]
    return collection

def write_csv(stmt):
    f = open("tracked.csv","a")
    stmt = str(stmt) + ","
    f.write(stmt)
    f.close()
def get_untracked(users):
    f=open("tracked.csv")
    l=f.read()
    a=set(l.split(","))
    b=set(users)
    b_a = list(b - a)
    return b_a

if __name__ == '__main__':
    instagram=InstaConfig()
    app=0
    db_users=get_collection("moma2.past_users")
    db_posts=get_collection("moma2.past_users_timeline_posts")
    users= db_users.distinct("id")
    last_updated_time="";
    counted=0
    print len(users)
    users=get_untracked(users)
    print len(users)
    for uid in users:
        print "User Id"+str(uid)
        counted+=1
        exception  = False
        print "counted" +str(counted)
        if(counted%100 == 0):
            print "api switched"
            app = (app+1)%5
            if(app == 0):
                instagram = InstaConfig()
            elif(app==1):
                instagram = InstaConfig2()
            elif(app==2):
                instagram=InstaConfig3()
            elif(app==3):
                instagram=InstaConfig4()
            elif(app==4):
                instagram=InstaConfig5()
        time.sleep(0.5)
        last_updated=db_posts.find({"user.id":str(uid)}).sort("created_time",-1).limit(1)
        for last_time in last_updated:
            last_updated_time = datetime.utcfromtimestamp(float(last_time["created_time"]))
        print last_updated_time
        try:
            recent_posts,next_=instagram.api.user_recent_media(user_id=int(uid),count=300,min_timestamp=last_updated_time,return_json=True)
        except Exception as ex:
            print "api exception"
            print ex
            next_= None
            exception = True
            recent_posts=[]

        for recent_post in recent_posts:
            try:
                db_posts.insert(recent_post)
            except Exception as inst:
                print "exception"
                print inst
                exception = True
                break

        while next_:
            time.sleep(0.1)
            try:
                recent_posts,next_ = instagram.api.user_recent_media(with_next_url=next_,return_json=True,count=300)
            except Exception as ex:
                print "api exception"
                print ex
                recent_posts=[]
                next_ = False
            for recent_post in recent_posts:
                try:
                    db_posts.insert(recent_post)
                except Exception as inst:
                    print "exception"
                    print inst
                    exception = True
                    break
        if exception == False:
            write_csv(uid)

