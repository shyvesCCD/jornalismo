from django.shortcuts import render
import snscrape.modules.twitter as sntwitter
from datetime import date
from .models import Tweet, Article, Reference
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import requests


def tweets_list(request):
  return render(request, 'portal/tweets_list.html', {'tweets': ['Realize uma busca para verificar os resultados!']})

def home(request):
  return render(request, 'portal/home.html')

def articles(request):
  articles = Article.objects.all()
  return render(request, 'portal/articles.html', {'articles': articles})

def portals(request):
  references = Reference.objects.all()
  return render(request, 'portal/portals.html', {'references': references})

def tweets_search(request):
  if request.method == 'POST':
    key_groups = []
    username = request.POST.get('username')

    start_date = request.POST.get('startDate').split('-')
    end_date = request.POST.get('endDate').split('-')
    keywords = request.POST.get('words').split(',')

    begin_date = f'{start_date[2]}-{start_date[1]}-{start_date[0]}'
    end_date = f'{end_date[2]}-{end_date[1]}-{end_date[0]}'

    num = len(keywords)
    j = 0
    search = ''
    while num > j:
      if username != '' and j == 0:
        search = search + f'from:{username}'
      if j == 0:
        search = search + f' {keywords[0]}'
      if j != 0:
        search = search + f' OR {keywords[j]}'
      j += 1

    search = search+ f' since:{begin_date}' + f' until:{end_date}'

    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
      if i > 50:
        break
      tweets.append(tweet.content)

    return render(request, 'portal/tweets_list.html', {'tweets': tweets})
  else:
    return render(request, 'portal/tweets_search.html')

def graphics(request):
  if request.method == 'POST':
    data = []
    attributes = []
    data_group = request.POST.get('dataAttributes').split('\n')

    attributes = data_group[0].split(',')
    attributes[len(attributes)-1] = attributes[len(attributes)-1][:-1]

    if attributes == ['']:
      return render(request, 'portal/graphics.html')

    for i, line in enumerate(data_group):
      if i != 0:
        if i + 1 != len(data_group):
          data.append(line[:-1].split(','))
        else:
          data.append(line.split(','))
        try:
          data[i-1] = list(map(int, data[i-1]))
        except:
          return render(request, 'portal/graphics.html')

    if not all(len(attributes)== len(i) for i in data) or len(data) == 0:
      return render(request, 'portal/graphics.html')

    chart = request.POST.get('graphic')
    fig = plt.figure()

    if chart == 'pie':
      data = sum(map(np.array, data))
      df = pd.DataFrame(data)
      plt.pie(data, labels=attributes, autopct='%1.1f%%')
    elif chart == 'line':
      df = pd.DataFrame(np.array(data), columns=attributes)
      plt.plot(df)
      plt.legend(df.columns)
    else:
      df = pd.DataFrame(np.array(data), columns=attributes, index=np.arange(0, len(data)))
      fig = df.plot(kind = chart).get_figure()

    fig.savefig('portal/static/graph.jpg')

    return render(request, 'portal/graphics_result.html')
  
  else:
    return render(request, 'portal/graphics.html')

def query_constructor(exact_match = [], partial_match = []):
  query = ''
  for i in range(0, len(exact_match)):
    if (i != len(exact_match) - 1):
      query += '"' + exact_match[i] + '" OR '
    else:
      query += '"' + exact_match[i] + '" '

  if len(partial_match) > 0:
    query += 'OR '

  for i in range(0, len(partial_match)):
    query += '('
    for j in range(0, len(partial_match[i])):
      if (j != len(partial_match[i]) - 1):
        query += '"' + partial_match[i][j] + '" AND '
      else:
        query += '"' + partial_match[i][j] + '"'
    if (i != len(partial_match) - 1):
      query += ') OR '
    else:
      query += ') '

  return query