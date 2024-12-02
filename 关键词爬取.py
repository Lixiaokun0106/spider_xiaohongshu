import time
import requests
import execjs
import json
import csv

# 请求头，使用之前需要修改cookie
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "dnt": "1",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "cookie":"abRequestId=2367acb5-9370-59cb-ae9a-0dbd8ffb6d3d; webBuild=4.36.5; a1=1923205a94d603le0pn47s2d3zan1xlfdw4vrx7nd50000102807; webId=3f226ee73051288121383b4365638d87; gid=yjJqJ82D80fKyjJqJ820jECW4fK8q1d8UI4W4IfMJfqu0h28IyC1iF888y8JY8W84Kdjd8W4; x-user-id-creator.xiaohongshu.com=60efe33a000000002002a808; customerClientId=689571066172264; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517419222714448348472m2oz7f0nw9vimp64; galaxy_creator_session_id=9htB7JcSypgnoQ2tpNzvbN27BE0yq0QQHWez; galaxy.creator.beaker.session.id=1727422400170099651640; timeslogin=687e7ba7258e00adbfc76352213dcae7; newresults=; web_session=040069b19ba072d0f85e57bfcc344bb50b4638; access-token-open.xiaohongshu.com=customer.open.AT-68c517420244371204185482xdnibegphrrezdvk; access-token-open.beta.xiaohongshu.com=customer.open.AT-68c517420244371204185482xdnibegphrrezdvk; xsecappid=xhs-pc-web; unread={%22ub%22:%2266efc6340000000027007dc4%22%2C%22ue%22:%2266ee31b9000000001e01bd44%22%2C%22uc%22:26}; acw_tc=59c42c386b44753f5cac005c6ba6962609af23215f15c0af11f31f5285237ba4; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=110c6ef0-edda-4844-b20c-cf4064040f00; mp_851392464b60e8cc1948a193642f793b_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A1923205ad318fa-0fe8f9377d8c0b-4c657b58-1fa400-1923205ad318fa%22%2C%22%24device_id%22%3A%20%221923205ad318fa-0fe8f9377d8c0b-4c657b58-1fa400-1923205ad318fa%22%2C%22%24search_engine%22%3A%20%22bing%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.bing.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.bing.com%22%7D",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# 加载js文件,用于js逆向获取签名
xhs_sign_obj = execjs.compile(open('xhs.js', encoding='utf-8').read())

# 后续记录爬取的笔记数量，达到数量后停止爬取
note_count = 0

