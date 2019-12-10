## 写在前面

世界是复杂的,每一种思想都是为了解决某些现实问题而简化成的模型,想解决就得先面对,面对就需要选择角度,角度决定了模型的质量, 喜欢此UP主[汤质看本质](https://space.bilibili.com/362588980?from=search&seid=11461744258011572799)的哲学科普,其中简洁又不失细节的介绍了人类解决问题的思路,以及由概念搭建的思维模型对人类解决问题的重要性与限制.也认识到学习的本质就是: **认识获取(了解概念) -> 知识学习(建立模型) -> 技能训练(实践)**

阅读也好, 学习也好, 妨碍我们「理解」的障碍主要有两个：

* 高度抽象的概念
* 「模型」无法关联现象
也就是说 概念明确 + 关系明确, 才能构成「模型」, 对照「现象」, 形成「理解」。

在理解编程知识时可以关键归纳为两点：**理解核心概念群+使用场景思考与故事化讲述**

这里特别推荐码农翻身中大话编程式的科普:

[码农翻身全年文章精华](https://www.cnblogs.com/jinloooong/p/7286293.html)

## 并发模型

并发思想的一些探寻[并发之痛 Thread, Goroutine, Actor](http://jolestar.com/parallel-programming-model-thread-goroutine-actor/)中有较好的总结:
**陈力就列, 不能者止** 能干活的代码片段就放在线程里, 如果干不了活（需要等待, 被阻塞等）, 就摘下来。通俗的说就是不要占着茅坑不拉屎, 如果拉不出来, 需要酝酿下, 先把茅坑让出来, 因为茅坑是稀缺资源。

要做到这点一般有两种方案：

* 异步回调方案
典型如NodeJS, 遇到阻塞的情况, 比如网络调用, 则注册一个回调方法（其实还包括了一些上下文数据对象）给IO调度器（linux下是libev, 调度器在另外的线程里）, 当前线程就被释放了, 去干别的事情了。等数据准备好, 调度器会将结果传递给回调方法然后执行, 执行其实不在原来发起请求的线程里了, 但对用户来说无感知。但这种方式的问题就是很容易遇到callback hell, 因为所有的阻塞操作都必须异步, 否则系统就卡死了。还有就是异步的方式有点违反人类思维习惯, 人类还是习惯同步的方式。

* GreenThread/Coroutine/Fiber方案
这种方案其实和上面的方案本质上区别不大, 关键在于回调上下文的保存以及执行机制。为了解决回调方法带来的难题, 这种方案的思路是写代码的时候还是按顺序写, 但遇到IO等阻塞调用时, 将当前的代码片段暂停, 保存上下文, 让出当前线程。等IO事件回来, 然后再找个线程让当前代码片段恢复上下文继续执行, 写代码的时候感觉好像是同步的, 仿佛在同一个线程完成的, 但实际上系统可能切换了线程, 但对程序无感。


GreenThread

    * 用户空间 首先是在用户空间, 避免内核态和用户态的切换导致的成本。
    * 由语言或者框架层调度
    * 更小的栈空间允许创建大量实例（百万级别）

几个概念

    * Continuation 这个概念不熟悉FP编程的人可能不太熟悉, 不过这里可以简单的顾名思义, 可以理解为让我们的程序可以暂停, 然后下次调用继续（contine）从上次暂停的地方开始的一种机制。相当于程序调用多了一种入口。
    * Coroutine 是Continuation的一种实现, 一般表现为语言层面的组件或者类库。主要提供yield, resume机制。
    * Fiber 和Coroutine其实是一体两面的, 主要是从系统层面描述, 可以理解成Coroutine运行之后的东西就是Fiber。

Goroutine其实就是前面GreenThread系列解决方案的一种演进和实现。


[程序员修神之路--分布式高并发下Actor模型如此优秀](https://www.cnblogs.com/zhanlang/p/10585749.html)中说:
**传统多数流行的语言并发是基于多线程之间的共享内存, 使用同步方法防止写争夺, Actors使用消息模型, 每个Actor在同一时间处理最多一个消息, 可以发送消息给其他Actor, 保证了单独写原则。从而巧妙避免了多线程写争夺。和共享数据方式相比, 消息传递机制最大的优点就是不会产生数据竞争状态。实现消息传递有两种常见的类型：基于channel（golang为典型代表）的消息传递和基于Actor（erlang为代表）的消息传递。二者的格言都是："Don’t communicate by sharing memory, share memory by communicating"**


### 进程通信模型

[进程间8种通信方式详解](https://blog.csdn.net/violet_echo_0908/article/details/51201278)

[Linux 线程间通信方式+进程通信方式 总结](https://blog.csdn.net/sinat_34166518/article/details/82744410)

每个进程各自有不同的用户地址空间,任何一个进程的全局变量在另一个进程中都看不到, 所以进程之间要交换数据必须通过内核,在内核中开辟一块缓冲区,进程A把数据从用户空间拷到内核缓冲区,进程B再从内核缓冲区把数据读走,内核提供的这种机制称为进程间通信。

进程间几种通信方式:

    管道：速度慢, 容量有限, 只有父子进程能通讯
    FIFO：任何进程间都能通讯, 但速度慢
    消息队列：容量受到系统限制, 且要注意第一次读的时候, 要考虑上一次没有读完数据的问题
    信号量：不能传递复杂消息, 只能用来同步 5.共享内存区：能够很容易控制容量, 速度快, 但要保持同步, 比如一个进程在写的时候, 另一个进程要注意读写的问题, 相当于线程中的线程安全, 当然, 共享内存区同样可以用作线程间通讯, 不过没这个必要, 线程间本来就已经共享了同一进程内的一块内存
    Socket通信(又名客户机服务器系统)

Python 为进程通信提供了两种机制：

    Queue：一个进程向 Queue 中放入数据, 另一个进程从 Queue 中读取数据。如multiprocessing.Queue()
    Pipe：Pipe 代表连接两个进程的管道。程序在调用 Pipe() 函数时会产生两个连接端, 分别交给通信的两个进程, 接下来进程既可从该连接端读取数据, 也可向该连接端写入数据。如multiprocessing.Pipe()

方式有很多种,其他模型中也都能在此找到影子.

### CSP模型
CSP(communicating sequential processes)模型里消息和Channel是主体
也就是说发送方需要关心自己的消息类型以及应该写到哪个Channel, 但不需要关心谁消费了它, 以及有多少个消费者。
Golang是自己解决的通信问题, 从概念上就当消息队列理解, 但是技术上, golang用的不是linux的消息队列.

[Go的CSP并发模型实现：M, P, G](https://www.cnblogs.com/sunsky303/p/9115530.html)

### Actor模型
Actor模型是1973年提出的一个分布式并发编程模式, 在Erlang语言中得到广泛支持和应用。

[Actor模型](https://www.jianshu.com/p/d803e2a7de8e)

![Actor模型](https://upload-images.jianshu.io/upload_images/4933701-b75859a15d14b508.png?imageMogr2/auto-orient/strip|imageView2/2/w/558/format/webp)


[Actor模型和CSP模型的区别](https://blog.csdn.net/woshiyuanlei/article/details/51285701)CSP模型和Actor模型是两门非常复古且外形接近的并发模型。但CSP与Actor有以下几点比较大的区别：

* CSP并不Focus发送消息的实体/Task, 而是关注发送消息时消息所使用的载体, 即channel。
* 在Actor的设计中, Actor与信箱是耦合的, 而在CSP中channel是作为first-class独立存在的。
* 另外一点在于, Actor中有明确的send/receive的关系, 而channel中并不区分这样的关系, 执行块可以任意选择发送或者取出消息。


## Go并发

以上的铺垫应该对并发涉及到的概念有清晰的认识,也能发现这些概念都不是go或python原创的,这里有较好的总结
[Go/Python/Erlang编程语言对比分析及示例](https://www.cnblogs.com/wahaha02/p/8876445.html) 说:
**Go的很多语言特性借鉴与它的三个祖先：C, Pascal和CSP。Go的语法、数据类型、控制流等继承于C, Go的包、面对对象等思想来源于Pascal分支, 而Go最大的语言特色, 基于管道通信的协程并发模型, 则借鉴于CSP分支。**

![灵感来源](https://images2018.cnblogs.com/blog/756873/201804/756873-20180418153852139-1131047688.png)

**不要用共享内存来通信, 要用通信来共享内存**大概是golang在推广中最容易被人提及的了,类似python之禅一样.

Golang调度器有三个主要数据结构。
```
G (goroutine) 协程, 被Golang语言本身管理的线程
    举例来说, func main() { go other() }, 这段代码创建了两个goroutine,
    一个是main, 另一个是other, 注意main本身也是一个goroutine.

    goroutine的新建, 休眠, 恢复, 停止都受到go运行时的管理.
    goroutine执行异步操作时会进入休眠状态, 待操作完成后再恢复, 无需占用系统线程,
    goroutine新建或恢复时会添加到运行队列, 等待M取出并运行.

M (machine) 操作系统的线程, 被操作系统管理的, 原生线程
    M可以运行两种代码:

    go代码, 即goroutine, M运行go代码需要一个P
    原生代码, 例如阻塞的syscall, M运行原生代码不需要P
    M会从运行队列中取出G, 然后运行G, 如果G运行完毕或者进入休眠状态, 则从运行队列中取出下一个G运行, 周而复始.
    有时候G需要调用一些无法避免阻塞的原生代码, 这时M会释放持有的P并进入阻塞状态, 其他M会取得这个P并继续运行队列中的G.
    go需要保证有足够的M可以运行G, 不让CPU闲着, 也需要保证M的数量不能过多.

P (process) 调度的上下文, 运行在M上的调度器。
    P是process的头文字, 代表M运行G所需要的资源.
    一些讲解协程的文章把P理解为cpu核心, 其实这是错误的.
    虽然P的数量默认等于cpu核心数, 但可以通过环境变量GOMAXPROC修改, 在实际运行时P跟cpu核心并无任何关联.

    P也可以理解为控制go代码的并行度的机制,
    如果P的数量等于1, 代表当前最多只能有一个线程(M)执行go代码,
    如果P的数量等于2, 代表当前最多只能有两个线程(M)执行go代码.
    执行原生代码的线程数量不受P控制.

    因为同一时间只有一个线程(M)可以拥有P, P中的数据都是锁自由(lock free)的, 读写这些数据的效率会非常的高.
```

G的状态

* 空闲中(_Gidle): 表示G刚刚新建, 仍未初始化
* 待运行(_Grunnable): 表示G在运行队列中, 等待M取出并运行
* 运行中(_Grunning): 表示M正在运行这个G, 这时候M会拥有一个P
* 系统调用中(_Gsyscall): 表示M正在运行这个G发起的系统调用, 这时候M并不拥有P
* 等待中(_Gwaiting): 表示G在等待某些条件完成, 这时候G不在运行也不在运行队列中(可能在channel的等待队列中)
* 已中止(_Gdead): 表示G未被使用, 可能已执行完毕(并在freelist中等待下次复用)
* 栈复制中(_Gcopystack): 表示G正在获取一个新的栈空间并把原来的内容复制过去(用于防止GC扫描)

M的状态
M并没有像G和P一样的状态标记, 但可以认为一个M有以下的状态:

* 自旋中(spinning): M正在从运行队列获取G, 这时候M会拥有一个P
* 执行go代码中: M正在执行go代码, 这时候M会拥有一个P
* 执行原生代码中: M正在执行原生代码或者阻塞的syscall, 这时M并不拥有P
* 休眠中: M发现无待运行的G时会进入休眠, 并添加到空闲M链表中, 这时M并不拥有P
* 自旋中(spinning)这个状态非常重要, 是否需要唤醒或者创建新的M取决于当前自旋中的M的数量.

P的状态

* 空闲中(_Pidle): 当M发现无待运行的G时会进入休眠, 这时M拥有的P会变为空闲并加到空闲P链表中
* 运行中(_Prunning): 当M拥有了一个P后, 这个P的状态就会变为运行中, M运行G会使用这个P中的资源
* 系统调用中(_Psyscall): 当go调用原生代码, 原生代码又反过来调用go代码时, 使用的P会变为此状态
* GC停止中(_Pgcstop): 当gc停止了整个世界(STW)时, P会变为此状态
* 已中止(_Pdead): 当P的数量在运行时改变, 且数量减少时多余的P会变为此状态


Golang 的协程本质上其实就是对 IO 事件的封装, 并且通过语言级的支持让异步的代码看上去像同步执行的一样。

[Golang源码探索(二) 协程的实现原理](https://studygolang.com/articles/11627)

## Python并发

本段落涉及的代码基本是对[深入理解Python异步编程(上)](https://mp.weixin.qq.com/s?__biz=MzIxMjY5NTE0MA==&mid=2247483720&idx=1&sn=f016c06ddd17765fd50b705fed64429c) 的注解,之前也学习过yield,也总结了几次,
但之前都没有把事件循环联系进来,感性的知道python中的协程就是靠:"事件循环 + 回调",其中细节一直没深入看,asyncio源码也看过几次,也是走马观花.这次偶然看到这么有系统且有示例代码辅助的文章,所以下面的东西很多都来自此文章以及对其代码的注解.

在asyncio正式转正前,就有很多人和库尝试了其他方式,如:

1. stackless 的通道(channel)
    * 能够在微进程之间交换信息。channel.send + channel.receive
    * 能够控制运行的流程。
2. yield和greenlet
    * 都可以实现协程,不过每一次都要人为的去指向下一个该执行的协程, 显得太过麻烦
3. gevent
    * gevent每次遇到io操作, 需要耗时等待时, 会自动跳到下一个协程继续执行。邪恶的猴子补丁(Monkey patching)在这种情况下, gevent能够修改标准库里面大部分的阻塞式系统调用, 包括socket、ssl、threading和 select等模块, 而变为协作式运行。

[Python yield与实现](https://www.cnblogs.com/coder2012/p/4990834.html)

[Stackless Python并发式编程介绍](https://blog.csdn.net/changbaohua/article/details/3777410)

[python greenlet背景介绍与实现机制](https://blog.csdn.net/offbye/article/details/39368781)


### 理解yield以及yield from
先了解 py3.3 -> py3.8 之间的异步方式演进,建议使用官方yield例子,在idea中debug调试运行,**着重看函数中yield处中断执行后又如何被恢复,其实主要就是通过next或send让函数恢复执行.然后就是找到那些next和send以及是被怎么推动的**
总结来说,协程就是对可以中断/恢复执行的函数的调度.
题外话[阅读源码的三种境界](https://mp.weixin.qq.com/s/PDhEKM2XG_qzOmBjWb-M7Q)

#### yield 的四种常见用法：
    1. 生成器
    2. 用于定义上下文管理器
    3. 协程
    4. 配合 from 形成 yield from 用于消费子生成器并传递消息

这四种用法, 其实都源于 yield 所具有的暂停的特性, 也就说程序在运行到 yield 所在的位置 result = yield expr 时, 先执行 yield expr 将产生的值返回给调用生成器的 caller
, 然后暂停, 等待 caller 再次激活并恢复程序的执行。而根据恢复程序使用的方法不同, yield expr 表达式的结果值 result 也会跟着变化。
如果使用 __next()__ 来调用, 则 yield 表达式的值 result 是 None；如果使用 send() 来调用, 则 yield 表达式的值 result 是通过 send 函数传送的值。

#### 用 yield from 改进生成器协程
yield from 一方面可以迭代地消耗生成器, 另一方面则建立了一条双向通道, 把最外层的调用方与最内层的子生成器连接起来, 并自动地处理异常, 接收子生成器返回的值。

yield from 更多地被用于协程, 而 await 关键字的引入会大大减少 yield from 的使用频率。

 实现yield from语法的伪代码如下：
```python
"""
_i：子生成器, 同时也是一个迭代器
_y：子生成器生产的值
_r：yield from 表达式最终的值
_s：调用方通过send()发送的值
_e：异常对象
"""
#简化版
_i = iter(EXPR)
try:
    _y = next(_i)
except StopIteration as _e:
    _r = _e.value
else:
    while 1:
        try:
            _s = yield _y
        except StopIteration as _e:
            _r = _e.value
            break
RESULT = _r


#完整版
 _i = iter(EXPR)
try:
    _y = next(_i)
except StopIteration as _e:
    _r = _e.value

else:
    while 1:
        try:
            _s = yield _y
        except GeneratorExit as _e:
            try:
                _m = _i.close
            except AttributeError:
                pass
            else:
                _m()
            raise _e
        except BaseException as _e:
            _x = sys.exc_info()
            try:
                _m = _i.throw
            except AttributeError:
                raise _e
            else:
                try:
                    _y = _m(*_x)
                except StopIteration as _e:
                    _r = _e.value
                    break
        else:
            try:
                if _s is None:
                    _y = next(_i)
                else:
                    _y = _i.send(_s)
            except StopIteration as _e:
                _r = _e.value
                break
RESULT = _r

```

##### 通过示例来理解
参考 yield_to_from.py,划分一下方便理解:

    1、调用方：调用委派生成器的客户端（调用方）代码
    2、委托生成器：包含yield from 表达式的生成器函数
    3、子生成器：yield from 后面加的生成器函数
有不清晰的地方,就在IDE中debug下,着重来看包含yield的函数之间的跳转,以及yield from存在的意义.
```python
n = m = 5
flag = "stop"  # 子生成器停止信号,此例子中是有调用者控制,也可以改写成子生成器控制,调用者检查到信号还停止迭代子生成器.

"""
1、调用方：调用委派生成器的客户端（调用方）代码
2、委托生成器：包含yield from 表达式的生成器函数
3、子生成器：yield from 后面加的生成器函数

重点:yield让函数中断执行,next或send让函数恢复执行,使用debug查看各个函数间的跳转,或者直接运行,看print打印.
"""


def gen():  # 子生成器
    print("start 子生成器")
    # for k in range(n):    # 有限子生成器
    k = "k"
    while True:  # 无限子生成器
        print("子生成器--要返回的值:", k)
        t = yield k  # 1.运行到这里就会停下来,切换到其他地方,等待send或next触发后再从此处继续执行 2.yield功能相当于golang中的chan,可接受可发送
        print("子生成器--接受到的值:", t)
        if t is flag:
            break
    print("end 子生成器")
    return "这就是result"  # 生成器退出时, 生成器(或子生成器)中的return expr表达式会出发StopIteration(expr)异常抛出


def proxy_gen():  # 委托生成器--类似go-chan
    # 在调用方与子生成器之间建立一个双向通道,调用方可以通过send()直接发送消息给子生成器,而子生成器yield的值,也是直接返回给调用方
    # while True:
    result = yield from gen()
    print("委托生成器result:", result)
    yield result


def main1():  # 调用方1--不通过proxy_gen迭代子生成器
    g = gen()  # 子生成器
    print(g.send(None))
    print(g.send(1))  # 发送1到子生成器中
    print(next(g))
    try:
        print(g.send(flag))  # 不使用委托器 子生成器的停止信号就得手动处理
    except StopIteration as e:
        print("StopIteration")
        print("子生成器return的值:", e.value)


def main2():  # 调用方2--常用迭代
    g = proxy_gen()
    g.send(None)  # 需要先激活子生成器,否则会报错 TypeError: can't send non-None value to a just-started generator
    for k in range(m):
        print("调用方--要发送的值:", k)
        print("调用方--接受到的值:", g.send(k))
        print("--------------------")
    g.send(flag)  # 针对无限子生成器的停止信号


def main3():  # 调用方3--死循环
    g = proxy_gen()
    g.send(None)  # 需要先激活子生成器,否则会报错 TypeError: can't send non-None value to a just-started generator
    for k in g:  # for调用能完整的遍历生成器,遍历的时候已经调用了__next__,相当于g.send(None)
        print("调用方--接受到的值:", k)
        print("调用方--要发送的值:", g.send("m"))
        print("调用方--接受到的值:", k)
        print("--------------------")


print("*********************")
main1()
print("*********************")
main2()
print("*********************")
main3()
print("*********************")

```


#### 文字描述

包含yield语句的函数就是一个生成器对象, 调用一个生成器函数, 返回的是一个迭代器对象。迭代器Iterator表示的是一个数据流, 迭代器可以被next()函数调用并不断返回下一个数据, 直到没有数据时抛出StopIteration错误。迭代器控制生成器函数的执行, 当函数开始运行, 执行到第一个yield语句时暂停, 将yield表达式后的表达式的值返回给调用者。
在生成器函数暂停时, 其现阶段的状态都被保存下来, 包括生成器函数局部变量当前绑定的值、指令指针、函数内部执行堆栈以及任何异常状态的处理。当生成器函数再次被调用时则直接从上次暂停的yield表达式处接着运行, 直到遇到下一个yield语句, 或者没有遇到yield语句则运行结束。
需要说明的是, 在函数重新运行时, 其实上次暂停处的yield表达式会先接收一个值作为结果, 然后才接着运行直到碰到下一个yield表达式。
如果调用者使用next函数或者__next__()方法, 则默认返回给yield表达式None值；使用send()方法则传递一个值作为yield表达式的结果。

对于简单的迭代器, yield from iterable本质上等于for item in iterable: yield item的缩写版(iterable 也可以是generator),yield 和 send(next)成对出现,有点类似于go中的chan,彼此通知对方数据到位请继续执行下去
一般将yield from视为提供了一个调用者和子生成器之间的透明的双向通道。包括从子生成器获取数据以及向子生成器传送数据。

* generator.__next__()：启动或从上个yield表达式处恢复生成器运行；当生成器被__next__()方法恢复运行时, 当前yield表达式被赋值为None；for循环和next()函数都隐式调用__next__()。
* generator.send(value)：恢复并返回值给生成器函数；返回给生成器函数的值将赋予当前的yield表达式, 并向调用者返回下一个yield表达式产生的值。如果要启动生成器函数, 则用send(None)。
* StopIteration异常是特殊的,迭代完生成器都会抛出,但都会被自动catch住,让生成器之后的代码继续运行

总结：
1. 子生成器产出的值都直接传给委派生成器的调用方(即客户端代码)
2. 使用send()方法发送给委派生成器的值都直接传给子生成器。如果发送的值为None,那么会给委派调用子生成器的__next__()方法。如果发送的值不是None,那么会调用子生成器的send方法, 如果调用的方法抛出StopIteration异常, 那么委派生成器恢复运行, 任何其他异常都会向上冒泡, 传给委派生成器
3. 生成器退出时, 生成器(或子生成器)中的return expr表达式会出发StopIteration(expr)异常抛出
4. 子生成器可能只是一个迭代器, 并不是一个作为协程的生成器, 所以它不支持.throw()和.close()方法,即可能会产生AttributeError 异常。
5. yield from表达式的值是子生成器终止时传给StopIteration异常的第一个参数。yield from 结构的另外两个特性与异常和终止有关。
6. 传入委派生成器的异常, 除了GeneratorExit之外都传给子生成器的throw()方法。如果调用throw()方法时抛出StopIteration异常, 委派生成器恢复运行。StopIteration之外的异常会向上冒泡, 传给委派生成器
7. 如果把GeneratorExit异常传入委派生成器, 或者在委派生成器上调用close()方法, 那么在子生成器上调用clsoe()方法, 如果它有的话。如果调用close()方法导致异常抛出, 那么异常会向上冒泡, 传给委派生成器, 否则委派生成器抛出GeneratorExit异常



### asyncio
asyncio是Python 3.4 试验性引入的异步I/O框架（PEP 3156）, 提供了基于协程做异步I/O编写单线程并发代码的基础设施。其核心组件有事件循环（Event Loop）、协程(Coroutine）、任务(Task)、未来对象(Future)以及其他一些扩充和辅助性质的模块。

实现原理:

**事件循环+回调**
有一个任务调度器（event loop）, 然后可以用async def定义异步函数作为任务逻辑, 通过create_task接口把任务挂到event loop上。
event loop的运行过程应该是个不停循环的过程, 不停查看等待类别有没有可以执行的任务, 如果有的话执行任务, 直到碰到await之类的主动让出event loop的函数, 如此反复。
若是看源码的你就会发现使用yield和yield from实现协程也会用到类似EventLoop,Future,Future,Coroutine的东西,这在下面的示例部分再次看到.

* Eventloop 是asyncio应用的核心, 是中央总控。Eventloop实例提供了注册、取消和执行任务和回调的方法。
* Future 是结果存储+回调管理器
* Coroutine 使用生成器技术来替代连续的多个回调
* Task 负责将Coroutine接口和Future、EventLoop接口对接起来, 同时它自己也是一个Future.

对比生成器版的协程, 使用asyncio库后变化很大：

    * 没有了yield 或 yield from, 而是async/await
    * 没有了自造的loop(), 取而代之的是asyncio.get_event_loop()
    * 无需自己在socket上做异步操作, 不用显式地注册和注销事件, aiohttp库已经代劳
    * 没有了显式的 Future 和 Task, asyncio已封装

更少量的代码, 更优雅的设计



## 示例注解

分别使用yield,yield from,asyncio 模拟协程,并发的爬几个url的代码.

```python
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
selector的回调里只管给future设置值, 不再关心业务逻辑
loop 内回调callback()不再关注是谁触发了事件,因为协程能够保存自己的状态, 知道自己的future是哪个。也不用关心到底要设置什么值, 因为要设置什么值也是协程内安排的。
已趋近于同步代码的结构
无需程序员在多个协程之间维护状态, 例如哪个才是自己的sock
"""

"""
1.创建Crawler 实例；
2.调用fetch方法, 会创建socket连接和在selector上注册可写事件；
3.fetch内并无阻塞操作, 该方法立即返回；
4.重复上述3个步骤, 将10个不同的下载任务都加入事件循环；
5.启动事件循环, 进入第1轮循环, 阻塞在事件监听上；
6.当某个下载任务EVENT_WRITE被触发, 回调其connected方法, 第一轮事件循环结束；
7.进入第2轮事件循环, 当某个下载任务有事件触发, 执行其回调函数；此时已经不能推测是哪个事件发生, 因为有可能是上次connected里的EVENT_READ先被触发, 也可能是其他某个任务的EVENT_WRITE被触发；（此时, 原来在一个下载任务上会阻塞的那段时间被利用起来执行另一个下载任务了）
8.循环往复, 直至所有下载任务被处理完成
9.退出事件循环, 结束整个下载程序
"""


# 异步调用执行完的时候, 就把结果放在它里面。这种对象称之为未来对象。
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

```

```python
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
selector的回调里只管给future设置值, 不再关心业务逻辑
loop 内回调callback()不再关注是谁触发了事件,因为协程能够保存自己的状态, 知道自己的future是哪个。也不用关心到底要设置什么值, 因为要设置什么值也是协程内安排的。
已趋近于同步代码的结构
无需程序员在多个协程之间维护状态, 例如哪个才是自己的sock
"""

"""
1.创建Crawler 实例；
2.调用fetch方法, 会创建socket连接和在selector上注册可写事件；
3.fetch内并无阻塞操作, 该方法立即返回；
4.重复上述3个步骤, 将10个不同的下载任务都加入事件循环；
5.启动事件循环, 进入第1轮循环, 阻塞在事件监听上；
6.当某个下载任务EVENT_WRITE被触发, 回调其connected方法, 第一轮事件循环结束；
7.进入第2轮事件循环, 当某个下载任务有事件触发, 执行其回调函数；此时已经不能推测是哪个事件发生, 因为有可能是上次connected里的EVENT_READ先被触发, 也可能是其他某个任务的EVENT_WRITE被触发；（此时, 原来在一个下载任务上会阻塞的那段时间被利用起来执行另一个下载任务了）
8.循环往复, 直至所有下载任务被处理完成
9.退出事件循环, 结束整个下载程序
"""


# 结果保存, 每一个处需要异步的地方都会调用, 保持状态和callback
# 程序得知道当前所处的状态, 而且要将这个状态在不同的回调之间延续下去。
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
        yield的出现使得__iter__函数变成一个生成器, 生成器本身就有next方法, 所以不需要额外实现。
        yield from x语句首先调用iter(x)获取一个迭代器（生成器也是迭代器）
        """
        yield self  # 外面使用yield from把f实例本身返回
        return self.result  # 在Task.step中send(result)的时候再次调用这个生成器, 但是此时会抛出stopInteration异常, 并且把self.result返回


# 激活包装的生成器, 以及在生成器yield后恢复执行继续下面的代码
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


# 异步就是可以暂定的函数, 函数间切换的调度靠事件循环,yield 正好可以中断函数运行
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
    此处的chunck接收的是f中return的f.result, 同时会跑出一个stopIteration的异常, 只不过被yield from处理了。
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


# 事件驱动, 让所有之前注册的callback运行起来
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
        Task(crawler.fetch())  # 将各生成器和对应的callback注册到事件循环loop中, 并激活生成器
    loop()
    print(time.time() - start)

```


```python
__doc__ = "使用asyncio"

import asyncio
import aiohttp

host = 'http://127.0.0.1:5000'
urls_todo = {'/', '/1', '/2', '/3', '/4', '/5', '/6', '/7', '/8', '/9'}

loop = asyncio.get_event_loop()


async def fetch(url):
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(url) as response:
            response = await response.read()
            print("result:", response)
            return response


if __name__ == '__main__':
    import time

    start = time.time()
    tasks = [fetch(host + url) for url in urls_todo]
    loop.run_until_complete(asyncio.gather(*tasks))
    print(time.time() - start)

```

到这里基本python的协程改进历史就说完了,下面就是对比goroutine与asyncio.
这里[python协程与go协程的区别](https://www.cnblogs.com/lgjbky/p/10838035.html)有我以前写的一个简单对比,下面的一些东西是补充和联想.

## 对比select

python的select是基于eventloop的,是检测事件是否可读/可写,可以说是协程的心脏了.

```python
# 事件驱动, 让所有之前注册的callback运行起来
def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:  # 监听事件,触发回调,推动协程运行下去
            callback = event_key.data  # data就是 on_connected,和 on_readable
            callback()
```

go中的select是检测channel是否可读,可写,避免goroutine不必要的阻塞.

```go
select {
case v1 := <-c1:
    fmt.Printf("received %v from c1\n", v1)
case v2 := <-c2:
    fmt.Printf("received %v from c2\n", v1)
case c3 <- 23:
    fmt.Printf("sent %v to c3\n", 23)
default:
    fmt.Printf("no one was ready to communicate\n")
}
```

## 对比chan与yield

```go
var ch chan ElementType
ch := make(chan int)
ch <- value    //写入
value := <-ch  //读取
```

```python
def step(self, future):  # 管理fetch生成器: 第一次的激活/暂停后的恢复执行/以及配合set_result循环调用
    try:
        # send会进入到coro执行, 即fetch, 直到下次yield
        # next_future 为yield返回的对象,也就是下一次要调用的Future对象
        next_future = self.coro.send(future.result)  # __init__中的第一次step,将fetch运行到的82行的yield,
        # 返回EVENT_WRITE时的事件回调要用的future,然后等事件触发,由select调用on_connected,进而继续future中的回调
    except StopIteration:
        return
    next_future.add_done_callback(self.step)  # 这里需要重点理解,为下一次要调用的Future对象,注册下一次的step,供on_readable调用



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

```

**chunk = yield f**,返回f,并接受step中send进来的值,yield暂停子生成器函数的运行把cpu的使用权让出去,对比chan等待其他chan时处于等待中状态(_Gwaiting),是不是有点 chan 的味道了.
子生成器中包含多个yield和带缓存的chan,是不是也有相似呢?
python是单线程中调度多个协程,而go是多个进程中调度多个协程,感觉yield和chan是有异曲同工之妙的.


## 一点延伸

维特根斯坦说「在语言中显示自身的东西, 我们无法用语言来表示它」, 这句话不太好理解, 请允许我做一个不负责任的类比。比如计算机编程, 逻辑相当于机器语言或者汇编语言, 反正是比较底层的那种；人的语言相当于高级编程语言, 类似java和python；我们的生活就是软件的图形界面。如果你是一个工程师, 你一定是顺着理解这件事的——机器语言一定是基础啊, 它是一切得以运作绝对前提啊。维特根斯坦会说, 幼稚！我当年也是这么想的他说, 必须倒过来理解。因为人和图形界面的交互, 才会有高级语言的各种安排, 才会有机器语言的各种运作。为什么？因为人才是一切的尺度, 人这个主体和软件界面产生交互模式（人和生活）, 最终决定了你那些0和1的意义（语言和逻辑）。维特根斯坦那句话的意思是, 你从图形界面的维度能解释为什么这行代码要这样写, 但你在这行代码的维度解释不了它为什么会被写成这样, 在人与图形界面交互的过程中, 这段字符承载的意义远超过这段字符本身所显示的全部, 代码的意义在于使用, 「语言的意义也在于使用」, Meaning is use!
简单理解, 维特根斯坦的整个逻辑是：底层原理能解释表层现象, 但反过来却不行。表层最多能描述底层。
比如, 人性能解释商业为什么是那个样子的, 但商业却不能解释人性为什么是那个样子, 商业只能从它所在的侧面描述人性是什么样的, 因为商业形式就是被人性塑造的。之前, 我们以为代码是底层, 图形是表层。其实, 图形才是底层, 代码是表层, 这里的意思是, 生活能解释语言, 语言却只能描述生活。语言妄图解释生活, 表层妄图解释底层的结果就是哲学的出现。

这样就造就了一个可悲的事实,即人类对自然的认识永远只能无限的接近真理, 却永远无法探究到所谓的本源, 认识自然的过程其实都是在盲人摸象。
从实际出发, 不同问题用不同方法, 一个模型是否可靠, 看的从来不是理论或模型是否高明, 检验真理的唯一标准只有一条, 就是实践, 自己动手去尝试证实。


## 参考资料

[官方说明](https://www.python.org/dev/peps/pep-0380/)

[深入理解Python异步编程(上)](https://mp.weixin.qq.com/s?__biz=MzIxMjY5NTE0MA==&mid=2247483720&idx=1&sn=f016c06ddd17765fd50b705fed64429c)  # 十分期待后续的中与下.

[python3.6异步IO包asyncio部分核心源码思路梳理](https://www.cnblogs.com/olivertian/p/11444480.html)

[总结了才知道, 原来channel有这么多用法！](https://www.jianshu.com/p/76acce09da09)

[怎么掌握asyncio?](https://www.zhihu.com/question/294188439/answer/555273313)

[Python高级编程和异步IO并发编程视频系列教程](https://www.bilibili.com/video/av64192449?from=search&seid=5851197638749086818)

[浅谈 Go 语言实现原理](https://draveness.me/golang/)

[Golang中非CSP并发模型外的其他并行方法总结](https://juejin.im/post/5c1dce2d51882508506061f2)

[图解Go select语句原理](https://juejin.im/post/5ca0e2336fb9a05e2a301479)

[图解Golang的channel底层原理](https://juejin.im/post/5cb3445f6fb9a068b748ab75)

