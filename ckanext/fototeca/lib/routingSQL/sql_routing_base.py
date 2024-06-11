import psycopg2
import pandas as pd 
from sqlalchemy import engine, create_engine, text
import logging, heapq

class routingBase:
    logging.getLogger().addHandler(logging.StreamHandler())
    _engine = None
    _schema = {}
    _relation = {}
 
    _supported_services= ['postgres']

    def get_columns(self,columns: list):

        #Get route between tables
        tables = []
        for column in columns:
            tables.append(".".join(column.split(".")[0:2]))
        route = [heapq.heappop(tables)]
        prev = {}
        first_run = True
        while tables:
            next_route = ([],float("inf"))
            next_table = heapq.heappop(tables)
            if next_table not in route:  
                for node in route:
                    #print("node is : "+node+", next table is :"+next_table)
                    check_route = self._dijkastra(node,next_table)   
                    if next_route[1] > check_route[1]:
                        next_route = check_route
                route = route+next_route[0][1:]
                if first_run:
                    prev = next_route[2]
                else:
                    for key in prev.keys():
                        if prev[key] is None:
                            prev[key] = next_route[2][key]
                first_run = False
                
            print(prev)

        #create query 
        query = self._create_query(columns, route, prev, "left join")

    def _dijkastra(self,from_table, to_table):
        
        
        if from_table == to_table:
             raise ValueError("from_table can't be equal to to_table")
        costs = {}
        prev = {}
        route = []
        for table in self._relation.keys():
            costs[table] = float("inf")
            prev[table] = None
        costs[from_table] = 0

        queue = [(0,from_table)]

        while queue:
            current_cost, current_table = heapq.heappop(queue)
            if current_cost > costs[current_table]:
                continue
            for neighbor, key in self._relation[current_table].items():
                cost = current_cost + 1
                if cost < costs[neighbor]:
                    costs[neighbor] = cost
                    prev[neighbor] = current_table                    
                    heapq.heappush(queue, (cost, neighbor))
        route = [to_table] 
        prev_table = to_table    
        end = True
        while end: 
            if prev[prev_table] is not None:
                route.append(prev_table)
                prev_table = prev[prev_table]
            else:
                end = False

        return route, costs[to_table], prev

    
    def _create_query(self,columns,tables,prev,join):
        #print(prev)
        columns_joined = " ,".join(list(columns))
        query = "select "+columns_joined
        query += " from "+ tables[0]
        #print(tables)
        for i in range(len(tables)-1):
            print("tabla1 : "+tables[i+1]+ ", tabla2 : "+tables[i+2])
            relation_table = self._relation[prev[tables[i+1]]]
            if prev[tables[i+2]] not in relation_table:
                for table in tables:
                    if prev[table] in relation_table:
                        fk_table = table
                        break
                print(1)
            else:
                fk_table = tables[i+2]
                print(2)
            
            print(relation_table)
            pk = relation_table[fk_table]
            print(pk)
            query += " ".join([join,tables[i+1],"on",str(pk.keys()),str(pk.values())])
        return query
            

    def get_schema(self):
        return self._schema
        
    
    def get_relation(self):
        return self._relation