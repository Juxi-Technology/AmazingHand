/* WebSocket 传输层 —— 页面由 server.py 提供时使用。
 *
 * 接口与 io.js 的 window.AHIO 完全一致（init / send），所以 app.js 不需要知道
 * 串口到底在浏览器里（Web Serial）还是在 Python 服务端（WebSocket）。
 * server.py 在返回 index.html 时注入 window.AH_BACKEND = "ws" 来选中这一层。
 */
(function () {
  "use strict";

  const WS_PORT = 8765;
  const RECONNECT_MIN_MS = 800;
  const RECONNECT_MAX_MS = 6000;

  let ws = null;
  let onMessage = () => {};
  let retryDelay = RECONNECT_MIN_MS;
  let pending = [];        // 连接建立前发出的指令

  function wsUrl() {
    return `ws://${location.hostname || "localhost"}:${WS_PORT}`;
  }

  function flushPending() {
    const queue = pending;
    pending = [];
    for (const msg of queue) transmit(msg);
  }

  function transmit(msg) {
    ws.send(JSON.stringify(msg));
  }

  function open() {
    try {
      ws = new WebSocket(wsUrl());
    } catch (e) {
      setTimeout(open, RECONNECT_MIN_MS);
      return;
    }

    ws.onopen = () => {
      retryDelay = RECONNECT_MIN_MS;
      flushPending();
      transmit({ cmd: "hello" });
    };

    ws.onmessage = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch (e) { return; }
      onMessage(msg);
    };

    ws.onclose = () => {
      setTimeout(open, retryDelay);
      retryDelay = Math.min(retryDelay * 1.6, RECONNECT_MAX_MS);
    };

    ws.onerror = () => {};
  }

  function send(msg) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      transmit(msg);
      return true;
    }
    pending.push(msg);
    return false;
  }

  window.AH_WS = {
    init(opts) {
      onMessage = (opts && opts.onMessage) || (() => {});
      open();
    },
    send,
    isConnected: () => !!ws && ws.readyState === WebSocket.OPEN,
  };
})();
