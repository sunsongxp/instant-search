# TODO: rename set_to_build
# set_to_build needs to be in lexicographic order
def build_set(redis_instance, name_space, set_to_build):
    for i in set_to_build:
        for j in range(len(i)):
            redis_instance.zadd(name_space, 0, i[0:j+1])
            if i == i[0:j+1]:
                redis_instance.zadd(name_space, 0, i+"*")

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
                #break
                # The reason why we should return immediately is because in this condition, we are sure later queries to database will have no more results we want (due to the fact that the list is lexicographic order), so, stop more queries will save a lot of resources.
                return results
            if entry[-1:] == "*" and len(results) != count:
            #if len(results) != count:
                results.append(entry[:-1].decode("utf-8")) # All info stored in redis are utf-8

    return results
