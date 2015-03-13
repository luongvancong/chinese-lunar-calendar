#!/usr/bin/env python                                                     
# -*- coding: UTF-8 -*-  

import gtk
import pygtk
import os
import sys
import pango
import gobject

from date import *
import time

currentTime = time.localtime()
currentYear = currentTime[0]
currentMonth = currentTime[1]
currentDay = currentTime[2]

class Calendar:

    weeks_list = ["一", "二", "三", "四", "五", "六", "日"]

    def __init__(self):
        self.builder_obj = gtk.Builder()
        self.builder_obj.add_from_file("calendar.glade")
        
        # add window
        self.window = self.builder_obj.get_object("window1")
        if self.window:
            self.window.connect("destroy", gtk.main_quit)

        # add yearComboBox items
        self.yearComboBox = self.builder_obj.get_object("yearComboBox")
        liststore1 = self.builder_obj.get_object("liststore1")
        self.yearComboBox.set_text_column(0)

        self.yearDates = []
        for i in range(1900,2050):  
            self.yearDates.append(str(i)+"年")

        for a in self.yearDates:
            self.yearComboBox.append_text(a)

        self.currentyearIndex = self.yearDates.index(str(currentYear) + "年")
        self.yearComboBox.set_active(self.currentyearIndex)

        # add monthComboBox items
        self.monthComboBox = self.builder_obj.get_object("monthComboBox")
        liststore2 = self.builder_obj.get_object("liststore2")
        self.monthComboBox.set_text_column(0)

        self.monthDates = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        for i in self.monthDates:
            self.monthComboBox.append_text(i)

        self.currentmonthIndex = self.monthDates.index(str(currentMonth)+"月")
        self.monthComboBox.set_active(self.currentmonthIndex)

        # add signals for comboboxs and buttons
        signals_dic = {"on_yearComboBox_changed":self.ChangedTime,
                              "on_monthComboBox_changed":self.ChangedTime,
                              "on_yearLeft_clicked":self.yearLeft_clicked,
                              "on_yearRight_clicked":self.yearRight_clicked,
                              "on_monthLeft_clicked":self.monthLeft_clicked,
                              "on_monthRight_clicked":self.monthRight_clicked
                              }
        self.builder_obj.connect_signals(signals_dic)

        # add lunarLabel label
        self.lunarLabel = self.builder_obj.get_object("lunarLabel")
        yearDate = Date(currentYear, currentMonth)
        self.lunarLabel.set_text("农历:[%s]年  生肖:[%s]" \
                                %(yearDate.GanZhiYear(),yearDate.Zodiac()))

        # add week labels
        self.weeks = []
        for i in range(7):
            self.weeks.append(self.builder_obj.get_object("weeklabel" + str(i)))  
            self.weeks[i].modify_font(pango.FontDescription("Sans Bold Italic 12"))

        # add table
        self.calendar_table = self.builder_obj.get_object("calendar_tree")

        # add solar labels and lunar labels
        self.solar_labels = []
        self.lunar_labels = []
        for i in range(42):
            self.solar_labels.append(self.builder_obj.get_object("solarlabel" + str(i)))
            self.lunar_labels.append(self.builder_obj.get_object("lunarlabel" + str(i)))

        # add vboxs for showing tooltips
        self.vboxs = []
        for i in range(42):
            self.vboxs.append(self.builder_obj.get_object("box%s" % str(i)))

        # add buttons for grab focus
        self.buttons = []
        for i in range(42):
            self.buttons.append(self.builder_obj.get_object("button%s" % str(i)))

        # add event boxs for showing selected of current day
        self.event_boxs = []
        for i in range(43):
            self.event_boxs.append(self.builder_obj.get_object("eventbox%s" % str(i)))

            self.event_boxs[i].modify_bg(gtk.STATE_NORMAL,
                                                  gtk.gdk.color_parse("White"))

        # add tooltips
        self.tooltips = gtk.Tooltips()

        self.window.show_all()
        self.Draw(currentYear, currentMonth)

    def Draw(self, year, month):

        solarMonthFirstDay = Date(year, month, 1)
        for day in range(1, solarMonthFirstDay.SolarDaysInMonth() + 1):
            solarDay = Date(year, month, day)
            weekday = solarMonthFirstDay.Weekday()
            self.num = day + weekday - 1
            solarDay.SolarToLunar()
            lunarday = solarDay.LunarDay()
            lunarmonth = solarDay.LunarMonth()
            originallunarday = solarDay.OriginalLunarDay()
 
            if self.num < (weekday+solarMonthFirstDay.SolarDaysInMonth()):
                self.solar_labels[self.num].set_text(str(day))
                sh = solarDay.SolarHoliday()
                lh = solarDay.LunarHoliday()

            # grab focus and show blue color for current day
            if self.solar_labels[day].get_text() == str(currentDay):
                self.buttons[day].grab_focus()
                self.event_boxs[day].modify_bg(gtk.STATE_NORMAL,
                                                  gtk.gdk.color_parse("Blue"))
            else:
                self.event_boxs[day].modify_bg(gtk.STATE_NORMAL,
                                                  gtk.gdk.color_parse("White"))
                

            #destroy label0-label6 if the solar first day star at label7
            if self.solar_labels[7].get_text() == "1":
                for i in range(7):
                    self.solar_labels[i].set_text("")
                    self.lunar_labels[i].set_text("")

            if lh is not None:
                # change lunar label to show lunar holiday
                self.lunar_labels[self.num].set_text(lh)

                self.tooltips.set_tip(self.vboxs[self.num], 
                  "阳历：%s年%s月%s日 星期%s\n农历：%s年 %s %s\n干支：%s年 %s月 %s日\n节日：%s" % \
                  (str(year), str(month), str(day), 
                   self.weeks_list[solarDay.Weekday() - 1], 
                   str(solarDay.lunarYear - 1), lunarmonth, originallunarday,
                   solarDay.GanZhiYear(), solarDay.GanZhiMonth(), 
                   solarDay.GanZhiDay(), lh))

                self.lunar_labels[self.num].modify_fg(gtk.STATE_NORMAL, 
                                               gtk.gdk.color_parse("Blue"))
                self.lunar_labels[self.num].modify_font(pango.FontDescription("Sans Bold 10")) 

            elif sh is not None:
                # change lunar label to show solar holiday
                self.lunar_labels[self.num].set_text(sh)

                self.tooltips.set_tip(self.vboxs[self.num], 
                  "阳历：%s年%s月%s日 星期%s\n农历：%s年 %s %s\n干支：%s年 %s月 %s日\n节日：%s" % \
                  (str(year), str(month), str(day), 
                  self.weeks_list[solarDay.Weekday() - 1], 
                   str(solarDay.lunarYear - 1), lunarmonth, originallunarday,
                   solarDay.GanZhiYear(), solarDay.GanZhiMonth(), 
                   solarDay.GanZhiDay(), sh))

                self.lunar_labels[self.num].modify_fg(gtk.STATE_NORMAL, 
                                               gtk.gdk.color_parse("Red"))
                self.lunar_labels[self.num].modify_font(pango.FontDescription("Sans Bold 10"))
            else:
                self.lunar_labels[self.num].set_text(lunarday)
                self.lunar_labels[self.num].modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("Black"))
                self.lunar_labels[self.num].modify_font(pango.FontDescription("Sans normal 10"))

                self.tooltips.set_tip(self.vboxs[self.num], 
                  "阳历：%s年%s月%s日 星期%s\n农历：%s年 %s %s\n干支：%s年 %s月 %s日" % \
                  (str(year), str(month), str(day), 
                  self.weeks_list[solarDay.Weekday() - 1], 
                   str(solarDay.lunarYear - 1), lunarmonth, originallunarday,
                   solarDay.GanZhiYear(), solarDay.GanZhiMonth(), 
                   solarDay.GanZhiDay()))


    def ChangedTime(self, yearChosed=currentYear, monthChosed=currentMonth):
        self.yearChosed=int(self.yearComboBox.get_child().get_text().decode('utf-8')[:-1])
        self.monthChosed=int(self.monthComboBox.get_child().get_text().decode('utf-8')[:-1])

        self.yearDate = Date(self.yearChosed, self.monthChosed)
        self.lunarLabel.set_text("农历:[%s]年  生肖:[%s]" %(self.yearDate.GanZhiYear(),self.yearDate.Zodiac()))

        self.currentyearIndex =  self.yearDates.index(str(self.yearChosed) + "年")
        self.currentmonthIndex = self.monthDates.index(str(self.monthChosed) + "月")

        for i in range(42):
            self.solar_labels[i].set_text("")
            self.lunar_labels[i].set_text("")
        self.Draw(self.yearChosed, self.monthChosed)        

    def yearLeft_clicked(self, widget, data=None):
        self.currentyearIndex -= 1
        self.yearComboBox.set_active(self.currentyearIndex)
        self.ChangedTime(self.yearChosed, self.monthChosed)

        for i in range(7):
            self.solar_labels[i].set_text("")
            self.lunar_labels[i].set_text("")
        self.Draw(self.yearChosed, self.monthChosed)

    def yearRight_clicked(self, widget, data=None):
        self.currentyearIndex += 1
        self.yearComboBox.set_active(self.currentyearIndex)
        self.ChangedTime(self.yearChosed, self.monthChosed)

        for i in range(7):
            self.solar_labels[i].set_text("")
            self.lunar_labels[i].set_text("")
        self.Draw(self.yearChosed, self.monthChosed)

    def monthLeft_clicked(self, widget, data=None):
        # the valid month should be in 2 to 12
        # since the index start from 0, so the month larger than index as 1
        if self.currentmonthIndex < 1:
            self.yearComboBox.set_active(self.currentyearIndex - 1)
            self.monthComboBox.set_active(11)
        else:
            self.currentmonthIndex -= 1
            self.yearComboBox.set_active(self.currentyearIndex)
            self.monthComboBox.set_active(self.currentmonthIndex)
        self.ChangedTime(self.yearChosed, self.monthChosed)

        for i in range(7):
            self.solar_labels[i].set_text("")
            self.lunar_labels[i].set_text("")
        self.Draw(self.yearChosed, self.monthChosed)

    def monthRight_clicked(self, widget, data=None):
        # the valid month should be in 1 to 11
        # since the index start from 0, so the month larger than index as 1
        if self.currentmonthIndex > 10:
            self.yearComboBox.set_active(self.currentyearIndex + 1)
            self.monthComboBox.set_active(0)
        else:
            self.currentmonthIndex += 1
            self.monthComboBox.set_active(self.currentmonthIndex)
        self.ChangedTime(self.yearChosed, self.monthChosed)

        for i in range(7):
            self.solar_labels[i].set_text("")
            self.lunar_labels[i].set_text("")
        self.Draw(self.yearChosed, self.monthChosed)

def main():
    gtk.main()
    return 

if __name__ == "__main__":
    ca = Calendar()
    main()
