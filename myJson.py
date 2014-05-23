# -*- coding: utf-8 -*-
import urllib
import json
url=r'http://nb.kusu.cn/version/versionResponses.php'
rs=urllib.urlopen(url).read()
print rs
jsonObject=json.loads(rs)
print U"主程序版本号:%s" % jsonObject['cv']
print U"主程序ip文件版本号:%s" % jsonObject['iv']
print U"主程序资源文件笨笨号:%s" % jsonObject['mv']
