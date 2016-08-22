from sys import version_info
from lxml import etree
import json

# HTTP libraries depends upon Python 2 or 3
if version_info.major == 3 :
    import urllib.parse, urllib.request
else:
    from urllib import urlencode
    import urllib2

_BASE_URL = "http://www.airquality.dli.mlsi.gov.cy/site/ajax_exec"

data_cache = {};

def postRequest(url, params, json_resp=True, body_size=65535):
    # Netatmo response body size limited to 64k (should be under 16k)
    if version_info.major == 3:
        req = urllib.request.Request(url)
        req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        params = urllib.parse.urlencode(params, True).encode('utf-8')
        resp = urllib.request.urlopen(req, params).read(body_size).decode("utf-8")
    else:
        params = urlencode(params, True)
        headers = {"Content-Type" : "application/x-www-form-urlencoded;charset=utf-8"}
        req = urllib2.Request(url=url, data=params, headers=headers)
        resp = urllib2.urlopen(req).read(body_size)
    if json_resp:
        return json.loads(resp)
    else:
        return resp

def getData():
	postParams = {
		"ajax_call": 1,
		"post_data[action]": "get_markers_data",
		"post_data[measurement_type]": "pollutants"
	}
	resp = postRequest(_BASE_URL, postParams, json_resp=True)
	return resp["markers_data"]

def getMarkersData(location):
	return getData()[location]

def getMarkersDataParsed(location):
	data = getMarkersData(location)
	parsed = {
		"image_url": data["image_url"],
		"data": parseInfoWindowToJson(data["info_window"])
	}
	return parsed

def parseInfoWindowToJson(data):
	xslt_transform = etree.XML("""\
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="text"/>
	<xsl:template match="/">
{
		<xsl:apply-templates select="//div[@id='bodyContent']/table//table"/>
}
	</xsl:template>

	<xsl:template match="table">
	"<xsl:copy-of select="tr/td[1]"/>": {
			"measure": "<xsl:value-of select="tr/td[2]/div[1]"/>",
			"value": "<xsl:value-of select="tr/td[2]/div[2]"/>"
	}<xsl:if test="position() != last()">,</xsl:if>
	</xsl:template>
</xsl:stylesheet>""")
	transform = etree.XSLT(xslt_transform)
	return json.loads(str(transform(etree.XML(data))))
