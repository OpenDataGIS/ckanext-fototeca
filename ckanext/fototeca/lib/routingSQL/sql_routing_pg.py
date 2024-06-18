import psycopg2
import pandas as pd 
from sqlalchemy import engine, create_engine, text
import logging, heapq

from ckanext.fototeca.lib.routingSQL.sql_routing_base import routingBase

class routingPG(routingBase):
    
    
    def __init__(self, user: str, password: str, url: str, port: int, database: str):

        engine_params = "postgresql+psycopg2://"+user+":"+password+"@"+url+":"+str(port)+"/"+database
        self._engine = create_engine(engine_params)
        with self._engine.connect() as conn:
            logging.info("database "+database+" connected")

            #Get database schema
            query = conn.execute(text("SELECT distinct table_schema FROM information_schema.columns"))
            schemas = query.fetchall()
            for schema in schemas:
                query = conn.execute(text("SELECT distinct(table_name) FROM information_schema.columns WHERE table_schema like '"+schema[0]+"'"))
                tables = query.fetchall()
                self._schema[schema[0]] = {}
                for table in tables:
                    query = conn.execute(text("SELECT column_name FROM information_schema.columns	WHERE table_schema like '"+schema[0]+"' AND table_name like '"+table[0]+"';"))
                    columns = query.fetchall()
                    self._schema[schema[0]][table[0]] = []
                    for column in columns:
                        self._schema[schema[0]][table[0]].append(column[0])

            #Get database relations
            query = conn.execute(text("""SELECT
                                            distinct concat(tc.table_schema,'.', tc.table_name) as table_name, 
                                            concat(ccu.table_schema,'.', ccu.table_name) AS foreign_table_name,
                                            kcu.column_name, 
                                            ccu.column_name AS foreign_column_name 
                                        FROM information_schema.table_constraints AS tc 
                                        JOIN information_schema.key_column_usage AS kcu
                                            ON tc.constraint_name = kcu.constraint_name
                                            AND tc.table_schema = kcu.table_schema
                                        JOIN information_schema.constraint_column_usage AS ccu
                                            ON ccu.constraint_name = tc.constraint_name
                                        WHERE tc.constraint_type = 'FOREIGN KEY'"""))
            columns = query.keys()
            relations = query.fetchall()
            relationsdf = pd.DataFrame(data=relations, columns=columns)
            relationsdf = pd.concat([relationsdf,pd.DataFrame(data={"table_name":relationsdf["foreign_table_name"],
                                                        "foreign_table_name":relationsdf["table_name"],
                                                        "column_name":relationsdf["foreign_column_name"],
                                                        "foreign_column_name":relationsdf["column_name"]})])

            for table in relationsdf["table_name"].unique():
                relations_per_table = relationsdf.loc[relationsdf["table_name"]== table ]
                relations_dict = {}
                for foreign_table_name in relations_per_table["foreign_table_name"]:
                    relation = relations_per_table.loc[relations_per_table["foreign_table_name"]==foreign_table_name].values[0]
                    relations_dict[relation[1]] = {relation[2]:relation[3]}
                self._relation.update({table:relations_dict}) 
                
