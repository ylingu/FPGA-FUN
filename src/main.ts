import { app, BrowserWindow, Menu, ipcMain } from 'electron'
import path from 'path'
import { spawn, type ChildProcessWithoutNullStreams } from 'child_process'
import started from 'electron-squirrel-startup'
import { promisify } from 'util'
import * as fs from 'fs'
import kill from 'tree-kill'

const readFile = promisify(fs.readFile)
const unlinkFile = promisify(fs.unlink)
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
  server.stdout.on('data', (data) => {
    console.log(`${data}`)
  })
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

const readPort = async () => {
  let portInfoPath: string
  if (app.isPackaged) {
    portInfoPath = path.resolve(process.resourcesPath, 'main.dist', 'port.json')
  } else {
    portInfoPath = path.resolve(__dirname, '../../api/port.json')
  }
  try {
    let data: string
    const maxRetries = 5
    let retries = 0
    while (retries < maxRetries) {
      try {
        data = await readFile(portInfoPath, 'utf8')
        break
      } catch (e) {
        retries++
        if (retries === maxRetries) {
          throw e
        }
        await new Promise((resolve) => setTimeout(resolve, 100))
      }
    }
    const json = JSON.parse(data!)
    apiPort = json.port
    await unlinkFile(portInfoPath)
  } catch (e) {
    console.error(e)
    app.quit()
  }
}

startServer()

app.on('ready', () => {
  ipcMain.handle('get-port', async () => {
    if (apiPort === null) {
      await readPort()
    }
    return apiPort
  })
  createWindow()
})

app.on('window-all-closed', () => {
  if (server) {
    kill(server.pid as number)
  }
  app.quit()
})
