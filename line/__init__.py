import re
import urllib.request
import datetime
import json
from bs4 import BeautifulSoup

''' table_list
len = 20
[3] タイトル
[6] 曜日
[8] 方面
[11] ページリスト
[14] 時刻表大枠
[16] 更新日
'''

''' td_list
len = 206
[  0] - [205] All
[ 37] - [183]

len = 197
[  0] - [196] All
[ 37] - [174]

len = 206
[  0] - [205] All
[ 37] - [183] 147

len = 128
[  0] - [127] All
[ 37] - [102] 66
'''

class Line:
    def __init__(self, url):
        self.url = url
        self.get_data()
        self.parse_line()
        self.parse_stations()
        self.parse_train_types()
        self.parse_train_times()

    def get_data(self):
        response = urllib.request.urlopen(self.url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")

        self.table_list = soup.find_all("table")
        self.tr_list = soup.find_all("tr")

        self.train_count = len(self.tr_list[23].find_all("td")) - 1
        self.section_count = len(soup.find_all("td", class_="lowBg06", align="center"))
        self.page_count = len(self.tr_list[18].find_all("option"))
        self.page_number = self.tr_list[18].find("option", selected="selected").text.split("頁")[0]

        '''
        1 + (train_count + 1) * 6 + (train_count + 2) * section_count - 1
        → 1 + train_count * 6 + 6 + train_count * section_count + 2 * section_count - 1
        → train_count * 6 + train_count * section_count + section_count * 2 + 6
        → (train_count + 2) * (section_count + 6) - 6
        + 37
        '''
        td_list = soup.find_all("td")
        timetable_offset = 0
        for i, td in enumerate(td_list):
            class_ = td.get("class")
            if class_ is None:
                continue
            if "lowBg13" == td.get("class")[0]:
                timetable_offset = i
                break
        self.timetable_td_list = td_list[timetable_offset:timetable_offset+(self.train_count+2)*(self.section_count+6)-5]

    def parse_line(self):
        elm = self.table_list[3]
        self.line_name = elm.find("h1", class_="l").string
        self.line_section = elm.find("span", class_="s").contents[0]

    def parse_stations(self):
        self.stations = []
        for x in range(self.section_count):
            index = (self.train_count + 1) * 5 + 1 + (self.train_count + 2) * x
            # 駅名を代入
            stations = self.timetable_td_list[index].text.replace("\r", "").split("\n")[1:]
            # 発着を代入
            types = self.timetable_td_list[index+1].text.split("\n")[1:]
            for y in range(len(stations)-1):
                station_name = stations[y]
                if station_name == "                                                      〃":
                    station_name = stations[y-1]
                station_data = {
                    "name": station_name,
                    "type": types[y]
                }
                self.stations.append(station_data)

    def parse_train_types(self):
        self.trains = []
        for x in range(self.train_count):
            train = {
                "train_number": self.timetable_td_list[x+2].text.replace("\n", ""),
                "train_type": self.timetable_td_list[x+3+self.train_count].text.split("]")[0].replace("\n[", ""),
                "train_name": "" if "\xa0" in self.timetable_td_list[x+3+self.train_count].text else self.timetable_td_list[x+3+self.train_count].text.split("]")[1],
                "extra": True if "◆" in self.timetable_td_list[x+4+self.train_count*2].text else False,
                "train_url": self.timetable_td_list[x+5+self.train_count*3].find("a").get("href").replace("../../", "http://www.ekikara.jp/newdata/"),
            }
            self.trains.append(train)

    def parse_train_times(self):
        for x, train in enumerate(self.trains):
            times = []
            stations = []
            for y in range(self.section_count):
                index = (self.train_count + 1) * 5 + 3 + x + (self.train_count + 2) * y
                section_times = self.timetable_td_list[index].text.split("\n")
                section_times = section_times[1:len(section_times)-1]
                for z in section_times:
                    times.append(z)
            for y, station in enumerate(self.stations):
                time = times[y]
                passing = False
                via = True

                if time == "||":
                    time = None
                    via = False
                elif time in {"\xa0", "--", "=="}:
                    time = None
                elif "直通" in time:
                    time = None
                elif time == "レ":
                    time = None
                    passing = True

                stations.append({
                    "name": station["name"],
                    "type": station["type"],
                    "time": time,
                    "passing": passing,
                    "via": via
                })
            train["stations"] = stations
            self.trains[x] = train

    def get_timetable(self):
        return self.trains

    def get_all_timetable(self):
        timetable = []
        for i in range(self.page_count):
            url = self.url.replace("_" + self.page_number, "_" + str(i+1))
            timetable.extend(Line(url).get_timetable())
        return timetable

if __name__ == '__main__':
    L = Line("http://www.ekikara.jp/newdata/line/1304021/down1_1_holi.htm")
    # L = Line("http://www.ekikara.jp/newdata/line/2809011/down1_1.htm")
    f = open("dist/line.json", 'w')
    json.dump({"timetable": L.get_all_timetable()}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
