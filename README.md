# Lentil Namer
This application helps you name things.  Things like babies, your pets, a car, etc.  Think of anything where you want 2 partners to agree on the name.  Or even just 1 person and you need some ideas!  This is a [flask](https://flask.palletsprojects.com/en/1.0.x/) web application that implements a swiper interface: swipe left if you don't like the name; swipe right if you do like the name.  If you and your partner both like the name, it will show up in "mutual matches."

This application was my first Flask app and I've not really written much Python at all before, so I'm sure there are bugs.  Also bear in mind that this was not written with production deployments (or even long term maintenance) in mind: it doesn't have any tests, it's not written with any security in mind, and it's not well structured code.  If you find this useful and want to contribute to fix things, you're more than welcome to submit a PR.

# Setup
This uses (and requires) [Elasticsearch 7.x](https://www.elastic.co/products/elasticsearch) as a name backend, so you need to have that running.  You can run it yourself or use the [hosted version from the makers of Elasticsearch](https://www.elastic.co/cloud/elasticsearch-service/signup) if you're looking for a good Elasticsearch hosting provider.  Once you have Elasticsearch up, you'll need to import the index templates and import the name data.

You can import the index templates by setting ES_URL and then:
```
curl -H "Content-type: application/json" -XPUT $ES_URL/nameresults -d@elasticsearch-templates/nameresults.json
curl -H "Content-type: application/json" -XPUT $ES_URL/namedatabase -d@elasticsearch-templates/namedatabase.json
```

And then you should be able to start the application by `FLASK_APP=babynamesweb.py flask run`.  The `start-babynames.sh` does this and binds to `0.0.0.0`.

# Usage
When you first start up the application, you'll be greeted with a page to "start a new project."  A project is just a name picking instance between you and your partner.

![Screenshot from 2019-07-21 09-30-52](https://user-images.githubusercontent.com/2246002/61595617-11096b80-abae-11e9-8753-af72d23457db.png)

Start a new one and then go to settings.  At this point, maybe you're looking for a name with a particular origin or popularity or you want a name that's more assocaited with males or females, you can change those settings:

![Screenshot from 2019-07-21 18-16-20](https://user-images.githubusercontent.com/2246002/61600127-d3bfd080-abe3-11e9-9a96-6a05932a2190.png)

If you want stronger biasing toward a particular male/female side, slide that slider either direction.

You can share the URL in the copy/paste box with your partner (assuming you've got a static IP or a hostname that's valid, unlike this screenshot) and you can each go off and swipe right/left in the "pick names" section:

![Screenshot from 2019-07-21 18-19-35](https://user-images.githubusercontent.com/2246002/61600166-1d102000-abe4-11e9-8748-557721b36995.png)

Generally names will be biased toward:
1) Popular names
2) Names which match the male/female slider
3) Names which your partner has already swiped right on
