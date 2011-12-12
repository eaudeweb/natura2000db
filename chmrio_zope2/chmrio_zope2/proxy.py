from Products.Five.browser import BrowserView


class ChmRioFormsProxy(BrowserView):

    def __call__(self):
        # TODO view is not protected by ViewManagementScreens permission :(
        return ":)\n"
