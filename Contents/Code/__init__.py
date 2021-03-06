import urllib, re, time, random

NAME = 'RedTube'
randomArt = random.randint(1,4)
ART = 'artwork-'+str(randomArt)+'.jpg'
ICON = 'icon-default.png'

REDTUBE_BASE						= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com'
REDTUBE_NEWEST					= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/?page=%s'
REDTUBE_RATED						= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/top?period=%s___page=%s'
REDTUBE_VIEWED					= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/mostviewed?period=%s___page=%s'
REDTUBE_FAVORED					= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/mostfavored?period=%s___page=%s'
REDTUBE_CHANNELS_LIST		= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/channels'
REDTUBE_CHANNELS				= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com%s?sorting=%s___page=%s'
REDTUBE_PORNSTARS_LIST	= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/pornstar/%s/%s'
REDTUBE_PORNSTAR				= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/pornstar/%s?page=%s'
REDTUBE_SEARCH					= 'http://plexchannels.flowsworld.com/redirect.php?page=redtube&url=http://www.redtube.com/%s?search=%s___page=%s'

####################################################################################################

def Start():
	# Initialize the plugin
	Plugin.AddPrefixHandler('/video/redtube', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")

	# Setup the artwork associated with the plugin
	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	MediaContainer.viewGroup = "List"
	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)

	HTTP.CacheTime = 60
	HTTP.Headers['Referer'] = 'http://plexchannels.flowsworld.com'
	HTTP.RandomizeUserAgent(browser=None)

####################################################################################################

def Thumb(url):
	try:
		data = HTTP.Request(url).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))

def GetDurationFromString(duration):
	try:
		durationArray = duration.split(":")
		if len(durationArray) == 3:
			hours = int(durationArray[0])
			minutes = int(durationArray[1])
			seconds = int(durationArray[2])
		elif len(durationArray) == 2:
			hours = 0
			minutes = int(durationArray[0])
			seconds = int(durationArray[1])
		elif len(durationArray)	==	1:
			hours = 0
			minutes = 0
			seconds = int(durationArray[0])
		return int(((hours)*3600 + (minutes*60) + seconds)*1000)
	except:
		return 0

def msToRuntime(ms):
	if ms is None or ms <= 0:
		return None
	ret = []
	sec = int(ms/1000) % 60
	min = int(ms/1000/60) % 60
	hr  = int(ms/1000/60/60)
	return "%02d:%02d:%02d" % (hr,min,sec)

####################################################################################################

def MainMenu():
	dir = MediaContainer(viewMode = "List")
	dir.Append(Function(DirectoryItem(MovieList, L('Newest')), url=REDTUBE_NEWEST, mainTitle='Newest'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Top Rated')), url=REDTUBE_RATED, mainTitle='Top Rated'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Most Viewed')), url=REDTUBE_VIEWED, mainTitle='Most Viewed'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Most Favored')), url=REDTUBE_FAVORED, mainTitle='Most Favored'))
	dir.Append(Function(DirectoryItem(CategoriesMenu, L('Categories'))))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Porn Stars')), url=REDTUBE_PORNSTARS_LIST, mainTitle='Porn Stars', pageFormat='pornstars'))
	dir.Append(Function(InputDirectoryItem(Search, L('Search'), L('Search'), thumb=R(ICON)), url=REDTUBE_SEARCH))
	dir.Append(Function(DirectoryItem(FavoriteVideos, L('Favorites'))))
	#dir.Append(Function(VideoItem(PlayVideo,L('Test Video')), url='http://www.redtube.com/55533'))
	return dir

def CategoriesMenu(sender):
	dir = MediaContainer(title2 = sender.itemTitle)
	pageContent = HTML.ElementFromURL(REDTUBE_CHANNELS_LIST)
	for categoryItem in pageContent.xpath('//ul[@class="videoThumbs"]/li'):
		categoryItemTitle = categoryItem.xpath('div/a')[0].get('title')
		categoryItemQuery = categoryItem.xpath('div/a')[0].get('href')
		categoryItemThumb = categoryItem.xpath('div/a/img')[0].get('src')
		categoryItemNrVids = categoryItem.xpath('p/text()')[0].replace('Videos', '').strip()
		categoryItemTitle = categoryItemTitle+' ('+categoryItemNrVids+' Videos)'
		#Log(categoryItemTitle+'__'+categoryItemNrVids+'__'+categoryItemQuery+'__'+categoryItemThumb)
		pageFormat = 'channels'
		dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L(categoryItemTitle), thumb=Function(Thumb, url=categoryItemThumb)), url=REDTUBE_CHANNELS, mainTitle=categoryItemTitle, searchQuery=categoryItemQuery, pageFormat=pageFormat))
	return dir

def PornstarsMenu(sender,sortOrder=''):
	dir = MediaContainer(title2 = sender.itemTitle+' Porn Stars')
	availAlphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
	dir.Append(Function(DirectoryItem(PornstarsList, L('All')), mainTitle=sender.itemTitle+' Porn Stars', searchQuery='', sortOrder=sortOrder))
	for alphabetItem in availAlphabet:
		dir.Append(Function(DirectoryItem(PornstarsList, L(alphabetItem.capitalize())), mainTitle=sender.itemTitle+' Porn Stars', searchQuery=alphabetItem, sortOrder=sortOrder))
	return dir

