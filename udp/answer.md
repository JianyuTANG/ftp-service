# UDP实现聊天客户端

软件71 唐建宇 2017012221

1. 使用`socket.socket(socket.AF_INET, socket.SOCK_DGRAM)`创建udp协议的socket

2. 将socket绑定一个端口

3. 开启一个额外的线程：

   - 在主线程中通过`while True`循环地接收用户输入，每次输入完毕调用`sendto`函数发送至对方

   - 在开启的另一个线程中，通过`while True`循环地使用`recvfrom`接收消息，收到消息后将消息内容打印在控制台或渲染在图形界面中