
from textwrap import dedent

from tornado import escape, httpclient

class Iris:

    def __init__(self, iris_url="https://iris.nersc.gov/graphql"):
        self.iris_url = iris_url

    async def query_accounts(self, name):
        query = dedent("""
        query {{
          systemInfo {{
            users(name: "{}") {{
              baseRepos {{
                computeAllocation {{
                  repoName
                }}
              }}
            }}
          }}
          systemInfo {{
            users(name: "{}") {{
              userAllocations {{
                computeAllocation {{
                  repoName
                }}
              }}
            }}
          }}
        }}""".format(name, name)).strip()
        data = await self.query(query)
        user = data["data"]["systemInfo"]["users"][0]
        default_account = user["baseRepos"][0]["computeAllocation"]["repoName"]
        accounts = [a["computeAllocation"]["repoName"] for a in user["userAllocations"]]
        accounts.sort()
        accounts.remove(default_account)
        accounts.insert(0, default_account)
        return accounts
    
    async def query(self, query):
        client = httpclient.AsyncHTTPClient()
        request = self.format_request(query)
        response = await client.fetch(request)
        return escape.json_decode(response.body)
    
    def format_request(self, query):
        return httpclient.HTTPRequest(self.iris_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=escape.json_encode({"query": query}))
