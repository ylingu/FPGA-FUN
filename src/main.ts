import { app, BrowserWindow, Menu, ipcMain } from 'electron'
import path from 'path'
import { spawn, type ChildProcessWithoutNullStreams } from 'child_process'
import started from 'electron-squirrel-startup'
import kill from 'tree-kill'

let apiPort: number | null = null
let server: ChildProcessWithoutNullStreams
// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit()
}
Menu.setApplicationMenu(null)

const startServer = () => {
  if (app.isPackaged) {
    server = spawn(path.resolve(process.resourcesPath, 'main.dist', 'main.exe'))
  } else {
    server = spawn('uv', ['run', path.join(__dirname, '../../api/main.py')])
  }
  const onData = (data: Buffer) => {
    const message = data.toString()
    console.log(`${message}`)
    const portMatch = message.match(/PORT:\s*(\d+)/)
    if (portMatch) {
      apiPort = parseInt(portMatch[1], 10)
      console.log(`API Port: ${apiPort}`)
      createWindow()
      // 移除监听器
      server.stdout.off('data', onData)
      server.stdout.on('data', (data) => {
        console.log(`${data}`)
      })
    }
  }
  server.stdout.on('data', onData)
  server.stderr.on('data', (data) => {
    console.error(`${data}`)
  })
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  })
  // and load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL)
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`))
  }

  // Open the DevTools.
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools()
  }
}

app.on('ready', () => {
  ipcMain.handle('get-port', async () => {
    return apiPort
  })
  startServer()
})

app.on('window-all-closed', () => {
  if (server) {
    kill(server.pid as number)
  }
  app.quit()
})
