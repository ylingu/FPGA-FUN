import { app, BrowserWindow, Menu, ipcMain } from 'electron'
import path from 'path'
import spawn from 'child_process'
import started from 'electron-squirrel-startup'
import { promisify } from 'util'
import * as fs from 'fs'

const readFile = promisify(fs.readFile)

let apiPort: number | null = null
// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit()
}
Menu.setApplicationMenu(null)

const startServer = () => {
  const server = spawn.spawn('python', [path.join(__dirname, '../../api/main.py')])
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
  //
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL)
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`))
  }

  // Open the DevTools.
  mainWindow.webContents.openDevTools()
}

const readPort = async () => {
  const portInfoPath = path.join(__dirname, '../../api/port.json')
  try {
    let data: string
    while (true) {
      try {
        data = await readFile(portInfoPath, 'utf8')
        break
      } catch (e) {
        const code = (e as { code: string }).code
        if (code !== 'ENOENT') {
          await new Promise((resolve) => setTimeout(resolve, 100))
        } else {
          throw e
        }
      }
    }
    const json = JSON.parse(data)
    apiPort = json.port
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

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
