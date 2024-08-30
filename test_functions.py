from ks_redis import *

def test_case_1():
    book_award={"award": "Golden Read", 
                "year": 2021,
                "category": "sci-fi",
                "rank": 2, 
                "author": "John Doe", 
                "book_title": "Tomorrow is here", 
                "publisher": "Ostrich books"}
    
    #insert an award to the DB and cache
    write_award(book_award)
    print("Test Case 1:")
    print("New book award inserted.")
    
    #cache hit - get award from cache
    print("\n")
    print("Verify cache hit:")
    res=get_award(book_award["award"], 
              book_award["year"], 
              book_award["category"], 
              book_award["rank"])
    print(res)

    #let the cache entry expire
    print("\n")
    print("Waiting for cached entry to expire, sleeping for 300 seconds...")
    time.sleep(300)
    
    #cache miss - get award from DB and lazy load to cache
    print("\n")
    print("Entry expired in cache, award expected to be fetched from DB:")
    res=get_award(book_award["award"], 
              book_award["year"], 
              book_award["category"], 
              book_award["rank"])
    print(res)

    #cache hit - get award from cache
    print("\n")
    print("Verify that award is lazy loaded into cache:")
    res=get_award(book_award["award"], 
              book_award["year"], 
              book_award["category"], 
              book_award["rank"])
    print(res)
    
    #delete the award from cache and DB
    print("\n")
    print("Deleting book award.")
    delete_award(book_award["award"], 
                 book_award["year"], 
                 book_award["category"], 
                 book_award["rank"])
    
    #confirm the award was deleted from cache and DB
    print("\n")
    print("Verify that the award was deleted from cache and DB:")
    res=get_award(book_award["award"], 
              book_award["year"], 
              book_award["category"], 
              book_award["rank"])
    if res:
        print(res)
        

def test_case_2():
    print("Test Case 2:")
    print("Get top 3 Must Read book awards for year 2021 in the Sci-Fi category")
    print("\n")
    res=get_awards(["Must Read", 2021, "Sci-Fi", 23])
    print(res)

    #cache-hit - get awards from cache
    print("\n")
    print("Verify cache hit on subsequent query with same parameters:")
    res=get_awards(["Must Read", 2021, "Sci-Fi", 23])
    print(res)

    #let the cache entry expire
    print("\n")
    print("Waiting for cached entry to expire, sleeping for 300 seconds...")
    time.sleep(300)
    
    #cache miss - get award from DB and lazy load to cache
    print("\n")
    print("Entry expired in cache, awards expected to be fetched from DB.")
    res=get_awards(["Must Read", 2021, "Sci-Fi", 23])
    print(res)

    #cache hit - get award from cache
    print("\n")
    print("Verify that awards are lazy loaded into cache:")
    res=get_awards(["Must Read", 2021, "Sci-Fi", 23])
    print(res)

test_case_1()
print(" ")

test_case_2()
