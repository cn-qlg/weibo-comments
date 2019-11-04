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
        return "SINAGLOBAL=7930653504713.758.1517897900165; _ga=GA1.2.351974237.1517973848; __gads=ID=549ad9fb1810064a:T=1517973845:S=ALNI_MYAvwtcBie0htqnDZNrxVeuHuebJw; NTKF_T2D_CLIENTID=guestD999E7A0-9EB4-BA99-2454-137F0864F962; YF-V5-G0=2583080cfb7221db1341f7a137b6762e; _s_tentry=-; Apache=2742846808097.5586.1566973818881; ULV=1566973818895:21:3:1:2742846808097.5586.1566973818881:1565344337057; login_sid_t=4962adc481a1e8c8e04e19af010f18ee; cross_origin_proto=SSL; Ugrow-G0=e1a5a1aae05361d646241e28c550f987; WBtopGlobal_register_version=307744aa77dd5677; SSOLoginState=1567752727; finger_id=7e4f6184eeb90545; visitor_id=dfec20cee2f141b7; TC-V5-G0=799b73639653e51a6d82fb007f218b2f; un=azazjjyjjy@sina.com; wvr=6; SCF=AjSjCWlAHvk8_c-AePYsNoaRbJ38gGkgrROYrZHPlNw0koGdWhDucCtYi-1tLeIlSpENXr5Xcpcfr93KEBEZoc0.; SUB=_2A25wu_ycDeRhGedP71oS-S7IwjyIHXVTsWlUrDV8PUJbmtAKLVnBkW9NX8N8qU_B_7usDrhgl3l_OVRzRlhpauZ6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5R65kJyRkRxPAbdIuvBhHG5JpX5K-hUgL.Fo2pShn01K5X1K52dJLoI0YLxKML1KBLBo-LxKqLBoeLBKzLxKMLBoeLB.zLxKqLBK-LBK5LxKMLBK-L1hnLxKMLBK-LBoMLxKBLBonLB-Bt; SUHB=0sqwDpV56Kq_ww; ALF=1604370496; wb_view_log_1148390490=1366*7681; UOR=,,login.sina.com.cn; webim_unReadCount=%7B%22time%22%3A1572834535528%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A18%2C%22msgbox%22%3A0%7D; TC-Page-G0=b993e9b6e353749ed3459e1837a0ae89|1572834532|1572834508"

    def view_blogs_comments_from_user(self, target_user):
        weibo_spider = WeiboCommentsSpider(target=target_user,cookies=self.cookies)
        weibo_spider.view_main_page()

class WeiboCommentsSpider:
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

        self.get_blogs_from_resp(jsonobj["html"])
        # print(jsonobj["html"])
        with open("D:/PE666/桌面/Work/PythonStudy/XCrawler/WeiboComments/result2.html", "w+", encoding="utf8") as f:
            f.write(jsonobj["html"])
        soup = BeautifulSoup(jsonobj["html"], features="html.parser")
        lazy_load_item = soup.find("div", attrs={"node-type": "lazyload"})
        print(lazy_load_item)
        if lazy_load_item is not None:
            self.lazy_load_blogs(1, 0)
            pass
    
    def get_blogs_from_resp(self, resp):
        soup = BeautifulSoup(resp, features="html.parser")
        mblogs = soup.findAll("div", attrs={"action-type": "feed_list_item"})
        if mblogs is None or len(mblogs) <= 0:
            print(resp)
        for blog in mblogs:
            feed_date_item = blog.find(
                "a", attrs={"node-type": "feed_list_item_date"})
            print(feed_date_item["name"],
                  feed_date_item["href"], feed_date_item.text.strip())
            feed_expand = blog.find("div", attrs={"class": "WB_feed_expand"})
            if feed_expand is not None:
                forward_from = feed_expand.find(
                    "div", attrs={"class": "WB_info"})
                print("转自", forward_from.a.text if forward_from is not None else "None")

    def lazy_load_blogs(self, page, pagebar):

        url = "https://weibo.com/p/aj/v6/mblog/mbloglist?"
        params = {
            "ajwvr": "6",
            "domain": self.config["domain"],
            "is_search": "0",
            "visible": "0",
            "is_all": "1",
            "is_tag": "0",
            "profile_ftype": "1",
            "page": page,
            "pagebar": pagebar,
            "pl_name": "Pl_Official_MyProfileFeed__21",
            "id": self.config["page_id"],
            "script_uri": "/yangmiblog",
            "feed_type": "0",
            "pre_page": "2",
            "domain_op": self.config["domain"],
            "__rnd": str(int(time.time() * 1000))
        }
        resp = get_response(url, encoding="utf8",
                            cookies=self.cookies, as_json=True)
        data = resp["data"]
        self.get_blogs_from_resp(data)

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
    # get_all_mblogs("baikehome")
    # get_all_blogs("yangmiblog")
    user = WeiboUser("Canana")
    user.view_blogs_comments_from_user("yangmiblog")
