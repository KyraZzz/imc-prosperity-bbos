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

headers = {'Authorization': 'Bearer eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMWNkNjUyMS0wNDRjLTQ0NDctYmNmYy02NzM5NDY4NmJlZGMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjMxY2Q2NTIxLTA0NGMtNDQ0Ny1iY2ZjLTY3Mzk0Njg2YmVkYyIsIm9yaWdpbl9qdGkiOiJkNmMxYjJlNS1hNmE1LTQ4M2UtODFjMi1lOTk5ZmIwYjNmMTQiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiZThlZTk4M2YtYzQ3NS00ZmUyLWJjYjQtYjA5ZTQxODUyNjY0IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzkzMTY2MjUsImV4cCI6MTY3OTYzMzE5NSwiaWF0IjoxNjc5NjI5NTk1LCJqdGkiOiIwYjc3ODViMC0xNGE4LTQyNjUtYjg2Ni0yODg4ODNlZGY4NTMiLCJlbWFpbCI6Inl6NzA5QGNhbS5hYy51ayJ9.DuXljHhRVIvysS3FZDakIv1TLQQ5xLHdaWy8M_SG9MI-ombI5jxFIxr63ef6aAXu0u4eBcN1pBPbRdGRJkIqeox2DI4EHPf7uNF86q6CjFH5wHve2_oe_dVHUo2aI74zAb5O9kGIMfaY7ClEE57FjRvShkWBq_4SYn9GIBT2Y6PjVbJd14SOBteLaFgo_2ZuyXB1KUQE8gyLVPFXIL_NzAYWvUMc0TBYC0Zb7h2PC_mDzypjiIj29--pFqJ-XzWnQAklcDBEYYfZqHFNDeSoL3mBTZoLGIEXSp5VjCxaeo0ZMQ4dFSFoNYmoWVcCPC-cVdK-EAbcmqH_OfYCnTGoUg'}
response = requests.get(
    'https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/cfbf4694-c53c-4a16-930f-6a0e3c1fc665', headers=headers)
res = response.json()

p = res['algo']['summary']['graphLog']
pv = [i.split(';') for i in p.split('\n')]
fp = pd.DataFrame(pv[1:], columns=pv[0])
fp = fp.applymap(lambda x: float(x) if x != '' and x !=
                 'None' and x != None else '')

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=fp['timestamp'],
    y=fp['value'],
    name='value',
    mode='lines+markers',
    line_shape='hv',
    text='value'))
fig.show()
