__doc__ = '如何使用yield完成协程(简化版的asyncio)'

import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

selector = DefaultSelector()
stopped = False
host = "127.0.0.1"  # 自建一个简单服务,模拟一个设置每个请求需要等待1s才返回结果
port = 5000
urls_todo = {'/', '/1', '/2', '/3', '/4', '/5', '/6', '/7', '/8', '/9'}
# urls_todo = {'/'}

# 在单线程内做协作式多任务调度
# 要异步,必回调
# 但为了避免地狱式回调,将回调一拆为三,回调链变成了Future-Task-Coroutine
# 下面的注解都是为了能方便理解Future-Task-Coroutine之间的互动以及怎么串起来的.

"""
无链式调用
selector的回调里只管给future设置值，不再关心业务逻辑
loop 内回调callback()不再关注是谁触发了事件,因为协程能够保存自己的状态，知道自己的future是哪个。也不用关心到底要设置什么值，因为要设置什么值也是协程内安排的。
已趋近于同步代码的结构
无需程序员在多个协程之间维护状态，例如哪个才是自己的sock
"""

"""
1.创建Crawler 实例；
2.调用fetch方法，会创建socket连接和在selector上注册可写事件；
3.fetch内并无阻塞操作，该方法立即返回；
4.重复上述3个步骤，将10个不同的下载任务都加入事件循环；
5.启动事件循环，进入第1轮循环，阻塞在事件监听上；
6.当某个下载任务EVENT_WRITE被触发，回调其connected方法，第一轮事件循环结束；
7.进入第2轮事件循环，当某个下载任务有事件触发，执行其回调函数；此时已经不能推测是哪个事件发生，因为有可能是上次connected里的EVENT_READ先被触发，也可能是其他某个任务的EVENT_WRITE被触发；（此时，原来在一个下载任务上会阻塞的那段时间被利用起来执行另一个下载任务了）
8.循环往复，直至所有下载任务被处理完成
9.退出事件循环，结束整个下载程序
"""


# 异步调用执行完的时候，就把结果放在它里面。这种对象称之为未来对象。
# 暂存task执行的结果和回调
class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):  # 各阶段的回调
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result  # 调用结果,b'http请求的结果字符'
        for fn in self._callbacks:  # 重要,回调函数集
            fn(self)  # Task.step


class Task:
    def __init__(self, coro):
        self.coro = coro  # Crawler(url).fetch()
        f = Future()
        # f.set_result(None)  # 感觉这句不是很必要
        self.step(f)  # 预激活

    def step(self, future):  # 管理fetch生成器: 第一次的激活/暂停后的恢复执行/以及配合set_result循环调用
        try:
            # send会进入到coro执行, 即fetch, 直到下次yield
            # next_future 为yield返回的对象,也就是下一次要调用的Future对象
            next_future = self.coro.send(future.result)  # __init__中的第一次step,将fetch运行到的82行的yield,
            # 返回EVENT_WRITE时的事件回调要用的future,然后等事件触发,由select调用on_connected,进而继续future中的回调
        except StopIteration:
            return
        next_future.add_done_callback(self.step)  # 这里需要重点理解,为下一次要调用的Future对象,注册下一次的step,供on_readable调用


# Coroutine yield实现的协程
class Crawler:
    def __init__(self, url):
        self.url = url
        self.response = b''

    def fetch(self):  # 函数内有了yield表达式,就是生成器了,生成器需要先调用next()迭代一次或者是先send(None)启动,遇到yield之后便暂停
        sock = socket.socket()
        sock.setblocking(False)
        try:
            sock.connect((host, port))
        except BlockingIOError:
            pass
        f = Future()  # 每到一个io事件都注册一个对应的Future

        def on_connected():
            # pass    # 若没有f.set_result,会报错KeyError: '236 (FD 236) is already registered'
            f.set_result(None)  # 必要语句,还涉及到恢复回调

        selector.register(sock.fileno(), EVENT_WRITE, on_connected)  # 连接io写事件
        yield f  # 注册完就yield出去,等待事件触发
        selector.unregister(sock.fileno())
        get = 'GET {0} HTTP/1.0\r\nHost: example.com\r\n\r\n'.format(self.url)  # self.url 区分每个协程
        sock.send(get.encode('ascii'))

        global stopped
        while True:
            f = Future()

            def on_readable():
                f.set_result(sock.recv(4096))  # 可读的情况下,读取4096个bytes暂存给Future,执行回调,使生成器继续执行下去

            selector.register(sock.fileno(), EVENT_READ, on_readable)  # io读事件
            chunk = yield f  # 返回f,并接受step中send进来的future.result值,也就是暂存的请求返回字符
            selector.unregister(sock.fileno())
            if chunk:
                self.response += chunk
            else:
                urls_todo.remove(self.url)
                if not urls_todo:
                    stopped = True
                break
        print("result:", self.response)


def loop():
    while not stopped:
        # 阻塞, 直到一个事件发生
        events = selector.select()
        for event_key, event_mask in events:  # 监听事件,触发回调,推动协程运行下去
            callback = event_key.data  # 就是 on_connected,和 on_readable
            callback()


if __name__ == '__main__':
    import time

    start = time.time()
    for url in urls_todo:
        crawler = Crawler(url)
        Task(crawler.fetch())
    loop()
    print(time.time() - start)
