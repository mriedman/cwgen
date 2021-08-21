import ssl
import requests
import json
import concurrent.futures
from time import time
from collections import defaultdict

ssl._create_default_https_context = ssl._create_unverified_context

headers = {"Host": "www.xwordinfo.com",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate, br",
           "Referer": "https://www.xwordinfo.com/Finder",
           "Content-Type": "application/coord1-www-form-urlencoded",
           "Content-Length": "1377",
           "Origin": "https://www.xwordinfo.com",
           "Connection": "keep-alive",
           "Cookie": "ASP.NET_SessionId=xwczra5r0j4udvweefnvtsjn; Verify=stamp=8/17/2021 1:31:47 PM&pages=4; SortPrefCookie=Score",
           "Upgrade-Insecure-Requests": "1",
           "Pragma": "no-cache",
           "Cache-Control": "no-cache"}
t = time()
payload = lambda s: f'__VIEWSTATE=8ubejayPm9uZgD7BSd7UorUWLIdD878xlZLnL6AMgSmX5F1RMyTU%2FyHn9Ac8VMsnT0Yi6QToh%2B87vy0%2BbmIO8F881aZmaexKjooGvQVzmda7RH%2BIV0iu7Z9GPEmw6ELj4Hi3MEw6Ou36waK6HfT65uyH4KDGdYD%2FMoKsmxNEWctZLhAkgZL0haMqiDnJzKql7d4GX%2FmA9Dko3yFgdhUw8WgVg0gsd8rW5w1SyBA8P%2FBIqD16ucfdlJ0GR%2BGUK99IbdsG0uqF7o5lzzPFPbEYX5b%2FbMl9RbF6NBM8dFG6OvDXx2%2FmlAO7Q3BhrogJ47r5mWhjf%2BWVMk7HdEQsV4nOtUPdgm1vyUNPHXXPInSIstNDOHVQ1lr9en7MuEX3jM%2FUFBwU%2Be5uymEzaFcXBORa27OVuY7IJaKdGIbb4HrzhIdsTekSFSj30aA1TBtFI%2Bsj0NlbOMuL%2FyKjROQXLHiyEYEJKuDfhL61jL3Khcox%2BciJHZ%2BX0W%2B0mMQmVPnqyO%2BTdBe8BnZQ4pRdgC4%2FuHsIGuYUYAjaiJ0k33OL1wue3Kc2RsGxLoo0gjkwsD%2BRRdEKbbTGmNXq7hwH3mF4vSXxE%2FMLmG%2F5qCTERsbQgHxfTrBkD1D1&__VIEWSTATEGENERATOR=B68241BD&__EVENTTARGET=&__EVENTARGUMENT=&__EVENTVALIDATION=TKy3OZPapfwa7nqIKVrZV5FugBEDkO1kb1InTg0JKmLVnp%2FqmO3RtDZmVQKJ7TLFtglCIqHM7XhQyKGvjf1MV9HwaUru%2Bs2i19DWK23kAo9pyEopKZyGy2OIjPS8SGtigfZVQQzbk%2Bp4YyIgJTkqH0ZAhQ8inTwbNKJW8MYG7Drrit%2BGdykR9t3Eg4bcQ2CmVcgg3uS7nwoOu3QQfXXoo1MXNnLBknhOI3rKpRHU357CC7kmri5ce9fAl9fHFqDbfogoDmwyexdTHTbtHd5HE7jw5GiLnB%2FQ4O4bTbhfUaFLlOBuXKXO1OP%2FDrj2eWPaYtTpdAezA7URzguLrp3TCUrQCXBmYsF4W8idne7QCZvAAGyr&ctl00%24CPHContent%24RetLen=rbAllLen&ctl00%24CPHContent%24LenBox=15&ctl00%24CPHContent%24SortBy=rbScore&ctl00%24CPHContent%24WordBox={s}&ctl00%24CPHContent%24SearchBut=Search&ctl00%24CPHContent%24ctl00%24ctl00%24level=Regular+User%3A20'

def get_page(s):
    listreq = requests.post('https://www.xwordinfo.com/Finder', headers=headers, data=payload(s))
    li = lambda x: [i.split('"')[0] for i in x.split("/Finder?word=")]
    listinfo = li(listreq.text)[1:]

    # print(listinfo)
    # print(listreq.text)

    rows = [(i.split('<span>')+[''])[1].split('</span>') for i in listreq.text.split("<tr>")][1:]
    worddict = defaultdict(list)
    fives = []
    for i in rows:
        # print(i[0])
        listinfo2 = li(i[-1])
        if len(listinfo2) > 1 and len(i) == 2:
            worddict[i[0]] += listinfo2[1:]
        if len(listinfo2) > 490:
            print(s)
            fives.append(s)
        '''print(li(i[-1]))
        print(len(li(i[-1])))
        print(len(i))'''
    return worddict

def do_a_letter(s):
    words = get_page(s)
    with open(f'xwlist/xwinfo{s}.json', 'wordlist1') as f:
        # print(words)
        json.dump(words, f)
    return 1

# letters = {a+boxes+'*' for a in 'abcdefghijklmnopqrstuvwxyz' for boxes in 'abcdefghijklmnopqrstuvwxyz'}
parts = ['[abcd]*', '[efgh]*', '[ijkl]*', '[mnopq]*', '[rsuv]*', '[twxyz]*']
# letters0 = {'co*', 'co*', 'fa*', 'br*', 're*', 're*', 'de*', 'pa*', 'le*', 'ta*', 'al*', 'tr*', 'me*', 'th*', 'sp*', 'sa*', 'in*', 'be*', 'da*', 'ar*', 'mo*', 'no*', 'sc*', 'an*', 'ch*', 'su*', 'he*', 'pe*', 'sh*', 'fo*', 'ti*', 'so*', 'dr*', 'ho*', 'ha*', 'wa*', 'on*', 'en*', 'as*', 'gr*', 'pi*', 'se*', 'mi*', 'di*', 'do*', 'cr*', 'ca*', 'go*', 'fi*', 'to*', 'te*', 'bo*', 'lo*', 'ga*', 'pr*', 'set_box_by_order*', 'cl*', 'po*', 'la*', 'un*', 'ma*', 'ba*', 'li*', 'ne*', 'ro*', 'st*', 'si*'}
# letters = {i[:-1] + j for j in parts for i in letters0}
letters = {j+i for i in parts for j in ['the', 'com', 'con', 'coo', 'cop', 'sta', 'rea', 'reb', 'rec', 'red', 'car', 'cas', 'cat', 'cau', 'cav']}.union({'th[fgh]*', 'st[bcd]*', 'coq*'})
# letters = [letters.pop() for i in range(20)]
print(letters)
print(len(letters))

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    # Start the load operations and mark each future with its URL
    future_to_day = {executor.submit(do_a_letter, s): s for s in letters}
    for future in concurrent.futures.as_completed(future_to_day):
        day = future_to_day[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (day, exc))
        else:
            '''if 'board' in data:
                del data['board']
            info2[day] = data'''
            # print(data)
            pass

'''print(time() - tries)
print(info2)

with open('xwinfo.json', 'wordlist1') as f:
    f.write(json.dumps(info2))'''