# 向csv文件写入表头，笔记数据csv文件
header = ["笔记标题", "用户名","笔记内容","笔记标签"]
f = open(f"result.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.DictWriter(f, header)
writer.writeheader()


# 保存笔记数据
def sava_data(note_data,note_num):
    '''
    保存笔记数据
    :param note_data: 一片笔记的详细数据
    :param note_num: 要爬取的笔记数量
    '''

    # 笔记标签需要额外处理
    tag_list = note_data['note_card']['tag_list']
    tag_content = ""
    if len(tag_list) > 0:
        for tag in tag_list:
            tag_content += tag['name'] + "\n"

    # 要保存的选项
    data_dict = {
        "笔记标题": note_data['note_card']['title'].strip(),
        "用户名": note_data['note_card']['user']['nickname'].strip(),
        "笔记内容": note_data['note_card']['desc'].strip().replace('\n', ''),
        "笔记标签": tag_content
    }

    # 笔记数量+1
    global note_count
    note_count += 1

    print(f"当前笔记数量: {note_count}\n",
          f"笔记标题：{data_dict['笔记标题']}\n",
          f"用户名：{data_dict['用户名']}\n",
          f"笔记内容：{data_dict['笔记内容']}\n",
          f"笔记标签: {tag_content}\n",
          )
    writer.writerow(data_dict)

    # 笔记数量达到要求后停止爬取
    if note_count >= note_num:
        print("爬取完毕")
        f.close()
        exit()

def get_note_info(note_id,note_num):
    '''
    获取笔记的详细信息
    :param note_id: 笔记id
    :param note_num: 要爬取的笔记数量
    '''
    note_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'

    # 参数
    data = {
        "source_note_id": note_id,
        "image_scenes": [
            "CRD_PRV_WEBP",
            "CRD_WM_WEBP"
        ]
    }

    # 更新请求头，得到签名
    sign_header = xhs_sign_obj.call('sign', '/api/sns/web/v1/feed', data, headers.get('cookie', ''))
    headers.update(sign_header)

    # 请求数据，得到json数据
    data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    response = requests.post(note_url, headers=headers, data=data.encode('utf-8'))
    json_data = response.json()


    try:
        # 每一篇笔记的详细数据
        note_data = json_data['data']['items'][0]
    except:
        print(f'笔记 {note_id} 不允许查看')
        return
    # 保存笔记数据
    sava_data(note_data,note_num)


def keyword_search(keyword,note_num):
    '''
    搜索关键词,处理搜索到的多篇笔记
    :param keyword: 关键词
    :param note_num: 要爬取的笔记数量
    '''
    api = '/api/sns/web/v1/search/notes'
    search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    page_count = 20  # 爬取的页数, 一页有 20 条笔记 最多只能爬取220条笔记
    for page in range(1, page_count):
        # 排序方式 general: 综合排序 popularity_descending: 热门排序 time_descending: 最新排序
        params = {
            "ext_flags": [],
            "image_formats": ["jpg", "webp", "avif"],
            "keyword": keyword,
            "note_type": 0,
            "page": page,
            "page_size": 20,
            'search_id': xhs_sign_obj.call('searchId'),
            "sort": "general"
        }

        # 更新请求头，得到签名
        sign_header = xhs_sign_obj.call('sign', api, params, headers.get('cookie', ''))
        headers.update(sign_header)

        # 请求数据，得到json数据
        data = json.dumps(params, separators=(',', ':'), ensure_ascii=False)

        # 响应数据
        response = requests.post(search_url, headers=headers, data=data.encode('utf-8'))

        # 将数据转化为json格式
        json_data = response.json()

        try:
            # 多篇笔记
            notes = json_data['data']['items']
        except:
            print('================爬取完毕================'.format(page))
            break

        for note in notes:
            note_id = note['id']
            if len(note_id) != 24:
                continue
            # 获取笔记的详细信息
            get_note_info(note_id,note_num)


def main(keyword:str = "北京",note_num:int = 5,user_cookie:str = ""):
    '''
    功能主函数
    :param keyword: 关键词
    :param note_num: 笔记数量
    :param user_cookie: 用户cookie
    '''
    # 修改请求头中的用户cookie
    global headers
    headers["cookie"] = user_cookie

    keyword_search(keyword,note_num)


if __name__ == "__main__":
    # 手动输入参数
    '''
    keyword = input("关键词：")  # 搜索的关键词
    note_num = int(input("笔记数量：")) # 搜索的笔记数量
    user_cookie = input("用户cookie：")  # 用户cookie
    '''

    # 测试时使用预设参数
    keyword = "河北"
    note_num = 5
    user_cookie = "abRequestId=2367acb5-9370-59cb-ae9a-0dbd8ffb6d3d; webBuild=4.36.5; a1=1923205a94d603le0pn47s2d3zan1xlfdw4vrx7nd50000102807; webId=3f226ee73051288121383b4365638d87; gid=yjJqJ82D80fKyjJqJ820jECW4fK8q1d8UI4W4IfMJfqu0h28IyC1iF888y8JY8W84Kdjd8W4; x-user-id-creator.xiaohongshu.com=60efe33a000000002002a808; customerClientId=689571066172264; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517419222714448348472m2oz7f0nw9vimp64; galaxy_creator_session_id=9htB7JcSypgnoQ2tpNzvbN27BE0yq0QQHWez; galaxy.creator.beaker.session.id=1727422400170099651640; timeslogin=687e7ba7258e00adbfc76352213dcae7; newresults=; web_session=040069b19ba072d0f85e57bfcc344bb50b4638; access-token-open.xiaohongshu.com=customer.open.AT-68c517420244371204185482xdnibegphrrezdvk; access-token-open.beta.xiaohongshu.com=customer.open.AT-68c517420244371204185482xdnibegphrrezdvk; xsecappid=xhs-pc-web; unread={%22ub%22:%2266dabb71000000001e018eab%22%2C%22ue%22:%2266f92134000000001b023b7c%22%2C%22uc%22:23}; websectiga=2a3d3ea002e7d92b5c9743590ebd24010cf3710ff3af8029153751e41a6af4a3; sec_poison_id=759f1325-bf60-4bb6-ab24-39ef59d381a8; acw_tc=36a5d33148ceddb558aa3b6b76ed7841ce394538a04d13d6b4539ad0d833fbc2; mp_851392464b60e8cc1948a193642f793b_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A1923205ad318fa-0fe8f9377d8c0b-4c657b58-1fa400-1923205ad318fa%22%2C%22%24device_id%22%3A%20%221923205ad318fa-0fe8f9377d8c0b-4c657b58-1fa400-1923205ad318fa%22%2C%22%24search_engine%22%3A%20%22bing%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.bing.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.bing.com%22%7D"
    main(keyword,note_num,user_cookie)





