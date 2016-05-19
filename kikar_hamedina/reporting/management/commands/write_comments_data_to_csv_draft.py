from csv import DictWriter
from facebook_feeds.models import Facebook_Status_Comments

a = Facebook_Status_Comments.objects.all().order_by('?')[:2000]

field_names = [
    'comment_id',
    'parent_status_id',
    'link',
    'content',
    'published',
    'commentator_id',
    'like_count',
    'comment_count'
]
f = open('name.csv', 'wb')
w = DictWriter(f, fieldnames=field_names, delimiter='~')

headers = {field_name: field_name for field_name in field_names}
csv_data.writerow(headers)

for row in a.all():
    dict_row = {
        'comment_id': row.comment_id,
        'parent_status_id': row.parent.status_id,
        'link': 'www.facebook.com/{}'.format(row.comment_id),
        'content': unicode(row.content).encode('utf-8').replace('\r\n', '\t\t').replace('~', '*').replace('\n','\t'),
        'published': row.published,
        'commentator_id': row.comment_from.facebook_id,
        'like_count': row.like_count,
        'comment_count': row.comment_count,       
    }
    w.writerow(dict_row)
    
f.close()