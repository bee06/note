demoService.sayHello("world" + i)
-->InvokerInvocationHandler.invoke
  -->invoker.invoke
    -->RpcInvocation//所有请求参数都会转换为RpcInvocation
    -->MockClusterInvoker.invoke //1.进入集群
      -->invoker.invoke(invocation)
        -->AbstractClusterInvoker.invoke
          -->list(invocation)
            -->directory.list//2.进入目录查找   从this.methodInvokerMap里面查找一个Invoker
              -->AbstractDirectory.list
                -->doList(invocation)
                  -->RegistryDirectory.doList// 从this.methodInvokerMap里面查找一个Invoker
                -->router.route //3.进入路由 
                  -->MockInvokersSelector.route
                    -->getNormalInvokers
          -->ExtensionLoader.getExtensionLoader(LoadBalance.class).getExtension("roundrobin")
          -->doInvoke
            -->FailoverClusterInvoker.doInvoke
              -->select//4.进入负载均衡
                -->AbstractClusterInvoker.select
                  -->doselect
                    -->loadbalance.select
                      -->AbstractLoadBalance.select
                        -->doSelect
                          -->RoundRobinLoadBalance.doSelect
                            -->invokers.get(currentSequence % length)//取模轮循
              -->Result result = invoker.invoke(invocation)
--------------------------------------------------------------------------扩展点----------------
                -->InvokerWrapper.invoke
                  -->ProtocolFilterWrapper.invoke
                    -->ConsumerContextFilter.invoke
                      -->ProtocolFilterWrapper.invoke
                        -->MonitorFilter.invoke
                          -->ProtocolFilterWrapper.invoke
                            -->FutureFilter.invoke
                              -->ListenerInvokerWrapper.invoke
                                -->AbstractInvoker.invoke
---------------------------------------------------------------------------扩展点---------------
                                  -->doInvoke(invocation)
                                    -->DubboInvoker.doInvoke//为什么DubboInvoker是个protocol? 因为RegistryDirectory.refreshInvoker.toInvokers： protocol.refer
                                      -->ReferenceCountExchangeClient.request
                                        -->HeaderExchangeClient.request
                                          -->HeaderExchangeChannel.request
                                            -->NettyClient.send
                                            -->AbstractPeer.send
                                              -->NettyChannel.send
                                                -->ChannelFuture future = channel.write(message);//最终的目的：通过netty的channel发送网络数据
//consumer的接收原理 
NettyHandler.messageReceived
  -->AbstractPeer.received
    -->MultiMessageHandler.received
      -->HeartbeatHandler.received
        -->AllChannelHandler.received
          -->ChannelEventRunnable.run //线程池 执行线程
            -->DecodeHandler.received
              -->HeaderExchangeHandler.received
                -->handleResponse(channel, (Response) message);
                  -->HeaderExchangeHandler.handleResponse
                    -->DefaultFuture.received
                      -->DefaultFuture.doReceived
                        private void doReceived(Response res) {
                  lock.lock();
                  try {
                      response = res;
                      if (done != null) {
                          done.signal();
                      }
                  } finally {
                      lock.unlock();
                  }
                  if (callback != null) {
                      invokeCallback(callback);
                  }
              }









                  
                  

灰度发布例子：
provider  192.168.100.38    192.168.48.32
1.发布192.168.48.32，切断192.168.48.32访问流量，然后进行服务的发布。
2.192.168.48.32发布成功后，恢复 192.168.48.32的流量，

3.切断192.168.100.38，继续发布 192.168.100.38
                  
2个疑问
1.启动路由规则，它触发了那些动作？
  a.什么时候加入ConditionRouter？
  b.ConditionRouter是怎么过滤的？
2.路由规则有哪些实现类？    
ConditionRouter：条件路由，后台管理的路由配置都是条件路由。
ScriptRouter：脚本路由       
              