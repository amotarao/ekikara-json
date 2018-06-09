import re
import urllib.request
import datetime
import json
from bs4 import BeautifulSoup

'''
len = 39
[3] タイトル
[8] 方面
[13] 時刻表大枠
[14]-[len-5] 時刻表行ごと（可変）
[len-3] 凡例
'''

class Station:
    def __init__(self, url):
        self.url = url
        self.get_data()
        self.parse_by_table()
        self.parse_name()
        self.parse_line()
        # self.parse_direction()
        self.parse_legend()
        self.parse_timetable()

    def get_data(self):
        response = urllib.request.urlopen(self.url)
        html = response.read()
        self.soup = BeautifulSoup(html, "html.parser")

    def parse_by_table(self):
        self.table_list = self.soup.find_all("table")

    def parse_name(self):
        elm = self.table_list[3]
        self.name = elm.find("span", class_="l").string
    def parse_line(self):
        elm = self.table_list[3]
        self.line = elm.find("h1", class_="l").string
    # def parse_direction(self):
    #     elm = self.table_list[8]
    #     print(elm)
    def parse_legend(self):
        elm = self.table_list[len(self.table_list)-3]
        spans = elm.find_all("span", class_="m")

        # [1] parse 種別
        types = []
        pattern = r'<span style="color:(?P<color>#[0-9A-F]{6});">(?:無|(?P<omission>\[.+\]))&hellip;\[(?P<type>.+)\](?P<train_name>.*)</span>'
        match_obj = re.compile(pattern)
        for match in match_obj.finditer(spans[1].decode_contents(formatter="html")):
            types.append(match.groupdict())
        self.types = types

        # [3] parse 行き先
        destinations = []
        pattern = r'(?P<omission>[^ ]{1,2})&hellip;(?P<destination>[^\r\n]+)'
        match_obj = re.compile(pattern)
        for match in match_obj.finditer(spans[3].decode_contents(formatter="html")):
            destinations.append(match.groupdict())
        self.destinations = destinations
    def parse_timetable(self):
        today = datetime.date.today()

        elm = self.table_list[13].tbody
        rows = elm.find_all("tr", recursive=False)[1:]

        trains = []
        for row in rows:
            tds = row.find_all("td", align="center")
            hour = tds[0].string.zfill(2)
            for td in tds[1:]:
                mins = td.find("a", href=True).string
                text = td.find("span", class_="s").string
                pattern = r'(?P<type>\[.+\])?(?P<destination>.+)'
                match_obj = re.compile(pattern)
                for match in match_obj.finditer(text):
                    type_ = match.groupdict()["type"]
                    destination = match.groupdict()["destination"]
                    break
                train = {
                    # "hour": int(hour),
                    # "mins": int(mins),
                    # "hour_str": hour,
                    # "mins_str": mins,
                    "departure_time": today.strftime('%Y-%m-%d ' + hour + ':' + mins + ':' + '%S'),
                    "operation": {
                        "weekday": True,
                        "holiday": False
                    },
                    "type": self.get_type_from_omission(type_),
                    "train_name": self.get_train_name_from_omission(type_),
                    "destination": self.get_destination_from_omission(destination)
                }
                trains.append(train)
        self.trains = trains
    def get_type_from_omission(self, omission):
        for item in self.types:
            if omission == item['omission']:
                return item['type']
    def get_train_name_from_omission(self, omission):
        for item in self.types:
            if omission == item['omission']:
                return item['train_name']
    def get_destination_from_omission(self, omission):
        for item in self.destinations:
            if omission == item['omission']:
                return item['destination']
    def get_timetable(self):
        return self.trains

if __name__ == '__main__':
    STA = Station("http://www.ekikara.jp/newdata/ekijikoku/2801011/up1_28106031.htm")
    f = open("test/station.json", 'w')
    json.dump({"timetable": STA.get_timetable()}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
