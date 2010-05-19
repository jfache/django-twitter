"""Templates tags for accessing to Twitter"""
from django.conf import settings
from django.core.cache import cache
from django.template import Library, Node

from twitter import Api
 
register = Library() 
 
class TwitterTimelineNode(Node): 
    def __init__(self, num, varname):
        self.num = int(num)
        self.varname = varname 
        self.key = '%s-%s' % (self.num, self.varname)
 
    def render(self, context): 
        tweets = cache.get(self.key) 
        if not tweets: 
            tweets = Api().GetUserTimeline(settings.TWITTER_USER, self.num)
            cache.set(self.key, tweets, settings.TWITTER_TIMEOUT)
 
        if self.num == 1:
            context[self.varname] = tweets[0]
        else:
            context[self.varname] = tweets 
            return ''
            
class TwitterFollowersNode(Node):
    def __init__(self, num, varname):
        self.num = int(num)
        self.varname = varname
        self.key = '%s-%s' % (self.num, self.varname)
        
    def render(self, context):
        followers = cache.get(self.key)
        if not followers:
            followers = Api(username=settings.TWITTER_USER, password=settings.TWITTER_PASSWORD).GetFollowers()
            cache.set(self.key, followers, settings.TWITTER_TIMEOUT)
            
        for follower in followers:
            follower.profile_image_url = follower.profile_image_url.replace('normal.', 'mini.')
            
        context[self.varname] = followers[:self.num]
        return ''
 
@register.tag
def get_twitter_timeline(parser, token): 
    """usage : {% get_twitter_timeline n as tweets %}""" 
    bits = token.split_contents()
    if len(bits) != 4: 
        raise TemplateSyntaxError, "get_twitter_timeline tag takes exactly three arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to get_twitter_timeline tag must be 'as'"
    return TwitterTimelineNode(bits[1], bits[3])
    
@register.tag
def get_twitter_followers(parser, token): 
    """usage : {% get_twitter_followers n as followers %}"""
    bits = token.split_contents()
    if len(bits) != 4: 
        raise TemplateSyntaxError, "get_twitter_followers tag takes exactly three arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to get_twitter_followers tag must be 'as'"
    return TwitterFollowersNode(bits[1], bits[3])
