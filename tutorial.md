我们实验室所使用的机器人型号是NAO V6，我们使用的环境是Python2.7 32位（64位也行，为了减少麻烦，建议使用32位），**尽量避免使用中文目录**。
### 安装 Python 2.7 32位
通过此链接 [https://www.python.org/downloads/](https://www.python.org/downloads/) 打开 Python 的下载页面，找到 
[Python 2.7.18](https://www.python.org/downloads/release/python-2718/)
，点开。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617025695782-ffdef18c-4d20-4594-b7f3-698f39529d6e.png#align=left&display=inline&height=321&margin=%5Bobject%20Object%5D&name=image.png&originHeight=642&originWidth=1543&size=100955&status=done&style=none&width=771.5)
会看到这个页面。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617025790324-0454a8fc-0970-431b-b2d6-141e0e84ee95.png#align=left&display=inline&height=381&margin=%5Bobject%20Object%5D&name=image.png&originHeight=761&originWidth=1504&size=139314&status=done&style=none&width=752)
[Windows x86 MSI installer](https://www.python.org/ftp/python/2.7.18/python-2.7.18.msi) 是 Windows 系统 32位 安装程序，X86-64 是64位。这里我们下载32位版本。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617026475293-967f8392-35c2-4bad-9b55-8ffde9878abc.png#align=left&display=inline&height=267&margin=%5Bobject%20Object%5D&name=image.png&originHeight=533&originWidth=618&size=108579&status=done&style=none&width=309)
到达这个步骤时，我们把 Add python.exe to Path 选上，这样就不需要去手动添加环境变量了。
OK， 安装 Python 就到这里了。
### 安装 PyCharm
通过此链接 [https://www.jetbrains.com/pycharm/download/](https://www.jetbrains.com/pycharm/download/) 打开 PyCharm 的下载页面
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617027243511-1cfee837-5f74-461d-8de2-56d8412ca9ae.png#align=left&display=inline&height=278&margin=%5Bobject%20Object%5D&name=image.png&originHeight=556&originWidth=1448&size=73871&status=done&style=none&width=724)
这里有两个版本，Professinoal 专业版，付费。Community 社区版，免费。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617027387560-5ab46348-92de-4275-8917-cedbebad18c6.png#align=left&display=inline&height=402&margin=%5Bobject%20Object%5D&name=image.png&originHeight=803&originWidth=1011&size=43215&status=done&style=none&width=505.5)
社区版已拥有其核心功能，足够我们使用了。所以我们选择社区版。
#### 小提示
可以安装中文插件来设置中文语言。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617027714397-2cf5a9ae-aeb5-4668-91b1-e5ad3f529a27.png#align=left&display=inline&height=430&margin=%5Bobject%20Object%5D&name=image.png&originHeight=859&originWidth=702&size=252490&status=done&style=none&width=351)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617081174269-3c5e9896-5c30-4ef2-8b77-dafd2de55c9e.png#align=left&display=inline&height=210&margin=%5Bobject%20Object%5D&name=image.png&originHeight=420&originWidth=726&size=30415&status=done&style=none&width=363)
关键词 `chinese` ，下载完成重启IDE即可。
### 创建项目
使用 Virtualenv 建立虚拟环境，解释器选 Python2.7 32位。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617081301346-a88d3eb6-b944-4344-adb7-e974d81de266.png#align=left&display=inline&height=305&margin=%5Bobject%20Object%5D&name=image.png&originHeight=609&originWidth=999&size=67382&status=done&style=none&width=499.5)
### 导入Nao机器人SDK
通过此链接 [https://www.softbankrobotics.com/emea/en/support/nao-6/downloads-softwares](https://www.softbankrobotics.com/emea/en/support/nao-6/downloads-softwares) 打开软银的软件下载页面。
**![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617089308886-d2057019-a3e3-4b67-8378-fa609e6b264a.png#align=left&display=inline&height=415&margin=%5Bobject%20Object%5D&name=image.png&originHeight=829&originWidth=1894&size=76776&status=done&style=none&width=947)**
但是这里我们不使用最新版本（使用最新版可能会导致一些问题，读者请自行解决），点开 
[Former versions](https://www.softbankrobotics.com/emea/en/support/nao-6/downloads-softwares/former-versions?os=45&category=76)
。选择Python 2.7 SDK Binaries。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617089494544-e42ad2d8-7afb-4473-834e-759f6c680ba1.png#align=left&display=inline&height=388&margin=%5Bobject%20Object%5D&name=image.png&originHeight=775&originWidth=1850&size=78592&status=done&style=none&width=925)
下载后将 SDK 压缩包内的文件复制到前面创建的 Pycharm 项目的 venv 文件夹下面的 Lib 文件夹下。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617090654682-9b4ace7e-b77e-41cd-9e8c-55df9086b9ba.png#align=left&display=inline&height=360&margin=%5Bobject%20Object%5D&name=image.png&originHeight=719&originWidth=553&size=58786&status=done&style=none&width=276.5)
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617089626315-c7343ccc-ea4e-4cf5-b4f9-2297c3e6c3d1.png#align=left&display=inline&height=488&margin=%5Bobject%20Object%5D&name=image.png&originHeight=976&originWidth=1780&size=593924&status=done&style=none&width=890)
### 安装 OpenCV 
打开设置，点开项目，Python 解释器，添加包，搜索`opencv-python` 然后安装。高版本 OpenCV 可能会安装失败，建议使用 4.0 版本。
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617084587196-b3b18679-1612-48b5-afcd-01347d160c8c.png#align=left&display=inline&height=521&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1042&originWidth=1920&size=183059&status=done&style=none&width=960)
#### 小提示
将 pip 源更改为阿里云可以提高安装速度。
在用户文件夹下新建名为 pip 的文件夹，再在 pip 文件夹内新建 pip.ini 文件。写入下面的代码。
```
[global]  
index-url = http://mirrors.aliyun.com/pypi/simple/
[install]  
trusted-host=mirrors.aliyun.com
```
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617085328868-fcdd169e-9e2c-4fb6-a056-b2e12378f116.png#align=left&display=inline&height=184&margin=%5Bobject%20Object%5D&name=image.png&originHeight=368&originWidth=1342&size=28800&status=done&style=none&width=671)
### 测试
在 main.py 写入以下代码（让机器人说你好）。


```python
# coding=utf-8
from naoqi import ALProxy

IP = "192.168.1.107"  # 机器人的IP地址
PORT = 9559           # 机器人的端口号，默认9559
ttsProxy = ALProxy("ALTextToSpeech", IP, PORT)


def sayHi():
    ttsProxy.say("你好")


if __name__ == '__main__':
    sayHi()

```
![image.png](https://cdn.nlark.com/yuque/0/2021/png/12357682/1617090550078-3c661a13-96b3-4c39-876f-4d11b9869529.png#align=left&display=inline&height=521&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1042&originWidth=1920&size=218508&status=done&style=none&width=960)
除了连接失败以外没有其他错误，开发环境搭建就完成了。




