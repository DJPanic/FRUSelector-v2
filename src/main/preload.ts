import { contextBridge } from 'electron';

contextBridge.exposeInMainWorld('api', {
  send: (channel: string, data: any) => {
    // Preload script implementation
  },
  receive: (channel: string, func: Function) => {
    // Preload script implementation
  },
});
