from pyquery import PyQuery as pq
from urllib.request import urlretrieve
from fake_useragent import UserAgent
from logging.handlers import TimedRotatingFileHandler
import time, os, queue, threading, re, requests, logging, configparser

INTRO = '''
COPYRIGHT 2018                     PTT 爬圖工具
      ____        ___    __ __  ___       _    
     |___ \      / _ \  / //_ |/ _ \     | |   
  ____ __) |_ __| | | |/ /_ | | | | | ___| | __
 |_  /|__ <| '__| | | | '_ \| | | | |/ __| |/ /
  / / ___) | |  | |_| | (_) | | |_| | (__|   < 
 /___|____/|_|   \___/ \___/|_|\___/ \___|_|\_\

@theburger91                github.com/limeless                                                   
    '''

DEF_SECTION = 'Config'
DEF_THDS = '10'
if os == 'nt':
    DEF_PREFIX = '\\'
    DEF_LOC = os.getcws() + '\\'
else:
    DEF_PREFIX = '/'
    DEF_LOC = os.getcwd() + '/'
DEF_ENPP = '0'
DEF_TMPP = '0'
DEF_URL = 'https://www.ptt.cc/bbs/'
DEF_BOARD = 'Beauty'
DEF_FILTER = '公告,男,帥哥,鮮肉'
DEF_TITLE_HEAD = ['Re: ', 'Fw: ']

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

#mark H
class myThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        logging.debug(" 開始線程 : " + self.name)
        process_data(self.name, self.q)
        logging.debug(" 結束線程 : " + self.name)

#mark G
def process_data(threadName, q):
    while not exitFlag: 
        queueLock.acquire()
        if not workQueue.empty():
            temp_list = q.get()
            queueLock.release()
            url, title, useragent = temp_list
            res = requests.get(url, headers=useragent, cookies={'over18': '1'})
            doc = pq(res.text)
            if sum(1 for i in (i for i in doc('#main-container a').items() if '.jpg' in i.attr('href'))) > 0:
                for x in DEF_TITLE_HEAD:
                    if x in title:
                        title = title.replace(x[2:4], '_')
                        logging.info(' 文章標題處理: {}'.format(title))
                logging.info('{}: 正在 {} 尋找圖檔……'.format(threadName, title))

                for index, img_url in enumerate((i for i in doc('#main-container a').items() if '.jpg' in i.attr('href'))):
                    try:
                        urlretrieve(img_url.attr('href'), '{}{}{}{}_{}.jpg'.format(loc, board, DEF_PREFIX, title, index))
                        logging.debug('{}: {} {}_{}.jpg 下載成功!'.format(threadName, img_url.attr('href'), title, index))
                    except:
                        logging.debug('{}: {} {}_{}.jpg 下載失敗!'.format(threadName, img_url.attr('href'), title, index))
                        logging.debug('{}{}{}{}_{}.jpg'.format(loc, board, DEF_PREFIX, title, index))
                    time.sleep(0.1)
        else: 
            queueLock.release()
        
#mark F
def get_latest_page(url, ua):
    url = url + board + '/index.html'
    logging.debug(' requesting page: {}'.format(url))
    res = requests.get(url, headers=ua, cookies={'over18': '1'})
    doc = pq(res.text)
    pagenum = re.findall(r'\d+', doc('.btn-group-paging > a:nth-child(2)').attr('href'))
    latest_page = int(pagenum[0]) + 1
    logging.debug(' Latest Page Number is :{}'.format(latest_page))
    return latest_page
            
            

#mark E
def gencfg():
    cp.add_section(DEF_SECTION)
    section = cp[DEF_SECTION]
    section['board'] = DEF_BOARD
    section['threads'] = DEF_THDS
    section['temp_page'] = DEF_TMPP
    section['end_page'] = DEF_ENPP
    section['filter'] = DEF_FILTER
    with open('config.ini', 'w') as f: cp.write(f)
    return

