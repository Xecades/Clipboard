/**
 * WebSocket client for real-time clipboard synchronization.
 */

const WS_BASE = import.meta.env.DEV
    ? "ws://localhost:8000/ws"
    : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`;

export type MessageHandler = (content: string) => void;

export class ClipboardWebSocket {
    private ws: WebSocket | null = null;
    private token: string;
    private onMessageCallback: MessageHandler | null = null;
    private reconnectTimer: number | null = null;
    private shouldReconnect = true;

    constructor(token: string) {
        this.token = token;
    }

    /**
     * Connect to WebSocket server.
     */
    connect(onMessage: MessageHandler): void {
        this.onMessageCallback = onMessage;
        this.shouldReconnect = true;
        this.createConnection();
    }

    private createConnection(): void {
        try {
            this.ws = new WebSocket(`${WS_BASE}?token=${this.token}`);

            this.ws.onopen = () => {
                console.log("WebSocket connected");
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.content !== undefined && this.onMessageCallback) {
                        this.onMessageCallback(data.content);
                    }
                } catch (error) {
                    console.error("Failed to parse WebSocket message:", error);
                }
            };

            this.ws.onerror = (error) => {
                console.error("WebSocket error:", error);
            };

            this.ws.onclose = () => {
                console.log("WebSocket closed");
                this.ws = null;

                // Attempt to reconnect after 3 seconds
                if (this.shouldReconnect) {
                    this.reconnectTimer = window.setTimeout(() => {
                        console.log("Reconnecting WebSocket...");
                        this.createConnection();
                    }, 3000);
                }
            };
        } catch (error) {
            console.error("Failed to create WebSocket connection:", error);
        }
    }

    /**
     * Send content update to server.
     */
    send(content: string): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ content }));
        }
    }

    /**
     * Close WebSocket connection.
     */
    disconnect(): void {
        this.shouldReconnect = false;

        if (this.reconnectTimer !== null) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
