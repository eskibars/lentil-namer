from flask import Flask, request, render_template, Response, json, redirect, make_response
from elasticsearch import Elasticsearch, helpers
from pprint import pprint
from datetime import datetime
import regex
import os
import csv
import uuid
import http.client  # or http.client if you're on Python 3
http.client._MAXHEADERS = 1000

es = Elasticsearch()
if 'ES_URL' in os.environ:
    es = Elasticsearch(os.environ['ES_URL'])
    pprint(os.environ['ES_URL'])
else:
    print("No ES_URL defined: using default")

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_partner_id(family, user):
    search_partner_body = {
        "query": {
            "bool": {
                "must": [
                    { "term": { "family": family } }
                ],
                "must_not": [
                    { "term": { "user": user } }
                ]
            }
        }
    }
    partnerres = es.search(index='nameresults', body=search_partner_body)
    partner = '-1'
    if (partnerres['hits']['total']['value'] > 0):
        partner = partnerres['hits']['hits'][0]['_source']['user']
    return partner

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/n/<string:family>/<string:user>')
def generatename(family, user):
    resp = make_response(render_template('swiper.html', user=user, family=family), 200)
    resp.set_cookie('family', family)
    resp.set_cookie('user', user)
    return resp

@app.route('/n/<string:family>')
def generatenewuser(family):
    user = uuid.uuid4().hex
    resp = make_response(redirect("/n/" + family + "/" + user, code=302))
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Last-Modified'] = datetime.now()
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    resp.headers['Expires'] = '0'
    resp.set_cookie('family', family)
    resp.set_cookie('user', user)
    return resp

@app.route('/n')
def generatenewfamily():
    family = uuid.uuid4().hex
    user = uuid.uuid4().hex
    resp = make_response(redirect("/n/" + family + "/" + user, code=302))
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Last-Modified'] = datetime.now()
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    resp.headers['Expires'] = '0'
    resp.set_cookie('family', family)
    resp.set_cookie('user', user)
    return resp

@app.route('/n/<string:family>/<string:user>/mutual-matches')
def getmutualmatches(family, user):
    partner = get_partner_id(family, user)
    search_mutual_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms" : {
                            "name" : {
                                "index" : "nameresults",
                                "id" : user,
                                "path" : "likes"
                            }
                        }
                    },
                    {
                        "terms" : {
                            "name" : {
                                "index" : "nameresults",
                                "id" : partner,
                                "path" : "likes"
                            }
                        }
                    }
                ]
            }
        },
        "size": 200
    }
    mutualres = es.search(index='namedatabase', body=search_mutual_body)
    return render_template('mutual-matches.html', user=user, family=family, hits=mutualres['hits']['hits']), 200

@app.route('/n/<string:family>/<string:user>/settings')
def settings(family, user):
    malefemaleprob = 4
    try:
        currentuser = es.get(index='nameresults', id=user)
        if 'malefemaleprob' in currentuser['_source']:
            malefemaleprob = currentuser['_source']['malefemaleprob']
    except Exception as e:
        # ignore missing user
        pass
    resp = make_response(render_template('settings.html', user=user, family=family,
                        malefemaleprob=malefemaleprob, base_url = request.url_root
    ), 200)
    return resp

@app.route('/n/<string:family>/<string:user>/getsettings', methods = ['GET'])
def getsettings(family, user):
    try:
        currentuser = es.get(index='nameresults', id=user)
        currentuser = currentuser['_source']
    except:
        current = { }
    if 'dislikes' in currentuser:
        currentuser.pop('dislikes')
    if 'likes' in currentuser:
        currentuser.pop('likes')
    js = json.dumps(currentuser)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/n/<string:family>/<string:user>/setsettings', methods = ['GET', 'POST'])
def setsettings(family, user):
    setting_name = None
    setting_value = None
    if request.is_json:
        try:
            json_request = request.get_json()
            if 'settingname' in json_request:
                setting_name = json_request['settingname']
                if 'settingvalue' in json_request:
                    setting_value = json_request['settingvalue']
        except Exception as e:
            pprint(request.headers)

        try:
            currentuser = es.get(index='nameresults', id=user)
            if currentuser != None:
                userdoc = currentuser['_source']

                if setting_name == 'malefemaleprob':
                    userdoc['malefemaleprob'] = int(setting_value)
                    indexres = es.index(index='nameresults', id=user, body=userdoc)
                elif setting_name == 'addregion':
                    regions = set()
                    try:
                        regions = set(userdoc['regions'])
                    except Exception as e:
                        pass
                    regions.add(setting_value)
                    userdoc['regions'] = list(regions)
                    indexres = es.index(index='nameresults', id=user, body=userdoc)
                elif setting_name == 'removeregion':
                    regions = set()
                    try:
                        regions = set(userdoc['regions'])
                    except Exception as e:
                        pass
                    regions.remove(setting_value)
                    userdoc['regions'] = list(regions)
                    indexres = es.index(index='nameresults', id=user, body=userdoc)
        except:
            # the user hasn't saved anything yet, so we need to create the user
            userdoc = {}
            # userdoc['malefemaleprob'] = 4
            indexres = es.index(index='nameresults', id=user, body=userdoc)
            pass

    json_response = { 'status': 'ok' }
    js = json.dumps(json_response)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/n/<string:family>/<string:user>/review-answers')
