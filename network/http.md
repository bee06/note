
## 定义

超文本传输​​协议 (HTTP) 是 Internet 上最普遍和广泛采用的应用协议之一：它是客户端和服务器之间的通用语言，使现代网络成为可能。从最初作为单个关键字和文档路径的简单开始，它已成为不仅浏览器而且几乎所有连接 Internet 的软件和硬件应用程序的首选协议。

在本章中，我们将简要回顾一下 HTTP 协议的演变历史。对不同 HTTP 语义的全面讨论超出了本书的范围，但是了解 HTTP 的关键设计变化以及每个变化背后的动机，将为我们讨论 HTTP 性能提供必要的背景知识，尤其是在上下文中HTTP/2 中许多即将到来的改进。

## HTTP 0.9: The One-Line Protocol HTTP 0.9：单行协议

Tim Berners-Lee 最初的 HTTP 提议在设计时考虑到了简单性，以帮助采用他的另一个新生想法：万维网。该策略似乎奏效了：有抱负的协议设计者请注意。

1991 年，Berners-Lee 概述了新协议的动机并列出了几个高级设计目标：文件传输功能、请求对超文本存档进行索引搜索的能力、格式协商以及将客户端引用到另一台服务器的能力.为了证明实际理论，构建了一个简单的原型，它实现了所提议功能的一小部分：

客户端请求是单个 ASCII 字符串。

Client request is terminated by a carriage return (CRLF).
客户端请求由回车 (CRLF) 终止。

Server response is an ASCII character stream.
服务器响应是一个 ASCII 字符流。

Server response is a hypertext markup language (HTML).
服务器响应是超文本标记语言 (HTML)。

Connection is terminated after the document transfer is complete.
文件传输完成后连接终止。
> 流行的 Web 服务器，如 Apache 和 Nginx，仍然支持 HTTP 0.9 协议——部分原因是它没有太多！如果您好奇，请打开一个 Telnet 会话并尝试通过 HTTP 0.9 访问 google.com 或您自己喜欢的站点，并检查此早期协议的行为和限制。


# HTTP/1.0: Rapid Growth and Informational RFC
HTTP/1.0：快速增长和信息化 RFC

越来越多的新兴 Web 所需功能及其在公共 Web 上的用例迅速暴露了 HTTP 0.9 的许多基本限制：我们需要一个协议，它不仅可以服务于超文本文档，还可以提供有关请求的更丰富的元数据和响应、启用内容协商等。反过来，新生的 Web 开发人员社区通过一个特别的过程产生大量实验性 HTTP 服务器和客户端实现作为回应：实施、部署，看看其他人是否采用它。

从这段快速实验开始，一组最佳实践和通用模式开始出现，1996 年 5 月，HTTP 工作组 (HTTP-WG) 发布了 RFC 1945，其中记录了许多 HTTP/1.0 实现的“通用用法”在野外发现。请注意，这只是一个参考性的 RFC：我们所知道的 HTTP/1.0 不是正式规范或 Internet 标准！

Having said that, an example HTTP/1.0 request should look very familiar:
话虽如此，一个示例 HTTP/1.0 请求看起来应该非常熟悉：

前面的交换并不是 HTTP/1.0 功能的详尽列表，但它确实说明了一些关键的协议更改：

Request may consist of multiple newline separated header fields.
请求可能包含多个换行符分隔的标头字段。

Response object is prefixed with a response status line.
响应对象以响应状态行为前缀。

Response object has its own set of newline separated header fields.
响应对象有自己的一组换行符分隔的标题字段。

Response object is not limited to hypertext.
响应对象不限于超文本。

The connection between server and client is closed after every request.
服务器和客户端之间的连接在每次请求后关闭。

### HTTP/1.1: Internet Standard HTTP/1.1：互联网标准
将 HTTP 转变为官方 IETF Internet 标准的工作与围绕 HTTP/1.0 的文档编制工作同时进行，历时大约四年：1995 年至 1999 年。事实上，第一个官方 HTTP/1.1 标准定义于RFC 2068，于 1997 年 1 月正式发布，大约在 HTTP/1.0 发布后六个月。然后，两年半后，即 1999 年 6 月，标准中包含了一些改进和更新，并作为 RFC 2616 发布

HTTP/1.1 标准解决了早期版本中发现的许多协议歧义，并引入了许多关键性能优化：保持活动连接、分块编码传输、字节范围请求、附加缓存机制、传输编码和请求流水线。

Request for HTML file, with encoding, charset, and cookie metadata
请求 HTML 文件，包括编码、字符集和 cookie 元数据

Chunked response for original HTML request
原始 HTML 请求的分块响应

Number of octets in the chunk expressed as an ASCII hexadecimal number (256 bytes)
块中的八位字节数，表示为 ASCII 十六进制数（256 字节）

End of chunked stream response  分块流响应结束

Request for an icon file made on same TCP connection
在同一 TCP 连接上请求图标文件

Inform server that the connection will not be reused
通知服务器连接不会被重用

Icon response, followed by connection close
图标响应，然后关闭连接
此外，HTTP/1.1 协议添加了内容、编码、字符集，甚至语言协商、传输编码、缓存指令、客户端 cookie，以及可以针对每个请求协商的其他十几种功能。

### HTTP/2：提高传输性能
自发布以来，RFC 2616 一直是互联网空前发展的基础：数十亿台各种形状和大小的设备，从台式电脑到我们口袋里的微型网络设备，每天都使用 HTTP 来传送新闻、视频、以及我们在生活中所依赖的数百万其他 Web 应用程序。