# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter


class GoldTimePipeline(object):
    def open_spider(self,spider):
        #爬去到的文件保成csv文件
        self.file = open("./js.csv", "wb")
        self.exporter = CsvItemExporter(self.file,
                                        fields_to_export=["ID", "展示时间", "标题内容","链接"])
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)

        return item

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()



