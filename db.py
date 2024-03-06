import requests
import json
import random
import time

class Lockout:
    def __init__(self,name,initial_rating,no_of_problems,lockout_length):
        self.name=name
        self.initial_rating=initial_rating
        self.no_of_problems=no_of_problems
        self.problems=[]
        self.generate_problems()
        self.users=[]
        self.handles=[]
        self.start_time=""
        self.has_started=False
        self.has_ended=False
        self.lockout_length=lockout_length*3600
        self.max_points=0
        self.maximum_attainable_points=(self.no_of_problems*(self.no_of_problems+1)/2)*100

    def generate_problems(self):
        res=json.loads(requests.get("https://codeforces.com/api/problemset.problems").text)
        problems=res['result']['problems'][:2000]
        ratings=[i for i in range(self.initial_rating,self.initial_rating+100*self.no_of_problems,100)]
        problems_dict={i:[] for i in ratings}
        for i in problems:
            try:
                problems_dict[i['rating']].append({
                    "name":i['name'],
                    "url":f"https://codeforces.com/problemset/problem/{i['contestId']}/{i['index']}"
                })
            except:
                continue
        for i in ratings:
            prob=random.choice(problems_dict[i])
            self.problems.append({
                "name":prob['name'],
                "url":prob['url'],
                "points":i-self.initial_rating+100,
                "solved":False,
                "solved_by":"",
                "solved_at":""
            })
        print(self.problems)
    def get_problems(self):
        problem_list=[{
            "name":i['name'],
            "url":i['url'],
            "solved_by":i['solved_by'],
            "points":i['points']
        } for i in self.problems]
        return problem_list
    
    def end_lockout(self):
        has_started=False
        has_ended=True

    def join_user(self,discord_user,cf_handle):
        self.users.append({
            "name":discord_user,
            "cf_handle":cf_handle,
            "points":0
        })
    
    def start_lockout(self):
        self.start_time=time.time()
        self.has_started=True
        return self.get_problems()
    
    def get_leaderboard(self):
        leaderboard=[]
        for i in self.users:
            leaderboard.append([i["points"],i["cf_handle"]])
        return sorted(leaderboard,reverse=True)
    
    def update_points(self,username,new_points):
        print(username,new_points)
        for i in self.users:
            if(i['cf_handle']==username):
                i['points']+=new_points
                self.max_points=max(self.max_points,i['points'])

    def get_points(self,username):
        for i in self.users:
            if(i['cf_handle']==username):
                return i['points']

    def get_users(self):
        return [i["cf_handle"] for i in self.users]

    def check_accepted_in_last_20(self,username,problems):
        res=requests.get(f"https://codeforces.com/api/user.status?handle={username}&from=1&count=20")
        res=json.loads(res.text)
        solved={}
        for i in res['result']:
            if(i['problem']['name'] in problems):
                if(i['verdict']=="OK"):
                    solved[i['problem']['name']]=i["creationTimeSeconds"]
                    print(f"{username} solved {i['problem']['name']}")
        return solved

    def update(self):
        print("updating")
        user_list=self.get_users()
        is_solved={}
        for i in user_list:
            print(f"checking {i}")
            problemset=[j["name"] for j in self.problems]
            solved=self.check_accepted_in_last_20(i,problemset)
            for j in self.problems:
                try:
                    time_solved=solved[j['name']]
                    if(not j["solved"]):
                        j["solved"]=True
                        j["solved_by"]=i
                        j["solved_at"]=time_solved
                        is_solved[j["name"]]=i
                        self.update_points(i,j["points"])
                    else:
                        if(j["solved_at"]>time_solved):
                            self.update_points(j["solved_by"],-j["points"])
                            j["solved_by"]=i
                            is_solved[j["name"]]=i
                            j["solved_at"]=time_solved
                            self.update_points(i,j["points"])
                except:
                    pass
            time.sleep(2)
        return is_solved
