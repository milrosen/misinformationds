import csv
from twscrape import API
import asyncio
import os
proxy = os.getenv("TWS_PROXY")

file = "./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv"
out =  "./data/mide22/mide22_en_misinfo_tweets_hydrated_retweets.tsv"

async def worker(api: API, writer, queue: asyncio.Queue):
    while True:
        [tweet_id, user_id]= await queue.get()
        try:
            async for retweeter in api.retweeters(int(tweet_id)):
                print(retweeter)
                writer.writerow([retweeter.id, user_id])
        finally:
            queue.task_done()

async def main():
    api = API(proxy=proxy)

    queue = asyncio.Queue()
    workers_count = 19
    
    with open(file, "r") as infile:
        with open(out, 'a') as outfile:
            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')
            workers = [asyncio.create_task(worker(api, writer, queue)) for _ in range(workers_count)]
            for tweet in reader:
                if int(tweet[7]) >= 0:
                    queue.put_nowait((tweet[3], tweet[4]))
            await queue.join()
            for worker_task in workers:
                worker_task.cancel()

if __name__ == "__main__": 
    asyncio.run(main())
