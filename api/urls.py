urlpatterns = {
    "FeedHandler" : r"/(?P<subdomain>[^/]+)/(?:private|public)/(?:(?P<lense>[^/]+)/posts|posts)/?$",
    "PostsHandler" : r"/(?P<subdomain>[^/]+)/(?:private|public)/(?:posts|[^/]+/posts)/.+",
}
