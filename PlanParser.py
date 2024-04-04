import xml.etree.ElementTree as ET
from pprint import pprint
import json
import re


class PlanParser:
    PATHES = {
        "Титул": "План/Титул",
        "АтрибутыЦиклов": ["План/Титул/АтрибутыЦикловНов/Цикл", "План/Титул/АтрибутыЦиклов/Цикл"],
        "Специальность": "План/Титул/Специальности/Специальность",
        "Квалификация": "План/Титул/Квалификации/Квалификация",
        "ВидДеятельности": "План/Титул/ВидыДеятельности/ВидДеятельности",
        "Дисциплины": "План/СтрокиПлана/Строка",
        "Семестр": "План/СтрокиПлана/Строка/Сем",
        "УчебныеПрактики": "План/СпецВидыРаботНов/",
        "Компетенции": "План/Компетенции/"
    }
    TRANSLITE_DICT = {
        "НовЦикл": "new_cycle",
        "Дис": "name",
        "НовИдДисциплины": "new_cycle_id",
        "НовИдДисциплины": "new_cycle_id",
        "Цикл": "cycle",
        "ИдетификаторДисциплины": "discipline_id",
        "ИдетификаторВидаПлана": "plan_view_id",
        "ГОС": "GOS",
        "СР": "SR",
        "ЧасовИнтер": "HoursInter",
        "КомпетенцииКоды": "competenciescodes",
        "Компетенции": "competencies",
        "Кафедра": "department",
        "Раздел": "chapter",
        "ПодлежитИзучению": "subject_study",
        "КредитовНаДисциплину": "credits_discipline",
        "ЧасовВЗЕТ": "HoursZET",
        "Сем": "semestr",
        "Семестр": "semestr",
        "Ном": "number",
        "Лек": "lec",
        "Лаб": "lab",
        "ИнтЛаб": "int_lab",
        "Пр": "pr",
        "ИнтПр": "intPr",
        "СРС": "SRS",
        "ЧасЭкз": "hourEx",
        "ЗЕТ": "ZET",
        "Экз": "exam",
        "Зач": "zach",
        "ЗачО": "zachO",
        "КонтрРаб": "controlWork",
        "Контр": "control",
        "КурсовойПроект": "course_project",
        "КурсоваяРабота": "course_work",
        "Тип": "type",
        "Наименование": "name",
        "ЗЕТвНеделе": "ZETinWeek",
        "ЗЕТэкспертное": "ZETexpert",
        "ПроектЗЕТ": "projectZET",
        "ИнтЛек": "intLec",
        "ПланНед": "planWeek",
        "ПланЧасов": "planHour",
        "ПланЗЕТ": "planZet",
        "Код": "code",
        "Индекс": "index",
        "Содержание": "content"
    }

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.__root_node = ET.parse(self.xml_path).getroot()
        self.xml_data = {
            "code_department": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="КодКафедры"),
            "shifr": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="ПоследнийШифр"),
            "year_priem": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="ГодНачалаПодготовки"),
            "level": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="Уровень"),
            "code_level": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="КодУровня"),
            "name_speciality": self.__get_specific_attr(tag_path=self.PATHES["Специальность"], attr_for_search="Ном",
                                                        search_parametr="1", attribute="Название"),
            # <Специальность Ном="1" Название="Специальность 14.05.04 Электроника и автоматика физических установок" />
            "educational_program": self.__get_specific_attr(tag_path=self.PATHES["Специальность"],
                                                            attr_for_search="Ном", search_parametr="2",
                                                            attribute="Название"),
            # <Специальность Ном="2" Название="Образовательная программа  &quot;Автоматизация и информационно-измерительные системы физических установок&quot;" />
            "year_issue": self.__get_specific_attr(tag_path=self.PATHES["Специальность"], attr_for_search="Ном",
                                                   search_parametr="3", attribute="Название"),
            # <Специальность Ном="3" Название="Выпуск - 2029" />
            "qualification": self.__get_specific_attr(tag_path=self.PATHES["Квалификация"], attr_for_search="Ном",
                                                      search_parametr="1", attribute="Название"),
            # <Квалификация Ном="1" Название="инженер-физик" СрокОбучения="5л 6м" />
            "training_period": self.__get_specific_attr(tag_path=self.PATHES["Квалификация"], attr_for_search="Ном",
                                                        search_parametr="1", attribute="СрокОбучения"),
            # <Квалификация Ном="1" Название="инженер-физик" СрокОбучения="5л 6м" />
            "kind_activity": self.__get_attrvalue_list(tag_path=self.PATHES["ВидДеятельности"], attrbiute="Название"),
            "sheet": {
                "type": self.__root_node.attrib['Тип'],
                "name": self.__get_tag_value(tag_path=self.PATHES["Титул"], attribute="ПолноеИмяПлана"),
            },
            "plan_descipline": self.__pars_descipline(tag_path=self.PATHES["Дисциплины"],
                                                      attribute_exceptions=["РГР", "КП", "КР", "Реф"],
                                                      parent_attribute_list=[
                                                          "Дис",
                                                          "НовЦикл",
                                                          "НовИдДисциплины",
                                                          'Цикл',
                                                          'ИдетификаторДисциплины',
                                                          'ИдетификаторВидаПлана',
                                                          'КомпетенцииКоды',
                                                          'Компетенции',
                                                          'Кафедра',
                                                          'Раздел',
                                                          'ПодлежитИзучению',
                                                          'КредитовНаДисциплину',
                                                          'ЧасовВЗЕТ',
                                                      ]),
            "practice": self.__pars_practice(tag_path=self.PATHES["УчебныеПрактики"],
                                             attribute_exception=["ПланЧасовАуд", "ПланЧасовСРС"]),
            "competencies": self.__pars_competences(tag_path=self.PATHES["Компетенции"], attribute_list=["Код", "Индекс", "Содержание"])
        }

        with open("plan_data.json", "w", encoding='utf-8') as write_file:
            json.dump(self.xml_data, write_file, ensure_ascii=False)

    def __get_attrvalue_list(self, tag_path, attrbiute):
        result = []
        for tag in self.__root_node.findall(tag_path):
            attr_value = tag.get(attrbiute)
            if attr_value is not None:
                result.append(attr_value)
            else:
                continue
        return result

    def __get_specific_attr(self, tag_path, attr_for_search, search_parametr, attribute):
        for tag in self.__root_node.findall(tag_path):
            if tag.get(attr_for_search) is search_parametr:
                attr_value = tag.get(attribute)
                return attr_value

    def __get_tag_value(self, tag_path: str, attribute: str) -> str:
        for tag in self.__root_node.findall(tag_path):
            attr_value = tag.get(attribute)
            return attr_value

    def __pars_descipline(self, tag_path: str, attribute_exceptions: list | None = None,
                          parent_attribute_list: list | None = None, child_attribute_list: list | None = None) -> list:
        result = []
        for tag in self.__root_node.findall(tag_path):
            attr_dict = {}
            if parent_attribute_list is not None:
                for attribute in parent_attribute_list:
                    attr_value = tag.get(attribute)
                    attr_list_key = self.TRANSLITE_DICT[attribute]
                    if attr_value is not None:
                        if "&" in attr_value or "," in attr_value and attr_list_key is not "name":
                            attr_dict[attr_list_key] = re.split(r',|&', attr_value.replace(" ", ""))
                        else:
                            attr_dict[attr_list_key] = attr_value
            if "модуль" in attr_dict["name"].lower():
                continue

            getted_child_tags = list(tag)
            sorted_child_tags = {tag.tag for tag in getted_child_tags}

            if len(sorted_child_tags) == 0:
                continue

            # Перевод тегов в транслит
            for child_tag in sorted_child_tags:
                dict_key = self.TRANSLITE_DICT[child_tag]
                attr_dict[dict_key] = []

            # Парсинг дочерних тегов
            for child_object in list(tag):
                child_tag = self.TRANSLITE_DICT[child_object.tag]
                child_attr_dict = child_object.attrib
                if len(child_attr_dict) == 0:
                    for inner_tag in child_object:
                        child_attr_dict = inner_tag.attrib
                if attribute_exceptions is not None:
                    for exception in attribute_exceptions:
                        if exception in child_attr_dict:
                            child_attr_dict.pop(exception)
                for old_key in list(child_attr_dict):
                    new_key = self.TRANSLITE_DICT[old_key]
                    child_attr_dict[new_key] = child_attr_dict.pop(old_key)
                attr_dict[child_tag].append(child_attr_dict)
            result.append(attr_dict)
        return result

    def __pars_practice(self, tag_path: str, attribute_exception: list | None = None):
        result = []
        for high_tree in self.__root_node.findall(tag_path):
            attr_dict = {}
            for tag in high_tree.iter("ПрочаяПрактика"):
                attr_dict = tag.attrib

                for old_key in list(attr_dict):
                    new_key = self.TRANSLITE_DICT[old_key]
                    attr_dict[new_key] = attr_dict.pop(old_key)
                    if "," in attr_dict[new_key] or "&" in attr_dict[new_key]:
                        attr_dict[new_key] = re.split(r"&|,", attr_dict[new_key].replace(" ", ""))

                for child_object in list(tag):
                    attr_child_dict = child_object.attrib
                    if attribute_exception is not None:
                        for attribute in attribute_exception:
                            if attribute in attr_child_dict:
                                attr_child_dict.pop(attribute)
                    key = self.TRANSLITE_DICT[child_object.tag]
                    sorted_dict = dict()
                    for old_key in list(attr_child_dict):
                        new_key = self.TRANSLITE_DICT[old_key]
                        sorted_dict[new_key] = attr_child_dict[old_key]
                    attr_child_dict = dict()
                    attr_child_dict[key] = sorted_dict
                    attr_dict = attr_dict | attr_child_dict

            result.append(attr_dict)
        return result

    def __pars_competences(self, tag_path: str, attribute_list: list | None = None, exception_list: list | None = None) -> list:
        result = []
        for tag in self.__root_node.findall(tag_path):
            attr_dict = {}
            sorted_attr_dict = tag.attrib
            if exception_list is not None:
                for exception in exception_list:
                    if exception in sorted_attr_dict:
                        sorted_attr_dict.pop(exception)
            for old_key in list(sorted_attr_dict):
                new_key = self.TRANSLITE_DICT[old_key]
                sorted_attr_dict[new_key] = sorted_attr_dict.pop(old_key)
            attr_dict = sorted_attr_dict
            result.append(attr_dict)
        return result



first_document = PlanParser(xml_path="C:/Users/epick/Desktop/Новая папка/140302_62-23-Д-153(1).plm.xml")
first_document_data = first_document.xml_data

pprint(first_document.xml_data)
