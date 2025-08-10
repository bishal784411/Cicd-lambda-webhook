import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


export const startagent = async () => {
  const response = await axios.post(`${API_BASE_URL}/agents/start-all`);
  return response.data;
};


export const stopagent= async () => {
  const response = await axios.post(`${API_BASE_URL}/agents/stop-all`);
  return response.data;
};


export const createLogStreamagent = (
// p0: string, //   agentName: string,
onMessage: (msg: string) => void): EventSource => {
  const eventSource = new EventSource(`${API_BASE_URL}/agents/stream-logs-all`);

  eventSource.onmessage = (event) => {
    onMessage(event.data);
  };

  eventSource.onerror = (event) => {
    console.error('EventSource error:', event);
    eventSource.close();
  };

  return eventSource;
};
