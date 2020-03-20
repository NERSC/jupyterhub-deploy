
from textwrap import dedent

from tornado import escape, httpclient

class Iris:

    def __init__(self, iris_url="https://iris.nersc.gov/graphql"):
        self.iris_url = iris_url

    async def query_user(self, name):
        query = dedent("""
		query {{
		  systemInfo {{
            uid
		    users(name: "{}") {{
		      baseRepos {{
		        computeAllocation {{
		          repoName
		        }}
		      }}
		      userAllocations {{
		        computeAllocation {{
		          repoName
		        }}
		        userAllocationQos {{
		          qos {{
		            qos
		          }}
		        }}
		      }}
		    }}
		  }}
		}}""".format(name)).strip()
        data = await self.query(query)
        return data["data"]["systemInfo"]["users"][0]
    
    async def query(self, query):
        client = httpclient.AsyncHTTPClient()
        request = self.format_request(query)
        response = await client.fetch(request)
        return escape.json_decode(response.body)
    
    def format_request(self, query):
        return httpclient.HTTPRequest(self.iris_url, method="POST",
                headers={"Content-Type": "application/json"},
                body=escape.json_encode({"query": query}))
