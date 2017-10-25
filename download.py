import requests
import json
import time

start_time = time.time()
last_time = time.time()
url = 'https://swarfarm.com/api/bestiary'
r1 = requests.get(url, headers={'Accept':'application/json',
                            'Content-Type':'application/json',})
response1 = r1.json()

for monster in response1:
    if any(x == monster['name'] for x in ['Magic Knight','Paladin','Iris','Lapis','Astar','Lupinus','Lanett','Leona','Jeanne','Josephine','Louise','Ophilia']):
        url2 = monster['url']
        name = monster['name']
        r2 = requests.get(url2, headers={'Accept':'application/json',
                                    'Content-Type':'application/json',})
        data = r2.json()

        if data['is_awakened'] is False:
            name = '{} {}'.format(monster['element'], name)

        with open('monsters/{}.json'.format(name), 'w') as outfile:
            json.dump(data, outfile)
        print('Successfully downloaded json for {} - {}s'.format(name, time.time()-last_time))
        last_time = time.time()
print('Overall time needed: {}s'.format(time.time()-start_time))

