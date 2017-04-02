"""
written by Alec Greaney, March 5-8, 2017
used a tutorial from Scrapy online
Check out EverNote for more info on how to use

to run via command prompt:
C:\Python27\Scripts\courses>C:\Python27\Scripts\scrapy crawl courseStep2 -o BCcourses2016-17_all1.1.csv
-->where courseStep2 is that name below; the file can be named whatever.csv or whatever.jl (JSON lines)

"""

from spring17mcasURLs import start_urls1
from fall16mcasURLs import fall16mcasURLs
from all1617csomURLs import fall16csomURLs, spring17csomURLs
from all1617otherURLs import fall16csonURLs, spring17csonURLs, fall16lawURLs, spring17lawURLs, fall16lsoeURLs, spring17lsoeURLs,fall16soswURLs, spring17soswURLs, fall16sotmURLs, spring17sotmURLs, fall16wcasURLs, spring17wcasURLs
from mcas17urls2 import mcas17urls2
import scrapy

class CoursesSpider(scrapy.Spider):
    name = "courseStep2"
    start_urls = []
    start_urls = mcas17urls2
    #start_urls = start_urls1 + fall16mcasURLs + fall16csomURLs + spring17csomURLs
    #start_urls += spring17csomURLs
    
    #start_urls += fall16csonURLs + spring17csonURLs + fall16lawURLs + spring17lawURLs + fall16lsoeURLs + spring17lsoeURLs + fall16soswURLs + spring17soswURLs + fall16sotmURLs + spring17sotmURLs + fall16wcasURLs + spring17wcasURLs
    ##gets the course titles--> response.selector.xpath("//span[re:test(@class, 'course_title')]/strong/text()").extract()
    ##gets the course URLs  --> response.selector.xpath("//tr[re:test(@class, 'course')]/td[1]/a[1]/@href").extract()

    def parse(self, response):
        
        for course in response.css("body"):

            #checks to see if the title array exists, meaning that there is a course on that page
            title = course.xpath('//h2[re:test(@class, "coursetitle")]/text()').extract()
            if(len(title) > 0):
                #cuts the code off the title
                titleOnly = course.xpath('//h2[re:test(@class, "coursetitle")]/text()').extract_first()[:-13]
                
                ##fixing error for course description having the out-of-bounds
                descArray = course.xpath("//tr[re:test(@class, 'course')]/td[1]/p[1]/text()").extract()
                if len(descArray) > 1:
                    descString = course.xpath("//tr[re:test(@class, 'course')]/td[1]/p[1]/text()").extract()[1].strip()
                else:
                    descString = "No desc."

                #grabbing just the code out of the title
                courseCode = title[0][-11:-1]

                #checks to see if there is any core satisfied, used below to yield the core string
                coreArray = course.xpath("//tr[re:test(@class, 'course')]/td[1]/strong/text()").extract()
                if(len(coreArray) > 0):
                    coreString = coreArray[0][32:]
                else:
                    coreString = ""

                #checks to see if the class "redText" is defined, which means a course is closed or cancelled
                #secondarily checks to see if certain text is in the span, meaning the course is only open to a certain class or restricted by major

                redTextArray = course.xpath("//span[re:test(@class, 'redtext')]/strong/text()").extract()
                if(len(redTextArray) > 0):
                    redTextString = course.xpath("//span[re:test(@class, 'redtext')]/strong/text()").extract_first()
                    
                    if redTextString != "":
                        negOrPos1 = redTextString.find("Closed"); #this will return -1 if closed isn't part of that string, aka the course is not closed
                        negOrPos2 = redTextString.find("Cancelled"); #this will return -1 if cancelled isn't part of that string, aka the course is not cancelled                       

                    else:
                        negOrPos1 = 1;
                        
                    if negOrPos1 == -1 and negOrPos2 == -1: ##couldn't find closed or cancelled, so must be open
                        closedOrOpen = 'open'

                    elif negOrPos1 == -1 and negOrPos2 != -1:  ##can't find closed, could find cancelled
                        closedOrOpen = 'cancelled'
                        
                    else:
                        closedOrOpen = 'closed'

                    gradeRestrictionString = ''
                    majorRestrictionString = ''
                    for part in redTextArray:
                        #if there's text in redTextString, look for each grade, if there, add to gradeRestrictionString
                        if part.find("Seniors") != -1:
                            gradeRestrictionString += "Seniors "
                        if part.find("Juniors") != -1:
                            gradeRestrictionString += "Juniors "
                        if part.find("Sophomores") != -1:
                            gradeRestrictionString += "Sophomores "
                        if part.find("Freshmen") != -1:
                            gradeRestrictionString += "Freshmen"

                        #if there's text in redTextString, look for "Course restricted to", then grab the rest of the string
                        
                        majorRestrictionNum = part.find("Course restricted to")
                        if majorRestrictionNum > -1:
                            majorRestrictionNum += 21
                            majorRestrictionString = part[majorRestrictionNum:]
                        
                else:
                    closedOrOpen = 'open'
                    gradeRestrictionString = ''
                    majorRestrictionString = ''

                #noticeArray = course


            #checks to see if the title array exists, meaning that there is a course on that page
            if(len(title) > 0):
                yield{
                    'courseCode': courseCode,
                    'title': course.xpath('//h2[re:test(@class, "coursetitle")]/text()').extract()[0].strip(),
                    'titleOnly': titleOnly,
                    'school': course.css("tr.course").xpath("//td/table/tbody/tr[1]/td[1]/text()").extract()[0].strip(),
                    'dept': course.css("tr.course").xpath("//td/table/tbody/tr[1]/td[2]/text()").extract()[0].strip(),
                    'instructor': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr/td[3]/text()").extract()[0].strip(),
                    'term': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[2]/td[1]/text()").extract()[0].strip(),
                    'maximumSize': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[2]/td[2]/text()").extract()[0].strip(),
                    'time': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[2]/td[3]/div/span[1]/text()").extract(),
                    'room': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[2]/td[3]/div/span[2]/text()").extract(),
                    'credits': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[3]/td[1]/text()").extract()[1].strip(),
                    'level': course.xpath("//tr[re:test(@class, 'course')]/td[1]/table/tbody/tr[3]/td[2]/text()").extract()[1].strip(),
                    'description': descString,
                    'courseClosed': closedOrOpen,
                    'frequency': course.xpath("//tr[re:test(@class, 'course')]/td[1]/p[6]/text()").extract()[0].strip(),
                    'courseIndex': course.xpath("//tr[re:test(@class, 'course')]/td[1]/p[5]/text()").extract_first().strip(),
                    'core': coreString,
                    'gradeRestriction': gradeRestrictionString,
                    'majorRestriction': majorRestrictionString,
                    
                }      
