import requests
from bs4 import BeautifulSoup
import re
import json
import time


def get_response(url, encoding=None, cookies=None, params=None, as_json=False):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'}
    if cookies is not None:
        header["cookie"] = cookies
    # , proxies = {
    #     "https": "192.168.10.88:8888", "http": "192.168.10.88:8888"}, verify = False
    resp = requests.get(url, headers=header, params=params)
    resp.encoding = encoding or resp.encoding
    if as_json:
        return resp.json()
    else:
        return resp.text


class WeiboUser:
    def __init__(self, user_name, cookies=None):
        self.user_name = user_name
        self.cookies = cookies or self.load_cookies()

    def load_cookies(self):
        with open("cookies.text","r") as f:
            cookies = f.read()
        return cookies

    def view_blogs_comments_from_user(self, target_user):
        weibo_spider = WeiboSpider(target=target_user, cookies=self.cookies)
        weibo_spider.view_main_page()


class WeiboSpider:
    def __init__(self, target, cookies):
        self.target = target
        self.cookies = cookies
        self.parameters = ["oid", "page_id",
                           "uid", "domain", "location", "pid"]
        self.config = dict()

    def get_config(self, resp):
        result = re.findall("\$CONFIG\['(\w+)'\]='(.*?)';", resp)
        print(result)
        for conf in result:
            if conf[0] in self.parameters:
                print(conf)
                self.config[conf[0]] = conf[1]
        print(self.config)

    def view_main_page(self):
        url = "https://weibo.com/{0}?profile_ftype=1&is_all=1".format(
            self.target)
        resp = get_response(url, encoding="utf8", cookies=self.cookies)
        self.get_config(resp)
        scripts = re.findall(
            "<script>FM\.view\((.*?pl\.content\.homeFeed\.index.*?)\)</script>", resp)
        jsonobj = json.loads(scripts[1])

        if self.get_blogs_from_resp(jsonobj["html"]):
            has_more = False
            for page in range(1, 4):
                for pagebar in range(2):
                    has_more = self.lazy_load_blogs(page, pagebar)
                    if not has_more:
                        break
                if not has_more:
                    break

    def get_blogs_from_resp(self, resp):
        soup = BeautifulSoup(resp, features="html.parser")
        mblogs = soup.findAll("div", attrs={"action-type": "feed_list_item"})
        if mblogs is None or len(mblogs) <= 0:
            print(resp)
        for blog in mblogs:
            feed_date_item = blog.find(
                "a", attrs={"node-type": "feed_list_item_date"})
            print(feed_date_item["name"],
                  feed_date_item["href"], feed_date_item.text.strip(), end=" ")
            feed_expand = blog.find("div", attrs={"class": "WB_feed_expand"})
            if feed_expand is not None:
                forward_from = feed_expand.find(
                    "div", attrs={"class": "WB_info"})
                print("转自", forward_from.a.text if forward_from is not None else "None")
            else:
                print()
        # <a bpfilter="page" action-type="feed_list_page_more" action-data="currentPage=1&countPage=89"
        next_page_button = soup.find(
            "a", attrs={"bpfilter": "page", "action-type": "feed_list_page_more"})
        if next_page_button is not None:
            action_data = next_page_button["action-data"]
            print("MaxPage:{0}".format(
                action_data[action_data.index("countPage")+10:]))

        lazy_load_item = soup.find("div", attrs={"node-type": "lazyload"})
        if next_page_button is not None or lazy_load_item is not None:
            return True
        return False

    def lazy_load_blogs(self, page, pagebar):
        print("page={0}, pagebar={1}".format(page, pagebar))
        url = "https://weibo.com/p/aj/v6/mblog/mbloglist?"
        params = {
            "__rnd": str(int(time.time() * 1000)),
            "ajwvr": "6",
            "domain": self.config["domain"],
            "domain_op": self.config["domain"],
            "feed_type": "0",
            "id": self.config["page_id"],
            "is_all": "1",
            "is_search": "0",
            "is_tag": "0",
            "page": page,
            "pagebar": pagebar,
            "pl_name": "Pl_Official_MyProfileFeed__21",
            "pre_page": page,
            "profile_ftype": "1",
            "script_uri": "/{0}".format(self.target),
            "visible": "0",
        }
        resp = get_response(url, encoding="utf8", params=params,
                            cookies=self.cookies, as_json=True)
        data = resp["data"]
        return self.get_blogs_from_resp(data)

    def get_all_comments(self, commentsid):
        url = "https://weibo.com/aj/v6/comment/big?"
        params = {
            "ajwvr": "6",
            "id": commentsid,
            "from": "singleWeiBo",
            "__rnd": str(int(time.time() * 1000))
        }

        jsonobj = get_response(url, cookies=self.cookie,
                               params=params, as_json=True)
        soup = BeautifulSoup(jsonobj["data"]["html"], features="html.parser")
        comments = soup.findAll("div", attrs={"node-type": "root_comment"})
        for cmt in comments:
            print(cmt.find("div", attrs={"class": "WB_text"}).text)


if __name__ == "__main__":
    user = WeiboUser("test")
    user.view_blogs_comments_from_user("yangmiblog")