def reviewanswers(family, user):
    search_events_body = {
        "query": {
            "bool": {
                "must": [
                    { "term": { "user": user } }
                ]
            }
        },
        "collapse": {
            "field": "name",
            "inner_hits": [
                {
                    "name": "most_recent",
                    "size": 1,
                    "sort": [{ "date": "desc" }]
                }
            ]
        },
        "size": 500,
        "sort": {"date": {"order" : "desc"} }
    }
    eventsres = es.search(index='nameresults_events', body=search_events_body)
    return render_template('review-answers.html', user=user, family=family, hits=eventsres['hits']['hits']), 200

@app.route('/n/<string:family>/<string:user>/nextname', methods = ['GET', 'POST'])
def nextname(family, user):
    name = None
    status = None
    currentuser =  { '_source': {} }
    regions = []
    malefemaleprob = 4

    if request.is_json:
        try:
            json_request = request.get_json()
            if 'name' in json_request:
                name = json_request['name']
                if 'status' in json_request:
                    status = json_request['status']
        except Exception as e:
            pprint(request.headers)

    if (name is not None and name is not '' and status is not None):
        # add a document to our event stream
        namedoc = {
            "family": family,
            "user": user,
            "name": name,
            "status": status,
            "date": datetime.now()
        }
        indexres = es.index(index='nameresults_events', body=namedoc)

        # get the current user likes/dislikes
        try:
            currentuser = es.get(index='nameresults', id=user)
            if 'likes' in currentuser['_source']:
                likes = currentuser['_source']['likes']
            if 'dislikes' in currentuser['_source']:
                dislikes = currentuser['_source']['dislikes']
            if 'malefemaleprob' in currentuser['_source']:
                malefemaleprob = currentuser['_source']['malefemaleprob']
            if 'regions' in currentuser['_source']:
                regions = currentuser['_source']['regions']
            if (name in likes):
                likes.remove(name)
            elif (name in dislikes):
                dislikes.remove(name)
        except:
            likes = []
            dislikes = []
        if (status == 'like'):
            likes.extend([name])
        elif (status == 'dislike'):
            dislikes.extend([name])
        userdoc = {
            "family": family,
            "user": user,
            "likes": likes,
            "dislikes": dislikes,
            "malefemaleprob": malefemaleprob,
            "regions": regions,
            "lastupdate": datetime.now()
        }
        indexres = es.index(index='nameresults', id=user, body=userdoc)
    else:
        try:
            currentuser = es.get(index='nameresults', id=user)
            if 'likes' in currentuser['_source']:
                likes = currentuser['_source']['likes']
            if 'dislikes' in currentuser['_source']:
                dislikes = currentuser['_source']['dislikes']
            if 'malefemaleprob' in currentuser['_source']:
                malefemaleprob = currentuser['_source']['malefemaleprob']
        except:
            currentuser =  { '_source': {} }

    partner = get_partner_id(family, user)

    search_body = {
        "query": {
            "bool": {
                "must_not": [
                    {
                        "terms" : {
                            "name" : {
                                "index" : "nameresults",
                                "id" : user,
                                "path" : "likes"
                            }
                        }
                    },
                    {
                        "terms" : {
                            "name" : {
                                "index" : "nameresults",
                                "id" : user,
                                "path" : "dislikes"
                            }
                        }
                    }
                ],
                "should": [
                    {
                        "rank_feature": {
                            "field": "total_popularity"
                        }
                    }
                ]
            }
        },
        "rescore": {
            "window_size" : 1000,
            "query" : {
                "rescore_query" : {
                    "function_score" : {
                       "script_score": {
                          "script": {
                            "source": "randomScore(" + str(datetime.now().microsecond) + ")"
                          }
                       }
                    }
                 },
                 "query_weight" : 1.2,
                 "rescore_query_weight" : 0.5
            }
        },
        "size": 1
    }

    if malefemaleprob == 7:
        # user wants male names
        search_body['query']['bool']['should'].append(
            {
                "rank_feature": { "field": "male_probability", "boost": 100 }
            }
        )
    elif malefemaleprob == 1:
        # user wants female names
        search_body['query']['bool']['should'].append(
            {
                "rank_feature": { "field": "female_probability", "boost": 100 }
            }
        )
    else:
        search_body['query']['bool']['should'].append({
            'rank_feature': {
                "field": 'male_probability',
                "boost": malefemaleprob
            }
        })

    if 'regions' in currentuser['_source']:
        for region in currentuser['_source']['regions']:
            search_body['query']['bool']['should'].append(
                {
                    "rank_feature": { "field": "popularity_regions." + region, "boost": 10 }
                }
            )

    if (partner != '-1'):
        search_body['query']['bool']['must_not'].append({
            "terms" : {
                "name" : {
                    "index" : "nameresults",
                    "id" : partner,
                    "path" : "dislikes"
                }
            }
        })

    print(json.dumps(search_body))
    nameres = es.search(index="namedatabase", body=search_body)
    nextname = nameres['hits']['hits'][0]['_source']
    js = json.dumps(nextname)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route("/setup")
