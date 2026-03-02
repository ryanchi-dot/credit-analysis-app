"""
心跳机制装饰器

在长时间任务中自动发送心跳消息，告知用户Agent还在工作
"""
import asyncio
import time
from typing import Callable, AsyncGenerator, Any, Optional
from langchain_core.messages import AIMessage


async def heartbeat_generator(
    base_generator: AsyncGenerator[Any, None],
    interval: float = 29.0,
    heartbeat_message: Optional[str] = None
) -> AsyncGenerator[Any, None]:
    """
    心跳生成器装饰器
    
    Args:
        base_generator: 基础生成器（Agent的输出流）
        interval: 心跳间隔（秒）
        heartbeat_message: 心跳消息模板
        
    Yields:
        来自基础生成器的消息，以及定期的心跳消息
    """
    if heartbeat_message is None:
        heartbeat_message = "⏳ 我还在努力生成报告中，请稍候..."
    
    last_heartbeat_time = time.time()
    
    async def send_heartbeat():
        """发送心跳消息"""
        return AIMessage(content=heartbeat_message)
    
    # 创建两个任务：1. 从基础生成器获取消息 2. 定期发送心跳
    base_task = asyncio.create_task(_collect_all(base_generator))
    heartbeat_task = asyncio.create_task(_heartbeat_loop(interval, last_heartbeat_time))
    
    try:
        # 等待基础生成器完成
        messages = await base_task
        # 取消心跳任务
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        # 返回所有消息
        for msg in messages:
            yield msg
    except asyncio.CancelledError:
        base_task.cancel()
        heartbeat_task.cancel()
        raise


async def _collect_all(generator: AsyncGenerator[Any, None]) -> list:
    """收集生成器的所有输出"""
    messages = []
    async for msg in generator:
        messages.append(msg)
    return messages


async def _heartbeat_loop(interval: float, last_heartbeat_time: float):
    """心跳循环"""
    while True:
        await asyncio.sleep(interval)
        last_heartbeat_time = time.time()
        # 注意：这里只是记录时间，实际发送心跳需要在更上层实现


class HeartbeatContext:
    """心跳上下文管理器"""
    
    def __init__(self, interval: float = 29.0):
        self.interval = interval
        self.last_heartbeat_time = time.time()
        self._heartbeat_task: Optional[asyncio.Task] = None
    
    async def __aenter__(self):
        """进入上下文，启动心跳任务"""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，取消心跳任务"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        return False
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while True:
            elapsed = time.time() - self.last_heartbeat_time
            if elapsed >= self.interval:
                self.last_heartbeat_time = time.time()
                # 返回需要发送心跳的信号
                yield True
            else:
                yield False
                await asyncio.sleep(1)
    
    def should_send_heartbeat(self) -> bool:
        """检查是否应该发送心跳"""
        elapsed = time.time() - self.last_heartbeat_time
        if elapsed >= self.interval:
            self.last_heartbeat_time = time.time()
            return True
        return False
