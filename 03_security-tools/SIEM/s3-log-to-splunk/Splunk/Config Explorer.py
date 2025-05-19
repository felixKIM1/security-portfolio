import os,sys
import json
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
from datetime import datetime, timezone
from time import time
from urllib import parse
         
@Configuration()
class GenerateELKCommand(GeneratingCommand):


    index = Option(require=True)
    query = Option(require=True)
    size = Option(require=True)
    start_time = Option(require=False)
    end_time = Option(require=False)
        
    def generate(self):
        
        if (self.start_time) and (self.end_time):
            url='http://ES_IP:9200/'+ self.index + '/_search?q=' + str(self.query) + ' AND @timestamp:[' + str(self.start_time) + ' TO ' + str(self.end_time) + ']&sort=@timestamp:desc&size=' + str(self.size)
        
        else:
            latestTime=self.search_results_info.search_lt
            earliestTime=self.search_results_info.search_et
            
            search_lt = datetime.utcfromtimestamp(int(latestTime)).isoformat()
            search_et = datetime.utcfromtimestamp(int(earliestTime)).isoformat()


            url='http://ES_IP:9200/'+ self.index + '/_search?q=' + str(self.query) + ' AND @timestamp:[' + str(search_et) + ' TO ' + str(search_lt) + ']&sort=@timestamp:desc&size=' + str(self.size)
        
        headers = {
            'Authorization': 'Basic awefFEWFdsfaWEFFFhgyfdREW',
            'Content-type': 'application/json'
            }
        
        response = requests.get(url,headers=headers)
        r = json.loads(response.text)
        
        if response.status_code == 200:
            thing = r['hits']['hits']
            results = []
        
            for row in thing:
                tmp = {}
                tmp['_raw'] = json.dumps(row['_source'])
                tmp['sourcetype'] = "elasticsearch"
                tmp['index'] = row['_index']
                tmp['_time'] = int(datetime.strptime(row['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%s")) + 32400
        
                for key in row['_source'].keys():
                    tmp[key] = row['_source'][key]
                results.append(tmp)
        
            for row in results:
                yield row




if __name__ == "__main__":
    dispatch(GenerateELKCommand, sys.argv, sys.stdin, sys.stdout, __name__)
