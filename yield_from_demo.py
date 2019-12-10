__doc__ = '如何使用yield from完成协程(简化版的asyncio)'

import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

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


# 结果保存，每一个处需要异步的地方都会调用，保持状态和callback
# 程序得知道当前所处的状态，而且要将这个状态在不同的回调之间延续下去。
class Future:
    def __init__(self):
        self.result = None  # 重要参数1
        self._callbacks = []  # 重要参数2

    def add_done_callback(self, fn):  # 各阶段的回调
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result  # 调用结果,b'http请求的结果字符'
        for fn in self._callbacks:
            fn(self)  # 执行Task.step

    def __iter__(self):
        """
        yield的出现使得__iter__函数变成一个生成器，生成器本身就有next方法，所以不需要额外实现。
        yield from x语句首先调用iter(x)获取一个迭代器（生成器也是迭代器）
        """
        yield self  # 外面使用yield from把f实例本身返回
        return self.result  # 在Task.step中send(result)的时候再次调用这个生成器，但是此时会抛出stopInteration异常，并且把self.result返回


# 激活包装的生成器，以及在生成器yield后恢复执行继续下面的代码
class Task:
    def __init__(self, coro):  # Crawler(url).fetch()
        self.coro = coro
        f = Future()
        # f.set_result(None)
        self.step(f)  # 激活Task包裹的生成器

    def step(self, future):
        try:
            # next_future = self.coro.send(future.result)
            next_future = self.coro.send(None)  # 驱动future
            # next_future = future.send(None)  # 这样是错误的
            # __init__中的第一次step,将fetch运行到的82行的yield,
            # 返回EVENT_WRITE时的事件回调要用的future,然后等事件触发,由select调用on_connected,进而继续future中的回调
        except StopIteration:
            return
        next_future.add_done_callback(self.step)  # 这里需要重点理解,为下一次要调用的Future对象,注册下一次的step,供on_readable调用


# 异步就是可以暂定的函数，函数间切换的调度靠事件循环,yield 正好可以中断函数运行
# Coroutine yield实现的协程
# 将yield_demo.py中的Crawler进行了拆解,并使用yield from
class Crawler:
    def __init__(self, url):
        self.url = url
        self.response = b""

    def fetch(self):  # 委托生成器,参考yield_to_from.py
        global stopped
        sock = socket.socket()
        yield from connect(sock, (host, port))
        get = "GET {0} HTTP/1.0\r\nHost:example.com\r\n\r\n".format(self.url)
        sock.send(get.encode('ascii'))
        self.response = yield from read_all(sock)
        print(self.response)
        urls_todo.remove(self.url)
        if not urls_todo:
            stopped = True


# 连接事件的子协程:注册+回调
def connect(sock, address):
    f = Future()
    sock.setblocking(False)
    try:
        sock.connect(address)
    except BlockingIOError:
        pass

    def on_connected():
        f.set_result(None)

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield from f  # f需要可迭代,需要新增Future.__iter__
    selector.unregister(sock.fileno())


# 可读事件的子协程:注册+回调
def read(sock):
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)  # 注册一个文件对象以监听其IO事件;
    """
    此处的chunck接收的是f中return的f.result，同时会跑出一个stopIteration的异常，只不过被yield from处理了。
    这里也可直接写成chunck = yiled f
    """
    chunck = yield from f  # f需要可迭代,需要新增Future.__iter__
    selector.unregister(sock.fileno())  # 从selection中注销文件对象, 即从监听列表中移除它; 文件对象应该在关闭前注销.
    return chunck


# 委托生成器,参考yield_to_from.py,生成器的嵌套
def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)  # yield from来解决生成器里玩生成器的问题
    result = b"".join(response)
    print("result:", result)  # 打印下结果吧
    return result


# 事件驱动，让所有之前注册的callback运行起来
def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:  # 监听事件,触发回调,推动协程运行下去
            callback = event_key.data  # data就是 on_connected,和 on_readable
            callback()


if __name__ == "__main__":
    import time

    start = time.time()
    for url in urls_todo:
        crawler = Crawler(url)
        Task(crawler.fetch())  # 将各生成器和对应的callback注册到事件循环loop中，并激活生成器
    loop()
    print(time.time() - start)
