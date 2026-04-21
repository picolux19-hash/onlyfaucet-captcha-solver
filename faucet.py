import requests
import re
import time
import random
from bs4 import BeautifulSoup

URL = "https://tronblow.site/?ref=campuraduk81@gmail.com"
EMAIL = "ojongono1001@gmail.com"

session = requests.Session()

headers = {
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
"Accept":"text/html,application/xhtml+xml",
"Accept-Language":"en-US,en;q=0.9",
"Connection":"keep-alive"
}

def random_delay(a=3,b=8):
    t=random.randint(a,b)
    print(f"Delay {t} detik")
    time.sleep(t)


def countdown(sec):

    while sec>0:
        m,s=divmod(sec,60)
        print(f"Next claim {m:02d}:{s:02d}")
        time.sleep(1)
        sec-=1


def solve_captcha(soup):

    q=soup.select_one(".captcha-q")

    if not q:
        return None

    nums=re.findall(r"\d+",q.text)

    if len(nums)<2:
        return None

    a=int(nums[0])
    b=int(nums[1])

    if "+" in q.text:
        return a+b
    elif "-" in q.text:
        return a-b
    elif "*" in q.text:
        return a*b
    elif "/" in q.text:
        return int(a/b)


def claim():

    print("Membuka faucet...")

    r=session.get(URL,headers=headers)

    soup=BeautifulSoup(r.text,"html.parser")

    answer=solve_captcha(soup)

    if answer is None:
        print("Captcha tidak ditemukan")
        return 30

    print("Captcha:",answer)

    q1=soup.select_one("input[name=math_q1]")["value"]
    q2=soup.select_one("input[name=math_q2]")["value"]
    op=soup.select_one("input[name=math_op]")["value"]

    data={
    "action":"claim",
    "email":EMAIL,
    "math_q1":q1,
    "math_q2":q2,
    "math_op":op,
    "math_answer":answer
    }

    random_delay()

    r2=session.post(URL,data=data,headers=headers)

    soup2=BeautifulSoup(r2.text,"html.parser")

    success=soup2.select_one(".alert-success")
    error=soup2.select_one(".alert-error")

    if success:

        print("SUCCESS:",success.text.strip())

        return 60+random.randint(10,20)

    if error:

        msg=error.text.strip()

        print("SERVER:",msg)

        t=re.search(r"(\d+)m\s*(\d+)s",msg)

        if t:

            minutes=int(t.group(1))
            seconds=int(t.group(2))

            return minutes*60+seconds

    return 45


while True:

    try:

        wait=claim()

        print("Menunggu claim berikutnya")

        countdown(wait)

    except Exception as e:

        print("Error:",e)

        time.sleep(20)