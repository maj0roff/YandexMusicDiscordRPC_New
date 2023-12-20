import wx.adv
import configparser
from wx import App, Frame, Icon, EVT_CLOSE
from wx.html2 import WebView

TRAY_ICON = 'resources/logo.ico'

config = configparser.ConfigParser()
config.read('config.ini')


class TokenFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Авторизация", size=(450, 600))
        self.token = None
        self.SetIcon(Icon(TRAY_ICON))

        self.browser = WebView.New(self)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_url_changed)
        msg = wx.adv.NotificationMessage(title="Привет!", message="Я не обнаружил конфиг в токене, пройди пожалуйста "
                                                                  "авторизацию.")
        msg.SetFlags(wx.ICON_INFORMATION)
        msg.Show()
        self.Bind(EVT_CLOSE, self.on_close)

    def on_url_changed(self, event):
        url = event.GetURL()

        if "#access_token" in url:
            self.token = url.split("=")[1].split("&")[0]
            self.Destroy()

    def on_close(self, event):
        self.token = None
        self.Destroy()


def update_token():
    app = App(redirect=False)
    token_frame = TokenFrame(None)
    token_frame.browser.LoadURL(
        "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")
    token_frame.Show()
    app.MainLoop()
    print(token_frame.token)

    config.set('Settings', 'token', token_frame.token)
    with open('config.ini', 'w') as cfg:
        config.write(cfg)

    msg = wx.adv.NotificationMessage(title="Уже совсем скоро!", message="Мы получили токен и теперь осталось "
                                                                        "только перезапустить программу.")
    msg.SetFlags(wx.ICON_INFORMATION)
    msg.Show()