def setup():
    with open('elasticsearch-templates/namedatabase.json') as namedatabaseindex:
        es.indices.create(index='namedatabase', body=namedatabaseindex.read())
    return "OK"


@app.route("/importnames")
def importnames():
    name_origins_meanings = {}
    with open('name_data/names_with_meanings_and_origins.txt', newline='') as txtfile:
        for line in txtfile:
            nameheader = line
            namedesc = next(txtfile, None)
            namedesc = namedesc.replace("[more]","")
            m = regex.search('^([^\s]+)([\(\)\dfm \&]+)(.*)$', nameheader)
            name = m.group(1).lower().rstrip()
            origins = m.group(3).split(', ')

            name_origins_meanings[name] = { 'desc': namedesc.strip(), 'origins': [x.strip() for x in origins] }
            related_names = regex.findall('([[:upper:]]{3,})', namedesc)
            if related_names is not None:
                name_origins_meanings[name]['related'] = [x.lower().strip() for x in related_names]

    docs = []
    with open('name_data/names_with_locations.csv', newline='') as csvfile:
        namereader = csv.reader(csvfile, delimiter=';')
        next(namereader, None)
        for row in namereader:
            name = row[0].replace('+','-')
            gender = row[1]
            if (gender == 'M'):
                male_probability = '99'
                female_probability = '1'
            elif (gender == 'F'):
                male_probability = '1'
                female_probability = '99'
            elif (gender == '?'):
                male_probability = '50'
                female_probability = '50'
            elif (gender == '?F'):
                male_probability = '25'
                female_probability = '75'
            elif (gender == '?M'):
                male_probability = '75'
                female_probability = '25'

            total_popularity = 1
            for x in range(2,57):
                if (row[x] is not ''):
                    if int(row[x]) > 0:
                        row[x] = -1 * int(row[x])
                    row[x] = 10 ** (8 + int(row[x]))
                    total_popularity += int(row[x])

            popularity_regions = {
                "britain": row[2],
                "ireland": row[3],
                "usa": row[4],
                "italy": row[5],
                "malta": row[6],
                "portugal": row[7],
                "spain": row[8],
                "france": row[9],
                "belgium": row[10],
                "luxembourg": row[11],
                "netherlands": row[12],
                "east_frisia": row[13],
                "germany": row[14],
                "austria": row[15],
                "switzerland": row[16],
                "iceland": row[17],
                "denmark": row[18],
                "norway": row[19],
                "sweden": row[20],
                "finland": row[21],
                "estonia": row[22],
                "latvia": row[23],
                "lithuania": row[24],
                "poland": row[25],
                "czech_republic": row[26],
                "slovakia": row[27],
                "hungary": row[28],
                "romania": row[29],
                "bulgaria": row[30],
                "bosnia_herzegovina": row[31],
                "croatia": row[32],
                "kosovo": row[33],
                "macedonia": row[34],
                "montenegro": row[35],
                "serbia": row[36],
                "slovenia": row[37],
                "albania": row[38],
                "greece": row[39],
                "russia": row[40],
                "belarus": row[41],
                "moldova": row[42],
                "ukraine": row[43],
                "armenia": row[44],
                "azerbaijan": row[45],
                "georgia": row[46],
                "stans": row[47],
                "turkey": row[48],
                "arabia": row[49],
                "israel": row[50],
                "china": row[51],
                "india": row[52],
                "japan": row[53],
                "korea": row[54],
                "vietnam": row[55],
                "other_regions": row[56]
            }
            popularity_regions = {k: v for k, v in popularity_regions.items() if v is not ''}
            namedoc = {
                "name": name,
                "popularity_regions": popularity_regions,
                "male_probability": male_probability,
                "female_probability": female_probability,
                "total_popularity": total_popularity
            }


            if name.lower() in name_origins_meanings:
                namedoc['description'] = name_origins_meanings[name.lower()]['desc']
                namedoc['origins'] = name_origins_meanings[name.lower()]['origins']
                namedoc['related_names'] = name_origins_meanings[name.lower()]['related']

            if name.lower() is not None and name.lower() is not '':
                indexBulkDoc = { "_index": 'namedatabase', "_type": "_doc", "_id": name.lower(), "_source": namedoc }
            docs.append(indexBulkDoc)
    helpers.bulk(es, docs)
    return "OK"

@app.route("/")
def index():
    if 'family' in request.cookies:
        if 'user' in request.cookies:
            resp = make_response(redirect("/n/" + request.cookies['family'] + "/" + request.cookies['user'], code=302))
        else:
            resp = make_response(redirect("/n/" + request.cookies['family'], code=302))
        return resp
    else:
        return render_template('index.html'), 200
