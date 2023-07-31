import sqlite3
from utils import config

class Connection():
    "Used to access a SQLite3 database."
    
    def __init__(self):
        self.conn = sqlite3.connect(config.database_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def command(self, command, values):
        """Send command to the database. Returns `None`.
        
        ----------
        command: :class:`str`
            SQL Command.
        
        ----------
        `DataBase.command("UPDATE ...", [cookie_id])`
        """

        self.cursor.execute(command, values)
        self.conn.commit()

    def insert(self, table : str, values : list) -> None:
        """Insert data into a table.
        
        ----------
        table: :class:`str`
            Name of table to insert in.
        values: :class:`list`
            List of values to be added to the table, in order of columns.
        
        ----------
        `DataBase.insert("tablename", ["value1", "value2"])`
        """
        
        data = ""
        for _ in range(len(values)): data += "?,"
        data = data[:-1]
        
        newvalues = []
        for item in values:
            newvalues.append(str(item))

        self.cursor.execute(f"INSERT INTO {table} VALUES ({data})", newvalues)
        self.conn.commit()

    def query2(self, command:str, values:list, fetchOne:bool):
        """Querys the database. Returns `tuple`, `list`, `[]` or `None`.
        
        ----------
        command: :class:`str`
            SQL Command.
        values: :class:`list`
            List of values to replace ?
        fetchOne :class:`bool`
            Fetch one entry from database
        
        ----------
        `DataBase.query2("SELECT rowid, source FROM history WHERE cookie = ?", [cookie_id], True)`
        """

        if values == []:
            cur = self.conn.execute(command)
        else:
            cur = self.conn.execute(command, values)
        if fetchOne == True:
            res = cur.fetchone()
        else:
            res = cur.fetchall()
        cur.close()
        
        return res
    
    def query(self, table : str, columns : list, where : dict={}, fetchOne : bool=True, orOrAnd="AND"):
        """Querys the database. Returns `tuple`, `list`, `[]` or `None`.
        
        ----------
        table: :class:`str`
            Name of table to query in.
        columns: :class:`list`
            List of column names to gather data from.
        where: :class:`dict = {}`
            List of columm names used to filter data.
        fetchOne: :class:`bool = True`
            Fetch the first value which matched the arguements.
            Or to fetch all data from the table that matches.
        orOrAnd: :class:`str`
            Whether to use the "AND" or "OR" statement when using "WHERE".
        
        ----------
        `DataBase.query("tablename", ["column1", "column2"], {"column1": "value1"}, False)`
        
        "column1"'s value has to equal "value1"'s value to be valid and to not be filtered out.
        """
        
        columnsdata = "rowid, "
        for column in columns:
            columnsdata += f"{column}, "
        columnsdata = columnsdata[:-2]

        values = []
        if len(where) != 0:
            wheredata = " WHERE "
            for key, value in where.items():
                wheredata += f"{key} = ? {orOrAnd} "
                values.append(str(value))
            if orOrAnd == "AND": wheredata = wheredata[:-5]
            else: wheredata = wheredata[:-4]
        else: wheredata = ""

        cur = self.conn.execute(f"SELECT {columnsdata} FROM {table}{wheredata}", values)
        if fetchOne == True:
            res = cur.fetchone()
        else:
            res = cur.fetchall()
        cur.close()
        
        return res
    
    def edit(self, table : str, newvalues : dict, where : dict, orOrAnd="AND") -> None:
        """Edits an entry in the database.
        
        ----------
        table: :class:`str`
            Name of table to edit in.
        newvalues: :class:`dict`
            Dict of the new data to be edited.
        where: :class:`dict`
            Dict of the columns and values to be used.
        orOrAnd: :class:`str`
            Whether to use the "AND" or "OR" statement when using "WHERE".
        
        ----------
        `DataBase.edit("tablename", {"column1": "newvalue1"}, {"column2": "value2"})`
        
        "column2"'s value has to equal "value2"'s value to be valid and to not be filtered out.
        """
        
        values = []

        setData = ""
        for key, value in newvalues.items():
            setData += f"{key} = ?, "
            values.append(str(value))
        setData = setData[:-2]

        wheredata = ""
        for key, value in where.items():
            wheredata += f"{key} = ? {orOrAnd} "
            values.append(str(value))
        if orOrAnd == "AND": wheredata = wheredata[:-5]
        else: wheredata = wheredata[:-4]

        self.conn.execute(f"UPDATE {table} SET {setData} WHERE {wheredata}", values)
        self.conn.commit()

    def delete(self, table : str, where : dict, orOrAnd="AND", whereOverRide=None, valuesOverRide=None) -> None:
        """Deletes an entry in the database.
        
        ----------
        table: :class:`str`
            Name of table to edit in.
        where: :class:`dict`
            Dict of the columns and values to be used.
            
        
        ----------
        `DataBase.delete("tablename", {"column2": "value2"})`
        
        "column2"'s value has to equal "value2"'s value to be valid and to not be filtered out.
        """
        
        values = []

        if whereOverRide is None:
            wheredata = ""
            for key, value in where.items():
                wheredata += f"{key} = ? {orOrAnd} "
                values.append(str(value))
            if orOrAnd == "AND": wheredata = wheredata[:-5]
            else: wheredata = wheredata[:-4]

            self.cursor.execute(f"DELETE FROM {table} WHERE {wheredata}", values)
            self.conn.commit()
        else:
            self.cursor.execute(f"DELETE FROM {table} WHERE {whereOverRide}", valuesOverRide)
            self.conn.commit()

    def close(self) -> None:
        """Closes the database connection.

        ----------
        `DataBase.close()`
        """
        
        self.cursor.close()
        self.conn.close()