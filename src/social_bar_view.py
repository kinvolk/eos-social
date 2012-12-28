import gtk
import gobject
from facebook.fb_auth_view import FBAuthView
from ui import MainWindow
from ui import SimplePopUp
import webkit
from ui import PostMessage
from ui import PostMessageSendArea
import os
from ui import UserAvatar
from ui import WelcomePanel
from ui import MultiPanel
from ui import UserProfileMenu
from ui import LogoutLabel
from ui import UserNameLabel
import gettext

gettext.install('endlessm_social_bar', '/usr/share/locale', unicode=True, names=['ngettext'])

#gtk.gdk.threads_init()

class SocialBarView(MainWindow):


    def __init__(self):
        super(SocialBarView, self).__init__()
        self.connect('destroy', self._destroy)
        self._presenter = None

    def set_presenter(self, presenter):
        super(SocialBarView, self).set_background_image(
          '/usr/share/endlessm_social_bar/images/bg-right.png')
        self._presenter = presenter
        self._browser = webkit.WebView()
#        self._browser.set_size_request(-1, 600)
        self._browser.connect("navigation-requested", self._navigation_handler)
        self.post_message_area = PostMessageSendArea()
        self.user_avatar_menu = UserProfileMenu(self._presenter)
        self.user_avatar_menu.connect('user-profile-action', self._on_action)
        self.user_name = UserNameLabel(self._presenter.get_profil_display_name())
        self.user_name.connect('user-name-action', self._on_action)
        self.logout = LogoutLabel('x Logout')
        self.logout.connect('logout-label-action', self._on_action)
        self.user_avatar = UserAvatar(self.user_avatar_menu)
        self.user_avatar.set_presenter(self._presenter)
        #self.user_avatar.connect('user-profile-action', self._on_action)
        self.post_message_area.connect('post-panel-action', self._on_action)
        self.post_message = PostMessage(self.post_message_area, self.user_avatar, self.user_name, self.logout)
        self.post_message.connect('post-panel-action', self._on_action)

        # pack main container
        self.main_container = gtk.VBox()
        self.main_container.pack_start(self.post_message, expand=False, fill=False, padding=0)
        self.main_container.pack_start(self._browser, expand=True, fill=True, padding=0)

        self.welcome_panel = WelcomePanel()
        self.welcome_panel.connect('welcome-panel-action', self._on_action)

        self.wraper_main = MultiPanel()
        self.wraper_main.add_panel(self.main_container, 'main_container')
        self.wraper_main.add_panel(self.welcome_panel, 'welcome_panel')
        self.add(self.wraper_main)
        self.show_all()
        self.wraper_main.show_panel('welcome_panel')
        self.logout.hide()
        self.user_name.hide()

    def _on_action(self, widget, action):
        if action == 'post':
            self.post_message.toggle_text_field()
            self.post_message_area.set_default_text()
        elif action == 'cancel':
            self.post_message.collapse_text_field()
            self.post_message_area.set_default_text()
        elif action == 'close':
            self.iconify()
            #gtk.main_quit()
        elif action == 'send':
            text = self.post_message_area.get_post_message()
            #self.post_message_area.set_default_text()
            self.post_message_area.clear_text(True)
            self.post_message.collapse_text_field()
            if text is not None:
                self._presenter.post_to_fb(text)
        elif action == 'avatar':
            if self.user_avatar.get_is_expanded():
                self._presenter.show_profil_page()
                self.user_avatar.set_is_expanded(False)
                self.logout.hide()
                self.user_name.hide()
            else:
                self.user_avatar.set_is_expanded(True)
                x = self.user_avatar.allocation.x - self.user_name.allocation.width - 8
                y = self.user_name.allocation.y
                self.post_message.toolbar.move(self.user_name, x, y)
                x = self.user_avatar.allocation.x - self.logout.allocation.width - 8
                y = self.logout.allocation.y
                self.post_message.toolbar.move(self.logout, x, y)
                self.logout.show()
                self.user_name.show()
        elif action == 'user-name':
            self._presenter.show_profil_page()
            self.user_avatar.set_is_expanded(False)
            self.logout.hide()
            self.user_name.hide()
        elif action == 'user_profile':
            self._presenter.show_profil_page()
        elif action == 'login':
            self._perform_login()
        elif action == 'logout_on_shutdown_active':
            self._presenter.set_logout_on_shutdown_active(True)
        elif action == 'logout_on_shutdown_inactive':
            self._presenter.set_logout_on_shutdown_active(False)
        elif action == 'logout':
            print 'logout'
            self.user_avatar.set_is_expanded(False)
            self.logout.hide()
            self.user_name.hide()
            self.wraper_main.show_panel('welcome_panel')
            self._presenter.logout()
        else:
            print 'no action ->', action

    def _perform_login(self):

        def _callback():
            self._presenter.get_fb_news_feed()
            self._presenter.get_profil_picture()
            file_path = self._presenter.get_stored_picture_file_path()
            self.user_avatar.set_avatar(file_path)
            self.wraper_main.show_panel('main_container')

        if self._presenter.is_user_loged_in():
            _callback()
        else:
            self._presenter.fb_login(callback=_callback)

    def show_popup_notification(self, notification_text):
        SimplePopUp(notification_text).show()
    
    def show_browser(self):
        self._browser.show()
    
    def load_html(self, html):
#        print '='*80
#        print html
#        print '='*80
        result = self._browser.load_string(html, 'text/html', 'utf-8', '')
#        print 'RESULT:', result
        self.show_browser()
    
    def _navigation_handler(self, view, frame, request, data=None):
        print 'In navigation handler view function...'
        return self._presenter.navigator(request.get_uri())
    
    def _destroy(self, *args):
        if self._presenter.get_logout_on_shutdown_active():
            self._presenter.logout()
        gtk.main_quit()

    def main(self):
        gobject.threads_init()
        gtk.threads_init()
        gtk.main()

