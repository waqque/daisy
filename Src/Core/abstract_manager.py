from abc import ABC

#Класс для реалищзации обрабботки и загрудки данных
class abstract_manager(ABC):
    #Полный путь к файлу
    __file_name:str = ""
    #Флаг о том что загрузка произошла успешко
    __is_loaded:bool = False
    #Загруженные сырые данные 
    __data:list = []

    #Загурзка данных

    def load(self, file_name:str = "") -> None:
        pass

    #Обработка загруженных данных 

    def convert(self) -> bool:
        return False

    #Проверка на загрузку данных

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded