declare global {
  interface Window {
    electronAPI: { getPort: () => Promise<number | null> }
  }
}

export {} // 必须导出一个空对象，以确保该文件被作为模块处理
