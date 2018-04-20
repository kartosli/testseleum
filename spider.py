from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo

brower = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
wait = WebDriverWait(brower,10)
KEYWORD = "美短加白"
MAX_PAGE = 100

host = "127.0.0.1"
port = 27017
dbname = "mymango"
sheetname ="testSelenium"
# 创建MONGODB数据库链接
client = pymongo.MongoClient(host=host, port=port)
mydb = client[dbname]
sheetname =mydb[sheetname]
def index_page(page):
    """
  抓取索引页
  :param page: 页码
  """
    print('正在爬取第', page, '页')

    try:
        url =  'https://s.taobao.com/search?q=' + quote(KEYWORD)
        brower.get(url);
        if page>1:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager div.form > input')))
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()

        # wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.item.active > span'),str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.m-itemlist .items .item')))

        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    """
    提取商品数据
    """
    html = brower.page_source
    doc = pq(html)

    items = doc('#mainsrp-itemlist .items .item').items();
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text().replace('\xa0', '').replace('\n', ''),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text().replace('\xa0', '').replace('\n', ''),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)
    pass

def save_to_mongo(result):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        if sheetname.insert(result):
            print('存储到MongoDB成功')
    except Exception as e:
        print(e)
        print('存储到MongoDB失败')

def main():
    for i in range(1, MAX_PAGE + 1):
        index_page(i)
    brower.close()

if __name__ == '__main__':
    main()

