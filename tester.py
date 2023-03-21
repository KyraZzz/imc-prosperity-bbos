# When a algorithm finishes running
# press F12
# go to application
# go to local storage
# find row that ends with idtoken
# copy corresponding string to headers
# headers = {'Authorization': 'Bearer <value>'}
# response = requests.get('https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/<logfilename>',headers=headers)

import requests
import pandas as pd
import plotly.graph_objects as go

headers = {'Authorization' : 'Bearer eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI0MGE3ZGExNS1jNGQ0LTRlODctODk1NS0wOWY2YzYwMGY5YmYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjQwYTdkYTE1LWM0ZDQtNGU4Ny04OTU1LTA5ZjZjNjAwZjliZiIsIm9yaWdpbl9qdGkiOiI5NDk0YWI1YS02ZDE4LTRmNGQtYTA0Yy1kZjE3YmM3MGVmMjMiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiMmNkNjljNjAtYzc2OC00NTJlLWIyMmItMDgyZDQ3MTJlMzE5IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzkzMTA0NjEsImV4cCI6MTY3OTM2MzYwNSwiaWF0IjoxNjc5MzYwMDA1LCJqdGkiOiI0YzhiYTExZi02MTdhLTQzNTktYmQ4Yi05ZjQ3ZDEwMmU0OTciLCJlbWFpbCI6InljNTM4QGNhbS5hYy51ayJ9.pzFH6e7skgL1LpFO-iOaOOvlr-IUSP1Y0HN7ROQdcR6ANH0jMO5OMi1ZrvKsB3KHAAZJSOiXKXB55OUKEXxIdwAlBbqxfQ4jGKOLzQA9fYH8Tyr9R6Ue1xCsZW0bwTCH1VF0emFzHf_KOOAjejN0_67UvSpVjaxsH5IpxKl37ZqHTL5hDnl-f3G7Dr81uS6067lqZrCu-Id46EVXWeE9iVQ-iOAM4iIRJf1IxK5p4Nqqt6GGrcOgTS0_FxDnnhGMeGJeAZ4BUjMSYOWJBtQ1Out9HJIOXZZu9gpbjgecGWnq27IF6f5SuJ-2qRi3y_NKRwVQ6f31seoV5HRI6i9PgQ'}
response = requests.get('https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/e9fc1c9b-7fe4-4dc3-832e-b7b2db37f4ac',headers=headers)
res = response.json()

p = res['algo']['summary']['graphLog']
pv = [i.split(';') for i in p.split('\n')]
fp = pd.DataFrame(pv[1:], columns = pv[0])
fp = fp.applymap(lambda x: float(x) if x != '' and x != 'None' and x != None else '')

fig = go.Figure()
fig.add_trace(go.Scatter(
                x = fp['timestamp'],
                y = fp['value'],
                name = 'value',
                mode = 'lines+markers',
                line_shape = 'hv',
                text = 'value'))
fig.show()