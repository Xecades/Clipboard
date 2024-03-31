# Clipboard

Yeah, simply a "shared instant-view online clipboard".

I created this to make it more elegant to transfer code snippets with my remote desktop.

Anyone who is viewing the webpage can not only see BUT ALSO EDIT the clipboard content. Thus, it's NOT a wise idea to store sensitive information here or to use it in a public network.

The clipboard app is powered by Leancloud, mainly because I don't want to buy a server.

If you want to build it yourself, make sure to provide following environment variables:

```env
VITE_APP_ID
VITE_APP_KEY
VITE_SERVER_URL
```
