import pymongo
db = pymongo.MongoClient("MONGO-DB-LINK")

connection = db.goodrobots_blog
category_connection = connection['categories.goodrobots.ai']
admin_connection = connection['admins.goodrobots.ai']
post_connection = connection['posts.goodrobots.ai']
subcribers_connection = connection['subscribed.goodrobots.ai']
dataset_connection = connection['datasets.goodrobots.ai']
tag_connection = connection['tags.goodrobots.ai']
image_connection = connection['images.goodrobots.ai']
project_connection = connection['projects.goodrobots.ai']
