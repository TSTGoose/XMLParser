import xml.etree.ElementTree as ET
from pprint import pprint
import json


class CompetencesParser:
    PATHES = {
        "CODE": "Program/Direction/Code",
        "SKILLS": "Skills"
    }

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.__root_node = ET.parse(self.xml_path).getroot()
        self.xml_data = {"competence_models":
                             self.__parse_data(tag_path=self.PATHES["SKILLS"], tags=["Code"])}

        with open("competences_data.json", "w", encoding='utf-8') as write_file:
            json.dump(self.xml_data, write_file, ensure_ascii=False)

    def __get_specific_attr(self, tag_path: str) -> str:
        return self.__root_node.find(tag_path).text

    def __parse_data(self, tag_path: str, tags: list) -> list:
        result = list()

        for tag in self.__root_node.findall(tag_path):
            for skill_type in tag:
                for skill in skill_type.iter("Skill"):
                    skill_data = {
                        "id": skill.find("Code").text,
                        "name": skill.find("Name").text,
                        "type": skill_type.tag,
                        "type_name": self.__pars_indicators(tag_path=skill, indicator="ProfessionalTask", tag_parse="type_name"),
                        "object": self.__pars_indicators(tag_path=skill, indicator="ProfessionalTask", tag_parse="object"),
                        "subject": self.__pars_indicators(tag_path=skill, indicator="ProfessionalTask", tag_parse="subject"),
                        "know": self.__pars_indicators(tag_path=skill, indicator="KnowIndicator"),
                        "can": self.__pars_indicators(tag_path=skill, indicator="CanIndicator"),
                        "own": self.__pars_indicators(tag_path=skill, indicator="OwnIndicator"),
                    }
                    result.append(skill_data)

        return result

    def __pars_indicators(self, tag_path, indicator: str, tag_parse: str | None = None) -> list:
        result = []
        for tag in tag_path.iter(indicator):
            tag_data = {}
            if tag_parse is not None:
                if tag_parse == "subject":
                    return tag.find("Name").text
                elif tag_parse == "object":
                    return tag.find("Object").text
                else:
                    return tag.find("ProfessionalActivityTaskType").find("Name").text
            else:
                tag_data["name"] = tag.find("Name").text # Subject
                tag_data["id"] = tag.find("Code").text
                result.append(tag_data)
        return result


document = CompetencesParser(xml_path="./xml plans/competences xml/competence_model_90.xml")
pprint(document.xml_data)

