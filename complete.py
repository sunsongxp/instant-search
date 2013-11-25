import redis

def build_set(set_to_build):
    r = redis.StrictRedis(host="1.1.1.2", port=6379, db=0)
    for i in set_to_build:
        for j in range(len(i)):
            r.zadd("tmp", 0, i[0:j+1])
            if i == i[0:j+1]:
                r.zadd("tmp", 0, i+"*")
    return r


def complete(redis_instance, redis_key, prefix, count):
    prefix = prefix.encode("utf-8") # All info stored in redis are utf-8
    results = []
    rangelen = 50
    start = redis_instance.zrank(redis_key, prefix)
    if start == None:
        return []
    while len(results) < count:
        selected_range = redis_instance.zrange(redis_key, start, start+rangelen-1)
        start += rangelen

        if len(selected_range) == 0 or selected_range == None:
            break

        for entry in selected_range:
            if prefix != entry[0:len(prefix)]:
                break
            if entry[-1:] == "*" and len(results) != count:
            #if len(results) != count:
                results.append(entry[:-1].decode("utf-8")) # All info stored in redis are utf-8

    return results
