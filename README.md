# BFGTelegramBot
A bot that takes VK news and puts them on Telegram feed. With pictures! Was designed to work with BFGuns public, can be adapted
easily to any other. 

# Installation

1. Got to the project directory, locate `params.py`. Copy it and name it specific to the public you are parsing, e.g. `params_bfguns.py`
2. Correct all the params inside. Those are `bot_url`, `channel_id`, and `vk_public_domain`. They should be specific to your bot/vk public chain
3. Go to the bot.py, and find a line that says
```import params_bfguns as params```, note that `params_bfguns` might have a different name, but it should be in the begginning.
4. `python bot.py`, you can use `python bot.py >> /dev/null &` on Linux servers to avoid spamming in console and background execution.
5. Enjoy :)


# Properties inside bot.py

`articles_filename` - is simply a variable that determnes filename for the last stored articles

`articles` - container for processed articles. Don't modify unless you are sure what you are doing

`max_article_length` - Determines max preview length before script cuts it and puts link to article itself. Useful for long posts

`period_in_minutes` - Refresh rate in minutes. Defines how often script will poll for articles

`picture_temp_path` - Storage for a temp picture. Not really useful config option unless you need static temp.jpg

`remove_links` - This trigger will remove all <a>*</a> links from article

`include_article_link` - Trigger to determine whether include link to an actual article or not if the article doesn't fit in max length

`include_article_link_text` - Text of such articles. Can be changed to *More on CNN* or whatever you prefer

`delimeters` - List of things considered to be appropriate to use as end of logical sentence. E.g. if your max length is 300 and 
your article is 450, it will cut last 150, and then will search for first occuring delimeter in the list and cut to it. This ensures
you don't get cut in the middle of the sentence or the word. You can change the order, but that seems to be an OK order

