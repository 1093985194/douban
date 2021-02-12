from bs4 import BeautifulSoup     #网页解析
import re       #正则表达式
import urllib.request,urllib.response       #制定URL，获取网页数据
import xlwt     #进行excel操作
import sqlite3      #进行sqlite数据库操作


def main():
    baseurl="https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist=getData(baseurl)
    # savepath = "豆瓣电影Top250.xls"
    dbpath = "movie.db"
    #3.保存数据
    # saveData(datalist,savepath)
    # saveData2DB(datalist,dbpath)

    # askURL(baseurl)


#影片详情链接
findLink = re.compile(r'<a href="(.*?)">')         #创建正则表达式对象，表示规则(字符串的模式)
#影片图片链接
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)          #re.S让换行符包含在字符中
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#影片评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#影片概况
findInq = re.compile(r'<span class="inq">(.*?)</span>')
#影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

# 爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(1,2):   #获取页面信息函数10次
        url = baseurl + str(i*25)
        html = askURL(url)  #保存获取到的网页源码

        # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all("div",class_="item"):      #查找符合要求的字符串
            # print(item)       #测试查看电影item
            data = []       #保存电影信息
            item = str(item)
            item = item.replace("\u00a0", "")       #去除数据库NBSP问题

            #影片详情链接
            link = re.findall(findLink, item)[0]  # re库用来通过正则表达式查找指定字符串
            # print(link)
            data.append(link)  # 添加影片详情链接

            imgsrc = re.findall(findImgSrc, item)[0]
            data.append(imgsrc)  # 添加影片图片链接

            titles = re.findall(findTitle, item)
            if(len(titles)==2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/","")      #去掉无关字符
                data.append(otitle)
            else:
                data.append(titles[0])  # 添加影片片名
                data.append(' ')

            rating = re.findall(findRating, item)[0]
            data.append(rating)  # 添加影片评分

            judge = re.findall(findJudge, item)[0]
            data.append(judge)  # 添加影片评价人数

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")
                data.append(inq)  # 添加影片概况
            else:
                data.append(" ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)         #去掉<br/>
            bd = re.sub('/', " ", bd)
            data.append(bd.strip())  # 添加影片相关内容,去掉空格

            datalist.append(data)
        print(datalist)
    return datalist

# 得到一个指定的URL网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56",
        "Cookie":'ll="118270"; bid=4YQbty686r4; _vwo_uuid_v2=D70936AC87C69F8BC8F4BF6C5AB424046|57bc340fdcbf53cb4b16576594fe2b9e; __utmc=30149280; __utmc=223695111; dbcl2="173056973:CIFtTpdZ52Q"; ck=xbJG; push_doumail_num=0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1612514149%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.883681393.1612335085.1612489281.1612514150.6; __utmb=30149280.0.10.1612514150; __utmz=30149280.1612514150.6.4.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1785544053.1612335087.1612489281.1612514150.6; __utmb=223695111.0.10.1612514150; __utmz=223695111.1612514150.6.4.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; _pk_id.100001.4cf6=4e19a79dbcbe37e7.1612335087.5.1612514169.1612489288.'

    }#用户代理，告诉浏览器我们可以接受什么样的信息

    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e,"code")
        if hasattr(e,"reason"):
            print(e.reason)

    return html


#保存数据
def saveData(datalist,savepath):
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet('豆瓣电影Top250')
    col = ("影片详情链接","影片图片链接","影片中文名","影片外文名","影片评分","影片评价人数","影片概况","影片相关内容")
    for i in range(0,8):
        worksheet.write(0,i,col[i])     #列名
    for i in range(0,250):
        print("第%d条"%i)
        data = datalist[i]
        for j in range(0,8):
            worksheet.write(i+1,j,data[j])

    workbook.save(savepath)

def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index==4 or index==5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
            insert into movie250(
                info_link,pic_link,cname,ename,score,rated,instroduction,info)
                values(%s)'''%",".join(data)
        cursor.execute(sql)
        conn.commit()
    cursor.close()
    conn.close()


def init_db(dbpath):
    sql = '''
        create table movie250
        (
            id INTEGER primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            instroduction text,
            info text
        )
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
    # init_db("movietest.db")

    print("爬取完毕")