# 多线程下载小说
import threading, requests, time, os
from lxml import etree
from queue import Queue

gen_urls_done = False
file_list = []


def gen_urls(index_url, q):
    global file_list, gen_urls_done
    r = requests.get(index_url)
    html = etree.HTML(r.text)
    links = html.xpath('//div[@class="listmain"]/dl/dd/a/@href')[3:]
    titles = html.xpath('//div[@class="listmain"]/dl/dd/a/text()')[3:]
    break_index = links.index("javascript:dd_show()")
    next_links = html.xpath('//span[@class="dd_hide"]/dd/a/@href')
    next_titles = html.xpath('//span[@class="dd_hide"]/dd/a/text()')
    links = (links[:break_index] + next_links)[:100]
    titles = (titles[:break_index] + next_titles)[:100]
    file_list = titles
    # print(links, titles)
    for link in links:
        link = "https://www.zsdade.com" + link
        q.put(link)
    gen_urls_done = True


def download(q, path):
    global gen_urls_done
    while True:
        if q.empty() and gen_urls_done:
            print("已完成全部下载")
            break
        else:
            url = q.get()
            r = requests.get(url)
            # print(r.text)
            html = etree.HTML(r.text)
            content = html.xpath('//div[@id="chaptercontent"]/text()')
            content = "".join(content).strip().replace("\u3000\u3000", "\n")
            title = html.xpath('//h1[@class="wap_none"]/text()')[0].replace("*", "")
            # print(title)
            with open(f"{path}/{title}.txt", "w", encoding="utf-8") as f:
                f.write(title + "\n\n")
                f.write(content + "\n\n")
                print(f"{threading.current_thread().name}已完成..{title}的下载")


def combine_files(path):
    while not file_list:
        print("未发现fileList，等待0.5秒")
        time.sleep(0.5)
    fp = open(f"{path}/{time.time()}.txt", "a", encoding="utf-8")
    for filename in file_list:
        while True:
            filename = filename.replace("*", "")
            if os.path.isfile(f"{path}/{filename}.txt"):
                with open(f"{path}/{filename}.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                    fp.write(content)
                    print(f"已完成...{filename}的合并")
                os.remove(f"{path}/{filename}.txt")
                print("已删除...{filename}")
                break
            else:
                print(f"未发现...{filename}，等待0.5秒")
                time.sleep(0.5)
    fp.close()
    print("已完成全部文件合并")


def main():
    index_url = "https://www.zsdade.com/books/2206/"
    path = r"C:\\Learn\\python_basic\\Chapter 14 - threading\\files"
    q = Queue(maxsize=2000)
    th1 = threading.Thread(target=gen_urls, args=(index_url, q))
    th1.start()

    for i in range(3):
        th2 = threading.Thread(target=download, args=(q, path), name=f"线程{i}")
        th2.start()

    th3 = threading.Thread(target=combine_files, args=(path,))
    th3.start()


if __name__ == "__main__":
    main()
