# -*- coding: utf-8 -*-
import mysql.connector

class DBConn:
    def __init__(self, host = "localhost", user = "root", password = "**********", database = "db_edu"):
        try:
            self.conn = mysql.connector.connect(host=host, user=user, passwd=password, database = database)
            self.cursor = self.conn.cursor()
        except Exception as ex:
            print(ex)
     
    def GetKeywordAssociations(self, keyword_id):
        self.cursor.execute("SELECT artifacts.artifact_number, artifacts.artifact_name FROM artifacts INNER JOIN artifact_keywords ON artifacts_artifact_id = artifact_id WHERE artifact_keywords.keywords_keyword_id = "+str(keyword_id))
        results = []
        for res in self.cursor.fetchall():
                Number, Header = res
                results.append([Number, Header])
        return results

    def GetKeywordID(self, keyword_term):
        self.cursor.execute("SELECT keyword_id FROM keywords where keyword_term = "+str("'"+keyword_term+"'"))
        result = 0
        result = int(self.cursor.fetchone()[0])
        return result
    
    def GetKeywordsList(self):
        self.cursor.execute("SELECT keyword_term FROM keywords")
        results = []
        for res in self.cursor.fetchall():
            results.append(res[0])
        return results