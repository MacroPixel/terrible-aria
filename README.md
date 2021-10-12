# Terrible-aria
This is my attempt to recteate Terraria without using a graphics engine, and also without any non-standard libraries. Its set of features is currently rather limited, but I'd be happy to expand on this if the project sees enough attention. For more information, you can [watch this.](https://youtu.be/nCSx0Gq7zP8)

### Executing the project
In order to run the project, all you should need is a Python interpreter (since it only uses the standard library). There is a variable named “DEBUG” that you can change to toggle debug mode. There is also a variable named “SHOW_PROG” that can be marked false to prevent the game from printing the world progress (which is useful because some terminals take a long time to buffer their output).

### Web Port
Unfortunately, there currently exists no web port. I would like to make one, but there’s one big problem that’s preventing me from doing so. The code I wrote in Python requires receiving return values from blocking functions (i.e. input()). This is a problem because for some reason, browser code only runs in a single thread, so waiting on an input will freeze the browser. I don’t think I can use asyncio either, because that still requires waiting for the input. If anybody knows a way to fix this, I’d appreciate if you [emailed me](mailto:macropixelyt@gmail.com) :)
