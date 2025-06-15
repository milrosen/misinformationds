# USAGE: 
#   1) Add correct api keys and cookies to a file called "accounts.txt" 
#   2) Find out the correct format of your data, mine was username:password:email:email_password:_:_:cookies
#       (hints: the cookies should be base64 encoded json, so you can check manually if the format isn't supplied)
#   3) Run "twscrape add_accounts ./accounts.txt [FORMAT]" this creates the file accounts.db which 
#       will be used when the script is run




import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
import os
proxy = os.environ["TWS_PROXY"]

async def main():
    api = API(proxy=proxy)
    await api.pool.login_all()
    print(api.proxy)

if __name__ == "__main__": 
    asyncio.run(main())