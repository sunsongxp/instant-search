import redis
from complete import build_set, complete

r = redis.StrictRedis(host='1.1.1.2', port=6379, db=0)
r.flushall()
data = []
file = open('names', 'r')
for name in file:
    data.append(name.strip("\n"))

build_set(r, "tmp", data)

print "Start Testing..."

for name in data:
    results = complete(r, "tmp", name, 10)
    if results[0] != name:
        print "ERROR:", name, results
    #else:
    #    print "CORRECT:", name, results
