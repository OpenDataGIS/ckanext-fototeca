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

        #create query 
        query = self._create_query(columns, route, prev, "left join")
        print(query)

        with self._engine.connect() as conn:
            request = conn.execute(text(query))
            columns = request.fetchall()
        
        print(columns)

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
        print("tablas ",tables)
        tables_in_query = [tables[0]]
        for i in tables[:0:-1]:
            key1 = i
            key2 = ""
            print(i)
            for table in tables_in_query:
                print("relations in ",table," : \n",self._relation[table])
                print("relations in ",i," : \n",self._relation[i])
                if i in self._relation[table]:
                    print("Está")
                    key1 += "."+str(list(self._relation[i][table].keys())[0])
                    key2 = table+"."+str(list(self._relation[i][table].values())[0])
                    break

                elif table in self._relation[i]:
                    print("Está - alt")
                    key1 += "."+str(list(self._relation[table][i].keys())[0])
                    key2 = table+"."+str(list(self._relation[table][i].values())[0])

                else:
                    print("no está")

            tables_in_query.append(i)
            #for table in tables_in_query:
            #    if join_table is None:
            #        print("es None")
            #        if prev[table] in self._relation[i]:
            #            join_table = table
                    
            #print(prev)
            query += " ".join([" ",join," ",i," on ",key1," = ",key2])
                
        return query
            

    def get_schema(self):
        return self._schema
        
    
    def get_relation(self):
        return self._relation