#mark D
def getConfig(setting_key, default_value):
    value = None
    try: value = cp.get(DEF_SECTION, setting_key)
    except Exception as e:
        cp[DEF_SECTION][setting_key] = default_value
        with open('config.ini', 'w') as f: cp.write(f)
        logging.warn(' 選項遺失, 正在重建... {}: {}'.format(setting_key, default_value))
        return getConfig(setting_key, default_value)
    return value

#mark C
def setlog():
    root = logging.getLogger()
    if len(root.handlers) == 0: #避免重复
        level = logging.DEBUG
        filename = 'debug.log'
        format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s\n   Line:%(lineno)d%(message)s'
        hdlr = TimedRotatingFileHandler(filename,'M' ,1 ,10 )
        fmt = logging.Formatter(format)
        hdlr.setFormatter(fmt)
        root.addHandler(hdlr)
        root.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        root.addHandler(ch)
    return

#mark B
def filter_title(title):
    for x in filt:
        if x in title: 
            return None
        else: 
            return title
   
#mark A
if __name__ == '__main__':
    print(INTRO)
    time.sleep(2.0)
    setlog()
    cp = configparser.ConfigParser()
    try: cp.read('config.ini')
    except Exception as e: cp.add_section(DEF_SECTION)
    
    if not os.path.exists('config.ini'):
        gencfg()
        cp.read('config.ini')

    try: cp.sections()
    except: cp.add_section(DEF_SECTION)

    loc = DEF_LOC
    board = getConfig('board', DEF_BOARD)
    thds = int(getConfig('threads', DEF_THDS))
    endp = int(getConfig('end_page', DEF_ENPP))
    tmpp = int(getConfig('temp_page', DEF_TMPP))
    filt = getConfig('filter', DEF_FILTER).split(',')
    logging.debug(filt)

    if not os.path.exists(loc + DEF_PREFIX + board):
        os.makedirs(loc + DEF_PREFIX + board)
    
    logging.debug(' 讀取 User-Agent 資料...')    
    useragent = {'User-Agent': UserAgent().random}
    if thds > 20:
        thds = 20
        logging.info('PTT 一頁只有 20 篇文章，線程更改為 20.')

    if tmpp == 0:
        pagenum = get_latest_page(DEF_URL, useragent)
    else:
        pagenum = tmpp

    while pagenum > endp:
        exitFlag = 0
        threadList = []

        for x in range(0, thds):
            threadList.append(x)
        queueLock = threading.Lock()
        workQueue = queue.Queue()
        threads = []
        threadID = 1

        for tName in threadList:
            thread = myThread(threadID, tName, workQueue)
            thread.start()
            threads.append(thread)
            threadID += 1
        
        queueLock.acquire()
        logging.info('目前頁面: {}'.format(pagenum))
        curres = 'https://www.ptt.cc/bbs/{}/index{}.html'.format(board, pagenum)
        useragent = {'User-Agent': UserAgent().random}
        logging.debug('UA:{}'.format(useragent))
        res = requests.get(curres, headers=useragent, cookies={'over18': '1'})
        doc = pq(res.text).make_links_absolute(base_url=res.url)
        logging.info(' Loading page: {}'.format(curres))
        for article in doc('#main-container .r-ent a').items():
            temp_list = []
            url = article('a').attr('href')
            title = article.text()
            
            if 'search' in url: pass
            elif [i for i in filt if i in title]:
                logging.info('條件符合, 跳過 {}'.format(title))
                pass
           # elif filter_title(title) == None:
           #     logging.info('條件符合, 跳過 {}'.format(title))
           #     pass

            else:
                temp_list.extend((url,title,useragent))
                workQueue.put(temp_list)

        queueLock.release()

        while not workQueue.empty(): pass
        exitFlag = 1
        for t in threads: t.join()
        logging.info(' DONE: {}'.format(curres))
        pagenum -= 1

        cp.set(DEF_SECTION, 'temp_page', str(pagenum))
        with open('config.ini', 'w') as f: cp.write(f)
        time.sleep(2.0)

    logging.info(' ALL DONE')



