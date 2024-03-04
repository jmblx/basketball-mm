// shared-websocket-worker.js
var ws;
var clients = [];

self.onconnect = function(e) {
    var port = e.ports[0];
    clients.push(port);

    if (!ws) {
        ws = new WebSocket(`ws://localhost:8000/finding-match/1x1/ws`);

        ws.onmessage = function(event) {
            // Передача сообщений от сервера всем подключенным клиентам (вкладкам)
            clients.forEach(client => {
                client.postMessage(event.data);
            });
        };

        ws.onclose = function() {
            // Обработка закрытия соединения
        };

        ws.onerror = function(error) {
            // Обработка ошибок
        };
    }

    port.onmessage = function(event) {
        // Обработка сообщений от клиентов (вкладок)
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(event.data);
        }
    };
};
