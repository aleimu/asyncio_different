__doc__ = 'yield与yield from总结'
"""
https://mp.weixin.qq.com/s?__biz=MzIxMjY5NTE0MA==&mid=2247483720&idx=1&sn=f016c06ddd17765fd50b705fed64429c  # 完整的论述了协程的进化
https://www.cnblogs.com/zhaof/p/10072934.html
https://www.cnblogs.com/wongbingming/p/9085268.html
https://www.python.org/dev/peps/pep-0380/   # 起始点
"""

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
    return "这就是result"  # 生成器退出时，生成器(或子生成器)中的return expr表达式会出发StopIteration(expr)异常抛出


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

"""
协程在运行过程中有四个状态：

1.GEN_CREATE:等待开始执行
2.GEN_RUNNING:解释器正在执行，这个状态一般看不到
3.GEN_SUSPENDED:在yield表达式处暂停
4.GEN_CLOSED:执行结束

关于yield from 几点重要的说明：

1.子生成器产出的值都直接传给委派生成器的调用方(即客户端代码)
2.使用send()方法发送给委派生成器的值都直接传给子生成器。如果发送的值为None,那么会给委派调用子生成器的__next__()方法。如果发送的值不是None,那么会调用子生成器的send方法，如果调用的方法抛出StopIteration异常，那么委派生成器恢复运行，任何其他异常都会向上冒泡，传给委派生成器
3.生成器退出时，生成器(或子生成器)中的return expr表达式会出发StopIteration(expr)异常抛出
4.子生成器可能只是一个迭代器，并不是一个作为协程的生成器，所以它不支持.throw()和.close()方法,即可能会产生AttributeError 异常。
5.yield from表达式的值是子生成器终止时传给StopIteration异常的第一个参数。yield from 结构的另外两个特性与异常和终止有关。
6.传入委派生成器的异常，除了GeneratorExit之外都传给子生成器的throw()方法。如果调用throw()方法时抛出StopIteration异常，委派生成器恢复运行。StopIteration之外的异常会向上冒泡，传给委派生成器
7.如果把GeneratorExit异常传入委派生成器，或者在委派生成器上调用close()方法，那么在子生成器上调用clsoe()方法，如果它有的话。如果调用close()方法导致异常抛出，那么异常会向上冒泡，传给委派生成器，否则委派生成器抛出GeneratorExit异常

#实现yield from语法的伪代码如下：
_i：子生成器，同时也是一个迭代器
_y：子生成器生产的值
_r：yield from 表达式最终的值
_s：调用方通过send()发送的值
_e：异常对象

# 简化版
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
"""
