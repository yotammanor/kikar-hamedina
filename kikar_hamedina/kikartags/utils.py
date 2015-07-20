

def build_classifier_format(status):
    return {'id': status.id, 'text': status.content,
            'tags': [str(tag.tag.id) for tag in status.tagged_items.all()]}



