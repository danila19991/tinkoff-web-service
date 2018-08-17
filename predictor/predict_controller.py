from django.core.files import File


#todo add any prediction algorithm
def make_prediction(menu, people, hash_key):
    result = File(open('prediction/'+hash_key+'.csv', 'wb+'))
    for chunk in menu.chunks():
        result.write(chunk)
    result.write(b' ')
    for chunk in people.chunks():
        result.write(chunk)
    return result