def PornstarsList(sender,mainTitle,searchQuery='',sortOrder=''):
	dir = MediaContainer(title2 = mainTitle+' ('+sender.itemTitle+')')
	if searchQuery != '':
		pageContent = HTML.ElementFromURL(REDTUBE_PORNSTARS_LIST % (searchQuery, sortOrder))
	else:
		if sortOrder != '':
			pageContent = HTML.ElementFromURL(REDTUBE_PORNSTARS_LIST % (sortOrder, searchQuery))
		else:
			pageContent = HTML.ElementFromURL(REDTUBE_PORNSTARS_LIST % (searchQuery, sortOrder))
	for pornstarItem in pageContent.xpath('//ul[@class="pornStarsThumbs"]/li[not(@class="clear")]'):
		pornstarItemTitle = pornstarItem.xpath('div/a')[0].get('title')
		pornstarItemQuery = pornstarItem.xpath('div/a')[0].get('href').replace('/pornstar/', '').strip()
		pornstarItemThumb = pornstarItem.xpath('div/a/img')[0].get('src')
		pornstarItemNrVids = pornstarItem.xpath('div[@class="videosCount"]/text()')[0].replace('Videos', '').strip()
		pornstarItemTitle = pornstarItemTitle+' ('+pornstarItemNrVids+' Videos)'
		#Log(pornstarItemTitle+'__'+pornstarItemQuery+'__'+pornstarItemThumb+'__'+pornstarItemNrVids)
		pageFormat = 'pornstars'
		dir.Append(Function(DirectoryItem(MovieList, L(pornstarItemTitle), thumb=Function(Thumb, url=pornstarItemThumb)), url=REDTUBE_PORNSTAR, mainTitle=pornstarItemTitle, searchQuery=pornstarItemQuery, pageFormat=pageFormat, sortOrder=''))
	return dir

