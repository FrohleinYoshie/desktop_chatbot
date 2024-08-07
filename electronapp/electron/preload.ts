import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("myAPI", {
  counter: (count: number) => {
    return count + 1;
  },
});