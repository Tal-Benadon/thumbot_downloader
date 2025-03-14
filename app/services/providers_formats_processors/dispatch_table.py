from .facebook import choose_facebook_format
from .instagram import choose_instagram_format
from .reddit import choose_reddit_format

dispatch_table = {
        'facebook': choose_facebook_format,
        'fb.watch': choose_facebook_format,
        'instagram': choose_instagram_format,
        'reddit': choose_reddit_format,
    }


# Here we consolidate the available providers(and their url format) and their respective extraction functions.