def SortOrderSubMenu(sender,url,mainTitle,searchQuery='',pageFormat='normal'):
	dir = MediaContainer()
	if pageFormat == 'channels':
		dir.Append(Function(DirectoryItem(MovieList, L('Newest')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=''))
		dir.Append(Function(DirectoryItem(MovieList, L('Top Rated')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='rating'))
		dir.Append(Function(DirectoryItem(MovieList, L('Most Viewed')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostviewed'))
		dir.Append(Function(DirectoryItem(MovieList, L('Most Favored')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostfavored'))
	elif pageFormat == 'search':
		dir.Append(Function(DirectoryItem(MovieList, L('Most Relevant')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=''))
		dir.Append(Function(DirectoryItem(MovieList, L('Newest')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='new'))
		dir.Append(Function(DirectoryItem(MovieList, L('Top Rated')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='top'))
		dir.Append(Function(DirectoryItem(MovieList, L('Most Viewed')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostviewed'))
		dir.Append(Function(DirectoryItem(MovieList, L('Most Favored')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='mostfavored'))
	elif pageFormat == 'pornstars':
		dir.Append(Function(DirectoryItem(PornstarsMenu, L('Female')), sortOrder=''))
		dir.Append(Function(DirectoryItem(PornstarsMenu, L('All')), sortOrder='all'))
		dir.Append(Function(DirectoryItem(PornstarsMenu, L('Male')), sortOrder='male'))
	else:
		dir.Append(Function(DirectoryItem(MovieList, L('Weekly')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=''))
		dir.Append(Function(DirectoryItem(MovieList, L('Monthly')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='monthly'))
		dir.Append(Function(DirectoryItem(MovieList, L('All Time')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='alltime'))
	return dir

def MovieList(sender,url,mainTitle='',searchQuery='',pageFormat='normal',sortOrder='',page=1):
	#Log(searchQuery+'__'+pageFormat+'__'+sortOrder+'__'+str(page))
	pageShow	= page
	pageShowM	= page-1
	pageShowP	= page+1
	pageM = page-1
	pageP = page+1

	dir = MediaContainer(viewMode = "List", title2 = mainTitle+' | Page: '+str(pageShow))
	if pageFormat == 'channels':
		pageContent = HTML.ElementFromURL(url % (searchQuery, sortOrder, str(page)))
	elif pageFormat == 'pornstars':
		pageContent = HTML.ElementFromURL(url % (searchQuery, str(page)))
	elif pageFormat == 'search':
		pageContent = HTML.ElementFromURL(url % (sortOrder, searchQuery, str(page)))
	else:
		try:
			pageContent = HTML.ElementFromURL(url % (sortOrder, str(page)))
		except:
			pageContent = HTML.ElementFromURL(url % (str(page)))
	initialXpath = '//ul[@class="videoThumbs"]/li'
	for videoItem in pageContent.xpath(initialXpath):
		videoItemTitle = videoItem.xpath('div/a')[0].get('title').strip()
		videoItemID	= videoItem.xpath('div/a')[0].get('href').replace('/', '').strip()
		videoItemURL = REDTUBE_BASE+videoItem.xpath('div/a')[0].get('href').strip()
		videoItemThumb = None
		try: videoItemThumb = videoItem.xpath('div/a/img')[0].get('src').replace('m.jpg', 'b.jpg')
		except: pass
		duration = None
		try: duration = videoItem.xpath('div[@class="time"]/div[@style="float:left;"]/span[@class="d"]/text()')[0].strip()
		except: pass
		videoItemDuration = GetDurationFromString(duration)
		videoItemViews = None
		try: videoItemViews = videoItem.xpath('div[@class="lastMovieRow"]/div[@style="float:left;"]/text()')[0].replace(' views', '').strip()
		except: pass
		videoItemRating = None
		try: videoItemRating = round((float(videoItem.xpath('div[@class="time"]/div[@style="float:right;"]/text()')[0].strip())*2),2)
		except: pass
		#Log(videoItemTitle+'__'+videoItemID+'__'+videoItemURL+'__'+videoItemThumb+'__'+str(videoItemDuration)+'__'+videoItemViews)
		dir.Append(Function(PopupDirectoryItem(VideoSubMenu, title=videoItemTitle, duration=videoItemDuration, subtitle=duration+' | Rating: '+str(videoItemRating)+ ' | Views: '+videoItemViews, rating=videoItemRating, thumb=Function(Thumb, url=videoItemThumb), infoLabel=Function(msToRuntime, ms=videoItemDuration)), id=videoItemID, title=videoItemTitle, url=videoItemURL, thumb=videoItemThumb))
	if len(pageContent.xpath('//a[@id="navNext"]')) > 0:
		dir.Append(Function(DirectoryItem(MovieList, L('+++Next Page ('+str(pageShowP)+')+++')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=sortOrder, page=pageP))
	return dir

def VideoSubMenu(sender,id,title,url,thumb):
	dir = MediaContainer()
	dir.Append(Function(VideoItem(PlayVideo,L('Play Video')), url=url))
	dir.Append(Function(DirectoryItem(AddVideoToFavorites, L('Add to Favorites'), ''), id=id, title=title, url=url, thumb=thumb))
	return dir

####################################################################################################
def AddVideoToFavorites(sender,id,title,url,thumb):
	favs = {}
	if Data.Exists('favoritevideos'):
		favs = Data.LoadObject('favoritevideos')
		if id in favs:
			return MessageContainer('Already a Favorite', 'This Video is already on your list of Favorites.')
	favs[id] = [id, title, url, thumb]
	Data.SaveObject('favoritevideos', favs)
	return MessageContainer('Added to Favorites', 'This Video has been added to your Favorites.')

def RemoveVideoFromFavorites(sender,id):
	favs = Data.LoadObject('favoritevideos')
	if id in favs:
		del favs[id]
		Data.SaveObject('favoritevideos', favs)
		return MessageContainer('Removed from Favorites', 'This Video has been removed from your Favorites.')

def FavoriteVideos(sender):
	dir = MediaContainer(viewMode = "List", title2 = 'Favorites', noCache=True)
	favs = Data.LoadObject('favoritevideos')
	values = favs.values()
	output = [(f[1], f[0], f[2], f[3]) for f in values]
	output.sort()
	for title, id, url, thumb in output:
		dir.Append(Function(PopupDirectoryItem(FavoritesSubMenu, title=title, thumb=Function(Thumb, url=thumb)), id=id, title=title, url=url, thumb=thumb))
	return dir

def FavoritesSubMenu(sender,id,title,url,thumb):
	dir = MediaContainer()
	dir.Append(Function(VideoItem(PlayVideo,L('Play Video')), url=url))
	dir.Append(Function(DirectoryItem(RemoveVideoFromFavorites, L('Remove from Favorites'), ''), id=id))
	return dir
####################################################################################################

def Search(sender,url,query='',mainTitle='Search',pageFormat='search'):
	dir = MediaContainer()
	searchQueryCorrect = String.Quote(query)
	dir = SortOrderSubMenu(sender=None, url=url, mainTitle=mainTitle+': '+query, searchQuery=searchQueryCorrect, pageFormat=pageFormat)
	return dir

####################################################################################################

def PlayVideo(sender, url):
	request = HTTP.Request(url)
	content = request.content
	#headers = request.headers
	#Log(content)
	#Log(headers)
	#vidurl = re.compile('so.addVariable\("file","(.+?)"\)').findall(content, re.DOTALL)
	#vidurl = re.compile('"<source src=\'(.+?)\' type=\'video/mp4\'>"').findall(content, re.DOTALL)
	vidurl = re.compile('flv_h264_url=(.+?)%0A&http\.startparam').findall(content, re.DOTALL)
	if len(vidurl) < 1:
		vidurl = re.compile('"<source src=\'(.+?)\' type=\'video/mp4\'>"').findall(content, re.DOTALL)
	#Log(vidurl)
	#urlresult = urllib.unquote(vidurl[0])
	#Log.Debug("urlresult:" + urlresult)
	if len(vidurl) > 0:
		#return Redirect(vidurl[0])
		return Redirect(urllib.unquote(vidurl[0]))
	else:
		return None
