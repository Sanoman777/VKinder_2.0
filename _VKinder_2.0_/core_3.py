from pprint import pprint
from datetime import datetime

import vk_api

from vk_api.exceptions import ApiError
from config import acces_token


class VKTools:
    def __init__(self, acces_token):
        self.vkapi = vk_api.VkApi(token=acces_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id) :
        try :
            info = self.vkapi.method('users.get', {'user_id' : user_id, 'fields' : 'city,sex,bdate,relation'})
        except ApiError as e :
            info = []
            print(f'error = {e}')

        if info :
            info = info[0]
            result = {
                'name' : (info['first_name'] + ' ' + info[
                    'last_name']) if 'first_name' in info and 'last_name' in info else None,
                'sex' : info.get('sex'),
                'city' : info.get('city')['title'] if info.get('city') is not None else None,
                'year' : self._bdate_toyear(info.get('bdate'))
            }
        else :
            result = {}

        return result

    def search_worksheet(self, params, offset) :
        fields = ['sex', 'bdate', 'city', 'relation']
        search_params = {}

        for field in fields :
            if field in params and params[field] is not None :
                search_params[field] = params[field]

        if 'city' not in search_params :
            self.message_send(params['user_id'], 'Введите город для поиска:')
            city = self.wait_for_user_response(params['user_id'])
            search_params['city'] = city

        try :
            users = self.vkapi.method('users.search', {
                'count' : 50,
                'offset' : offset,
                'hometown' : search_params['city'],
                'sex' : 1 if search_params['sex'] == 2 else 2,
                'has_photo' : True,
                'age_from' : search_params.get('bdate_from', 0),
                'age_to' : search_params.get('bdate_to', 100)
            })
        except ApiError as e :
            users = []
            print(f'error = {e}')

        result = [
            {'name' : item['first_name'] + ' ' + item['last_name'], 'id' : item['id']}
            for item in users['items']
            if not item['is_closed']
        ]

        return result

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get', {'owner_id': id, 'album_id': 'profile', 'extended': 1})
        except ApiError as e:
            photos = []
            print(f'error = {e}')

        result = [
            {
                'owner_id': item['owner_id'],
                'id': item['id'],
                'likes': item['likes']['count'],
                'comments': item['comments']['count']
            }
            for item in photos['items']
        ]

        # Комент 2. Нужно отсортировать словарь result по лайкам и комментариям
        result.sort(key=lambda x: (x['likes'], x['comments']), reverse=True)

        return result[:3]


if __name__ == '__main__':
    user_id = 805000288
    tools = VKTools(acces_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 5)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])
    pprint(worksheets)