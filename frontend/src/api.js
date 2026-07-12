import axios from 'axios';

// Create a configured axios instance
export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  // Read from localStorage or environment if dynamic, but hardcoding for demo
  config.headers['X-API-Key'] = 'dev-secret-key';
  return config;
});

// Utility to wrap API calls
export const fetcher = async (url) => {
  const res = await api.get(url);
  return res.data;
};

// WebSocket Hook setup (can be expanded later)
export class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.listeners = new Set();
  }

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.listeners.forEach(listener => listener(data));
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connect(), 3000); // basic reconnect
    };
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Global instance for ATS
export const wsClient = new WebSocketClient('ws://localhost:8000/api/v1/ws');
