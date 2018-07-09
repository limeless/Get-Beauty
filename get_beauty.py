from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from fake_useragent import UserAgent
import time, os, queue, threading, chardet, re, requests, logging, configparser

INTRO = '''
COPYRIGHT 2018              PTT Beauty 爬圖工具
      ____        ___    __ __  ___       _    
     |___ \      / _ \  / //_ |/ _ \     | |   
  ____ __) |_ __| | | |/ /_ | | | | | ___| | __
 |_  /|__ <| '__| | | | '_ \| | | | |/ __| |/ /
  / / ___) | |  | |_| | (_) | | |_| | (__|   < 
 /___|____/|_|   \___/ \___/|_|\___/ \___|_|\_\

@theburger91                github.com/limeless                                                   
    '''

DEF_SECTION = 'Beauty'
DEF_THDS = '10'
DEF_LOC = 'D:\Beauty'
DEF_ENPP = '1200'
DEF_TMPP = '0'
BEAUTY_URL = 'https://www.ptt.cc/bbs/Beauty/index.html'

class myThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        logging.info("開始線程 : " + self.name)
        process_data(self.name, self.q)
        logging.info("結束線程 : " + self.name)

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            temp_list = q.get()
            queueLock.release()
            url = temp_list[0]
            title = temp_list[1]
            useragent = temp_list[2]
            if 'Re:' in title:
                title = title.replace('Re: ', 'Re_')
                logging.info('文章標題處理: {}'.format(title))
            elif 'Fw:' in title:
                title = title.replace('Fw: ', 'Fw_')
                logging.info('文章標題處理: {}'.format(title))
            res = requests.get(url, headers=useragent)
            soup = BeautifulSoup(res.text, 'lxml')
            if len(soup.findAll('a', {'href':re.compile('http:\/\/i\.imgur\.com\/.*')})) > 0:
                logging.info('{}: 正在尋找正妹……'.format(threadName))
                for index, img_url in enumerate(soup.findAll('a', {'href':re.compile('http:\/\/i\.imgur\.com\/.*')})):
                    try:
                        urlretrieve(img_url['href'], '{}\{}_{}.jpg'.format(loc, title, index))
                        logging.info('{}: {} {}_{}.jpg 下載成功!'.format(threadName, img_url['href'], title, index))
                    except:
                        logging.info('{}: {} {}_{}.jpg 下載失敗!'.format(threadName, img_url['href'], title, index))
                    
                    time.sleep(0.1)
        else:
            queueLock.release()
        

def get_latest_page(url, ua):
    res = requests.get(url, headers=ua)
    soup = BeautifulSoup(res.text, 'lxml')
    for btn in soup.select('.action-bar a'):
        if '上頁' in btn.text:
            pagenum = re.findall( r'\d+', btn.get('href'))
            latest_page = int(pagenum[0]) + 1
            return latest_page


def gencfg():
    cp.add_section(DEF_SECTION)
    section = cp[DEF_SECTION]
    section['location'] = DEF_LOC
    section['threads'] = DEF_THDS
    section['temp_page'] = DEF_TMPP
    section['end_page'] = DEF_ENPP
    with open('config.ini', 'w') as f:
        cp.write(f)
    return

def getConfig(setting_key, default_value):
    value = None
    try:
        value = cp.get(DEF_SECTION, setting_key)
    except Exception as e:
        cp[DEF_SECTION][setting_key] = default_value
        with open('config.ini', 'w') as f:
           cp.write(f)
        logging.warn('選項遺失, 正在重建... {}: {}'.format(setting_key, default_value))
        return getConfig(setting_key, default_value)
    return value

if __name__ == '__main__':
    print(INTRO)
    time.sleep(5.0)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    cp = configparser.ConfigParser(allow_no_value=True)
    try:
        cp.read('config.ini')
    except Exception as e:
        cp.add_section(DEF_SECTION)
    
    if not os.path.exists('config.ini'):
        gencfg()
        cp.read('config.ini')

    try:
        cp.sections()
    except:
        cp.add_section(DEF_SECTION)
    
    loc = getConfig('location', DEF_LOC)
    thds = int(getConfig('threads', DEF_THDS))
    endp = int(getConfig('end_page', DEF_ENPP))
    tmpp = int(getConfig('temp_page', DEF_TMPP))

    if not os.path.exists(loc):
        os.makedirs(loc)

    logging.info('讀取 User-Agent 資料...')    
    ua = UserAgent()
    useragent = {'User-Agent': ua.random}

    if tmpp == 0:
        pagenum = get_latest_page(BEAUTY_URL, useragent)
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
        logging.debug('目前頁面: {}'.format(pagenum))
        curres = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(pagenum)
        useragent = {'User-Agent': ua.random}
        logging.info('UA:{}'.format(useragent))
        res = requests.get(curres, headers=useragent)
        soup = BeautifulSoup(res.text, 'lxml')
        logging.info('Loading page: {}'.format(curres))
        for article in soup.select('.r-ent a'):
            temp_list = []
            url = 'https://www.ptt.cc' + article['href']
            title = article.text
            if 'search' in url:
                pass
            elif '[帥哥]' in title:
                logging.info('發現非正妹, 跳過! {}'.format(title))
                pass
            elif '鲜肉' in title:
                logging.info('發現非正妹, 跳過! {}'.format(title))
                pass
            elif '男' in title:
                logging.info('發現非正妹, 跳過! {}'.format(title))
                pass
            elif '公告' in title:
                logging.info('發現非正妹, 跳過! {}'.format(title))
                pass
            else:
                temp_list.append(url)
                temp_list.append(title)
                temp_list.append(useragent)
                workQueue.put(temp_list)
        queueLock.release()

        while not workQueue.empty():
            pass
        
        exitFlag = 1
        
        for t in threads:
            t.join()
        logging.info('DONE: {}'.format(curres))
        pagenum -= 1
        cp.set('Beauty', 'temp_page', str(pagenum))
        with open('config.ini', 'w') as f:
            cp.write(f)
        time.sleep(0.2)
    logging.info('ALL DONE')
