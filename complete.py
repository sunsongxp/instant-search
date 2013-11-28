import mmseg
mmseg.Dictionary.load_dictionaries()
# TODO: rename set_to_build
# set_to_build needs to be in lexicographic order
# name_space and redis_key are supposed to be functioning as the same.
def build_set(redis_instance, name_space, set_to_build=[]):
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

# entries = [(1, "Text"), (2, "Text")]
# two sets to build: keywordset=set(), which have all individual words, keyword_index(with name of word) are sets of members of ids of entries
# or topics containing this word, eg: keyword:index:abacus = set([1, 4, 7]).
def build_index(redis_instance, redis_key, entries=[], keyword_set_name="keywordset", keyword_index="keyword:index"):
    all_words = []
    for entry_id, entry in entries:
        segmented_entry = mmseg.Algorithm(entry)
        for word in segmented_entry:
            all_words.append(word.text)
            redis_instance.sadd(keyword_set_name, word)
            redis_instance.sadd(keyword_index+':'+word.text, entry_id)

    build_set(redis_instance, redis_key, all_words)

# There are many things to improve in this function, focus on the number of results retrieved from complete function
def search(user_input, redis_instance, redis_key, keyword_index="keyword:index"):
    word_list = []
    completed_list = []
    segmented_entry = mmseg.Algorithm(user_input)
    for word in segmented_entry:
        word_list.append(word.text)
    for word in word_list:
        completed_list.append(
            keyword_index + ":" + complete(redis_instance, redis_key, word, 1)[0]
        )
    completed_set = redis_instance.sinter(completed_list)
    return completed_set

