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


class WeiboBlogComments:
    def __init__(self, userid):
        self.userid = userid
        self.cookie = None
        self.config = dict()
        self.load_cookies()

    def load_cookies(self):
        self.cookie = "SINAGLOBAL=7930653504713.758.1517897900165; _ga=GA1.2.351974237.1517973848; __gads=ID=549ad9fb1810064a:T=1517973845:S=ALNI_MYAvwtcBie0htqnDZNrxVeuHuebJw; NTKF_T2D_CLIENTID=guestD999E7A0-9EB4-BA99-2454-137F0864F962; YF-V5-G0=2583080cfb7221db1341f7a137b6762e; _s_tentry=-; Apache=2742846808097.5586.1566973818881; ULV=1566973818895:21:3:1:2742846808097.5586.1566973818881:1565344337057; login_sid_t=4962adc481a1e8c8e04e19af010f18ee; cross_origin_proto=SSL; Ugrow-G0=e1a5a1aae05361d646241e28c550f987; WBtopGlobal_register_version=307744aa77dd5677; SSOLoginState=1567752727; finger_id=7e4f6184eeb90545; visitor_id=dfec20cee2f141b7; UOR=,,rsj.luan.gov.cn; TC-V5-G0=799b73639653e51a6d82fb007f218b2f; wb_view_log=1366*7681; SCF=AjSjCWlAHvk8_c-AePYsNoaRbJ38gGkgrROYrZHPlNw0qe_u0qWe8vZOlraJFz_xZJvo0TH7UsIAAY6_fIovHAI.; SUB=_2A25wv-6qDeRhGedP71oS-S7IwjyIHXVTzUdirDV8PUNbmtAKLXPnkW9NX8N8qUo7Ye-Qz7ilYFyQRsFT8q6datud; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5R65kJyRkRxPAbdIuvBhHG5JpX5K2hUgL.Fo2pShn01K5X1K52dJLoI0YLxKML1KBLBo-LxKqLBoeLBKzLxKMLBoeLB.zLxKqLBK-LBK5LxKMLBK-L1hnLxKMLBK-LBoMLxKBLBonLB-Bt; SUHB=0d4P8VWlPdnsdT; ALF=1573181820; un=azazjjyjjy@sina.com; wb_view_log_1148390490=1366*7681; wvr=6; TC-Page-G0=8afba920d7357d92ddd447eac7e1ec5c|1572585596|1572585491; webim_unReadCount=%7B%22time%22%3A1572585655700%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A16%2C%22msgbox%22%3A0%7D"

    def get_config(self, resp):
        result = re.findall("\$CONFIG\['(\w+)'\]='(.*?)';", resp)
        print(result)
        for conf in result:
            if conf[0] in ("oid", "uid", "location", "page_id","domain"):
                print(conf)
                self.config[conf[0]] = conf[1]
        print(self.config)

    def get_config_from_mainpage(self):
        url = "https://weibo.com/{0}?profile_ftype=1&is_all=1".format(self.userid)
        resp = get_response(url, encoding="utf8", cookies=self.cookie)
        self.get_config(resp)
        scripts = re.findall(
            "<script>FM\.view\((.*?pl\.content\.homeFeed\.index.*?)\)</script>", resp)
        jsonobj = json.loads(scripts[1])

        self.get_blogs_from_resp(jsonobj["html"])
        # print(jsonobj["html"])
        # with open("D:/PE666/桌面/Work/PythonStudy/XCrawler/WeiboComments/result2.html", "w+", encoding="utf8") as f:
        #     f.write(jsonobj["html"])
        soup = BeautifulSoup(jsonobj["html"], features="html.parser")
        lazy_load_item = soup.find("div", attrs={"node-type": "lazyload"})
        if lazy_load_item is not None:
            # lazy_load_blogs()
            pass

    def get_blogs_from_resp(self, resp):
        soup = BeautifulSoup(resp, features="html.parser")
        mblogs = soup.findAll("div", attrs={"action-type": "feed_list_item"})
        if mblogs is None:
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
            "domain": "100406",
            "is_search": "0",
            "visible": "0",
            "is_all": "1",
            "is_tag": "0",
            "profile_ftype": "1",
            "page": "2",
            "pagebar": "0",
            "pl_name": "Pl_Official_MyProfileFeed__21",
            "id": "1004061195242865",
            "script_uri": "/yangmiblog",
            "feed_type": "0",
            "pre_page": "2",
            "domain_op": "100406",
            "__rnd": "1572598724001",
        }
        resp = get_response(url, encoding="utf8",
                            cookies=self.cookie, as_json=True)

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
    weibo = WeiboBlogComments("yangmiblog")
    weibo.get_config_from_mainpage()
